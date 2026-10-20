"""Read-only pelvic mesh/anchor measurements; no anatomical point acceptance."""
import base64, hashlib, io, json, sys
from pathlib import Path
import numpy as np
import trimesh
from geometry_distance import SurfaceQuery
ROOT=Path(__file__).resolve().parents[1];out=Path(sys.argv[1]).resolve()
assert out.is_relative_to(ROOT/'research/evidence-runs') and out.is_dir()
pins=json.loads((out/'inventory-before.json').read_text(encoding='utf8'))
sources={'site/leg-q-glb.txt':{'hip_bone','sacrum'},'build_context_bones/leg_extra_hi.glb':{'hip_bone_left'}}
rows=[];anchors=[]
for file,wanted in sources.items():
    raw=(ROOT/file).read_bytes();digest=hashlib.sha256(raw).hexdigest()
    scene=trimesh.load(io.BytesIO(base64.b64decode(raw) if file.endswith('.txt') else raw),file_type='glb',force='scene',process=False)
    groups={b:[] for b in wanted}
    for node in scene.graph.nodes_geometry:
        name=node
        while name and not str(name).startswith('b|'):name=scene.graph.transforms.parents.get(name)
        bone=str(name).split('|')[1] if name else None
        if bone not in wanted:continue
        matrix,key=scene.graph[node];mesh=scene.geometry[key].copy();mesh.apply_transform(matrix);groups[bone].append(mesh)
    for bone,meshes in groups.items():
        assert meshes,bone
        mesh=trimesh.util.concatenate(meshes);query=SurfaceQuery(mesh)
        assert np.isfinite(mesh.vertices).all() and np.isfinite(mesh.face_normals).all()
        side_ok=mesh.bounds[1,0]<0 if bone=='hip_bone' else mesh.bounds[0,0]>0 if bone=='hip_bone_left' else True
        assert side_ok,bone
        rows.append(dict(bone=bone,source=file,sha256=digest,vertices=len(mesh.vertices),triangles=len(mesh.faces),boundsM=mesh.bounds.tolist(),sideCheck=bool(side_ok),anatomyAccepted=False))
        for p in pins:
            if p['b']!=bone or not p.get('p'):continue
            closest,dist,faces=query.closest([p['p']])
            anchors.append(dict(id=p['id'],bone=bone,t=p['t'],p=p['p'],distanceMm=float(dist[0]),triangle=int(faces[0]),anatomicalAcceptance=False))
    assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest
assert len(rows)==3 and len(anchors)==74
result=dict(status='passed',rows=rows,anchors=anchors,boneAnchors=sum(p['t']=='ta' for p in anchors),attachmentAnchors=sum(p['t']=='att' for p in anchors),
    scope='World transforms, side signs, finite vertices/normals, nearest-triangle distance. No repeated self-intersection scan or anatomical acceptance.',newCoordinates=0)
payload=json.dumps(result,ensure_ascii=False,indent=2)
name=sys.argv[2] if len(sys.argv)>2 else 'trimesh-pelvis.json';assert Path(name).name==name
with (out/name).open('x',encoding='utf8') as f:f.write(payload+'\n')
print(json.dumps(dict(status='passed',meshes=len(rows),anchors=len(anchors),maximumDistanceMm=max(p['distanceMm'] for p in anchors))))
