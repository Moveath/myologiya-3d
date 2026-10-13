// Authorized USB check: local site on 8871, adb reverse tcp:8871 tcp:8871,
// adb forward tcp:9223 localabstract:chrome_devtools_remote.
// Reads only its new atlas tab and closes only that tab. No viewport emulation.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),out=path.join(root,'shots/mobile-device');
await fs.mkdir(out,{recursive:true});
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function connect(url){
 const ws=new WebSocket(url),pending=new Map();let seq=0;const exceptions=[];
 ws.onmessage=e=>{const d=JSON.parse(e.data);if(d.method==='Runtime.exceptionThrown')exceptions.push(d.params.exceptionDetails.exception?.description||d.params.exceptionDetails.text);if(d.id&&pending.has(d.id)){const p=pending.get(d.id);clearTimeout(p.timer);pending.delete(d.id);d.error?p.reject(new Error(JSON.stringify(d.error))):p.resolve(d.result);}};
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
 return {exceptions,close:()=>ws.close(),send:(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;const timer=setTimeout(()=>{pending.delete(id);reject(new Error('Timeout: '+method));},30000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}));})};
}
const info=await(await fetch('http://127.0.0.1:9223/json/version')).json(),browser=await connect(info.webSocketDebuggerUrl);
const report={physicalDevice:'OPPO Reno5 Lite / CPH2205',browser:info.Browser,method:'Real Android Chrome over USB, CDP touch gestures; no viewport emulation',cases:[],errors:[]};
let target,cdp;
try{
 target=(await browser.send('Target.createTarget',{url:'http://localhost:8871/local.html?theme=dark#head'})).targetId;
 const tabs=await(await fetch('http://127.0.0.1:9223/json/list')).json(),own=tabs.find(t=>t.id===target);assert.ok(own,'Own test tab');
 cdp=await connect(own.webSocketDebuggerUrl);await cdp.send('Runtime.enable');await cdp.send('Page.enable');await cdp.send('Page.bringToFront');
 const evaluate=async expression=>{const r=await cdp.send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true,userGesture:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 const visible=selector=>evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});return !!e?.getClientRects().length;})()`);
 const tap=async selector=>{const p=await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()`);await cdp.send('Input.synthesizeTapGesture',{...p,duration:80,tapCount:1,gestureSourceType:'touch'});await delay(400);};
 const choose=(selector,value)=>evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});e.value=${JSON.stringify(value)};e.dispatchEvent(new Event('change',{bubbles:true}));})()`);
 const shot=async name=>{const r=await cdp.send('Page.captureScreenshot',{format:'png'});await fs.writeFile(path.join(out,name+'.png'),Buffer.from(r.data,'base64'));};
 let ready=false;for(let n=0;n<180;n++){ready=await evaluate(`!!(window.__ready&&window.__atlas.state.sec==='head'&&document.querySelector('#veil').hidden)`);if(ready)break;await delay(500);}assert.ok(ready,'Atlas loaded on phone');await delay(600);
 report.viewport=await evaluate(`({width:innerWidth,height:innerHeight,dpr:devicePixelRatio,canvasWidth:document.querySelector('canvas').width,canvasHeight:document.querySelector('canvas').height})`);
 assert.ok(report.viewport.width<900);assert.equal(await visible('#sheet'),false);await shot('head-dark');
 await tap('#mobileCard');assert.equal(await visible('#sheet'),true,'Description opens with touch');await tap('#closeMobileCard');assert.equal(await visible('#sheet'),false);
 await tap('#bOptions');await tap('[data-peel="3"]');await tap('#bBoneColors');await choose('#renderQualityChoice','detail');await shot('options-dark');await tap('#closeOptions');
 for(const mode of ['detail','auto']){
  await tap('#bOptions');await choose('#renderQualityChoice',mode);await tap('#closeOptions');
  await evaluate(`(()=>{window.__rafTimes=[];window.__rafStop=false;let last=performance.now();const tick=t=>{__rafTimes.push(t-last);last=t;if(!__rafStop)requestAnimationFrame(tick);};requestAnimationFrame(tick);})()`);
  const x=Math.round(report.viewport.width/2),y=Math.round(report.viewport.height*.48);
  await cdp.send('Input.synthesizePinchGesture',{x,y,scaleFactor:1.25,relativeSpeed:250,gestureSourceType:'touch'});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:x-45,y,id:1,radiusX:4,radiusY:4}]});
  for(let i=0;i<18;i++){await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x-45+i*5,y:y+Math.sin(i/3)*12,id:1,radiusX:4,radiusY:4}]});await delay(24);}
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await delay(700);
  const frames=await evaluate(`(()=>{__rafStop=true;const a=__rafTimes.filter(x=>x>0).sort((a,b)=>a-b);return {samples:a.length,medianMs:a[Math.floor(a.length/2)],p95Ms:a[Math.floor(a.length*.95)],settledRatio:document.querySelector('canvas').width/document.querySelector('canvas').clientWidth};})()`);
  const expected=Math.min(report.viewport.dpr,3),restorationStarted=Date.now();
  for(let n=0;n<50&&frames.settledRatio!==expected;n++){await delay(100);frames.settledRatio=await evaluate(`document.querySelector('canvas').width/document.querySelector('canvas').clientWidth`);}
  frames.additionalRestorationWaitMs=Date.now()-restorationStarted;
  report.cases.push({quality:mode,browserAnimationFrameIntervals:frames});assert.equal(frames.settledRatio,expected);
 }
 await shot('skull-dark-detail');
 await evaluate(`__atlas.goTo('frontal')`);assert.equal(await visible('#sheet'),true);await shot('card-dark');await tap('#closeMobileCard');assert.equal(await evaluate(`__atlas.state.sel`),'frontal');
 await evaluate(`__atlas.enterSection('trunk')`);await choose('#mobileSub','spine');await tap('#bOptions');await tap('#bContext');await tap('#closeOptions');await tap('#mobileFit');await delay(700);await shot('thorax-dark');
 assert.equal(await evaluate('document.documentElement.scrollWidth>innerWidth+1'),false);report.errors=cdp.exceptions;assert.deepEqual(report.errors,[]);report.status='passed';
}catch(e){report.status='failed';report.failure=String(e);process.exitCode=1;}
finally{
 if(cdp)cdp.close();if(target)await browser.send('Target.closeTarget',{targetId:target}).catch(()=>{});browser.close();
 await fs.writeFile(path.join(root,'verify/mobile-device.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}
