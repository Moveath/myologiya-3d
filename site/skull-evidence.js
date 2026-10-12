// Published examples and native-model landmarks remain separate kinds of evidence.
const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
export function exampleFigure(e){
 if(!e)return '';
 return `<figure class="example"><a href="${esc(e.image)}" target="_blank" rel="noopener" aria-label="Открыть исходный рисунок"><img loading="lazy" src="${esc(e.image)}" alt="${esc(e.caption)}"></a><figcaption><strong>Пример другого препарата · изображение</strong><p>${esc(e.caption)}</p><p class="hint">${esc(e.author)} · <a href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.locator)}</a> · <a href="${esc(e.license.url)}" target="_blank" rel="noopener">${esc(e.license.name)}</a></p><details><summary>Происхождение и анатомические источники</summary><p class="hint">${esc(e.title)}. ${esc(e.changes)} ${esc(e.repository||'')}</p><ul class="sources">${(e.anatomyRefs||[]).map(r=>`<li><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a><small>${esc(r.locator)}</small></li>`).join('')}</ul></details></figcaption></figure>`;
}
export async function showFeatures(container,code,detailURL){
 container.innerHTML='<h2>Подробные ориентиры</h2><p class="notice">Каждый вид открывается на том исходном образце, где он проверен. Маркер стенки или края отверстия не означает, что весь канал восстановлен в 3D.</p><label class="feature-search">Найти образование<input id="featureSearch" type="search" placeholder="Название, латынь или код TA98" autocomplete="off"></label><div id="featureResults" aria-live="polite">Загружаю проверенные виды…</div>';
 const result=container.querySelector('#featureResults'),input=container.querySelector('#featureSearch');
 try{
  const response=await fetch('skull-feature-catalogue.json');if(!response.ok)throw Error();const data=await response.json();if(!result.isConnected)return;
  const render=()=>{
   const query=input.value.trim().toLocaleLowerCase('ru');
   const rows=data.features.filter(r=>[r.c,r.ru,r.lat].join(' ').toLocaleLowerCase('ru').includes(query));
   result.innerHTML=`<p class="hint">Найдено терминов: ${rows.length}. Счётчик относится к этому каталогу дополнительных материалов.</p>`+rows.map(r=>`<article class="variant"><h3>${esc(r.ru)}</h3><p class="latin">${esc(r.lat)}</p><p class="hint">TA98 ${esc(r.c)}</p>${r.views.map(v=>`<div class="feature-view"><p><b>${esc(v.ru)}</b> · ${esc(v.specimen)}</p><p class="hint">${esc(v.modelNote)}</p><a class="btn" data-native-marker="${esc(v.id)}" href="${esc(detailURL(v.mode)+'&marker='+encodeURIComponent(v.id)+'&from=features&code='+encodeURIComponent(r.c))}">Открыть проверенный вид ↗</a></div>`).join('')}${exampleFigure(r.example)}</article>`).join('')+(rows.length?'':'<p>В этом каталоге пока нет проверенного дополнительного вида для этого запроса. Это не доказательство отсутствия образования в анатомии.</p>');
  };
  input.value=code||'';input.oninput=render;render();
 }catch{if(result.isConnected)result.innerHTML='<p>Не удалось загрузить подробные ориентиры. Вернись к учебным группам и попробуй ещё раз.</p>';}
}
