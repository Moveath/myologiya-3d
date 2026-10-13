const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
export function wholeSources(refs){return '<ul class="sources">'+(refs||[]).filter(r=>/^https:\/\//.test(r.url||'')).map(r=>`<li><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a><small>${esc(r.locator)}</small></li>`).join('')+'</ul>';}
export function wholeDescription(row){return `<h3>${esc(row.ru)}</h3><p class="latin">${esc(row.lat)}</p><p class="hint">TA98 ${esc(row.c)}</p><p>${esc(row.description)}</p>${row.geometry?.modelNote?`<p class="notice">${esc(row.geometry.modelNote)}</p>`:''}${row.note?`<p class="notice">${esc(row.note)}</p>`:''}<details><summary>Анатомические источники и терминология</summary>${wholeSources(row.refs)}${wholeSources(row.nomenclatureRefs)}</details>`;}
export async function showWhole(container,code,detailURL){
 container.innerHTML='<h2>Череп как целое · TA98</h2><p class="intro">Здесь собраны общие области, стенки, ямки и виды черепа. Ракурс показывает существующую модель; степень подтверждения конкретного образования указана в карточке.</p><label class="feature-search">Найти в перечне<input id="wholeSearch" type="search" placeholder="Название, латынь или код TA98" autocomplete="off"></label><label><input id="wholeFuture" type="checkbox"> Показать также термины будущих разделов</label><div id="wholeResults" aria-live="polite">Загружаю перечень…</div>';
 const result=container.querySelector('#wholeResults'),input=container.querySelector('#wholeSearch'),future=container.querySelector('#wholeFuture');
 input.value=code||'';
 try{
  const response=await fetch('skull-whole.json');if(!response.ok)throw Error();const data=await response.json();if(!result.isConnected)return;
  const render=()=>{
   const query=input.value.trim().toLocaleLowerCase('ru'),rows=data.rows.filter(r=>(future.checked||r.current)&&[r.c,r.ru,r.lat].join(' ').toLocaleLowerCase('ru').includes(query));
   result.innerHTML=`<p class="hint">Найдено: ${rows.length}. Полный перечень — ${data.total}; текущий раздел — ${data.current}, будущие разделы — ${data.future}.</p>`+rows.map(r=>`<article class="variant" data-whole-code="${esc(r.c)}">${wholeDescription(r)}${!r.current?'<p class="hint">Отнесено к будущему разделу атласа. Не включено в приёмку взрослого костного черепа.</p>':''}${r.launch?`<div class="choices"><a class="btn" data-whole-view="${esc(r.c)}" href="${esc(detailURL(r.launch.mode||'z',r.launch.region)+'&from=whole&code='+encodeURIComponent(r.c))}">Открыть учебный вид ↗</a></div>`:'<p class="hint">Отдельный проверенный 3D-вид пока не подготовлен.</p>'}</article>`).join('')+(rows.length?'':'<p>Совпадений нет. Проверь написание или включи термины будущих разделов.</p>');
  };
  if(code&&data.rows.some(r=>r.c===code&&!r.current))future.checked=true;input.oninput=render;future.onchange=render;render();
 }catch{if(result.isConnected)result.innerHTML='<p>Не удалось загрузить перечень. Вернись к учебным группам и попробуй ещё раз.</p>';}
}
