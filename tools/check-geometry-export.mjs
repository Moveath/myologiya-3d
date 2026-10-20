import {inspectGeometry,validateExport} from './geometry-export-check.mjs';
const [reference,output]=process.argv.slice(2);
if(!reference||!output)throw Error('Usage: check-geometry-export.mjs REFERENCE.glb OUTPUT.glb');
const a=await inspectGeometry(reference),b=await inspectGeometry(output),errors=validateExport(a,b);
const referenceBones={};
for(const m of a.meshes)if(m.owner.startsWith('b|')){
  const key=m.owner.split('|')[1];referenceBones[key]=(referenceBones[key]??0)+m.faces;
}
console.log(JSON.stringify({reference:a.file,output:b.file,meshes:b.meshes.length,referenceBones,errors}));
if(errors.length)process.exitCode=1;
