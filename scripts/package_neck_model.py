"""Package a previously built neck GLB and record its actual source provenance."""
from pathlib import Path
import base64
import hashlib
import json
import trimesh
import manifest_neck as manifest

ROOT = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
meta = json.loads((ROOT/'build_neck/meta.json').read_text(encoding='utf-8'))
source = []
for fid in sorted(set(manifest.all_ids())):
    path = ROOT/'stl_neck'/f'{fid}.stl'
    source.append({'id':fid, 'sha256':sha(path), 'bytes':path.stat().st_size,
                   'url':f'https://raw.githubusercontent.com/Kevin-Mattheus-Moerman/BodyParts3D/main/assets/BodyParts3D_data/stl/{fid}.stl'})
bones = {}
for bone, fids in manifest.BONES.items():
    original = sum(len(trimesh.load(ROOT/'stl_neck'/f'{fid}.stl', process=True).faces) for fid in fids)
    built = meta['parts'][f'b|{bone}']['faces']
    if original != built:
        raise ValueError((bone, original, built))
    bones[bone] = {'source_ids':fids, 'source_triangles':original, 'built_triangles':built, 'decimation':False}
from package_geometry_guard import validate_candidates
validate_candidates(ROOT, 'build_neck/neck_hi.glb', ['build_neck/neck.glb','build_neck/neck_q.glb'],
                    {bone:row['source_triangles'] for bone,row in bones.items()})
report = {
    'source':'BodyParts3D 3.0, The Database Center for Life Science (DBCLS)',
    'license':'CC BY-SA 2.1 Japan', 'license_url':'https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en',
    'transformation':'BP3D millimetres [x,y,z] to metres [x,z,-y]/1000; no registration or mirroring',
    'processing':'Bone triangles retained before meshopt compression/quantization. Muscles and context simplified by build_glb.py. No synthetic structures.',
    'bones':bones, 'muscles':manifest.MUSCLES, 'context':manifest.CONTEXT,
    'source_files':source, 'stats':meta['stats'],
    'assets':{dest:hashlib.sha256(base64.b64encode((ROOT/'build_neck'/name).read_bytes())).hexdigest() for name,dest in [('neck.glb','neck-glb.txt'),('neck_q.glb','neck-q-glb.txt')]},
    'geometry_complete_claim':False,
}
for name, destination in [('neck.glb','neck-glb.txt'), ('neck_q.glb','neck-q-glb.txt')]:
    (ROOT/'site'/destination).write_text(base64.b64encode((ROOT/'build_neck'/name).read_bytes()).decode('ascii'), encoding='ascii')
(ROOT/'research/neck-model-provenance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Neck:', len(bones), 'unchanged source bone meshes;', len(manifest.MUSCLES), 'muscle instances;',meta['stats']['faces'],'triangles')
