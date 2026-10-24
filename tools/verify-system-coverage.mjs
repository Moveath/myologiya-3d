import fs from 'node:fs/promises';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {systemCoverage} from '../site/atlas-systems.js';
let checks=0;
const check=(v,label)=>{assert.ok(v,label);checks++;};
const c={window:{}};vm.createContext(c);
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','data-muscle-recovery','data-neck-recovery','data-cardiovascular'])
  vm.runInContext(await fs.readFile('site/'+name+'.js','utf8'),c);
const A=c.window.ATLAS,groups=Object.fromEntries(A.structureGroups.map(g=>[g.id,g]));
const systems={arteries:true,veins:true},regions={};
for(const [sec,cards,models]of [['arm',16,0],['neck',8,8],['leg',30,12],['trunk',33,26]]){
  const result=systemCoverage(A.structures,groups,sec,'both',systems);
  check(result.ids.length===cards,sec+' actual cards');check(result.models.length===models,sec+' admitted models');
  check(result.missing===cards-models,sec+' missing geometry');regions[sec]={cards,models};
}
check(systemCoverage(A.structures,groups,'arm','left',systems).ids.length===8,'left arm keeps only eight cards');
check(systemCoverage(A.structures,groups,'neck','left',systems).models.length===4,'left neck has four models');
check(systemCoverage(A.structures,groups,'arm','both',{}).ids.length===0,'disabled systems do not report missing geometry');
check(systemCoverage(A.structures,groups,'arm','both',{heart:true}).ids.length===0,'heart not invented in arm');
const leftHeart=systemCoverage(A.structures,groups,'trunk','left',{heart:true}).models;
check(leftHeart.length===3&&leftHeart.includes('cv_heart')&&!leftHeart.includes('cv_valve_tricuspid'),'heart side filter retains unseparated models and excludes the right valve');
const html=await fs.readFile('site/index.html','utf8');
const script=html.match(/<script type="module"[^>]*>([\s\S]*?)<\/script>/)[1];
new vm.Script(script.replace(/^import .*;$/gm,''));check(true,'main module syntax');
const frameSub=script.slice(script.indexOf('function frameSub('),script.indexOf('function resetView()'));
for(const section of ['neck','trunk']){
  const list=new Map(['atlas','axis','cervical_7','hyoid','sternocleidomastoid_right','sternocleidomastoid_left','vessel'].map(id=>[id,{id,kind:id==='vessel'?'s':'b'}]));
  let framed;
  const ctx={state:{sec:section},SEC:{[section]:{subs:[{id:'all',v:'ant'}]}},curSub:()=> 'all',structs:list,shownIds:()=>[...list.keys()],visState:s=>s.kind==='s'?2:0,frame:ids=>{framed=ids;},resetView:()=>{}};
  vm.createContext(ctx);vm.runInContext(frameSub+'\nframeSub(true)',ctx);
  check(framed.length===1&&framed[0]==='vessel',section+' vessels-only camera frames visible geometry');
  ctx.visState=s=>s.kind==='b'?2:0;vm.runInContext('frameSub(true)',ctx);
  check(framed.length>0&&!framed.includes('vessel'),section+' ordinary bone framing preserved');
}
const result={status:'passed',checks,regions};
if(process.argv[2])await fs.writeFile(process.argv[2],JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
