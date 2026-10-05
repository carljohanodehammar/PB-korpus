'use strict';
(() => {
 const data=window.PB_BELLMAN,$=id=>document.getElementById(id),loaded=new Map();
 if(!data)return;
 const node=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
 const norm=s=>s.toLocaleLowerCase('sv').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,' ').trim();
 $('bellman-coverage').textContent=`${data.wordTokens.toLocaleString('sv-SE')} ordtoken · ${data.books.length} textenheter · Språkbanken Text`;
 for(const b of data.books){const o=node('option',b.title);o.value=b.id;$('bellman-source').append(o);}
 function load(b){if(loaded.has(b.id))return loaded.get(b.id);const p=new Promise((resolve,reject)=>{const s=node('script');s.src='reference-texts/'+b.id+'.js';s.onload=()=>{const book=window.PB_REFERENCES?.[b.id];if(!book){reject(new Error('Textdata saknas'));return;}resolve(book.pages.map(p=>({...p,search:norm(p.tokens.join(' '))})));};s.onerror=()=>reject(new Error('Kunde inte läsa '+b.title));document.head.append(s);});loaded.set(b.id,p);return p;}
 let hits=[],page=1,query='',seq=0;
 function render(){const count=Math.max(1,Math.ceil(hits.length/10));$('bellman-status').textContent=hits.length?`${hits.length} textavsnitt matchar ”${query}” · sida ${page} av ${count}`:`Inga träffar för ”${query}”. Prova även äldre stavning.`;
  $('bellman-results').replaceChildren(...hits.slice((page-1)*10,page*10).map(h=>{const card=node('article');card.className='text-hit';card.append(node('h3',h.book.title),node('p','Sidangivelse i datakällan: '+(h.p.sourcePage??'saknas')+' · avsnitt '+h.p.ordinal));const text=h.p.tokens.join(' '),at=h.p.search.indexOf(norm(query).split(' ')[0]),start=Math.max(0,at-100);card.append(node('p',(start?'… ':'')+text.slice(start,start+420)+(start+420<text.length?' …':'')));const details=node('details');details.append(node('summary','Läs textavsnittet'));const pre=node('pre',h.p.paragraphs.join('\n\n'));pre.className='page-text';details.append(pre);card.append(details);const ref=node('p',h.p.id+' · Språkbanken Text · CC BY 4.0');ref.className='meta';card.append(ref);const a=node('a','Hämta text och källans meningsidentifierare');a.href='reference-texts/'+h.book.id+'.json';a.download=h.book.id+'.json';card.append(a);return card;}));
  $('bellman-pagination').hidden=!hits.length;$('bellman-prev').disabled=page===1;$('bellman-next').disabled=page===count;$('bellman-page').textContent=`${page} / ${count}`;
 }
 $('bellman-form').addEventListener('submit',async e=>{e.preventDefault();query=$('bellman-query').value.trim();if(!query){$('bellman-status').textContent='Skriv ett ord eller en fras.';return;}const token=++seq;const terms=$('bellman-mode').value==='phrase'?[norm(query)]:norm(query).split(' ');$('bellman-status').textContent='Läser jämförelsetexterna…';try{const chosen=data.books.filter(b=>!$('bellman-source').value||b.id===$('bellman-source').value);const groups=await Promise.all(chosen.map(async book=>(await load(book)).filter(p=>terms.every(t=>p.search.includes(t))).map(p=>({book,p}))));if(token!==seq)return;hits=groups.flat();page=1;render();}catch(error){if(token===seq)$('bellman-status').textContent=error.message;}});
 $('bellman-prev').addEventListener('click',()=>{page--;render();});$('bellman-next').addEventListener('click',()=>{page++;render();});
})();
