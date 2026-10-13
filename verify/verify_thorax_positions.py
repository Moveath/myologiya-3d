"""Check reviewed thoracic anchors against unchanged STL and published fallback.

Surface distances do not independently validate anatomical names or full extent.
Sternal parts are retained and concatenated in the original coordinate frame.
"""
from pathlib import Path
import base64
import hashlib
import io
import json
import sys
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from prepare_thorax_landmark_review import BONES, source_path

rows=json.loads((ROOT/'pins_thorax/ta.json').read_text(encoding='utf8'))
assert len({(r['bone'],r['code']) for r in rows})==len(rows)

def source_meshes():
    result={}
    for bone,fids in BONES.items():
        parts=[]
        for fid in fids:
            mesh=trimesh.load(source_path(fid),process=True)
            mesh.vertices=mesh.vertices[:,[0,2,1]]*np.array([1,1,-1])/1000
            parts.append(mesh)
        result[bone]=trimesh.util.concatenate(parts)
    return result

def meshes_of(scene):
    groups={}
    parents=scene.graph.transforms.parents
    for node in scene.graph.nodes_geometry:
        label=node
        while label and not label.startswith('b|'):
            label=parents.get(label)
        if not label: continue
        transform,geometry=scene.graph[node]
        mesh=scene.geometry[geometry].copy()
        mesh.apply_transform(transform)
        groups.setdefault(label.split('|')[1],[]).append(mesh)
    assert len(groups.get('sternum',[]))==3, 'All three sternal source parts must survive'
    return {bone:trimesh.util.concatenate(parts) for bone,parts in groups.items()}

sources={'source_stl':source_meshes()}
fallback=ROOT/'site/thorax-q-glb.txt'
if fallback.exists():
    scene=trimesh.load(io.BytesIO(base64.b64decode(fallback.read_bytes())),file_type='glb',force='scene')
    sources['published_fallback']=meshes_of(scene)
elif '--source-only' not in sys.argv:
    raise FileNotFoundError('Generate site/thorax-q-glb.txt, or explicitly use --source-only for interim checks')

results=[]
for row in rows:
    assert row['localization']=='surface'
    assert len(row['refs'])>=2 and all(ref.get('locator') for ref in row['refs'])
    assert row['evidence']['fullExtentVerified'] is False
    assert (ROOT/row['evidence']['screenshot']).exists()
    for fid,expected in row['evidence']['sourceSha256'].items():
        assert hashlib.sha256(source_path(fid).read_bytes()).hexdigest()==expected
    assert abs(np.linalg.norm(row['n'])-1)<.003,(row['bone'],row['code'],'normal')
    for name,meshes in sources.items():
        _,distance,_=trimesh.proximity.closest_point_naive(meshes[row['bone']],np.array([row['p']]))
        mm=float(distance[0])*1000
        assert mm<.3,(name,row['bone'],row['code'],mm)
        results.append(dict(model=name,bone=row['bone'],code=row['code'],distance_mm=round(mm,5)))

report=dict(check='Assigned bone surface; tolerance 0.3 mm; SHA-256 of every cited source STL',
            models=list(sources),publishedFallbackChecked='published_fallback' in sources,
            anatomicalExpertAcceptance=False,wholeFeatureGeometryVerified=False,
            primaryMarkers=len(rows),maximumDistanceMm=max(r['distance_mm'] for r in results),records=results)
(ROOT/'verify/thorax-position-geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Thorax positions passed:',len(results),'checks; max',report['maximumDistanceMm'],'mm; models',list(sources))
