#!/usr/bin/env python3
"""Kontrollera original, råtext, OCR-proveniens och arkiverade revisioner."""
import argparse,datetime,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('corpus',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];site=root/'docs';manifest=json.loads((a.corpus/'04_metadata/corpus_manifest.json').read_text());documents={r['document_id']:r for r in manifest};checks=dict(originalFiles=0,pdfDocuments=0,rawPagesUnchanged=0,ocrPagesWithSourceProvenance=0,editorialRevisionsUnchanged=0)
for r in manifest:
 assert hashlib.sha256((a.corpus/r['file']).read_bytes()).hexdigest()==r['sha256'],r['file'];checks['originalFiles']+=1
for p in (site/'texts').glob('*.json'):
 d=json.loads(p.read_text());id=d['documentId'];m=documents[id];raw=json.loads((a.corpus/'02_ocr/full'/p.name).read_text());assert d['sourceSha256']==raw['sourceSha256']==m['sha256'];assert len(d['pages'])==len(raw['pages'])==m['page_count'];js=json.loads(re.split(r'\]\s*=\s*',(p.with_suffix('.js')).read_text(),maxsplit=1)[1].rstrip(';\n'));assert js==d;checks['pdfDocuments']+=1
 for i,(page,original) in enumerate(zip(d['pages'],raw['pages']),1):
  assert page['pdfPage']==original['pdfPage']==i;assert page['text']==original['text'];checks['rawPagesUnchanged']+=1
  if 'ocrText' in page:
   v=page['machineAssessment']['version'];folder='tesseract-core-v4' if v=='core-v4' else 'tesseract-best-v2';c=json.loads((a.corpus/'02_ocr'/folder/id/f'p{i:04d}.json').read_text());assert c['sourceSha256']==m['sha256'];assert page['ocrText']==c['text'];assert c['reviewStatus']=='machine-ocr-unreviewed' and page['machineAssessment']['needsReview'];checks['ocrPagesWithSourceProvenance']+=1
for p in (root/'editorial/revisions').glob('*.json'):
 assert p.read_bytes()==(a.corpus/'03_normaliserad_text/reviews'/p.name).read_bytes();checks['editorialRevisionsUnchanged']+=1
pdfs=[r for r in manifest if r['file'].lower().endswith('.pdf')]
assert checks['pdfDocuments']==len(pdfs) and checks['rawPagesUnchanged']==sum(r['page_count'] for r in pdfs)
for id,n in [('PB-2F363B3D4BB42055',3),('PB-2B9FD909245A77C2',3)]:
 page=json.loads((site/'texts'/(id+'.json')).read_text())['pages'][n-1];assert page['autoTextLayer']=='original'
result=dict(schemaVersion=1,checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),result='passed',checks=checks,scope='Integritet och proveniens; inget bevis för OCR-korrekthet')
(site/'bulk-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(a.corpus/'04_metadata/bulk_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
