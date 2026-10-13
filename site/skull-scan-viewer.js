// Actual source CT reslices, kept distinct from clipping a 3D surface.
export function createScanViewer(host,onFrame=()=>{}) {
  host.innerHTML=`<h3>Проверить на КТ</h3><button class="btn" data-expand aria-expanded="false">Увеличить срез</button><p class="hint">Косые срезы этого же препарата. Ползунок перемещает плоскость вдоль выбранного участка.</p><canvas width="520" height="520" aria-label="Срез исходной КТ"></canvas><label class="check"><input type="checkbox" data-overlay>Граница костной маски и просвет</label><label class="range-label"><span>Срез выбранного участка</span><output></output></label><input type="range" min="0" value="0" step="1" aria-label="Номер среза КТ"><p class="hint" data-status role="status"></p><p class="hint" data-source></p>`;
  const canvas=host.querySelector('canvas'),slider=host.querySelector('input[type=range]'),overlay=host.querySelector('[data-overlay]'),output=host.querySelector('output'),status=host.querySelector('[data-status]');
  const images=new Map();let series=null,metadata=null,key=null,ticket=0;
  async function draw(){
    if(!series)return;
    const current=++ticket,index=Number(slider.value),frame=series.frames[index];
    canvas.getContext('2d').clearRect(0,0,canvas.width,canvas.height);delete canvas.dataset.frame;canvas.dataset.loaded='false';
    onFrame(null);
    host.querySelector('[data-source]').textContent='';
    output.value=`${index+1} / ${series.frames.length}`;status.textContent='Загрузка среза…';
    try{
      if(!images.has(frame.image))images.set(frame.image,new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>reject(Error('image'));image.src=frame.image;}));
      const image=await images.get(frame.image);if(current!==ticket)return;
      const [x,y,w,h]=overlay.checked?frame.overlayRect:frame.rawRect;
      canvas.getContext('2d').clearRect(0,0,canvas.width,canvas.height);
      canvas.getContext('2d').imageSmoothingEnabled=false;
      canvas.getContext('2d').drawImage(image,x,y,w,h,0,0,canvas.width,canvas.height);
      status.textContent=overlay.checked?'Красный — граница исходной костной маски; голубой — область просвета, если контур маски замкнут. Это разметка поверх КТ.':'Исходные плотности КТ, пересчитанные в косую плоскость. Это не изображение 3D-сетки.';
      canvas.dataset.frame=String(frame.index);canvas.dataset.loaded='true';
      onFrame(frame);
      const acquisition=frame.source_acquisition_step_mm??series.source_acquisition_step_mm??metadata.source_acquisition_step_mm;
      const grid=frame.registered_grid_step_mm??series.registered_grid_step_mm??metadata.registered_grid_step_mm;
      const decimal=value=>String(value).replace('.',',');
      host.querySelector('[data-source]').textContent=`${frame.source_label||series.source||metadata.source}. Шаг исходной съёмки ${decimal(acquisition)} мм; сетка срезов ${decimal(grid)} мм. Более мелкая сетка не означает более высокое разрешение съёмки. ${metadata.license}.`;
    }catch{images.delete(frame.image);if(current!==ticket)return;canvas.getContext('2d').clearRect(0,0,canvas.width,canvas.height);delete canvas.dataset.frame;status.textContent='Срез не загрузился. Перемести ползунок, чтобы повторить.';canvas.dataset.loaded='false';}
  }
  slider.oninput=draw;overlay.onchange=draw;
  const expand=host.querySelector('[data-expand]');
  expand.onclick=()=>{const enabled=document.body.classList.toggle('scan-expanded');expand.textContent=enabled?'Вернуться к 3D':'Увеличить срез';expand.setAttribute('aria-expanded',String(enabled));host.scrollIntoView({block:'start'});};
  return {
    select(data,id){
      const next=data?.series?.find(row=>row.id===id);host.hidden=!next;
      if(!next){ticket++;series=null;key=null;onFrame(null);document.body.classList.remove('scan-expanded');expand.textContent='Увеличить срез';expand.setAttribute('aria-expanded','false');return;}
      if(key===id&&metadata===data)return;
      host.querySelector('h3').textContent=next.ru+' · КТ';canvas.setAttribute('aria-label',next.ru+' — срез исходной КТ');
      key=id;metadata=data;series=next;slider.max=String(next.frames.length-1);slider.value=String(Math.max(0,next.frames.findIndex(f=>f.index===next.selectedSlice)));
      draw();
    }
  };
}
