#!/usr/bin/env python3
import argparse,concurrent.futures,json,subprocess,time
from pathlib import Path
from pypdf import PdfReader
p=argparse.ArgumentParser();p.add_argument('corpus',type=Path);p.add_argument('--pdfimages',default='pdfimages');a=p.parse_args();root=a.corpus;manifest=json.loads((root/'04_metadata/corpus_manifest.json').read_text());qa=json.loads((root/'04_metadata/page_quality_screening.json').read_text());checks={(p['documentId'],p['pdfPage']):p for p in qa['pages']};engine=a.pdfimages;started=time.monotonic()
benchdocs={'PB-2AA72AC4BCC169AA','PB-B077EA633FFBFD29'}
def run(x):
 id=x['document_id'];source=root/x['file'];reader=PdfReader(source);sizes=[(float(p.mediabox.width),float(p.mediabox.height)) for p in reader.pages];out=subprocess.check_output([engine,'-list',str(source)],timeout=120).decode();coverage={}
 for line in out.splitlines()[2:]:
  cols=line.split()
  try:
   if cols[2]!='image' or '[inline]' in cols:continue
   n=int(cols[0]);w,h=float(cols[3]),float(cols[4]);xppi,yppi=float(cols[-4]),float(cols[-3]);pw,ph=sizes[n-1];area=(w*72/xppi)*(h*72/yppi)/(pw*ph);coverage[n]=max(coverage.get(n,0),min(area,1))
  except (ValueError,IndexError,ZeroDivisionError):continue
 rows=[]
 for n,(pw,ph) in enumerate(sizes,1):
  c=checks[(id,n)];cover=coverage.get(n,0);scan=cover>=.65;needs=('no-text' in c['flags']) or scan
  if not needs:continue
  rows.append(dict(documentId=id,pdfPage=n,file=x['file'],sourceSha256=x['sha256'],title=x['title'],width=pw,height=ph,scanCoverage=round(cover,3),split=pw/ph>1.18,reason='missing-text' if 'no-text' in c['flags'] else 'scanned-page',priority=100 if id in benchdocs else c['priority']+20,referenceBenchmark=id in benchdocs,flags=c['flags']))
 print(x['file'],len(rows),'OCR-sidor',flush=True);return rows
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for result in pool.map(run,[x for x in manifest if x['file'].endswith('.pdf')]):rows.extend(result)
rows.sort(key=lambda x:(-x['priority'],x['documentId'],x['pdfPage']));plan=dict(schemaVersion=1,createdAt=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),elapsedSeconds=time.monotonic()-started,pages=rows);(root/'04_metadata/ocr_batch_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n');print('KLART',len(rows),'sidor',time.monotonic()-started,'sekunder',flush=True)
