import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {indexLandmarks,relatedBoneIds,hasLandmarkPosition} from '../site/atlas-landmarks.js';
const out=path.resolve(process.argv[2]);assert.ok(out.startsWith(path.resolve('research/evidence-runs')+path.sep));
const tag=process.argv[3]||'';assert.ok(!tag||/^[a-z0-9-]+$/.test(tag));const suffix=tag?'-'+tag:'';
const box={window:{}};vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)), before=JSON.parse(await fs.readFile(out+'/atlas-before.json','utf8')), idx=indexLandmarks(A.pins);
assert.equal(new Set(A.pins.map(p=>p.id)).size,A.pins.length);
for(const p of before.pins)assert.deepEqual(idx.byId[p.id],p,p.id);
for(const [id,b] of Object.entries(before.bones))assert.deepEqual(A.bones[id],b,id);
assert.deepEqual(A.muscles,before.muscles);assert.deepEqual(A.contextBoneSources,before.contextBoneSources);
const added=A.pins.filter(p=>!before.pins.some(q=>q.id===p.id));assert.equal(added.length,44);
const bones=Object.keys(A.bones).filter(id=>!before.bones[id]);assert.deepEqual(bones,['radius_left','ulna_left']);
for(const b of bones){assert.equal(A.bones[b].noModel,true);assert.equal(A.bones[b].side,'left');assert.ok(!A.contextBoneSources[b]);
 assert.ok(!A.bones[b].sourceId);assert.deepEqual(A.bones[b].contextTargets,['humerus_left']);}
let edges=0;const types={};
for(const p of added){assert.equal(p.p,null);assert.equal(p.n,null);assert.deepEqual(p.m,[]);assert.equal(hasLandmarkPosition(p),false);
 assert.equal(p.side,'left');assert.equal(p.geometryReview.coordinateAcceptance,false);assert.equal(p.geometryReview.extentAcceptance,false);
 assert.equal(p.geometryRequirements.status,'missing_source_model');assert.ok(new Set(p.refs.map(r=>new URL(r.url).host)).size>=2);
 assert.ok(['point','line','area','space','volume'].includes(p.geometryKind));types[p.geometryKind]=(types[p.geometryKind]||0)+1;
 if(p.partOf)assert.ok(idx.byId[p.partOf],p.partOf);
 for(const b of relatedBoneIds(p)){assert.ok(A.bones[b]);assert.ok(b.endsWith('_left'));assert.equal(idx.byBone[b].filter(q=>q.id===p.id).length,1);assert.equal(idx.byBone[b].find(q=>q.id===p.id),p);}
 if(p.anatomicalEntity==='joint')edges+=relatedBoneIds(p).length;
}
assert.equal(edges,11);assert.equal(added.filter(p=>p.t==='ta'&&p.b==='radius_left').length,19);assert.equal(added.filter(p=>p.t==='ta'&&p.b==='ulna_left').length,16);
assert.deepEqual(relatedBoneIds(idx.byId.extra_humerus_left_elbow_joint),['humerus_left','radius_left','ulna_left']);
assert.equal(idx.byId.context_ulna_left_A02_4_06_016.partOf,'context_ulna_left_A02_4_06_015');
const allow=new Set(['scripts/ta98.py','scripts/make_context_bone_data.py','site/data-context-bones.js','site/pins-context-bones.js','site/index.html','site/local.html','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']);
let protectedFiles=0;for(const [f,h] of Object.entries(JSON.parse(await fs.readFile(out+'/hashes-before.json','utf8'))))if(!allow.has(f)){assert.equal(createHash('sha256').update(await fs.readFile(f)).digest('hex'),h,f);protectedFiles++;}
const resources=JSON.parse(await fs.readFile(out+'/left-forearm-resources.json','utf8'));
for(const r of resources.resources)assert.equal(createHash('sha256').update(await fs.readFile(r.file)).digest('hex'),r.sha256,r.file);
const blender=JSON.parse(await fs.readFile(out+'/blender-left-forearm.json','utf8'));assert.ok(blender.originalScenePreserved);assert.equal(blender.meshes.length,resources.trimeshMeshes.length);
// Pair independent world bounds by file and ancestor identity; both imports preserve identities.
const identity=chain=>chain.find(n=>/^[bmoc]\|/.test(n));let maxDifference=0;const vertexCountDifferences=[],faceCountDifferences=[];
for(const b of blender.meshes){const q=resources.trimeshMeshes.find(t=>t.file===b.file&&identity(t.ancestry)===identity(b.ancestry));assert.ok(q,b.name);
 // glTF split vertices may be merged by the Blender importer. Compare triangles and world bounds,
 // record vertex indexing differences without treating them as changed source geometry.
 if(q.vertices!==b.vertices)vertexCountDifferences.push({identity:identity(b.ancestry),trimesh:q.vertices,blender:b.vertices});
 if(q.faces!==b.triangles)faceCountDifferences.push({identity:identity(b.ancestry),trimesh:q.faces,blender:b.triangles});
 if(['b|radius','b|ulna','b|humerus_left','b|scapula_left','b|clavicle_left'].includes(identity(b.ancestry)))assert.equal(q.faces,b.triangles);
 for(let i=0;i<2;i++)for(let j=0;j<3;j++)maxDifference=Math.max(maxDifference,Math.abs(q.boundsM[i][j]-b.boundsThreeM[i][j]));}
assert.ok(maxDifference<1e-6,maxDifference);
const result={status:'passed',addedBoneCards:bones,addedRecords:44,types,sharedJoints:5,sharedEdges:edges,unchangedPins:before.pins.length,
 totalPins:A.pins.length,withoutPosition:A.pins.filter(p=>!p.p).length,protectedFiles,protectedModelResources:resources.resources.length,
 geometryObjectsCompared:blender.meshes.length,maximumBoundsDifferenceM:maxDifference,vertexCountDifferences,faceCountDifferences,
 geometryScope:'Identity/bounds inventory only. Triangle equality required for forearm and left upper-girdle bones; other importer count differences retained, no whole-mesh quality acceptance.',newCoordinates:0,geometryAccepted:false};
for(const [file,value] of [['data-regression',result],['added-records',added]])await fs.writeFile(path.join(out,file+suffix+'.json'),JSON.stringify(value,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({...result,vertexCountDifferences:vertexCountDifferences.length,faceCountDifferences:faceCountDifferences.length}));
