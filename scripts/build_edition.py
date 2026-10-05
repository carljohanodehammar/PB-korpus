#!/usr/bin/env python3
"""Validera och exportera redaktionella tillägg utan att skriva över textlager."""
import argparse,collections,hashlib,json,re
from pathlib import Path
STATUSES={'selected','partial','proofread'}
def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def build(root,corpus=None):
 src=root/'editorial';edition=json.loads((src/'edition.json').read_text());registry=json.loads((src/'register.json').read_text());docs={d['id']:d for d in json.loads((root/'docs/assets/pilot.js').read_text().split(' = ',1)[1].rstrip(';\n'))['documents']};versions={};active={};evidence={};works=json.loads((src/'works.json').read_text())['works'];assert len({w['id'] for w in works})==len(works)
 for w in works:
  assert w['documentVersions'] and all(id in docs for id in w['documentVersions'])
 work_documents=[id for w in works for id in w['documentVersions']];assert len(set(work_documents))==len(work_documents);assert len({p['pageId'] for p in edition['pages']})==len(edition['pages'])
 for item in edition['pages']:
  assert item['documentId'] in work_documents
  key=item['pageId'];assert key==f"{item['documentId']}:p{item['pdfPage']:04d}"
  base=json.loads((root/'docs/texts'/(item['documentId']+'.json')).read_text());assert base['sourceSha256']==item['sourceSha256']==docs[item['documentId']]['sourceSha256'];assert 1<=item['pdfPage']<=len(base['pages'])
  history=[]
  for name in item['revisions']:
   path=src/'revisions'/name;assert path.resolve().is_relative_to((src/'revisions').resolve());r=json.loads(path.read_text());assert r['documentId']==item['documentId'] and r['pdfPage']==item['pdfPage'];assert r['pageId']==key and r['status'] in STATUSES and r['sourceSha256']==item['sourceSha256'];assert r['rawTextSha256']==digest(base['pages'][item['pdfPage']-1]['text']);assert r['revision'] not in [v['revision'] for v in history];assert r['parentRevision']==(history[-1]['revision'] if history else None)
   for passage in r['passages']:
    evkey=passage['id']+'@'+str(r['revision']);assert evkey not in evidence;assert all(v['pageId']==key for v in evidence.values() if v['id']==passage['id'])
    assert passage['text'] and passage['reviewStatus']=='checked-against-image'
    if r['status']=='proofread':assert passage['text'] in '\n'.join(r['segments'])
    evidence[evkey]={**passage,'pageId':key,'revision':r['revision'],'documentId':item['documentId'],'pdfPage':item['pdfPage']}
   if r['status']=='proofread':
    assert r['segments'] and not r['unresolved'];assert r['textSha256']==digest('\n\n'.join(r['segments']));assert [m['segment'] for m in r['pageMap']]==list(range(len(r['segments'])))
   if r['status']=='partial':assert r['passages'] and r['unresolved']
   history.append(r)
  current=next(v for v in history if v['revision']==item['activeRevision']);active[key]=current;versions[key]=history
 for entry in registry['entries']:
  assert entry['id'] and entry['kind'] in {'person','term'} and entry['evidence']
  for ref in entry['evidence']:assert ref['id']+'@'+str(ref['revision']) in evidence
 assert len({e['id'] for e in registry['entries']})==len(registry['entries'])
 data=dict(schemaVersion=1,release=edition['release'],policy=edition['policy'],pages=list(active.values()),history=versions,register=registry['entries'],evidence=evidence,works=works)
 if corpus:
  assert re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',edition['release'])
  snapshots=[]
  for folder,kind,name in [('05_lexikon','term','begreppsregister'),('06_entiteter','person','personregister')]:
   content=json.dumps(dict(schemaVersion=1,release=edition['release'],entries=[e for e in registry['entries'] if e['kind']==kind]),ensure_ascii=False,indent=2)+'\n';out=corpus/folder/(name+'-'+edition['release']+'.json')
   if out.exists() and out.read_text()!=content:raise ValueError('Registerversionen finns redan; öka release innan registret ändras')
   snapshots.append((out,content))
  target=corpus/'03_normaliserad_text/reviews'
  for p in (src/'revisions').glob('*.json'):
   out=target/p.name
   if out.exists() and out.read_bytes()!=p.read_bytes():raise ValueError('Befintlig revision får inte ändras: '+p.name)
 public=root/'docs';payload=json.dumps(data,ensure_ascii=False,indent=2);(public/'edition.json').write_text(payload+'\n');(public/'assets/edition.js').write_text('window.PB_EDITION = '+payload.replace('<','\\u003c')+';\n')
 if corpus:
  target=corpus/'03_normaliserad_text/reviews';target.mkdir(parents=True,exist_ok=True)
  for p in (src/'revisions').glob('*.json'):
   out=target/p.name
   if out.exists() and out.read_bytes()!=p.read_bytes():raise ValueError('Befintlig revision får inte ändras: '+p.name)
   out.write_bytes(p.read_bytes())
  (corpus/'04_metadata/editorial_edition.json').write_bytes((src/'edition.json').read_bytes());(corpus/'04_metadata/editorial_register.json').write_bytes((src/'register.json').read_bytes());(corpus/'04_metadata/editorial_works.json').write_bytes((src/'works.json').read_bytes())
  for out,content in snapshots:out.parent.mkdir(parents=True,exist_ok=True);out.write_text(content)
 print('Sidor:',len(active),'Kvalitetsstatus:',dict(collections.Counter(v['status'] for v in active.values())),'Registerposter:',len(registry['entries']),'Belägg:',len(evidence))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--corpus',type=Path);a=p.parse_args();build(Path(__file__).resolve().parents[1],a.corpus)
