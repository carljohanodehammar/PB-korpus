#!/usr/bin/env python3
"""Exportera Språkbankens text separat från korpusens PDF-sidor."""
import argparse,bz2,hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('corpus',type=Path);a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=root/'docs/reference-texts';out.mkdir(exist_ok=True)
source=a.corpus/'01_original/bellman.xml.bz2';sha=hashlib.sha256(source.read_bytes()).hexdigest()
existing=out/'index.json'
if existing.exists():
 assert json.loads(existing.read_text())['sourceSha256']==sha,'Ändrad källversion: bevara tidigare export och skapa en separat versionsmapp'
manifest=json.loads((a.corpus/'04_metadata/corpus_manifest.json').read_text())
assert any(d.get('sha256')==sha for d in manifest),'Källans kontrollsumma finns inte i manifestet'
data=ET.fromstring(bz2.open(source,'rt').read());books=[];words=sentences=pages=0
for i,t in enumerate(data,1):
 book=dict(id=f'bellman-{i:02d}',title=t.attrib['title'],author=t.attrib.get('author'),sourceSha256=sha,pages=[])
 # Sidgränser kan ligga inuti meningar och stycken. Besök varje ord
 # exakt en gång och ärv närmaste sidangivelse, även över sådana gränser.
 units=[];orphan=None;wordOrdinal=0
 def visit(e,unit=None,paragraph=None,sentence=None):
  global orphan,wordOrdinal
  if e.tag=='page':
   unit=dict(sourcePage=e.attrib.get('n'),groups=[],tokens=[],ordinals=[]);units.append(unit)
  if e.tag=='paragraph':paragraph=id(e)
  if e.tag=='sentence':sentence=e.attrib.get('id')
  if e.tag=='w':
   if unit is None:
    if orphan is None:orphan=dict(sourcePage=None,groups=[],tokens=[],ordinals=[]);units.append(orphan)
    unit=orphan
   key=(paragraph,sentence)
   if not unit['groups'] or unit['groups'][-1]['key']!=key:unit['groups'].append(dict(key=key,sentenceId=sentence,tokens=[]))
   token=e.text or '';unit['groups'][-1]['tokens'].append(token);unit['tokens'].append(token);wordOrdinal+=1;unit['ordinals'].append(wordOrdinal)
  for child in e:visit(child,unit,paragraph,sentence)
 visit(t)
 for j,unit in enumerate(units,1):
  groups=unit['groups'];count=len(unit['tokens']);words+=count;pages+=1
  book['pages'].append(dict(id=f'{book["id"]}:page-{j:04d}',ordinal=j,sourcePage=unit['sourcePage'],paragraphs=[' '.join(g['tokens']) for g in groups],sentenceIds=[g['sentenceId'] for g in groups],tokens=unit['tokens'],sourceWordOrdinals=unit['ordinals'],wordTokens=count))
 sentences+=sum(1 for s in t.iter('sentence'))
 assert sum(p['wordTokens'] for p in book['pages'])==sum(1 for w in t.iter('w'))
 payload=json.dumps(book,ensure_ascii=False,separators=(',',':'))
 (out/f'{book["id"]}.json').write_text(payload+'\n')
 (out/f'{book["id"]}.js').write_text('window.PB_REFERENCES=window.PB_REFERENCES||{};window.PB_REFERENCES['+json.dumps(book['id'])+']='+payload+';\n')
 books.append({k:v for k,v in book.items() if k!='pages'}|{'pageUnits':len(book['pages']),'wordTokens':sum(p['wordTokens'] for p in book['pages'])})
meta=dict(schemaVersion=1,source='Språkbanken Text (2015). Bellman.',sourceUrl='https://spraakbanken.gu.se/resurser/bellman',doi='https://doi.org/10.23695/5DRX-FH45',license='CC BY 4.0',licenseUrl='https://creativecommons.org/licenses/by/4.0/',sourceSha256=sha,wordTokens=words,sentences=sentences,pageUnits=pages,books=books,layout='Ordens följd och meningsfragment kommer från XML. Mellanrum sätts mellan token; ursprunglig typografi och versradbrytning återskapas inte.',edition='Carl Michael Bellmans skrifter, standardupplagan 1921–2003. Sidangivelserna gäller datakällan och är inte kopplade till PDF-originalen.')
payload=json.dumps(meta,ensure_ascii=False,indent=2)
(out/'index.json').write_text(payload+'\n');(root/'docs/assets/bellman-data.js').write_text('window.PB_BELLMAN='+payload+';\n')
(a.corpus/'04_metadata/bellman_reference_export.json').write_text(payload+'\n')
print(json.dumps({k:meta[k] for k in ['wordTokens','sentences','pageUnits']})+' · '+str(len(books))+' textenheter')
