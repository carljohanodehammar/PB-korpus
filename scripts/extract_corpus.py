#!/usr/bin/env python3
"""Extrahera hela PDF-korpusen; bevara pilotens redan granskade textlager."""
import argparse,concurrent.futures,datetime,hashlib,json,subprocess,time,unicodedata
from pathlib import Path

def metrics(text):
 import re
 words=re.findall(r'\S+',text);letters=sum(c.isalpha() for c in text);single=sum(len(w)==1 and w.isalpha() for w in words);bad=sum(c=='\ufffd' or (unicodedata.category(c).startswith('C') and c not in '\n\t\r') for c in text)
 flags=[]
 if not text.strip():flags.append('no-text')
 elif letters<40:flags.append('little-text')
 if words and single/len(words)>.12:flags.append('many-single-letters')
 if text and letters/len(text)<.4:flags.append('low-letter-ratio')
 if bad:flags.append('invalid-characters')
 return dict(characters=len(text),words=len(words),flags=flags,priority=100 if 'no-text' in flags else 80 if 'invalid-characters' in flags else 60 if 'many-single-letters' in flags else 40 if 'low-letter-ratio' in flags else 20 if flags else 0)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('corpus',type=Path);p.add_argument('--pdftotext',default='pdftotext');p.add_argument('--workers',type=int,default=3);a=p.parse_args();started=time.monotonic();site=Path(__file__).resolve().parents[1]/'docs';dest=site/'texts';dest.mkdir(exist_ok=True);local=a.corpus/'02_ocr/full';local.mkdir(parents=True,exist_ok=True);meta=a.corpus/'04_metadata';manifest=json.loads((meta/'corpus_manifest.json').read_text());pdfs=[x for x in manifest if x['file'].lower().endswith('.pdf')];old=json.loads((site/'assets/pilot.js').read_text().split(' = ',1)[1].rstrip(';\n'));old_ids={d['id'] for d in old['documents']};qa=[]
 def run(x):
  source=a.corpus/x['file'];h=hashlib.sha256(source.read_bytes()).hexdigest()
  if h!=x['sha256']:raise ValueError('Kontrollsumma avviker: '+x['file'])
  id=x['document_id'];target=dest/(id+'.json')
  if id in old_ids and target.exists():data=json.loads(target.read_text());units=data['pages']
  else:
   raw=subprocess.check_output([a.pdftotext,'-layout','-enc','UTF-8',str(source),'-'],timeout=180).decode();texts=raw.split('\f')
   if not texts[-1].strip():texts.pop()
   if len(texts)!=x['page_count']:raise ValueError('Sidantal avviker: '+x['file'])
   units=[dict(pdfPage=i+1,printedPage=None,text=t.strip()) for i,t in enumerate(texts)];data=dict(schemaVersion=1,documentId=id,title=x['title'],sourceSha256=h,method='Poppler pdftotext -layout; existing PDF text layer; no new OCR',extractedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),pages=units);payload=json.dumps(data,ensure_ascii=False);target.write_text(payload+'\n');(dest/(id+'.js')).write_text('window.PB_TEXTS=window.PB_TEXTS||{};window.PB_TEXTS['+json.dumps(id)+']='+payload.replace('<','\\u003c')+';\n')
  # Grundextraktionen bevaras som råtext, även om webbversionen har läsordningstillägg.
  rawdata={**data,'pages':[dict(pdfPage=u['pdfPage'],printedPage=u.get('printedPage'),text=u['text']) for u in units]};(local/(id+'.json')).write_text(json.dumps(rawdata,ensure_ascii=False)+'\n')
  checks=[dict(documentId=id,pdfPage=u['pdfPage'],**metrics(u['text'])) for u in units];row=dict(id=id,title=x['title'],pages=len(units),textPages=sum(bool(u['text']) for u in units),emptyPages=[u['pdfPage'] for u in units if not u['text']],characters=sum(len(u['text']) for u in units),sourceSha256=h,documentUrl=x.get('download_url') or x.get('url'),extractedAt=data['extractedAt'])
  return row,checks
 documents=[];errors=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
  futures={pool.submit(run,x):x for x in pdfs}
  for f in concurrent.futures.as_completed(futures):
   try:row,checks=f.result();documents.append(row);qa.extend(checks);print(len(documents),row['title'],row['textPages'],'/',row['pages'],flush=True)
   except Exception as e:errors.append(dict(file=futures[f]['file'],error=str(e)));print('FEL',errors[-1],flush=True)
 documents.sort(key=lambda d:d['title']);data=dict(schemaVersion=1,method='Befintliga textlager i hela PDF-korpusen',documents=documents);(site/'assets/pilot.js').write_text('window.PB_PILOT = '+json.dumps(data,ensure_ascii=False,indent=2).replace('<','\\u003c')+';\n');(meta/'full_text_extraction.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');qa.sort(key=lambda x:(-x['priority'],x['documentId'],x['pdfPage']));report=dict(schemaVersion=1,checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='Heuristisk screening av textlager; inga sidor märks korrekturlästa av detta',elapsedSeconds=round(time.monotonic()-started,1),errors=errors,pages=qa);(meta/'page_quality_screening.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(site/'quality-screening.json').write_text(json.dumps(report,ensure_ascii=False)+'\n');print('KLART',len(documents),'dokument',len(qa),'sidor',report['elapsedSeconds'],'sekunder',len(errors),'fel',flush=True)
