#!/usr/bin/env python3
"""Lägg till en ny sidrevision; äldre revisionsfiler skrivs aldrig över."""
import argparse,json,shutil,re
from pathlib import Path
from build_edition import build
p=argparse.ArgumentParser();p.add_argument('revision',type=Path);p.add_argument('--corpus',type=Path);p.add_argument('--keep-active',action='store_true',help='Behåll nuvarande aktiva revision');a=p.parse_args()
root=Path(__file__).resolve().parents[1];src=root/'editorial';manifest=src/'edition.json';before=manifest.read_bytes();edition=json.loads(before);r=json.loads(a.revision.read_text());key=r['pageId'];assert re.fullmatch(r'PB-[0-9A-F]{16}',r['documentId']);assert isinstance(r['pdfPage'],int) and r['pdfPage']>0;item=next((x for x in edition['pages'] if x['pageId']==key),None)
if item:
 latest=json.loads((src/'revisions'/item['revisions'][-1]).read_text())
 if r['parentRevision']!=latest['revision'] or r['revision']!=latest['revision']+1:raise ValueError('Ny revision måste följa den senaste publicerade revisionen')
else:
 if r['revision']!=1 or r['parentRevision'] is not None:raise ValueError('En ny sida börjar med revision 1')
 if a.keep_active:raise ValueError('En ny sida måste ha en aktiv revision')
 item=dict(pageId=key,documentId=r['documentId'],pdfPage=r['pdfPage'],sourceSha256=r['sourceSha256'],activeRevision=1,revisions=[]);edition['pages'].append(item)
name=f"{r['documentId']}-p{r['pdfPage']:04d}-v{r['revision']:03d}.json";dest=src/'revisions'/name
if dest.exists():raise ValueError('Revisionen finns redan; välj nästa revisionsnummer')
item['revisions'].append(name)
if not a.keep_active:item['activeRevision']=r['revision']
try:
 shutil.copyfile(a.revision,dest);manifest.write_text(json.dumps(edition,ensure_ascii=False,indent=2)+'\n');build(root,a.corpus)
except Exception:
 manifest.write_bytes(before);dest.unlink(missing_ok=True);raise
print('Revision tillagd:',name)
