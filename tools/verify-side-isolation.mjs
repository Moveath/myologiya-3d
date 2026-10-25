import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import {structureSide, sideAllows, muscleBoneIds, selectionVisibility} from '../site/atlas-visibility.js';
import {MODEL_SIDES} from '../site/atlas-model-sides.js';
import {indexLandmarks} from '../site/atlas-landmarks.js';
import {createEvidenceRun} from './evidence-run.mjs';

const tests=[];
function test(name, fn) { fn(); tests.push(name); }
const box={window:{}}; vm.createContext(box);
for(const n of ['data','data-leg','data-head','data-neck','data-thorax','data-context-bones','pins','pins-leg','pins-head','pins-head-extra','pins-neck','pins-thorax','pins-context-bones','pins-shared'])
  vm.runInContext(await fs.readFile('site/'+n+'.js','utf8'),box);
const A=JSON.parse(JSON.stringify(box.window.ATLAS)),idx=indexLandmarks(A.pins);
const bone=id=>!!A.bones[id]&&!A.bones[id].g.startsWith('b_soft');
const p={side:'both',hidden:new Set(),isolate:null,boundary:[],muscle:null,related:[]};
const s=(id,kind='b',side='right')=>({id,kind,side});
test('Legacy right IDs and left noModel cards retain correct side',()=>{
  for(const id of ['humerus','radius','ulna','biceps_brachii','metacarpal_1'])assert.equal(structureSide('arm',id,A.bones[id]),'right');
  for(const id of ['humerus_left','radius_left','scaphoid_left'])assert.equal(structureSide('arm',id,A.bones[id]),'left');
  assert.equal(structureSide('head','mandible',A.bones.mandible),'unseparated');
});
test('Both sides, midline and unseparated sources remain available',()=>{
  for(const side of ['left','right','unseparated'])assert.equal(sideAllows(side,'both'),true);
  assert.equal(sideAllows('left','right'),false);assert.equal(sideAllows('unseparated','left'),true);
});
test('Context source IDs are independently sided',()=>{
  assert.equal(MODEL_SIDES.arm['context:FMA7857'],'right');
  assert.equal(MODEL_SIDES.arm['context:FMA12519'],'unseparated');
  assert.equal(MODEL_SIDES.leg['context:FMA16587'],'left');
});
test('Isolated muscle excludes unrelated bones, soft tissues and background',()=>{
  const q={...p,isolate:'biceps_brachii'};
  assert.equal(selectionVisibility(s('biceps_brachii','m'),q),2);
  for(const x of [s('radius'),s('scapula_left','b','left'),s('context:FMA7857','c'),s('interosseous_membrane','o')])assert.equal(selectionVisibility(x,q),0);
});
test('Muscle bone allowlist follows recorded attachments, including part filter',()=>{
  assert.deepEqual(muscleBoneIds(idx.byMuscle.biceps_brachii,null,bone).sort(),['radius','scapula']);
  const rows=[{pin:{b:'scapula'},part:'long'},{pin:{b:'humerus'},part:'short'},{pin:{b:'radius'},part:null},{pin:{b:'flexor_retinaculum'},part:null}];
  assert.deepEqual(muscleBoneIds(rows,'long',bone),['scapula']);
  assert.deepEqual(muscleBoneIds([],null,bone),[]);
});
test('Only explicitly enabled muscle context survives isolation',()=>{
  const q={...p,isolate:'biceps_brachii',muscle:'biceps_brachii',related:['scapula','radius']};
  assert.equal(selectionVisibility(s('radius'),q),2);assert.equal(selectionVisibility(s('humerus'),q),0);
  assert.equal(selectionVisibility(s('radius'),{...q,hidden:new Set(['radius'])}),0);
});
test('Shared boundary participants survive bone isolation, not merely adjacent bones',()=>{
  const q={...p,isolate:'metacarpal_4',boundary:['metacarpal_4','hamate']};
  assert.equal(selectionVisibility(s('hamate'),q),2);assert.equal(selectionVisibility(s('capitate'),q),0);
  assert.equal(selectionVisibility(s('hip_bone_left','b','left'),{...q,side:'right',boundary:['hip_bone_left']}),0);
});
test('Normal layers are delegated; unilateral filter applies before all overrides',()=>{
  assert.equal(selectionVisibility(s('humerus'),p),null);
  assert.equal(selectionVisibility(s('humerus_left','b','left'),{...p,side:'right'}),0);
  assert.equal(selectionVisibility(s('humerus'),{...p,muscle:'biceps_brachii',related:['radius']}),0);
});
test('No coordinates or geometry created for missing left bones',()=>{
  // Left forearm/carpals were admitted as labelled educational models in stage 6; MCP I sesamoids carry the
  // labelled NLM Visible Human CT reconstruction since LOG-20261025-04. No landmark coordinates on sesamoids.
  for(const id of ['sesamoid_mcp1_radial_left','sesamoid_mcp1_ulnar_left'])assert.ok(!A.bones[id].noModel&&A.bones[id].modelAttribution?.startsWith('Courtesy of the U.S. National Library of Medicine'));
  for(const id of ['radius_left','ulna_left','scaphoid_left'])assert.ok(!A.bones[id].noModel&&A.bones[id].modelFile&&A.bones[id].modelNotice);
  assert.equal(A.pins.filter(q=>q.b.startsWith('sesamoid_mcp1')&&q.p).length,0);
});
if(process.argv[2]){
 const before=JSON.parse(await fs.readFile(process.argv[2]+'/hashes-before.json','utf8'));
 for(const [name,hash] of Object.entries(before))assert.equal(createHash('sha256').update(await fs.readFile('site/'+name)).digest('hex'),hash,name+' immutable');
 tests.push('All original published models, catalogue and pin files have unchanged SHA-256');
}
const result={status:'passed',tests,modelIdentities:Object.values(MODEL_SIDES).reduce((n,m)=>n+Object.keys(m).length,0),pins:A.pins.length};
const run=await createEvidenceRun(process.cwd(),'side-isolation-unit');await run.write('result.json',result);
const coverage=Object.entries(A.muscles).flatMap(([id,m])=>[null,...Object.keys(m.parts||{})].map(part=>({
  muscleId:id,part,ru:part?m.parts[part].ru:m.ru,noModel:!!(part?m.parts[part].noModel:m.noModel),
  boneIds:muscleBoneIds(idx.byMuscle[id]||[],part,bone),
  sourcePinIds:[...new Set((idx.byMuscle[id]||[]).filter(e=>!part||e.part===part).map(e=>e.pin.id))],
})));
await run.write('muscle-bone-context.json',{scope:'Existing explicit pin.m -> pin.b only. Zero links do not by themselves prove an anatomical omission. Text descriptions are not parsed; no completeness or coordinate acceptance.',rows:coverage});
console.log(JSON.stringify({status:result.status,tests:tests.length,run:run.dir}));
