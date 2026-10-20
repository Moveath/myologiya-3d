import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import {createEvidenceRun} from './evidence-run.mjs';
import {indexLandmarks,relatedBoneIds} from '../site/atlas-landmarks.js';
const root=process.cwd(), baseline='research/evidence-runs/stage5-thorax-batch2-2026-10-18T14-33-52-383Z-ETS7Lh';
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile(`site/${n}.js`,'utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)), idx=indexLandmarks(A.pins);
const old=JSON.parse(await fs.readFile(path.join(baseline,'atlas-before.json'),'utf8'));
const isOriginal=p=>/^thorax_(rib_|sternum_)/.test(p.id), rows=A.pins.filter(isOriginal);
assert.equal(rows.length,246);assert.equal(new Set(rows.map(p=>p.b)).size,25);
assert.equal(rows.filter(p=>p.p).length,113);
assert.deepEqual(A.bones,old.bones);assert.deepEqual(A.muscles,old.muscles);assert.deepEqual(A.thoraxWholeTerms,old.thoraxWholeTerms);
for(const p of old.pins){const q=idx.byId[p.id];assert.ok(q,p.id);
 for(const k of ['id','b','c','ru','lat','p','n','loc','secondaryMarkers','anchorStatus'])assert.deepEqual(q[k],p[k],p.id+':'+k);
 if(!isOriginal(p))assert.deepEqual(q,p,p.id+' unrelated record');
 else {assert.ok(['area','volume','line','space'].includes(q.geometryKind));assert.ok(q.geometryKindReason);assert.equal(q.geometryReview.coordinateAcceptance,false);assert.equal(q.geometryRequirements.coordinateReuse,false);assert.ok(q.modelNote.startsWith(p.modelNote));}
}
const previous=new Set(old.pins.map(p=>p.id)), added=A.pins.filter(p=>!previous.has(p.id));assert.equal(added.length,48);
const shared=added.filter(p=>p.relations);assert.equal(shared.length,24);assert.equal(shared.reduce((s,p)=>s+p.relations.length,0),54);
assert.ok(added.filter(p=>!p.relations).every(p=>p.t==='additional'&&!p.c),'Descriptive instances must not inflate TA98 list');
for(const p of [...rows,...added]){
 assert.ok(new Set(p.refs.map(r=>r.url.split('#')[0])).size>=2,p.id+' references');
 for(const id of p.relatedLandmarks||[])assert.ok(idx.byId[id],p.id+' linked '+id);
 if(p.partOf)assert.ok(idx.byId[p.partOf],p.id+' parent');
 for(const b of relatedBoneIds(p)){assert.ok(A.bones[b]);assert.equal(idx.byBone[b].filter(q=>q.id===p.id).length,1);assert.equal(idx.byBone[b].find(q=>q.id===p.id),p);}
 if(added.includes(p)){assert.ok(!p.p&&!p.n);assert.equal(p.geometryReview.extentAcceptance,false);}
}
for(let i=1;i<=12;i++)for(const side of ['right','left']){
 const b=`rib_${i}_${side}`, get=n=>idx.byId[`thorax_${b}_A02_3_02_${String(n).padStart(3,'0')}`];
 assert.ok(rows.filter(p=>p.b===b).every(p=>p.side===side));
 if(i===1)for(const n of [4,6,10,11,12])assert.ok(!get(n));
 if(i>=11)for(const n of [4,5,6,8,9])assert.ok(!get(n));
 if(i===12)for(const n of [10,11])assert.ok(!get(n));
 if(i===10){assert.equal(get(4).inc,1);assert.equal(get(9).inc,1);assert.ok(!get(3).relatedLandmarks.some(id=>id.includes('thoracic_9')));}
 if(i>1){assert.equal(get(12).p,null);assert.equal(get(12).anatomyVerification,'incomplete');assert.equal(get(12).evidenceScope,'nomenclature_and_body_region_only');assert.ok(get(12).unresolvedFields.includes('topography'));assert.equal(get(12).refs.filter(r=>r.id==='rib_crest_academy').length,1);}
 if(i<12){const p=idx.byId[`shared_thorax_intercostal_${i}_${side}`];assert.deepEqual(relatedBoneIds(p),[b,`rib_${i+1}_${side}`]);assert.equal(p.side,side);assert.equal(p.level,i);assert.ok(p.missingParticipants.length);}
}
for(const side of ['right','left'])for(let i=1;i<=7;i++){
 const p=idx.byId[`extra_sternum_costal_notch_${i}_${side}`];assert.equal(p.side,side);assert.equal(p.level,i);
 const parts=i===1?[2]:i===2?[2,6]:i===7?[6,7]:[6];
 assert.deepEqual(p.sternalParts,parts.map(n=>`thorax_sternum_A02_3_03_00${n}`));assert.ok(!p.relations,'Cartilage must not be replaced by a bone relation');
}
assert.deepEqual(relatedBoneIds(idx.byId.shared_thorax_superior_aperture),['thoracic_1','rib_1_right','rib_1_left','sternum']);
assert.deepEqual(relatedBoneIds(idx.byId.shared_thorax_inferior_aperture),['thoracic_12','rib_11_right','rib_11_left','rib_12_right','rib_12_left','sternum']);
const hashes=JSON.parse(await fs.readFile(path.join(baseline,'hashes-before.json'),'utf8'));
const changed=new Set(['scripts/make_pins_thorax.py','scripts/make_shared_landmarks.py','site/pins-thorax.js','site/pins-shared.js','site/index.html','site/local.html','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);let protectedFiles=0;
const oldHtml=await fs.readFile(path.join(baseline,'index-before.html'),'utf8');
assert.equal(await fs.readFile('site/index.html','utf8'),oldHtml.replace("q.t === 'ta' ? 'TA98' : 'мышца'","q.t === 'ta' ? 'TA98' : q.t === 'additional' ? 'ориентир' : 'мышца'"),'Only search classification text may change');
for(const [f,h]of Object.entries(hashes))if(!changed.has(f)){assert.equal(createHash('sha256').update(await fs.readFile(f)).digest('hex'),h,f);protectedFiles++;}
const result={status:'passed',bones:25,ribs:24,originalRecords:246,classified:246,kinds:Object.fromEntries(['point','line','area','space','volume'].map(k=>[k,rows.filter(p=>p.geometryKind===k).length])),
 newRecords:48,newOwn:24,newShared:24,newBoneRelations:54,originalCoordinates:113,unlocated:181,unchangedOtherRecords:old.pins.length-246,
 cristaTopographyUnresolved:22,globalRecords:A.pins.length,globalUnlocated:A.pins.filter(p=>!p.p).length,protectedFiles,acceptedCoordinates:0,acceptedExtents:0,
 records:[...rows,...added].map(p=>({id:p.id,bone:p.b,name:p.ru,kind:p.geometryKind,located:!!p.p,side:p.side||null,partOf:p.partOf||null,bones:relatedBoneIds(p),related:p.relatedLandmarks||[],requirements:p.geometryRequirements,refs:p.geometryTypeRefs||p.refs}))};
const run=await createEvidenceRun(root,'stage5-ribs-data');await run.write('data-regression.json',result);
console.log(JSON.stringify({...result,records:undefined,evidence:run.dir}));
