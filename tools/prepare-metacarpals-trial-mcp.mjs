import fs from 'node:fs/promises';import path from 'node:path';
const dir=path.resolve(process.argv[2]),root=process.cwd();
const old=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');const probe=old.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__forearmCheck').replaceAll('\\n','\n');
const models={};for(const i of [1,3])models[`metacarpal_${i}_left.glb`]=(await fs.readFile(`build_stage6/left_metacarpals_v1/metacarpal_${i}_left.glb`)).toString('base64');
async function trial(page,{dir,root,width,probe,models}){
 const checks=[];let timer;const errors=[];const onError=e=>errors.push(String(e));page.on('pageerror',onError);
 const check=(ok,label)=>{if(!ok)throw Error(label);checks.push(label);};
 const job=async()=>{
 await page.unrouteAll({behavior:'ignoreErrors'});await page.setViewportSize({width,height:width===390?844:900});page.setDefaultTimeout(5000);
 await page.route('https://fonts.googleapis.com/**',r=>r.fulfill({body:'',contentType:'text/css'}));
 await page.route('**/__mc-trial/*.glb',async r=>{const name=new URL(r.request().url()).pathname.split('/').pop();if(!['metacarpal_1_left.glb','metacarpal_3_left.glb'].includes(name))throw Error('Unexpected trial file');await r.fulfill({contentType:'model/gltf-binary',body:Buffer.from(models[name],'base64')});});
 await page.route('**/local.html*',async r=>{const response=await r.fetch();let html=await response.text();
 const anchor="'metacarpal_5_left']";check(html.split(anchor).length===2,'Unique test-only supplemental anchor');html=html.replace(anchor,"'metacarpal_5_left','metacarpal_1_left','metacarpal_3_left']");
 html=html.replace('const A = window.ATLAS;',`const A = window.ATLAS;
 for(const id of ['metacarpal_1_left','metacarpal_3_left'])A.bones[id]={...A.bones[id],noModel:false,modelFile:'__mc-trial/'+id+'.glb',note:'ТОЛЬКО ТЕСТОВАЯ СБОРКА: совмещение основания не принято'};
 const trialBanner=document.createElement('div');trialBanner.textContent='ТЕСТ: 13 костей. I и III пястные НЕ ДОПУЩЕНЫ в основной атлас';trialBanner.style.cssText='position:fixed;bottom:0;z-index:9999;background:#7c3300;color:white;pointer-events:none;font-size:12px';document.body.append(trialBanner);`);
 html=html.replace('window.__atlas =',probe+'window.__atlas =');await r.fulfill({response,body:html});});
 await page.goto('http://127.0.0.1:8783/local.html?theme=dark',{waitUntil:'domcontentloaded',timeout:18000});await page.waitForFunction(()=>window.__ready);
 await page.evaluate(async()=>{await __atlas.enterSection('arm');await __atlas.goTo('metacarpal_2_left');__atlas.setSub('hand');__atlas.setSide('left');});
 const expected=['scaphoid_left','lunate_left','triquetrum_left','pisiform_left','trapezium_left','trapezoid_left','capitate_left','hamate_left',...Array.from({length:5},(_,i)=>`metacarpal_${i+1}_left`)];
 const visible=await page.evaluate(()=>__forearmCheck.snapshot().visible);check(expected.every(id=>visible.includes(id)),'All thirteen source-frame models loaded together in trial only');
 check(visible.every(id=>id.endsWith('_left')),'No right-side substitute');
 if(await page.locator('#closeMobileCard').isVisible())await page.locator('#closeMobileCard').click();
 await page.waitForTimeout(1000);check(await page.locator('#app').getAttribute('data-card-open')!=='true','Trial model viewport not covered by mobile card');
 await page.screenshot({path:dir+`/trial13-v3-${width}.png`});check(!errors.length,'No trial page errors');return {status:'passed',width,phase:'trial13',checks,errors,productionAdmission:false};
 };
 try{return await Promise.race([job(),new Promise((_,reject)=>timer=setTimeout(()=>{page.close().catch(()=>{});reject(Error('40000ms deadline'));},40000))]);}catch(e){return {status:'failed',width,phase:'trial13',checks,errors,error:String(e)};}finally{clearTimeout(timer);page.off('pageerror',onError);}
}
for(const width of [1280,390])await fs.writeFile(path.join(dir,`mcp-trial13-v3-${width}.js`),`async(page)=>(${trial.toString()})(page,${JSON.stringify({dir,root,width,probe,models})})`,{flag:'wx'});
