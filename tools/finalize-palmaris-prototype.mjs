// Normalize only Blender's scene-global name suffix, never geometry or atlas IDs.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
const [build,run]=process.argv.slice(2),raw=await fs.readFile(build+'/palmaris_brevis-v2.glb');
const jl=raw.readUInt32LE(12),doc=JSON.parse(raw.subarray(20,20+jl).toString());
if(doc.meshes?.length!==1||doc.nodes?.filter(n=>n.mesh!==undefined).length!==1)throw Error('Unexpected exported mesh');
const owner=doc.nodes.find(n=>n.mesh!==undefined);
if(!/^m\|palmaris_brevis\|(\.\d+)?$/.test(owner.name))throw Error('Unexpected owner');
const oldName=owner.name;owner.name='m|palmaris_brevis|';doc.meshes[0].name=owner.name;
const json=Buffer.from(JSON.stringify(doc)),padding=Buffer.alloc((4-json.length%4)%4,32),chunk=Buffer.concat([json,padding]);
const tail=raw.subarray(20+jl),header=Buffer.alloc(20);raw.copy(header,0,0,12);header.writeUInt32LE(20+chunk.length+tail.length,8);header.writeUInt32LE(chunk.length,12);header.writeUInt32LE(0x4e4f534a,16);
const output=Buffer.concat([header,chunk,tail]);
await fs.writeFile(build+'/palmaris_brevis-trial.glb',output,{flag:'wx'});
await fs.writeFile(run+'/export-finalization.json',JSON.stringify({oldName,newName:owner.name,method:'JSON name normalization only; remaining GLB chunks byte-identical',source:build+'/palmaris_brevis-v2.glb',file:build+'/palmaris_brevis-trial.glb',sha256:crypto.createHash('sha256').update(output).digest('hex'),discardedFirstExport:'palmaris_brevis.glb contains selected foreign-scene Cube and FMA71443; never load',admitted:false},null,2),{flag:'wx'});
console.log('Canonical trial written; binary geometry unchanged');
