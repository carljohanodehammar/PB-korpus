#!/usr/bin/env python3
"""Extrahera befintliga textlager; ändra aldrig original eller antag tryckta sidnummer."""
import argparse,datetime,hashlib,json,subprocess,tempfile
from pathlib import Path

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('corpus',type=Path);p.add_argument('--pdftotext',default='pdftotext');p.add_argument('--sources',type=Path,default=Path(__file__).resolve().parents[1]/'editorial/text_sources.json');a=p.parse_args();files=json.loads(a.sources.read_text())['files'];assert len(set(files))==len(files)
 manifest=json.loads((a.corpus/'04_metadata/corpus_manifest.json').read_text());byname={Path(x['file']).name:x for x in manifest};site=Path(__file__).resolve().parents[1]/'docs';dest=site/'texts';dest.mkdir(exist_ok=True);local=a.corpus/'02_ocr/pilot';local.mkdir(parents=True,exist_ok=True);summary=[]
 for filename in files:
  x=byname[filename];source=a.corpus/x['file'];h=hashlib.sha256(source.read_bytes()).hexdigest()
  if h!=x['sha256']:raise ValueError('Originalets kontrollsumma avviker: '+filename)
  with tempfile.TemporaryDirectory() as folder:
   temp=Path(folder)/'text.txt';subprocess.run([a.pdftotext,'-layout','-enc','UTF-8',str(source),str(temp)],check=True);raw=temp.read_text()
  pages=raw.split('\f')
  if pages[-1].strip()=='':pages.pop()
  if len(pages)!=x['page_count']:raise ValueError('Sidantal avviker: '+filename)
  units=[dict(pdfPage=i+1,printedPage=None,text=text.strip()) for i,text in enumerate(pages)]
  now=datetime.datetime.now(datetime.timezone.utc).isoformat();result=dict(schemaVersion=1,documentId=x['document_id'],title=x['title'],sourceSha256=h,method='Poppler pdftotext -layout; existing PDF text layer; no new OCR',extractedAt=now,pages=units)
  payload=json.dumps(result,ensure_ascii=False)
  (local/(x['document_id']+'.json')).write_text(payload+'\n')
  (dest/(x['document_id']+'.json')).write_text(payload+'\n')
  (dest/(x['document_id']+'.js')).write_text('window.PB_TEXTS = window.PB_TEXTS || {}; window.PB_TEXTS['+json.dumps(x['document_id'])+'] = '+payload.replace('<','\\u003c')+';\n')
  item=dict(id=x['document_id'],title=x['title'],pages=len(units),textPages=sum(bool(u['text']) for u in units),emptyPages=[u['pdfPage'] for u in units if not u['text']],characters=sum(len(u['text']) for u in units),sourceSha256=h,documentUrl=x.get('download_url') or x.get('url'),extractedAt=now)
  summary.append(item);print(filename,item['pages'],'sidor',item['textPages'],'med text',flush=True)
 data=dict(schemaVersion=1,method='Befintliga textlager extraherade med Poppler pdftotext -layout',documents=summary)
 (site/'assets/pilot.js').write_text('window.PB_PILOT = '+json.dumps(data,ensure_ascii=False,indent=2).replace('<','\\u003c')+';\n')
 (a.corpus/'04_metadata/pilot_text_extraction.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
