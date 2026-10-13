"""Package a previously built thorax GLB and record its actual source provenance."""
from pathlib import Path
import base64
import hashlib
import json
import trimesh
import manifest_thorax as manifest

ROOT = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
for name, destination in [('thorax.glb','thorax-glb.txt'), ('thorax_q.glb','thorax-q-glb.txt')]:
    (ROOT/'site'/destination).write_text(base64.b64encode((ROOT/'build_thorax'/name).read_bytes()).decode('ascii'), encoding='ascii')
meta = json.loads((ROOT/'build_thorax/meta.json').read_text(encoding='utf-8'))
source = []
for fid in sorted(set(manifest.all_ids())):
    path = ROOT/'stl_thorax'/f'{fid}.stl'
    source.append({'id':fid, 'sha256':sha(path), 'bytes':path.stat().st_size,
                   'url':f'https://raw.githubusercontent.com/Kevin-Mattheus-Moerman/BodyParts3D/main/assets/BodyParts3D_data/stl/{fid}.stl'})
bones = {}
for bone, fids in manifest.BONES.items():
    original = sum(len(trimesh.load(ROOT/'stl_thorax'/f'{fid}.stl', process=True).faces) for fid in fids)
    built = sum(row['faces'] for key,row in meta['parts'].items() if key == f'b|{bone}' or key.startswith(f'b|{bone}|'))
    assert original == built, (bone, original, built)
    bones[bone] = {'source_ids':fids, 'source_triangles':original, 'built_triangles':built, 'decimation':False}
report = {
    'source':'BodyParts3D 3.0, The Database Center for Life Science (DBCLS)',
    'license':'CC BY-SA 2.1 Japan', 'license_url':'https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en',
    'transformation':'BP3D millimetres [x,y,z] to metres [x,z,-y]/1000; no registration or mirroring',
    'processing':'Bone triangles retained before meshopt compression/quantization. Muscles and context simplified by build_glb.py. No synthetic structures.',
    'bones':bones, 'muscles':manifest.MUSCLES, 'context':manifest.CONTEXT, 'other':manifest.OTHER,
    'source_files':source, 'stats':meta['stats'],
    'assets':{name:sha(ROOT/'site'/name) for name in ['thorax-glb.txt','thorax-q-glb.txt']},
    'geometry_complete_claim':False,
}
(ROOT/'research/thorax-model-provenance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(ROOT/'site/LICENSE-THORAX.txt').write_text('''Thoracic model assets: thorax-glb.txt and thorax-q-glb.txt

BodyParts3D 3.0, copyright The Database Center for Life Science (DBCLS).
Source: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/
Mirror: https://github.com/Kevin-Mattheus-Moerman/BodyParts3D
Publication: https://pubmed.ncbi.nlm.nih.gov/18835852/

License of the original and these derivative model assets:
Creative Commons Attribution-ShareAlike 2.1 Japan (CC BY-SA 2.1 JP)
https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en

Changes: original coordinates converted from millimetres to metres and to the
atlas axes; muscles, costal cartilage and context simplified; source objects
named and grouped; GLB export, meshopt compression and quantization. All original
bone triangles retained before quantization. Sternal components keep their
original alignment. No mirroring, synthetic anatomy or scan-derived accuracy
beyond the original BodyParts3D surfaces is claimed.

Full per-file source IDs, SHA-256 and transformation audit are in the project
research/thorax-model-provenance.json and scripts/manifest_thorax.py.
Linked third-party anatomical publications retain their own rights; their
figures and full texts are not distributed as part of these model assets.
''',encoding='utf-8')
print('Thorax:', len(bones), 'unchanged source bone meshes;', len(manifest.MUSCLES), 'muscle instances;',meta['stats']['faces'],'triangles')
