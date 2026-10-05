'use strict';
(() => {
 const input=document.getElementById('people-filter'),box=document.getElementById('people-cards');if(!box)return;
 function render(){const query=input.value.toLocaleLowerCase('sv');const rows=window.PB_PEOPLE.filter(x=>[x.name,...x.forms].join(' ').toLocaleLowerCase('sv').includes(query));box.replaceChildren();document.getElementById('people-status').textContent=rows.length+' namn i urvalet';for(const x of rows){const b=document.createElement('button');b.type='button';b.className='person-card';const title=document.createElement('strong');title.textContent=x.name;const desc=document.createElement('span');desc.textContent=x.passages+' textavsnitt · sökform: '+x.forms.join(' / ');b.append(title,desc);b.addEventListener('click',()=>{const q=x.forms[0];document.getElementById('bellman-source').value='';document.getElementById('bellman-mode').value='words';document.getElementById('bellman-query').value=q;window.PB_PERSON_QUERY={query:q,forms:x.forms};document.getElementById('bellman-form').requestSubmit();document.getElementById('bellman').scrollIntoView({block:'start'});});box.append(b);}}
 input.addEventListener('input',render);render();
})();
