#!/usr/bin/env python3
"""Jämför separat OCR-version mot det befintliga arbetsfacit, inte ett oberoende test."""
import argparse,datetime,json,re,unicodedata
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('corpus',type=Path);parser.add_argument('--version',default='tesseract-core-v4');parser.add_argument('--field',default='coreCalibrationV4');args=parser.parse_args();root=Path(__file__).resolve().parents[1];corpus=args.corpus;selected=json.loads((root/'editorial/edition.json').read_text())['pages']
def words(s):
 s=unicodedata.normalize('NFC',s.lower());s=re.sub(r'([a-zåäöé])-\s*\n\s*(?=[a-zåäöé])',r'\1',s);return re.findall(r'[^\W_]+',s)
def distance(a,b):
 prev=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  row=[i]
  for j,y in enumerate(b,1):row.append(min(row[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
  prev=row
 return prev[-1]
rows=[]
for p in selected:
 r=json.loads((root/'editorial/revisions'/p['revisions'][-1]).read_text());ref=words('\n\n'.join(r['segments']));c=json.loads((corpus/'02_ocr'/args.version/p['documentId']/f'p{p["pdfPage"]:04d}.json').read_text());errors=distance(ref,words(c['text']));rows.append(dict(documentId=p['documentId'],pdfPage=p['pdfPage'],referenceWords=len(ref),errors=errors,wordErrorRate=errors/len(ref),confidence=c['confidence'],languages=[s['selectedLanguage'] for s in c['candidates']]))
b=json.loads((root/'docs/ocr-benchmark.json').read_text());b[args.field]=dict(method=args.version,wordErrorRate=sum(r['errors'] for r in rows)/sum(r['referenceWords'] for r in rows),pages=rows);b['checkedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
for p in b['pages']:
 for m in p['methods']:m.pop('textFile',None)
(root/'docs/ocr-benchmark.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');(corpus/'04_metadata/ocr_benchmark.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');print(json.dumps(b[args.field],ensure_ascii=False,indent=2))
