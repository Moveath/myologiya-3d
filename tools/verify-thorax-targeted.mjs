import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const out=path.resolve(process.argv[2]);assert.ok(out.startsWith(path.resolve('research/evidence-runs')+path.sep));
const box={window:{}};vm.createContext(box);
for(const name of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile('site/'+name+'.js','utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS));
const write=(name,data)=>fs.writeFile(path.join(out,name),JSON.stringify(data,null,2)+'\n',{flag:'wx'});
if(process.argv.includes('--snapshot')){
 await write('atlas-before.json',A);
 const prior=JSON.parse(await fs.readFile('research/evidence-runs/stage5-thorax-batch2-2026-10-18T14-33-52-383Z-ETS7Lh/hashes-before.json','utf8'));
 const names=[...new Set([...Object.keys(prior),'scripts/thorax_terms.py','scripts/thorax_ribs_stage5.py','scripts/manifest_thorax.py','site/data-thorax.js','stl_thorax/BP24.stl','stl_thorax/BP28.stl','site/arm-q-glb.txt'])],hashes={};
 for(const f of names)hashes[f]=createHash('sha256').update(await fs.readFile(f)).digest('hex');
 await write('hashes-before.json',hashes);
 for(const n of ['ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md'])await fs.copyFile(n,path.join(out,'before-'+n),fs.constants.COPYFILE_EXCL);
 console.log(JSON.stringify({snapshot:A.pins.length,files:names.length}));
}else{
 const before=JSON.parse(await fs.readFile(path.join(out,'atlas-before.json'),'utf8')),byId=new Map(A.pins.map(p=>[p.id,p]));assert.equal(byId.size,2017);assert.equal(A.pins.length,before.pins.length);
 let changed=0;
 for(const p of before.pins){
  const q=byId.get(p.id);assert.ok(q);for(const k of ['id','b','c','t','ru','lat','p','n','geometryKind','side','inc','anchors','relations','partOf','relatedLandmarks'])assert.deepEqual(q[k],p[k],p.id+':'+k);
  const targeted=/^thorax_rib_\d+_(right|left)_A02_3_02_012$/.test(p.id)||/^shared_thorax_(intercostal_|superior_aperture|inferior_aperture)/.test(p.id);
  if(!targeted)assert.deepEqual(q,p,p.id);else if(JSON.stringify(q)!==JSON.stringify(p))changed++;
 }
 const crests=A.pins.filter(p=>/^thorax_rib_\d+_(right|left)_A02_3_02_012$/.test(p.id));assert.equal(crests.length,22);
 for(const p of crests){assert.equal(p.p,null);assert.equal(p.anatomyVerification,'incomplete');assert.equal(p.evidenceScope,'nomenclature_and_body_region_only');assert.equal(p.applicabilityReview.specimenPresence,'unconfirmed');assert.equal(p.applicabilityReview.variantClassification,'not_established');assert.ok(p.unresolvedFields.includes('specimen_presence'));assert.ok(p.x.includes('этом экземпляре'));}
 for(const side of ['right','left']){const b='thorax_costal_cartilages_'+side;assert.ok(A.bones[b].note.includes('I–VII'));assert.ok(A.bones[b].note.includes('не включены'));}
 assert.deepEqual(A.muscles,before.muscles);
 for(const [id,b]of Object.entries(before.bones))if(!id.startsWith('thorax_costal_cartilages_'))assert.deepEqual(A.bones[id],b);
 const hashes=JSON.parse(await fs.readFile(path.join(out,'hashes-before.json'),'utf8'));
 const allowed=new Set(['scripts/thorax_terms.py','scripts/thorax_ribs_stage5.py','scripts/manifest_thorax.py','site/pins-thorax.js','site/pins-shared.js','site/data-thorax.js','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);let protectedFiles=0;
 for(const [f,h]of Object.entries(hashes))if(!allowed.has(f)){assert.equal(createHash('sha256').update(await fs.readFile(f)).digest('hex'),h,f);protectedFiles++;}
 const rows=A.pins.filter(p=>/^(thorax_(rib_|sternum_|thoracic_)|extra_(sternum_|thoracic_)|shared_thorax_)/.test(p.id));
 assert.equal(rows.length,536);
 const inventory=rows.map(p=>({id:p.id,bone:p.b,code:p.c||null,kind:p.geometryKind,hasPoint:!!p.p,acceptedExtent:p.geometryReview?.extentAcceptance===true,needed:p.geometryRequirements?.neededEvidence||p.modelNote,issue:p.c==='A02.3.02.012'?'PIN-003':'GEO-THORAX-LANDMARKS',stage6:'Render accepted trace/mask/volume; do not infer from anchor',stage8:'Independent anatomical acceptance on identified specimen'}));
 assert.ok(inventory.every(p=>!p.acceptedExtent));
 await write('geometry-markup-inventory.json',inventory);
 const kinds={};for(const p of inventory)kinds[p.kind]=(kinds[p.kind]||0)+1;
 const result={status:'passed',global:2017,unchangedCoordinates:true,crestsReviewed:22,changedPins:changed,unchangedOtherPins:2017-changed,inventory:536,kinds,unlocated:inventory.filter(p=>!p.hasPoint).length,protectedFiles,acceptedCoordinates:0,acceptedExtents:0};
 await write('data-regression.json',result);console.log(JSON.stringify(result));
}

