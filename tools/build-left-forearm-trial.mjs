// Separate review build. Never changes production HTML/data/noModel flags.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
const root=process.cwd(),dir=path.join(root,'build_stage6/left_forearm_v1/browser');
const entry=process.argv[2]??'local-v1.html';
if(!/^local(?:-v[0-9]+)?\.html$/.test(entry))throw Error('Invalid trial entry name');
await fs.mkdir(dir,{recursive:true});
const sha=b=>createHash('sha256').update(b).digest('hex');
let html=await fs.readFile('site/local.html','utf8');
const sourceHash=sha(html);
function replace(old,next){if(html.split(old).length!==2)throw Error('Trial patch anchor must occur once: '+old.slice(0,80));html=html.replace(old,next);}
replace('<head>','<head><base href="/">');
replace("const A = window.ATLAS;",`const A = window.ATLAS;
// Trial-only catalogue view; canonical data files keep noModel=true.
for(const id of ['radius_left','ulna_left']){
  A.bones[id]={...A.bones[id],noModel:false,note:'ПРОБНАЯ МОДЕЛЬ BodyParts3D 3.0. Сторона и масштаб проверены; точное суставное совмещение и разметка поверхностей не приняты. Основной атлас сохраняет noModel.',
  refs:[...A.bones[id].refs,{title:'BodyParts3D © DBCLS — CC BY-SA 2.1 Japan',url:'https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en'}]};
}
for(const pin of A.pins){
  if(['radius_left','ulna_left'].includes(pin.b)||(pin.relations||[]).some(r=>['radius_left','ulna_left'].includes(r.bone))){
    pin.modelNote='Только в этой тестовой сборке загружены две пробные сетки предплечья. Суставные поверхности, капсула, контуры и координаты не приняты. В основном атласе noModel сохраняется.';
  }
}
const trialBanner=document.createElement('div');
trialBanner.id='trialNotice';trialBanner.textContent='ТЕСТОВАЯ СБОРКА · суставное совмещение не принято';
trialBanner.style.cssText='position:fixed;bottom:0;left:0;right:0;z-index:9000;background:#7c3300;color:white;text-align:center;padding:4px;font:11px sans-serif;pointer-events:none';
document.body.append(trialBanner);`);
replace('Кости обеих рук; левая кисть и предплечье пока без 3D-моделей','Пробные модели левого предплечья; левая кисть пока без 3D-моделей');
replace('    return register(main, id);',`    return (async()=>{
      if(id==='arm'){
        for(const bone of ['radius_left','ulna_left']){
          const response=await fetch('/stage6-trial/'+bone+'.glb');
          if(!response.ok)throw Error('Trial model load failed: '+bone);
          const gltf=await new GLTFLoader().parseAsync(await response.arrayBuffer(),'');
          main.scene.add(gltf.scene);
        }
      }
      return register(main,id);
    })();`);
await fs.writeFile(path.join(dir,entry),html,{flag:'wx'});
const files=[];
for(const bone of ['radius_left','ulna_left']){
 const bytes=await fs.readFile('build_stage6/left_forearm_v1/'+bone+'.glb');
 try{await fs.writeFile(path.join(dir,bone+'.glb'),bytes,{flag:'wx'});}
 catch(e){if(e.code!=='EEXIST'||!(await fs.readFile(path.join(dir,bone+'.glb'))).equals(bytes))throw e;}
 files.push({id:bone,sha256:sha(bytes),bytes:bytes.length});
}
const license=`BodyParts3D, Copyright© The Database Center for Life Science licensed by CC Attribution-Share Alike 2.1 Japan.
Source: BodyParts3D 3.0 / 20110915 / BodyParts3D_3.0_obj_95.zip; FMA23465 and FMA23468.
https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/README_e.html
https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en
https://creativecommons.org/licenses/by-sa/2.1/jp/legalcode.ja
Changes: OBJ to GLB in Blender 5.2.2; millimetres to metres and Z-up to Y-up. No decimation, reflection, mesh repair or fitted registration.
These derivative model files remain CC BY-SA 2.1 Japan. Commercial use is permitted subject to its terms: attribution, ShareAlike for derivatives, licence notice and no added restrictions on licensed material.
Research trial: joint surfaces/registration and pin locations are not accepted. Not a clinical model.
`;
try{await fs.writeFile(path.join(dir,'LICENSE-MODELS.txt'),license,{flag:'wx'});}
catch(e){if(e.code!=='EEXIST'||(await fs.readFile(path.join(dir,'LICENSE-MODELS.txt'),'utf8'))!==license)throw e;}
await fs.writeFile(path.join(dir,entry+'.manifest.json'),JSON.stringify({entry,sourceHTMLSHA256:sourceHash,trialHTMLSHA256:sha(html),files,productionNoModelChanged:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({dir,files,productionChanged:false}));
