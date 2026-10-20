import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds,contributingBoneIds,hasLandmarkPosition} from '../site/atlas-landmarks.js';
const out=path.resolve(process.argv[2]);assert.ok(out.startsWith(path.resolve('research/evidence-runs')+path.sep));
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)), before=JSON.parse(await fs.readFile(out+'/atlas-before.json','utf8')),idx=indexLandmarks(A.pins);
const owners=Object.keys(before.bones).filter(b=>before.bones[b].sub==='hand');
const original=before.pins.filter(p=>owners.includes(p.b)),rows=original.map(p=>idx.byId[p.id]);assert.equal(rows.length,81);
assert.deepEqual(A.muscles,before.muscles);assert.deepEqual(A.contextBoneSources,before.contextBoneSources);
for(const p of before.pins){const q=idx.byId[p.id];assert.ok(q,p.id);assert.deepEqual(q.p,p.p);assert.deepEqual(q.n,p.n);assert.deepEqual(q.m,p.m);
 if(!owners.includes(p.b))assert.deepEqual(q,p,p.id);else{assert.equal(q.b,p.b);assert.equal(q.c,p.c);}}
for(const [b,d] of Object.entries(before.bones))assert.deepEqual(A.bones[b],owners.includes(b)?{...d,side:'right'}:d,b);
const newBones=Object.keys(A.bones).filter(b=>!before.bones[b]);assert.deepEqual(newBones,['sesamoid_mcp1_radial_right','sesamoid_mcp1_ulnar_right']);
for(const b of newBones){assert.equal(A.bones[b].noModel,true);assert.equal(A.bones[b].side,'right');assert.ok(!A.bones[b].sourceId);assert.ok(!A.bones[b].code);assert.equal(A.bones[b].collectiveCode,'A02.4.11.001');}
assert.equal(A.bones.radius_left.noModel,true);assert.equal(A.bones.ulna_left.noModel,true);
const added=A.pins.filter(p=>!before.pins.some(q=>q.id===p.id));assert.equal(added.length,32);
const kinds={},newKinds={};let edges=0;
for(const p of [...rows,...added]){assert.ok(['point','line','area','space','volume'].includes(p.geometryKind),p.id);
 assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
 assert.equal(p.side,'right');assert.ok(p.geometryKindReason.length>30);assert.ok(p.refs.length>=2);assert.ok(p.modelNote);
 if(p.partOf)assert.ok(idx.byId[p.partOf]);for(const b of relatedBoneIds(p)){assert.ok(A.bones[b],b);assert.equal(idx.byBone[b].filter(q=>q.id===p.id).length,1);}
 (original.some(q=>q.id===p.id)?kinds:newKinds)[p.geometryKind]=((original.some(q=>q.id===p.id)?kinds:newKinds)[p.geometryKind]||0)+1;
}
for(const p of added){assert.equal(p.p,null);assert.equal(p.n,null);assert.deepEqual(p.m,[]);assert.equal(hasLandmarkPosition(p),false);if(p.anatomicalEntity==='joint')edges+=relatedBoneIds(p).length;}
assert.equal(added.filter(p=>p.anatomicalEntity==='joint').length,17);
assert.equal(added.filter(p=>p.anatomicalVariant).length,5);
assert.deepEqual(relatedBoneIds(idx.byId.carp_os_centrale),['scaphoid','trapezoid','capitate']);assert.equal(contributingBoneIds(idx.byId.carp_os_centrale).length,0);assert.equal(hasLandmarkPosition(idx.byId.carp_os_centrale),false);
assert.equal(contributingBoneIds(idx.byId.carp_sulcus_carpi).length,8);assert.equal(idx.byId.carp_sulcus_carpi.geometryKind,'area');
assert.equal(idx.byId.extra_hand_carpal_tunnel.geometryKind,'space');assert.deepEqual(idx.byId.extra_hand_carpal_tunnel.softTissueComponents,['flexor_retinaculum']);
assert.deepEqual(relatedBoneIds(idx.byId.extra_hand_mcp1_joint),['metacarpal_1','phalanx_prox_1',...newBones]);
assert.ok(!relatedBoneIds(idx.byId.extra_hand_radiocarpal_joint).includes('ulna'));
const allow=new Set(['scripts/make_pins.py','scripts/make_context_bone_data.py','site/data-context-bones.js','site/pins.js','site/index.html','site/local.html','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);
let protectedFiles=0;for(const [f,h] of Object.entries(JSON.parse(await fs.readFile(out+'/hashes-before.json','utf8'))))if(!allow.has(f)){assert.equal(createHash('sha256').update(await fs.readFile(f)).digest('hex'),h,f);protectedFiles++;}
const prior='research/evidence-runs/stage5-left-forearm-2026-10-18T19-20-46-330Z-35NAkG/left-forearm-resources.json';
const resources=JSON.parse(await fs.readFile(prior,'utf8'));
for(const r of resources.resources)assert.equal(createHash('sha256').update(await fs.readFile(r.file)).digest('hex'),r.sha256,r.file);
const geometry=JSON.parse(await fs.readFile(out+'/trimesh-hand.json','utf8'));assert.equal(geometry.status,'passed');
const result={status:'passed',originalBoneCards:27,softCards:1,originalRecords:81,kinds,newKinds,addedBoneCards:newBones,addedRecords:added.length,
 sharedJoints:17,jointEdges:edges,unchangedOtherPins:before.pins.length-81,totalPins:A.pins.length,withoutPosition:A.pins.filter(p=>!p.p).length,
 protectedFiles,protectedModelResources:resources.resources.length,resourceEvidenceReused:prior,newCoordinates:0,acceptedCoordinates:0,originalMarkersSuppressed:['carp_os_centrale']};
for(const [file,data] of [['data-regression',result],['reviewed-records',rows],['added-records',added],['bone-inventory',Object.entries(A.bones).filter(([b,d])=>d.sub==='hand').map(([id,d])=>({id,...d}))]])
 await fs.writeFile(path.join(out,file+'.json'),JSON.stringify(data,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
