#!/usr/bin/env python3
"""Redovisa avslutad bearbetning, tidsunderlag och kontroller."""
import argparse,datetime,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('corpus',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];site=root/'docs'
report=json.loads((site/'bulk-processing.json').read_text());checks=json.loads((site/'bulk-validation.json').read_text());bellman=json.loads((site/'bellman-validation.json').read_text());docs=json.loads((a.corpus/'04_metadata/full_text_extraction.json').read_text())['documents']
assert report['batch']['state']=='complete','Huvudkörningen är inte klar'
assert report.get('tail',{}).get('state','complete')=='complete','Extra körningen är inte klar'
assert report['totals']['processed']==len(json.loads((a.corpus/'04_metadata/ocr_batch_plan.json').read_text())['pages'])
assert not report['batch']['errors'] and not report.get('tail',{}).get('errors')
assert checks['result']==bellman['status']=='passed'
pilot=json.loads((a.corpus/'04_metadata/pilot_text_extraction.json').read_text());pilotIds={d['id'] for d in pilot['documents']};massFirst=min(datetime.datetime.fromisoformat(d['extractedAt']) for d in docs if d['id'] not in pilotIds);first=min(datetime.datetime.fromisoformat(d['extractedAt']) for d in docs);now=datetime.datetime.now(datetime.timezone.utc);elapsed=(now-first).total_seconds();allowance=15*60
receipt=dict(schemaVersion=1,finishedAt=now.isoformat(),firstRecordedExtractionAt=first.isoformat(),firstRecordedMassExtractionAt=massFirst.isoformat(),elapsedSecondsSinceFirstRecordedMassExtraction=round((now-massFirst).total_seconds()),elapsedSecondsSinceFirstRecordedExtraction=round(elapsed),preparationAllowanceMinutes=15,budgetAccountingSeconds=round(elapsed+allowance),timeAccountingNote='Tid sedan första sparade grundextraktionen, plus 15 minuters schablon för förberedelser. Schablonen är en uppskattning, inte en loggad starttid. Körtider för överlappande OCR-jobb summeras inte.',withinTenHours=elapsed+allowance<36000,totals=report['totals'],integrity=checks,bellman=bellman,browser=json.loads((site/'browser-validation.json').read_text()),resources=json.loads((site/'processing-resources.json').read_text()))
assert receipt['withinTenHours'],'Tidsramen har överskridits enligt den angivna beräkningen'
for f in [site/'processing-receipt.json',a.corpus/'04_metadata/processing_receipt.json']:f.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'withinTenHours':receipt['withinTenHours'],'hoursIncludingPreparationAllowance':round(receipt['budgetAccountingSeconds']/3600,2)},ensure_ascii=False))
