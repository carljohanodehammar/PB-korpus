#!/usr/bin/env python3
"""Återupptagbar OCR-körning med tidsgräns. Råtext och original ändras aldrig."""
import argparse,concurrent.futures,csv,datetime,hashlib,json,os,subprocess,tempfile,time
from pathlib import Path

def read_statistics(path):
 conf=[]
 with path.open() as f:
  for row in csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE):
   if row['text'].strip() and float(row['conf'])>=0:conf.append((float(row['conf']),max(1,len(row['text']))))
 return (sum(c*n for c,n in conf)/sum(n for _,n in conf) if conf else 0),len(conf)

def ocr(engine,models,image,target,language):
 start=time.monotonic();subprocess.run([str(engine),str(image),str(target),'--tessdata-dir',str(models),'-l',language,'--oem','1','--psm','3','-c','tessedit_create_txt=1','-c','tessedit_create_tsv=1'],check=True,capture_output=True,timeout=180,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
 text=target.with_suffix('.txt').read_text();score,count=read_statistics(target.with_suffix('.tsv'))
 return dict(text=text.strip(),confidence=round(score,2),words=count,language=language,elapsedSeconds=round(time.monotonic()-start,2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('corpus',type=Path);p.add_argument('--plan',type=Path,required=True);p.add_argument('--engine',type=Path,required=True);p.add_argument('--models',type=Path,required=True);p.add_argument('--renderer',type=Path,required=True);p.add_argument('--python',default='python3');p.add_argument('--workers',type=int,default=3);p.add_argument('--version',default='tesseract-best-v2');p.add_argument('--reuse-version',default='tesseract-best');p.add_argument('--run-id',default='batch',choices=['batch','benchmark','tail','checks']);p.add_argument('--deadline',required=True,help='Absolut UTC-tid, ISO-format');a=p.parse_args();deadline=datetime.datetime.fromisoformat(a.deadline);started=time.monotonic();startutc=datetime.datetime.now(datetime.timezone.utc);dest=a.corpus/'02_ocr'/a.version;dest.mkdir(parents=True,exist_ok=True);plan=json.loads(a.plan.read_text())['pages'];modelhashes={f.stem:hashlib.sha256(f.read_bytes()).hexdigest() for f in a.models.glob('*.traineddata')};progress=a.corpus/f'04_metadata/ocr_{a.run_id}_progress.json';events=a.corpus/f'04_metadata/ocr_{a.run_id}_events.jsonl';completed=[];errors=[];skipped=[]
 # Bildbeskärning körs med den Python-miljö som har Pillow, från samma process.
 from PIL import Image,ImageOps
 def run(row):
  id=row['documentId'];n=row['pdfPage'];out=dest/id/f'p{n:04d}.json'
  if out.exists():
   old=json.loads(out.read_text())
   if old['sourceSha256']==row['sourceSha256'] and old['modelHashes']==modelhashes:return dict(documentId=id,pdfPage=n,cached=True,confidence=old['confidence'],characters=len(old['text']))
   raise ValueError('Befintlig OCR-version avviker; använd ny versionsmapp')
  previous=a.corpus/'02_ocr'/a.reuse_version/id/f'p{n:04d}.json'
  if previous.exists():
   old=json.loads(previous.read_text())
   reliable=old['sourceSha256']==row['sourceSha256'] and old['modelHashes']==modelhashes
   for segment,c in zip(old['segments'],old['candidates']):
    selected=next(x for x in c['alternatives'] if x['language']==c['selectedLanguage']);count=len(segment.split());reliable &= '"' not in segment and len(c['alternatives'])==1 and abs(selected['words']-count)<=max(2,.03*count)
   if reliable:
    old['statisticsParser']='tsv-quote-none-v1; prior row counts checked';old['reusedFrom']=a.reuse_version;out.parent.mkdir(parents=True,exist_ok=True);tmpout=out.with_suffix('.tmp');tmpout.write_text(json.dumps(old,ensure_ascii=False)+'\n');tmpout.replace(out);return dict(documentId=id,pdfPage=n,cached=True,confidence=old['confidence'],characters=len(old['text']))
  if datetime.datetime.now(datetime.timezone.utc)>=deadline:return dict(documentId=id,pdfPage=n,skipped='time-budget')
  with tempfile.TemporaryDirectory(prefix='pb-ocr-') as folder:
   temp=Path(folder);imfile=temp/'page';subprocess.run([str(a.renderer),'-f',str(n),'-l',str(n),'-scale-to','3200','-singlefile','-png',str(a.corpus/row['file']),str(imfile)],check=True,capture_output=True,timeout=180);image=Image.open(imfile.with_suffix('.png')).convert('RGB');w,h=image.size;boxes=[(0,0,w//2,h),(w//2,0,w,h)] if row['split'] else [(0,0,w,h)];segments=[];candidates=[]
   for i,box in enumerate(boxes):
    crop=temp/f'segment-{i}.png';ImageOps.grayscale(image.crop(box)).save(crop);first=ocr(a.engine,a.models,crop,temp/f'swe-{i}','swe');options=[first]
    # Frakturstil provas bara när svensk antikva-OCR har låg säkerhet.
    if first['words']>=10 and first['confidence']<85 and 'Fraktur' in modelhashes and datetime.datetime.now(datetime.timezone.utc)<deadline:
     alternative=ocr(a.engine,a.models,crop,temp/f'fraktur-{i}','Fraktur');options.append(alternative)
    chosen=max(options,key=lambda x:x['confidence']);segments.append(chosen['text']);candidates.append(dict(segment=i,selectedLanguage=chosen['language'],alternatives=[{k:v for k,v in x.items() if k!='text'} for x in options]))
   weights=[max(1,len(x)) for x in segments];confidence=sum(max(c['alternatives'],key=lambda x:x['confidence'])['confidence']*weight for c,weight in zip(candidates,weights))/sum(weights);text='\n\n'.join(segments)
  result=dict(schemaVersion=1,documentId=id,pdfPage=n,sourceSha256=row['sourceSha256'],createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),engineVersion='Tesseract 5.5.3; LSTM; psm 3',modelHashes=modelhashes,renderScaleTo=3200,automaticSplit=row['split'],selectionReason=row['reason'],referenceBenchmark=row.get('referenceBenchmark',False),segments=segments,text=text,confidence=round(confidence,2),candidates=candidates,reviewStatus='machine-ocr-unreviewed',needsReview=True,statisticsParser='tsv-quote-none-v1')
  out.parent.mkdir(parents=True,exist_ok=True);tmpout=out.with_suffix('.tmp');tmpout.write_text(json.dumps(result,ensure_ascii=False)+'\n');tmpout.replace(out);return dict(documentId=id,pdfPage=n,cached=False,confidence=result['confidence'],characters=len(text))
 def status(state):
  data=dict(schemaVersion=1,state=state,startedAt=startutc.isoformat(),updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),deadline=deadline.isoformat(),planned=len(plan),completed=len(completed),errors=errors,skipped=len(skipped),elapsedSeconds=round(time.monotonic()-started,1),nonempty=sum(x['characters']>0 for x in completed));tmp=progress.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.replace(progress);return data
 status('running')
 # Begränsad kö: inget nytt arbete startar efter tidsgränsen.
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
  iterator=iter(plan);pending={}
  def submit():
   try:row=next(iterator)
   except StopIteration:return False
   if datetime.datetime.now(datetime.timezone.utc)>=deadline:skipped.append(row);return False
   pending[pool.submit(run,row)]=row;return True
  for _ in range(a.workers):submit()
  while pending:
   done,_=concurrent.futures.wait(pending,return_when=concurrent.futures.FIRST_COMPLETED)
   for f in done:
    row=pending.pop(f)
    try:
     r=f.result()
     if r.get('skipped'):skipped.append(r)
     else:completed.append(r)
     with events.open('a') as event:event.write(json.dumps(r,ensure_ascii=False)+'\n')
    except Exception as e:errors.append(dict(documentId=row['documentId'],pdfPage=row['pdfPage'],error=str(e)));print('FEL',errors[-1],flush=True)
    submit()
   data=status('running')
   if len(completed)%25<a.workers:print('KLARA',len(completed),'/',len(plan),'sekunder',data['elapsedSeconds'],'fel',len(errors),flush=True)
 # Återstående planposter räknas när tidsbudgeten löper ut.
 if datetime.datetime.now(datetime.timezone.utc)>=deadline:skipped.extend(iterator)
 data=status('complete' if len(completed)==len(plan) else 'budget-stopped' if skipped else 'complete-with-errors');print('SLUT',json.dumps(data,ensure_ascii=False),flush=True)
