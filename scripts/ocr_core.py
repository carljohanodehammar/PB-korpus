#!/usr/bin/env python3
"""Separat kalibrerad OCR-version av två äldre kärnverk; ingen råtext ersätts."""
import argparse,concurrent.futures,datetime,hashlib,json,subprocess,tempfile,time
from pathlib import Path
from PIL import Image
from ocr_batch import ocr
p=argparse.ArgumentParser();p.add_argument('corpus',type=Path);p.add_argument('--plan',type=Path,required=True);p.add_argument('--engine',type=Path,required=True);p.add_argument('--models',type=Path,required=True);p.add_argument('--renderer',type=Path,required=True);p.add_argument('--reference-only',action='store_true');p.add_argument('--workers',type=int,default=1);p.add_argument('--document-id',action='append',help='Dokument att bearbeta; får upprepas');p.add_argument('--deadline',required=True);a=p.parse_args();deadline=datetime.datetime.fromisoformat(a.deadline);started=time.monotonic();ids=set(a.document_id or ['PB-2AA72AC4BCC169AA','PB-B077EA633FFBFD29']);plan=[r for r in json.loads(a.plan.read_text())['pages'] if r['documentId'] in ids];ref=json.loads((Path(__file__).resolve().parents[1]/'editorial/edition.json').read_text())['pages'];keys={(p['documentId'],p['pdfPage']) for p in ref};plan=[r for r in plan if not a.reference_only or (r['documentId'],r['pdfPage']) in keys];models={'swe':hashlib.sha256((a.models/'swe.traineddata').read_bytes()).hexdigest()};done=[];errors=[]
def run(row):
 id=row['documentId'];n=row['pdfPage'];out=a.corpus/'02_ocr/tesseract-core-v4'/id/f'p{n:04d}.json'
 if out.exists():
  old=json.loads(out.read_text());assert old['sourceSha256']==row['sourceSha256'] and old['modelHashes']==models;return dict(documentId=id,pdfPage=n,cached=True)
 if datetime.datetime.now(datetime.timezone.utc)>=deadline:return dict(documentId=id,pdfPage=n,skipped=True)
 with tempfile.TemporaryDirectory(prefix='pb-core-') as folder:
  tmp=Path(folder);imagepath=tmp/'page';subprocess.run([str(a.renderer),'-f',str(n),'-l',str(n),'-scale-to','2800','-singlefile','-png',str(a.corpus/row['file']),str(imagepath)],check=True,capture_output=True,timeout=180);im=Image.open(imagepath.with_suffix('.png')).convert('RGB');roundtrip=tmp/'roundtrip.jpg';im.save(roundtrip,quality=92);im=Image.open(roundtrip).convert('RGB');w,h=im.size;boxes=[(0,0,w//2,h),(w//2,0,w,h)] if row['split'] else [(0,0,w,h)];segments=[];candidates=[]
  for i,box in enumerate(boxes):
   crop=tmp/f'part-{i}.jpg';im.crop(box).save(crop,quality=92);r=ocr(a.engine,a.models,crop,tmp/f'text-{i}','swe');segments.append(r['text']);candidates.append(dict(segment=i,selectedLanguage='swe',alternatives=[{k:v for k,v in r.items() if k!='text'}]))
  weights=[max(1,len(s)) for s in segments];confidence=sum(r['alternatives'][0]['confidence']*w for r,w in zip(candidates,weights))/sum(weights)
  data=dict(schemaVersion=1,documentId=id,pdfPage=n,sourceSha256=row['sourceSha256'],createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),engineVersion='Tesseract 5.5.3; LSTM; psm 3; core-v4',modelHashes=models,renderScaleTo=2800,imageMode='RGB JPEG quality 92',automaticSplit=row['split'],selectionReason='calibrated core work; Swedish model',referenceBenchmark=(id,n) in keys,calibratedWork=True,segments=segments,text='\n\n'.join(segments),confidence=round(confidence,2),candidates=candidates,reviewStatus='machine-ocr-unreviewed',needsReview=True,statisticsParser='tsv-quote-none-v1')
 out.parent.mkdir(parents=True,exist_ok=True);temp=out.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False)+'\n');temp.replace(out);return dict(documentId=id,pdfPage=n,confidence=data['confidence'])
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
 for future in [pool.submit(run,row) for row in plan]:
  try:done.append(future.result())
  except Exception as e:errors.append(str(e))
  if len(done)%25==0:print('KLARA',len(done),'/',len(plan),flush=True)
report=dict(schemaVersion=1,completed=len(done),planned=len(plan),errors=errors,elapsedSeconds=round(time.monotonic()-started,1),updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),referenceOnly=a.reference_only)
(a.corpus/'04_metadata/ocr_core_progress.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('SLUT',json.dumps(report,ensure_ascii=False),flush=True)
