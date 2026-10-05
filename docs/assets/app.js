'use strict';
(() => {
 const data=window.PB_CATALOG;
 const $=id=>document.getElementById(id);
 if(!data || !Array.isArray(data.documents)){$('results').textContent='Katalogen kunde inte läsas. Försök ladda om sidan.';return;}
 const documents=data.documents, perPage=24;
 let page=1;
 const number=new Intl.NumberFormat('sv-SE');
 const normalize=value=>String(value??'').toLocaleLowerCase('sv').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,' ').trim();
 const element=(tag,text,className)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;};
 const link=(text,url)=>{const a=element('a',text);try{const parsed=new URL(url);if(parsed.protocol!=='https:')return null;a.href=parsed.href;}catch{return null;}a.target='_blank';a.rel='noopener noreferrer';a.setAttribute('aria-label',text+' (öppnas i ny flik)');return a;};
 $('total').textContent=number.format(documents.length);
 $('pages').textContent=number.format(documents.reduce((n,d)=>n+(d.pages||0),0));
 $('size').textContent=(documents.reduce((n,d)=>n+d.bytes,0)/1e9).toLocaleString('sv-SE',{maximumFractionDigits:2})+' GB';
 $('updated').textContent='Katalog uppdaterad '+new Intl.DateTimeFormat('sv-SE',{dateStyle:'long',timeZone:'Europe/Stockholm'}).format(new Date(data.generatedAt));
 for(const name of [...new Set(documents.map(d=>d.category))].sort((a,b)=>a.localeCompare(b,'sv'))){const option=element('option',name);option.value=name;$('category').append(option);}
 const searchable=new Map(documents.map(d=>[d.id,normalize([d.title,d.filename,d.id,d.category,d.publicationYear].join(' '))]));
 function render(){
  const terms=normalize($('query').value).split(' ').filter(Boolean), category=$('category').value;
  const found=documents.filter(d=>(!category||d.category===category)&&terms.every(t=>searchable.get(d.id).includes(t)));
  const sort=$('sort').value;found.sort((a,b)=>(sort==='pages'?(b.pages||0)-(a.pages||0):sort==='size'?b.bytes-a.bytes:0)||a.title.localeCompare(b.title,'sv'));
  const pages=Math.max(1,Math.ceil(found.length/perPage));page=Math.min(page,pages);
  $('results').textContent=found.length?`${number.format(found.length)} av ${number.format(documents.length)} källfiler · visar ${(page-1)*perPage+1}–${Math.min(page*perPage,found.length)}`:'Inga källor matchar sökningen. Ändra sökorden eller återställ filtren.';
  const cards=found.slice((page-1)*perPage,page*perPage).map(d=>{
   const card=element('article',undefined,'document');card.append(element('span',d.category,'tag'),element('h3',d.title));
   card.append(element('p',[d.format,d.pages?number.format(d.pages)+' sidor':null,(d.bytes/1e6).toLocaleString('sv-SE',{maximumFractionDigits:1})+' MB'].filter(Boolean).join(' · '),'meta'));
   const actions=element('div',undefined,'actions');for(const [text,url] of [['Öppna källdokument ↗',d.documentUrl],['Källsida ↗',d.sourceUrl]]){const a=link(text,url);if(a)actions.append(a);}card.append(actions);
   const details=element('details'), summary=element('summary','Proveniens och kontroll');details.append(summary);const dl=element('dl');
   const fields=[['Dokument-ID',d.id],['Originalets filnamn',d.filename],['Hämtat',d.retrievedAt?new Intl.DateTimeFormat('sv-SE',{dateStyle:'long',timeZone:'Europe/Stockholm'}).format(new Date(d.retrievedAt)):'Ej angivet'],['Kontroll',d.verification],['SHA-256',d.sha256],...(d.note?[['Anmärkning',d.note]]:[])];
   for(const [label,value] of fields){dl.append(element('dt',label),element('dd',value,label==='SHA-256'?'hash':undefined));}details.append(dl);card.append(details);return card;
  });
  $('documents').replaceChildren(...cards);$('previous').disabled=page===1;$('next').disabled=page===pages;$('page-label').textContent=found.length?`Sida ${page} av ${pages}`:'0 resultat';
 }
 $('filters').addEventListener('submit',event=>event.preventDefault());
 $('query').addEventListener('input',()=>{page=1;render();});
 for(const id of ['category','sort'])$(id).addEventListener('change',()=>{page=1;render();});
 $('reset').addEventListener('click',()=>{$('query').value='';$('category').value='';$('sort').value='title';page=1;render();$('query').focus();});
 for(const [id,step] of [['previous',-1],['next',1]])$(id).addEventListener('click',()=>{page+=step;render();$('results').scrollIntoView({block:'start'});});
 render();
})();
