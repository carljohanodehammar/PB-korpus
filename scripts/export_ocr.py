#!/usr/bin/env python3
"""Lägg till maskinella kandidater i webbexporten utan att ändra råfältet text."""
import argparse,collections,json
from pathlib import Path
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('corpus',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];site=root/'docs';data=json.loads((site/'assets/pilot.js').read_text().split(' = ',1)[1].rstrip(';\n'));stats=collections.Counter(dict(processed=0,chosen=0,filled=0,lowConfidence=0));queue=[]
 for doc in data['documents']:
  id=doc['id'];target=site/'texts'/(id+'.json');text=json.loads(target.read_text())
  for page in text['pages']:
   for field in ['ocrText','ocrSegments','autoTextLayer','machineAssessment']:page.pop(field,None)
   candidate=a.corpus/'02_ocr/tesseract-best-v2'/id/f'p{page["pdfPage"]:04d}.json'
   if not candidate.exists() and not (a.corpus/'02_ocr/tesseract-core-v4'/id/f'p{page["pdfPage"]:04d}.json').exists():continue
   core=a.corpus/'02_ocr/tesseract-core-v4'/id/f'p{page["pdfPage"]:04d}.json'
   if core.exists():candidate=core
   r=json.loads(candidate.read_text());assert r['sourceSha256']==text['sourceSha256'];letters=sum(c.isalpha() for c in r['text']);oldletters=sum(c.isalpha() for c in page['text']);confidence=r['confidence'];missing=not page['text'].strip()
   # Manuell textrevision har alltid företräde i sökgränssnittet.
   choose=letters>=20 and confidence>= (65 if missing or core.exists() else 85) and (missing or core.exists() or r['referenceBenchmark'] or .5<=letters/max(oldletters,1)<=2)
   page['ocrText']=r['text'];page['ocrSegments']=r['segments'];page['autoTextLayer']='ocr' if choose else 'original';page['machineAssessment']=dict(confidence=confidence,needsReview=True,automaticSplit=r['automaticSplit'],engine=r['engineVersion'],version='core-v4' if core.exists() else 'batch-v2',sourceSha256=r['sourceSha256'],modelHashes=r['modelHashes'],languages=[s['selectedLanguage'] for s in r['candidates']],selection='confidence-and-coverage-heuristic; not proofreading',createdAt=r['createdAt'],statisticsParser=r['statisticsParser']);stats['processed']+=1;stats['chosen']+=int(choose);stats['filled']+=int(choose and missing);stats['lowConfidence']+=int(confidence<85)
   queue.append(dict(documentId=id,pdfPage=page['pdfPage'],confidence=confidence,selected=choose,rawEmpty=missing,reason='low-confidence' if confidence<85 else 'automatic-layout' if r['automaticSplit'] else 'machine-unreviewed',priority=100-confidence+(15 if missing else 0),characters=len(r['text'])))
  payload=json.dumps(text,ensure_ascii=False)+'\n';target.write_text(payload);(site/'texts'/(id+'.js')).write_text('window.PB_TEXTS=window.PB_TEXTS||{};window.PB_TEXTS['+json.dumps(id)+']='+payload.replace('<','\\u003c')+';\n')
  doc['rawTextPages']=sum(bool(p['text']) for p in text['pages']);doc['ocrPages']=sum('ocrText' in p for p in text['pages']);doc['selectedOcrPages']=sum(p.get('autoTextLayer')=='ocr' for p in text['pages']);doc['textPages']=sum(bool((p['ocrText'] if p.get('autoTextLayer')=='ocr' else p.get('readingText') or p['text']).strip()) for p in text['pages']);doc['emptyPages']=[p['pdfPage'] for p in text['pages'] if not (p['ocrText'] if p.get('autoTextLayer')=='ocr' else p.get('readingText') or p['text']).strip()]
 data['method']='Befintliga textlager med separata maskinella OCR-kandidater; manuella revisioner har företräde';(site/'assets/pilot.js').write_text('window.PB_PILOT = '+json.dumps(data,ensure_ascii=False,indent=2).replace('<','\\u003c')+';\n');(a.corpus/'04_metadata/full_text_extraction.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');queue.sort(key=lambda p:-p['priority']);report=dict(schemaVersion=1,method='Prioritering med OCR-motorns säkerhet och layout; inte uppmätt korrekthet',stats=dict(stats),pages=queue);(site/'ocr-quality.json').write_text(json.dumps(report,ensure_ascii=False)+'\n');(a.corpus/'04_metadata/ocr_review_queue.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(stats)),sum(d['textPages'] for d in data['documents']),'sidor med söktext')
