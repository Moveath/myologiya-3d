/* Kept independent of ES modules and WebGL so failure messages remain usable. */
(() => {
  let panel, reason=null;
  function clear() { if(panel)panel.remove();panel=null;reason=null; }
  function fail(kind) {
    clear();reason=kind;
    panel=document.createElement('aside');panel.id='runtimeFailure';panel.setAttribute('role','alert');
    panel.style.cssText='position:fixed;z-index:10000;left:50%;bottom:18px;transform:translateX(-50%);width:min(520px,calc(100% - 28px));padding:18px;border:2px solid #9ecac1;border-radius:14px;background:#152a27;color:#f0f8f5;font:14px/1.5 Arial,sans-serif;box-shadow:0 8px 35px #0006';
    const title=document.createElement('strong'),body=document.createElement('p');
    title.textContent=kind==='context'?'3D-просмотр приостановлен':kind==='webgl'?'Не удалось включить 3D':'Не удалось загрузить программу просмотра';
    body.textContent=kind==='context'?'Браузер потерял графический контекст. Просмотр продолжится после восстановления. Если этого не произошло, перезагрузи страницу.':kind==='webgl'?'Для моделей нужен WebGL. Проверь аппаратное ускорение в браузере или открой сайт в другом браузере.':'Проверь соединение и перезагрузи страницу. Файлы 3D-просмотра загружаются с этого же сайта.';
    const reload=document.createElement('button');reload.type='button';reload.textContent='Перезагрузить';reload.onclick=()=>location.reload();
    reload.style.cssText='font:inherit;padding:8px 12px;border:1px solid #9ecac1;border-radius:8px;background:#e7f4ef;color:#152a27;cursor:pointer';
    const back=document.createElement('a'),q=new URLSearchParams(location.search);
    back.href=(q.get('entry')==='local'?'local.html':'./')+'#head';back.textContent='Вернуться в атлас';back.style.cssText='color:#a9e6d8;margin-left:14px';
    if(q.get('embed')==='1'&&parent!==window)back.onclick=e=>{e.preventDefault();parent.postMessage({type:'atlas-close-detail'},location.origin);};
    panel.append(title,body,reload,back);document.body.append(panel);
  }
  function watch(canvas,onRestore) {
    canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();fail('context');});
    canvas.addEventListener('webglcontextrestored',()=>{if(reason==='context')clear();onRestore();});
  }
  let stopStartup = null;
  function watchStartup() {
    stopStartup?.();
    const failed = () => { if (!window.__ready && !reason) fail('module'); };
    window.addEventListener('error', failed);
    window.addEventListener('unhandledrejection', failed);
    stopStartup = () => {
      window.removeEventListener('error', failed);
      window.removeEventListener('unhandledrejection', failed);
      stopStartup = null;
    };
  }
  window.__atlasRuntime={fail,watch,watchStartup,ready(){stopStartup?.();},get reason(){return reason;}};
})();
