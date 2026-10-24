// Isolated review build: canonical noModel flags and source HTML stay unchanged.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
const run=path.resolve(process.argv[2]),config=JSON.parse(await fs.readFile(path.join(run,'batch.json'),'utf8'));
const ids=Object.keys(config.targets),dir=path.join(config.output,'browser');
await fs.mkdir(dir,{recursive:true});
const sha=b=>createHash('sha256').update(b).digest('hex');
let html=await fs.readFile('site/local.html','utf8');const sourceHash=sha(html);
const probeSource=await fs.readFile('tools/prepare-stage5-thorax-mcp.mjs','utf8');
const probe=probeSource.match(/const probe=`([\s\S]*?)`;/)[1].replaceAll('__thoraxCheck','__footTrialCheck').replaceAll('\\n','\n');
function replace(a,b){if(html.split(a).length!==2)throw Error('Ambiguous anchor');html=html.replace(a,b);}
replace('<head>','<head><base href="/">');
replace('const A = window.ATLAS;',`const A = window.ATLAS;
for(const id of ${JSON.stringify(ids)}){
 A.bones[id]={...A.bones[id],noModel:false,modelFile:'/stage6-trial/'+id+'.glb',
 note:'ПРОБНАЯ ГЕОМЕТРИЯ: учебный допуск не получен. Пересечения суставных сеток требуют независимой проверки. Основной атлас сохраняет noModel.'};
}
const trialBanner=document.createElement('div');
trialBanner.id='trialNotice';trialBanner.textContent='ТЕСТОВАЯ СБОРКА · модели не допущены в основной атлас';
trialBanner.style.cssText='position:fixed;bottom:0;left:0;right:0;z-index:9000;background:#7c3300;color:white;padding:4px;pointer-events:none';
document.body.append(trialBanner);`);
const match=html.match(/id: 'leg',[^\n]+supplementalBones: (\[[^\]]+\])/);
if(!match)throw Error('Missing leg supplemental owners');
replace(match[0],match[0].replace(match[1],match[1].slice(0,-1)+','+ids.map(x=>JSON.stringify(x)).join(',')+']'));
replace('window.__atlas =',probe+'window.__atlas =');
await fs.writeFile(path.join(dir,'local-v1.html'),html,{flag:'wx'});
for(const id of ids)await fs.copyFile(path.join(config.output,id+'.glb'),path.join(dir,id+'.glb'),fs.constants.COPYFILE_EXCL);
await fs.writeFile(path.join(dir,'local-v1.html.manifest.json'),JSON.stringify({sourceHash,trialHash:sha(html),ids,canonicalNoModelChanged:false},null,2),{flag:'wx'});
console.log(JSON.stringify({dir,ids}));
