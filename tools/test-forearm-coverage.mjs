import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {upperLimbCoverage} from '../site/atlas-catalogue.js';
const bone=id=>({id,side:'left',kind:'b',meshes:[{}],data:{sub:['radius_left','ulna_left'].includes(id)?'forearm':'hand'}});
const checks=[];
for(const [ids,required,forbidden] of [
 [[],['Левая кисть и предплечье'],[]],
 [['radius_left'],['Левая кисть','Левая локтевая'],['Левое предплечье']],
 [['ulna_left'],['Левая кисть','Левая лучевая'],['Левое предплечье']],
 [['radius_left','ulna_left'],['Левая кисть'],['предплечье','лучевая','локтевая']],
 [['scaphoid_left'],['Левое предплечье','частично: 1 из 27'],['Левая кисть пока без']],
 [['radius_left','ulna_left','scaphoid_left'],['частично: 1 из 27'],['Левая кисть пока без','предплечье','лучевая','локтевая']],
 [['radius_left','ulna_left','scaphoid_left','lunate_left','triquetrum_left','pisiform_left'],['частично: 4 из 27'],['Левая кисть пока без','предплечье']]
]){
 const text=upperLimbCoverage('left','all',ids.map(bone));
 required.forEach(s=>assert.ok(text.includes(s),s));
 forbidden.forEach(s=>assert.ok(!text.includes(s),s));
 assert.ok(!upperLimbCoverage('right','forearm',ids.map(bone)).includes('Левая'));
 checks.push({ids,status:'passed'});
}
await fs.writeFile(path.join(process.argv[2],'coverage-unit.json'),JSON.stringify({status:'passed',checks},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:'passed',cases:checks.length}));
