#!/usr/bin/env python3
"""Kontrollera alla ord och deras ursprungliga följd mot Bellman-XML."""
import argparse,bz2,datetime,hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('corpus',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];out=root/'docs/reference-texts'
meta=json.loads((out/'index.json').read_text());source=a.corpus/'01_original/bellman.xml.bz2';assert hashlib.sha256(source.read_bytes()).hexdigest()==meta['sourceSha256'];data=ET.fromstring(bz2.open(source,'rt').read());count=0
assert len(data)==len(meta['books'])
for t,b in zip(data,meta['books']):
 book=json.loads((out/f'{b["id"]}.json').read_text());assert t.attrib['title']==book['title']
 js=(out/f'{b["id"]}.js').read_text().split(']=',1)[1].rstrip(';\n');assert json.loads(js)==book
 pairs=[]
 for page in book['pages']:
  assert len(page['tokens'])==len(page['sourceWordOrdinals'])==page['wordTokens']
  assert ' '.join(page['tokens'])==' '.join(page['paragraphs'])
  pairs.extend(zip(page['sourceWordOrdinals'],page['tokens']))
 pairs.sort();ref=[w.text or '' for w in t.iter('w')]
 assert [i for i,w in pairs]==list(range(1,len(ref)+1))
 assert [w for i,w in pairs]==ref,'Ordföljd eller text ändrad'
 count+=len(ref)
assert count==meta['wordTokens']==452030
receipt=dict(checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='passed',books=len(data),wordTokens=count,sourceSha256=meta['sourceSha256'],checks=['Varje ord exakt en gång','Ordtecken och ursprunglig följd oförändrade','JSON och lokalt laddbar JS identiska','Originalets kontrollsumma oförändrad'])
(root/'docs/bellman-validation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');(a.corpus/'04_metadata/bellman_reference_validation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))
