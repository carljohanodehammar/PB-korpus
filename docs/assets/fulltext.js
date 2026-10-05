'use strict';
(() => {
 const edition=new Map((window.PB_EDITION?.pages||[]).map(r=>[r.pageId,r]));
 const reviewedDocuments=new Set([...edition.values()].filter(r=>r.status==='proofread').map(r=>r.documentId));
 const pilot=window.PB_PILOT, $=id=>document.getElementById(id), pageSize=12;
 if(!pilot){$('text-status').textContent='Korpusens textregister kunde inte läsas.';return;}
 const node=(tag,text,className)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(className)n.className=className;return n;};
 const clean=text=>text.replace(/([A-Za-zÅÄÖåäöÉé])-\s*\n\s*(?=[A-Za-zÅÄÖåäöÉé])/g,'$1').replace(/\s+/g,' ').trim();
 const norm=text=>text.toLocaleLowerCase('sv').normalize('NFKD').replace(/[\u0300-\u036f]/g,'');
 const escape=text=>text.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
 const loading=new Map(), pages=new Map();let matches=[],page=1,seq=0,lastTerms=[],lastQuery='';
 const totals=pilot.documents.reduce((a,d)=>({pages:a.pages+d.pages,text:a.text+d.textPages}),{pages:0,text:0});
 $('pilot-coverage').textContent=`${pilot.documents.length} verk · ${totals.pages} PDF-sidor · ${totals.text} sidor med söktext`;
 for(const d of pilot.documents){const option=node('option',d.title);option.value=d.id;$('text-source').append(option);}
 function load(doc){
  if(loading.has(doc.id))return loading.get(doc.id);
  const promise=new Promise((resolve,reject)=>{
   const s=document.createElement('script');s.src='texts/'+doc.id+'.js';s.onload=()=>{const raw=window.PB_TEXTS?.[doc.id];if(!raw){reject(new Error('Textdata saknas'));return;}pages.set(doc.id,raw.pages.map(p=>{const review=edition.get(doc.id+':p'+String(p.pdfPage).padStart(4,'0')),corrected=review?.status==='proofread',segments=corrected?review.segments:p.autoTextLayer==='ocr'?p.ocrSegments:(p.readingText?p.readingText.split(/\n\n/):[p.text]),text=segments.join('\n\n');return {...p,review,segments,quality:corrected?'proofread':p.autoTextLayer==='ocr'?'machine':p.readingText?'reading':'raw',readable:clean(text),search:norm(clean(text))};}));resolve();};s.onerror=()=>reject(new Error('Kunde inte läsa '+doc.title));document.head.append(s);
  });loading.set(doc.id,promise);return promise;
 }
 function highlight(container,text){
  const patterns=lastTerms.filter(Boolean).map(t=>escape(t).replace(/a/g,'[aåä]').replace(/o/g,'[oö]').replace(/e/g,'[eéè]').replace(/s/g,'[sſ]'));
  if(!patterns.length){container.textContent=text;return;}
  const expression=new RegExp(patterns.join('|'),'gi');let start=0;
  for(const match of text.matchAll(expression)){container.append(document.createTextNode(text.slice(start,match.index)),node('mark',match[0]));start=match.index+match[0].length;}
  container.append(document.createTextNode(text.slice(start)));
 }
 function render(){
  const count=Math.max(1,Math.ceil(matches.length/pageSize));page=Math.min(page,count);
  $('text-status').textContent=matches.length?`${matches.length} ${matches.length===1?'sida':'sidor'} matchar ”${lastQuery}” · visar ${(page-1)*pageSize+1}–${Math.min(page*pageSize,matches.length)}`:`Inga träffar för ”${lastQuery}”. Äldre stavning och OCR-fel kan påverka resultatet.`;
  $('text-results').replaceChildren(...matches.slice((page-1)*pageSize,page*pageSize).map(hit=>{
   const card=node('article',undefined,'text-hit');card.append(node('p','PDF-SIDA '+hit.p.pdfPage,'tag'),node('h3',hit.doc.title));
   const at=Math.max(0,hit.p.search.indexOf(lastTerms[0])),start=Math.max(0,at-100),end=Math.min(hit.p.readable.length,at+260),excerpt=node('p',undefined,'excerpt');highlight(excerpt,(start?'… ':'')+hit.p.readable.slice(start,end)+(end<hit.p.readable.length?' …':''));card.append(excerpt);
   const a=node('a','Öppna originalets PDF-sida '+hit.p.pdfPage+' ↗');a.href=hit.doc.documentUrl.split('#')[0]+'#page='+hit.p.pdfPage;a.target='_blank';a.rel='noopener noreferrer';card.append(a);
   card.append(node('p',hit.doc.id+' · '+({proofread:'korrekturläst löptext · revision '+hit.p.review?.revision,reading:'granskad läsordning · OCR-tecken ej rättade',raw:'ogranskat textlager',machine:'ny maskinell OCR · ej korrekturläst'}[hit.p.quality]),'meta'));
   if(hit.p.quality==='proofread'){const r=hit.p.review,ref=node('a','Läs granskad text och versionshistorik →');ref.href='#review='+encodeURIComponent(r.pageId)+'&v='+r.revision;card.append(node('p',r.printedPages.length?'Tryckta sidor: '+r.printedPages.join(', '):'Ingen synlig tryckt sidnumrering','meta'),ref);}
   if(hit.p.ocrText){const candidate=node('details');candidate.append(node('summary','Läs ny OCR och dess kvalitetsbedömning'),node('p','Maskinens säkerhetsvärde: '+hit.p.machineAssessment.confidence+'/100. Det mäter inte faktisk korrekthet.','meta'),node('pre',hit.p.ocrText,'page-text'));card.append(candidate);}
   if(hit.p.readingText){const revised=node('details');revised.append(node('summary','Läs sidan med granskad läsordning'),node('pre',hit.p.readingText,'page-text'));card.append(revised);}
   const details=node('details'),summary=node('summary','Läs ursprungligt extraherat textlager'),text=node('pre',hit.p.text,'page-text');details.append(summary,text);card.append(details);window.PB_SAVED.attach(card,{id:hit.doc.id+':p'+String(hit.p.pdfPage).padStart(4,'0'),kind:'Korpus',title:hit.doc.title,location:'PDF-sida '+hit.p.pdfPage,query:lastQuery,excerpt:excerpt.textContent,url:a.href});return card;
  }));
  $('text-prev').disabled=page===1;$('text-next').disabled=page===count;$('text-page').textContent=matches.length?`Sida ${page} av ${count}`:'0 resultat';$('text-pagination').hidden=!matches.length;
 }
 $('text-clear').addEventListener('click',()=>{++seq;matches=[];page=1;lastTerms=[];lastQuery='';$('text-form').reset();$('text-results').replaceChildren();$('text-pagination').hidden=true;$('text-search').disabled=false;$('text-status').textContent='Sökningen är rensad. Skriv ett nytt ord eller namn.';$('text-query').focus();});
 $('text-form').addEventListener('submit',async event=>{
  event.preventDefault();const query=$('text-query').value.trim();if(!query){$('text-status').textContent='Skriv ett ord eller en fras att söka efter.';return;}
  const token=++seq;const phrase=$('text-mode').value==='phrase';const terms=phrase?[norm(clean(query))]:norm(clean(query)).split(' ').filter(Boolean), chosen=pilot.documents.filter(d=>(!$('text-source').value||d.id===$('text-source').value)&&($('text-quality').value!=='proofread'||reviewedDocuments.has(d.id))&&($('text-quality').value!=='machine'||d.selectedOcrPages>0));
  $('text-status').textContent='Läser korpusens textfiler och söker…';$('text-search').disabled=true;
  try{
   await Promise.all(chosen.map(load));if(token!==seq)return;
   matches=[];for(const d of chosen){for(const p of pages.get(d.id)){if(p.readable&&(!$('text-quality').value||p.quality===$('text-quality').value)&&(phrase?p.segments.some(part=>norm(clean(part)).includes(terms[0])):terms.every(t=>p.search.includes(t))))matches.push({doc:d,p});}}
   page=1;lastQuery=query;lastTerms=terms;render();
  }catch(error){if(token===seq){matches=[];$('text-results').replaceChildren();$('text-pagination').hidden=true;$('text-status').textContent='Textfilerna kunde inte läsas. Ladda om sidan och försök igen.';}}
  finally{if(token===seq)$('text-search').disabled=false;}
 });
 for(const [id,step] of [['text-prev',-1],['text-next',1]])$(id).addEventListener('click',()=>{page+=step;render();$('text-status').scrollIntoView({block:'start'});});
})();
