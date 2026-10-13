import {wholeSources} from './skull-whole.js';
import {educationLink} from './skull-education-link.js';
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const side={right:'справа',left:'слева',unpaired:'непарная'};
export async function showAttachments(container,openCard){
 container.innerHTML='<h2>Начала и прикрепления мышц</h2><p class="notice">Полный текстовый перечень включённых мышц и частей. Выборочные костные точки помогают ориентироваться, но не обозначают всю площадь прикрепления. Сведения всей мышцы у её частей подписаны отдельно.</p><label class="feature-search">Найти мышцу, часть или место прикрепления<input id="attachmentSearch" type="search" placeholder="Русское название, латынь, код TA98 или область" autocomplete="off"></label><div id="attachmentResults" aria-live="polite">Загружаю перечень…</div>';
 const result=container.querySelector('#attachmentResults'),input=container.querySelector('#attachmentSearch');
 try{
  const response=await fetch('skull-muscle-attachments.json');if(!response.ok)throw Error();const data=await response.json();if(!result.isConnected)return;
  const field=(label,f)=>`<div class="feature-view"><b>${label}</b>${f.scope==='whole_muscle'?' <span class="hint">· сведения всей мышцы</span>':''}${f.status==='unconfirmed'?' <span class="hint">· не подтверждено</span>':''}<p>${esc(f.text)}</p><details><summary>Источники этого утверждения</summary>${wholeSources(f.refs)}</details><p class="hint">${f.representativeMarkerIds?.length?'Есть выборочные ориентиры на костях.':'Отдельных проверенных точек этой записи пока нет.'} Полная область прикрепления в 3D не размечена.</p></div>`;
  const muscles=new Map(data.items.filter(r=>r.kind==='whole').map(r=>[r.id,r]));
  const render=()=>{
   const q=input.value.trim().toLocaleLowerCase('ru'),rows=data.items.filter(r=>[r.ru,r.lat,r.ta98,muscles.get(r.muscleId)?.ru,r.origin.text,r.insertion.text,side[r.side]].join(' ').toLocaleLowerCase('ru').includes(q));
   result.innerHTML=`<p class="hint">Найдено: ${rows.length}. В перечне 52 мышцы и 26 частей с учётом стороны.</p>`+rows.map(r=>`<article class="variant" data-attachment-id="${esc(r.id)}"><h3>${esc(r.ru)} · ${esc(side[r.side]||r.side)}</h3><p class="latin">${esc(r.lat)}</p>${r.kind==='part'?`<p>${esc(muscles.get(r.muscleId)?.ru||'')}</p>`:''}<p class="hint">TA98 ${esc(r.ta98)} · ${r.kind==='part'?'часть мышцы':'мышца'}</p><div class="choices">${educationLink('attachment:'+r.id,'Схема связей и границы известных сведений ↗')}</div>${field('Начало',r.origin)}${field('Прикрепление',r.insertion)}${r.note?`<p>${esc(r.note)}</p>`:''}${r.partNote?`<p>${esc(r.partNote)}</p>`:''}<p class="hint">${r.geometry.present?'Есть исходная 3D-модель.':'Отдельная 3D-модель отсутствует.'}</p><button class="btn" data-muscle-card="${esc(r.id)}">Открыть карточку в атласе</button></article>`).join('')+(rows.length?'':'<p>Совпадений нет.</p>');
   result.querySelectorAll('[data-muscle-card]').forEach(button=>button.onclick=()=>openCard(button.dataset.muscleCard));
  };
  input.oninput=render;render();
 }catch{if(result.isConnected)result.innerHTML='<p>Не удалось загрузить прикрепления. Вернись к учебным группам и попробуй ещё раз.</p>';}
}
