#!/usr/bin/env python3
"""Publicera enbart godkänd katalogmetadata; kopiera aldrig originalfiler."""
import argparse, datetime, json, re
from pathlib import Path

def group(name):
 n=name.lower()
 if 'klang' in n:return 'Klang!'
 if 'avisa' in n:return 'Avisa'
 if 'evoe' in n:return 'EVOE'
 if 'acta-bricolensia' in n:return 'Acta Bricolensia'
 if n.endswith('.html'):return 'Lokal historia'
 if n.endswith('.bz2') or n.startswith('lb'):return 'Jämförelsematerial'
 return 'Historiska kärnverk'

def build(manifest):
 raw=json.loads(manifest.read_text()); docs=[]
 for x in raw:
  name=Path(x['file']).name;kind=group(name)
  title=x.get('title',name)
  if kind in ['Klang!','Avisa','EVOE']:title=re.sub(r'[-_]+',' ',name.removesuffix('.pdf'))
  url=x.get('download_url') or x.get('url','');source=x.get('source_page') or x.get('source','')
  for u in [url,source]:
   if u and not u.startswith('https://'):raise ValueError('Källänkar ska använda HTTPS')
  docs.append(dict(id=x['document_id'],title=title,filename=name,category=kind,format='PDF' if name.endswith('.pdf') else 'XML (bzip2)' if name.endswith('.bz2') else 'HTML',publicationYear=x.get('publication_year'),pages=x.get('page_count'),bytes=x['bytes'],sha256=x['sha256'],sourceUrl=source,documentUrl=url,retrievedAt=x.get('retrieved_at'),verification='PDF-struktur och kontrollsumma kontrollerade' if x.get('pdf_parse_status')=='ok' and x.get('checksum_verified') else 'XML läst och kontrollsumma kontrollerad' if x.get('xml_parse_status')=='ok' and x.get('checksum_verified') else 'Fil hämtad och kontrollsumma registrerad',verified=bool(x.get('checksum_verified')),note=x.get('note','')))
 data=dict(schemaVersion=1,generatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),collectionStarted='2026-10-05',documents=docs)
 return data
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);a=p.parse_args();data=build(a.manifest)
 docs=Path(__file__).resolve().parents[1]/'docs';payload=json.dumps(data,ensure_ascii=False,indent=2)
 (docs/'catalog.json').write_text(payload+'\n')
 (docs/'assets/catalog.js').write_text('window.PB_CATALOG = '+payload.replace('<','\\u003c')+';\n')
 print(f"Katalog uppdaterad: {len(data['documents'])} dokument. Originalfiler har inte kopierats.")
