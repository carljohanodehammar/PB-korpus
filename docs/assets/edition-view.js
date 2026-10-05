'use strict';
(() => {
 const data=window.PB_EDITION,$=id=>document.getElementById(id);
 if(!data)return;
 const labels={selected:'Utvald för granskning',partial:'Delvis korrekturläst',proofread:'Korrekturläst löptext'};
 const node=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
 const docs=new Map(window.PB_PILOT.documents.map(d=>[d.id,d]));
 const norm=s=>s.toLocaleLowerCase('sv').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
 const rawLoading=new Map();let readerSeq=0;
 $('edition-coverage').textContent=`Version ${data.release} · ${data.pages.length} granskade PDF-sidor · ${data.register.filter(x=>x.kind==='person').length} personer · ${data.register.filter(x=>x.kind==='term').length} begrepp och motiv`;
 function link(pageId,revision,text){const a=node('a',text);a.href='#review='+encodeURIComponent(pageId)+'&v='+revision;return a;}
 function original(doc,page){const a=node('a','Öppna originalets PDF-sida '+page+' ↗');a.href=doc.documentUrl.split('#')[0]+'#page='+page;a.target='_blank';a.rel='noopener noreferrer';return a;}
 function raw(doc){
  if(window.PB_TEXTS?.[doc.id])return Promise.resolve(window.PB_TEXTS[doc.id]);
  if(!rawLoading.has(doc.id))rawLoading.set(doc.id,new Promise((resolve,reject)=>{const s=document.createElement('script');s.src='texts/'+doc.id+'.js';s.onload=()=>window.PB_TEXTS?.[doc.id]?resolve(window.PB_TEXTS[doc.id]):reject();s.onerror=reject;document.head.append(s);}));
  return rawLoading.get(doc.id);
 }
 $('edition-pages').replaceChildren(...data.pages.map(p=>{
  const doc=docs.get(p.documentId),card=node('article',undefined,'edition-page');
  card.append(node('p',doc.title,'meta'),node('h3','PDF-sida '+p.pdfPage),node('p',labels[p.status],'quality'),node('p',p.printedPages.length?'Tryckta sidor: '+p.printedPages.join(', '):'Ingen synlig tryckt sidnumrering','meta'),link(p.pageId,p.revision,'Läs texten och granskningen →'));return card;
 }));
 function renderRegister(){
  const q=norm($('register-query').value.trim()),kind=$('register-kind').value;
  const entries=data.register.filter(e=>(!kind||e.kind===kind)&&norm([e.label,...e.aliases,e.description].join(' ')).includes(q));
  $('register-status').textContent=`${entries.length} av ${data.register.length} registerposter`;
  $('register-results').replaceChildren(...entries.map(e=>{
   const card=node('article',undefined,'register-entry');card.id='entry-'+e.id;
   card.append(node('p',e.kind==='person'?'PERSON':'BEGREPP ELLER MOTIV','tag'),node('h3',e.label),node('p',e.description));
   if(e.aliases.length)card.append(node('p','Sökformer: '+e.aliases.join(', '),'meta'));
   const details=node('details');details.append(node('summary',e.evidence.length+' kontrollerade belägg'));
   for(const ref of e.evidence){const ev=data.evidence[ref.id+'@'+ref.revision],doc=docs.get(ev.documentId),quote=node('blockquote',ev.text),citation=node('p',undefined,'meta');
    citation.append(document.createTextNode(doc.title+' · PDF '+ev.pdfPage+' · revision '+ev.revision+' · '),link(ev.pageId,ev.revision,'Läs sidan'));details.append(quote,citation);
   }
   details.append(node('p',e.scope,'meta'));card.append(details);return card;
  }));
 }
 $('register-query').addEventListener('input',renderRegister);$('register-kind').addEventListener('change',renderRegister);renderRegister();
 function showRevision(pageId,revision){
  const history=data.history[pageId];if(!history)return;const r=history.find(x=>x.revision===revision)||history[history.length-1],doc=docs.get(r.documentId),host=$('edition-reader');const token=++readerSeq;
  host.hidden=false;host.replaceChildren();const heading=node('h3',doc.title+' · PDF-sida '+r.pdfPage);heading.id='reader-title';host.setAttribute('aria-labelledby',heading.id);host.append(heading,node('p',labels[r.status]+' · revision '+r.revision+' · '+r.createdAt.slice(0,10),'quality'));
  const label=node('label','Textversion '),select=node('select');select.id='revision-select';
  for(const v of history){const option=node('option','Revision '+v.revision+' – '+labels[v.status]);option.value=v.revision;option.selected=v.revision===r.revision;select.append(option);}
  label.append(select);host.append(label);select.addEventListener('change',()=>{location.hash='review='+encodeURIComponent(pageId)+'&v='+select.value;});
  host.append(node('p',r.changeReason),original(doc,r.pdfPage));
  for(const note of r.notes)host.append(node('p',note,'search-note'));
  if(r.unresolved.length)host.append(node('p','Återstår: '+r.unresolved.join('; '),'search-note'));
  r.segments.forEach((text,i)=>{const map=r.pageMap.find(x=>x.segment===i);host.append(node('h4',map?.printedPage?'Tryckt sida '+map.printedPage:'Onumrerad boksida eller sidhalva '+(i+1)),node('pre',text,'page-text'));});
  const details=node('details'),rawText=node('pre','Öppna för att läsa råtexten.','page-text');details.append(node('summary','Jämför med ursprungligt extraherat textlager'),rawText);let loaded=false;
  details.addEventListener('toggle',async()=>{if(!details.open||loaded)return;loaded=true;try{const d=await raw(doc);if(token===readerSeq)rawText.textContent=d.pages[r.pdfPage-1].text;}catch{rawText.textContent='Råtexten kunde inte läsas. Ladda om och försök igen.';loaded=false;}});host.append(details);
  const changes=node('details');changes.append(node('summary',r.changes.length+' ändringar jämfört med råtexten'));
  for(const c of r.changes){const block=node('div',undefined,'change-row');block.append(node('p','Råtext: '+(c.before||'(tomt)')),node('p','Granskad text: '+(c.after||'(borttaget)')));changes.append(block);}host.append(changes);
  host.append(node('p',r.reviewer,'meta'),node('p',data.policy.quality,'search-note'));
 }
 function route(){if(!location.hash.startsWith('#review='))return;const params=new URLSearchParams(location.hash.slice(1)),id=params.get('review');if(!data.history[id])return;showRevision(id,Number(params.get('v')));$('edition-reader').scrollIntoView({block:'start'});}
 window.addEventListener('hashchange',route);route();
})();
