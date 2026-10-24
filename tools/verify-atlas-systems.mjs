// Lightweight registry/relationship regressions; no GLB re-import or anatomy audit.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {ANATOMICAL_SYSTEMS,systemOf,systemDefaults,structureRelations,admittedModel} from '../site/atlas-systems.js';
const run=process.argv[2];if(!run)throw new Error('Pass an allocated evidence run directory');
const checks=[];
function test(name,body){body();checks.push({name,passed:true});}
test('Five independent system defaults',()=>assert.deepEqual(systemDefaults(),{bones:true,muscles:true,heart:false,arteries:false,veins:false}));
test('Saved booleans only; unknown systems excluded',()=>assert.deepEqual(systemDefaults({bones:false,veins:true,heart:'true',nerves:true}),{bones:false,muscles:true,heart:false,arteries:false,veins:true}));
test('All five can be enabled together',()=>assert(Object.values(systemDefaults(Object.fromEntries(Object.keys(ANATOMICAL_SYSTEMS).map(k=>[k,true])))).every(Boolean)));
test('Legacy bones keep ownership',()=>assert.equal(systemOf({kind:'b'}),'bones'));
test('Muscles and muscle parts keep ownership',()=>{assert.equal(systemOf({kind:'m'}),'muscles');assert.equal(systemOf({kind:'o'}),'muscles');});
test('New structures use explicit system',()=>assert.equal(systemOf({kind:'s',data:{system:'veins'}}),'veins'));
const catalogue={heart:{},valve:{partOf:'heart'},artery:{origin:'heart'},vein:{drainsTo:'heart'},unrelated:{},missing:{origin:'absent'}};
test('Missing card has no fabricated relations',()=>assert.deepEqual(structureRelations('absent',catalogue),[]));
test('Missing relation endpoint is omitted',()=>assert.deepEqual(structureRelations('missing',catalogue),[]));
test('Part, branch and tributary labels remain distinct',()=>assert.deepEqual(structureRelations('heart',catalogue),[{id:'valve',label:'Анатомическая часть'},{id:'artery',label:'Ветвь / продолжение'},{id:'vein',label:'Приток'}]));
test('Venous outflow is directed',()=>assert.deepEqual(structureRelations('vein',catalogue),[{id:'heart',label:'Отток в'}]));
test('Parent and origin are not venous outflow',()=>{assert.equal(structureRelations('valve',catalogue)[0].label,'Часть структуры');assert.equal(structureRelations('artery',catalogue)[0].label,'Начинается / продолжается от');});
test('No admission for absent or noModel cards',()=>{assert.equal(admittedModel(null),false);assert.equal(admittedModel({noModel:true,modelStatus:'educational_limited',modelFile:'example.glb'}),false);});
test('Candidate and missing model path are not admitted',()=>{assert.equal(admittedModel({noModel:false,modelStatus:'candidate',modelFile:'example.glb'}),false);assert.equal(admittedModel({noModel:false,modelStatus:'educational_limited'}),false);});
test('Explicit admission plus actual path permits loading',()=>assert.equal(admittedModel({noModel:false,modelStatus:'educational_limited',modelFile:'example.glb'}),true));
await fs.writeFile(path.join(run,'systems-unit.json'),JSON.stringify({status:'passed',scope:'Registry semantics, not physical GLB load or scientific acceptance',checks},null,2),{flag:'wx'});
console.log(JSON.stringify({status:'passed',checks:checks.length}));
