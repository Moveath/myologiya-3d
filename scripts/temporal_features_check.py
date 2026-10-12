"""Source-mask check of the corrected OpenEar bone winding and native picks.

The sampled triangles are exported from the final, meshopt-decoded published GLB
by the native Three.js inspection tool. Anatomy is assessed separately.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
from scipy.ndimage import map_coordinates
from temporal_features_scan import indices

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build_head/temporal_features'


def main():
    mask = np.load(ROOT / 'research/cache/complete-temporal/zeta/bone-mask.npy', mmap_mode='r')
    # Decode the file actually served by the atlas; no browser or saved mesh
    # dump is used as a substitute for the current published asset.
    javascript = """
import fs from 'node:fs';
import * as THREE from './tools/node_modules/three/build/three.module.js';
import {GLTFLoader} from './tools/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {MeshoptDecoder} from './tools/node_modules/three/examples/jsm/libs/meshopt_decoder.module.js';
const raw=fs.readFileSync('site/skull-openear.glb');
const g=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength),'');
g.scene.updateMatrixWorld(true);let mesh;
g.scene.traverse(m=>{if(!m.isMesh)return;let p=m;while(p&&!p.name.startsWith('openear|'))p=p.parent;if(p?.name==='openear|temporal_bone')mesh=m;});
if(!mesh)throw Error('Bone mesh absent');
const geometry=mesh.geometry,index=geometry.index,positions=geometry.attributes.position;
function triangle(j){let v=[0,1,2].map(k=>new THREE.Vector3().fromBufferAttribute(positions,index.getX(j*3+k)).applyMatrix4(mesh.matrixWorld));return {faceIndex:j,p:v[0].clone().add(v[1]).add(v[2]).multiplyScalar(1/3).toArray(),n:v[1].clone().sub(v[0]).cross(v[2].clone().sub(v[0])).normalize().toArray(),vertices:v.map(x=>x.toArray())};}
const samples=Array.from({length:1000},(_,i)=>triangle(Math.floor((index.count/3-1)*(i+.5)/1000)));
const markers=JSON.parse(fs.readFileSync('pins_head/temporal-native-features.json','utf8')).markers.map(m=>({...m,triangle:triangle(m.evidence.faceIndex)}));
console.log(JSON.stringify({samples,markers}));
"""
    decoded=json.loads(subprocess.check_output(['node','--input-type=module','-e',javascript],cwd=ROOT,text=True,encoding='utf-8'))
    faces = decoded['samples']
    p = np.array([f['p'] for f in faces]); n = np.array([f['n'] for f in faces])
    inside = map_coordinates(mask,indices(p-.00025*n),order=0)
    outside = map_coordinates(mask,indices(p+.00025*n),order=0)
    outward = int(np.sum((inside==1)&(outside==0)))
    inward = int(np.sum((inside==0)&(outside==1)))
    ambiguous = int(np.sum(inside==outside))
    assert outward >= len(faces)*.95 and inward == 0
    original = json.loads((OUT/'picks.json').read_text())
    corrected = json.loads((OUT/'verified-picks.json').read_text())
    compare = []
    for before, after in zip(original,corrected):
        assert before['id']==after['id']
        shift = float(np.linalg.norm(np.array(before['p'])-after['p']))
        assert shift < 1e-9
        assert np.dot(before['n'],after['n']) < -.999999
        compare.append({'id':after['id'],'position_change_mm':shift*1000,
                        'normal_reversed':True,'newFaceIndex':after['faceIndex']})
    marker_checks=[]
    for m in decoded['markers']:
        tri=m['triangle'];a,b,c=np.array(tri['vertices']);point=np.array(m['p'])
        normal=np.array(tri['n'])
        distance=abs(float(np.dot(point-a,normal)))
        assert distance<1e-8
        assert np.dot(normal,m['n'])>.999999
        # Barycentric point-in-triangle check, independent of stored ray picks.
        v0=b-a;v1=c-a;v2=point-a
        d00=np.dot(v0,v0);d01=np.dot(v0,v1);d11=np.dot(v1,v1)
        d20=np.dot(v2,v0);d21=np.dot(v2,v1);den=d00*d11-d01*d01
        v=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den;u=1-v-w
        assert min(u,v,w)>-1e-5
        marker_checks.append({'id':m['id'],'distance_to_triangle_mm':distance*1000,'within_triangle':True})
    sha=hashlib.sha256((ROOT/'site/skull-openear.glb').read_bytes()).hexdigest()
    report={'geometry_sha256':sha,'sample_count':len(faces),'offset_mm':.25,
            'outward':outward,'inward':inward,'ambiguous_thin_or_aliased':ambiguous,
            'same_published_coordinates':compare,
            'native_marker_checks':marker_checks,
            'anatomical_identity_proven_by_this_test':False,
            'method':'Final GLB triangle normals compared to original bone mask, +/-0.25 mm; unchanged ray coordinates before and after face winding correction.'}
    (OUT/'winding-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'{outward} outward / {inward} inward / {ambiguous} ambiguous; {len(compare)} unchanged ray positions')


if __name__=='__main__':
    main()
