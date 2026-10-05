#!/usr/bin/env python3
"""Bearbeta endast visuellt granskade uppslag; bevara råtext och varje OCR-ord."""
import argparse,collections,datetime,hashlib,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
REVIEWED={'PB-2AA72AC4BCC169AA':[20,55],'PB-B077EA633FFBFD29':[20]}
NS={'h':'http://www.w3.org/1999/xhtml'}
def reorder(xml):
 page=ET.fromstring(xml).find('.//h:page',NS);middle=float(page.get('width'))/2
 groups=[[],[]];original=[]
 for line in page.findall('.//h:line',NS):
  halves=[[],[]]
  for word in line.findall('h:word',NS):
   token=word.text or '';original.append(token)
   side=int((float(word.get('xMin'))+float(word.get('xMax')))/2>=middle)
   halves[side].append(token)
  for side,words in enumerate(halves):
   if words:groups[side].append((float(line.get('yMin')),float(line.get('xMin')),' '.join(words)))
 sections=['\n'.join(x[2] for x in sorted(g)) for g in groups]
 text='\n\n'.join(sections)
 assert collections.Counter(text.split())==collections.Counter(' '.join(original).split()),'Ord förlorade eller dubblerade'
 return text,len(original)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('corpus',type=Path);p.add_argument('--pdftotext',default='pdftotext');a=p.parse_args()
 site=Path(__file__).resolve().parents[1]/'docs';manifest={x['document_id']:x for x in json.loads((a.corpus/'04_metadata/corpus_manifest.json').read_text())};records=[]
 dest=a.corpus/'03_normaliserad_text/pilot';dest.mkdir(parents=True,exist_ok=True)
 for id,reviewed in REVIEWED.items():
  x=manifest[id];source=a.corpus/x['file'];assert hashlib.sha256(source.read_bytes()).hexdigest()==x['sha256']
  raw=json.loads((a.corpus/'02_ocr/pilot'/(id+'.json')).read_text());raw['schemaVersion']=2
  for n in reviewed:
   xml=subprocess.check_output([a.pdftotext,'-f',str(n),'-l',str(n),'-bbox-layout',str(source),'-']).decode()
   text,count=reorder(xml);unit=raw['pages'][n-1];unit['readingText']=text;unit['readingOrder']='Vänster boksida uppifrån ned, därefter höger; ordpositioner i PDF; visuellt granskat uppslag'
   records.append(dict(documentId=id,pdfPage=n,words=count,method=unit['readingOrder'],characterCorrections=0))
  payload=json.dumps(raw,ensure_ascii=False)+'\n';(dest/(id+'.json')).write_text(payload);(site/'texts'/(id+'.json')).write_text(payload)
  (site/'texts'/(id+'.js')).write_text('window.PB_TEXTS = window.PB_TEXTS || {}; window.PB_TEXTS['+json.dumps(id)+'] = '+payload.replace('<','\\u003c')+';\n')
 log=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),changes=records,scope='Endast tre granskade uppslag; råtext bevarad; inga tecken rättade')
 (a.corpus/'04_metadata/pilot_reading_order.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n');(site/'reading-order.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n');print(json.dumps(log,ensure_ascii=False,indent=2))
