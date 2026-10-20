"""Read-only arm/forearm world transforms and nearest surface measurements."""
import base64, hashlib, io, json, sys
from pathlib import Path
import numpy as np
import trimesh
from geometry_distance import SurfaceQuery
ROOT=Path(__file__).resolve().parents[1]; out=Path(sys.argv[1]).resolve()
assert out.is_relative_to(ROOT/'research/evidence-runs') and out.is_dir()
pins=json.loads((out/'atlas-before.json').read_text(encoding='utf8'))['pins']
sources={'site/arm-q-glb.txt':{'humerus','radius','ulna','interosseous_membrane'},'build_context_bones/arm_extra_hi.glb':{'humerus_left'}}
rows=[]; anchors=[]
for file,wanted in sources.items():
    raw=(ROOT/file).read_bytes(); digest=hashlib.sha256(raw).hexdigest()
    scene=trimesh.load(io.BytesIO(base64.b64decode(raw) if file.endswith('.txt') else raw),file_type='glb',force='scene',process=False)
    groups={b:[] for b in wanted}
    for node in scene.graph.nodes_geometry:
        name=node
        while name and not str(name).startswith(('b|','o|')):name=scene.graph.transforms.parents.get(name)
        bone=str(name).split('|')[1] if name else None
        if bone not in wanted:continue
        matrix,key=scene.graph[node]; mesh=scene.geometry[key].copy(); mesh.apply_transform(matrix); groups[bone].append(mesh)
    for bone,meshes in groups.items():
        assert meshes,bone
        mesh=trimesh.util.concatenate(meshes); query=SurfaceQuery(mesh)
        assert np.isfinite(mesh.vertices).all() and np.isfinite(mesh.face_normals).all()
        side_ok=mesh.bounds[0,0]>0 if bone.endswith('_left') else mesh.bounds[1,0]<0
        assert side_ok,bone
        rows.append(dict(bone=bone,source=file,sha256=digest,vertices=len(mesh.vertices),triangles=len(mesh.faces),boundsM=mesh.bounds.tolist(),sideCheck=bool(side_ok),anatomyAccepted=False))
        for p in pins:
            if p['b']!=bone or not p.get('p'):continue
            closest,dist,faces=query.closest([p['p']])
            anchors.append(dict(id=p['id'],bone=bone,p=p['p'],distanceMm=float(dist[0]),triangle=int(faces[0]),anatomicalAcceptance=False))
    assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest
assert len(rows)==5 and len(anchors)==67
blender=json.loads((out/'blender-arm-forearm.json').read_text(encoding='utf8'))
distances={p['id']:p['nearestSurfaceMm'] for p in blender['records']}
discrepancy=max(abs(p['distanceMm']-distances[p['id']]) for p in anchors)
assert discrepancy<.005,discrepancy
result=dict(status='passed',rows=rows,anchors=anchors,blenderDifferenceMm=discrepancy,newCoordinates=0,
    scope='Side signs, world transforms, finite vertices/normals and nearest triangle; no anatomical localisation acceptance or repeated self-intersection scan.')
with (out/'trimesh-arm-forearm.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='passed',bones=4,softStructures=1,anchors=67,maximumDistanceMm=max(p['distanceMm'] for p in anchors),blenderDifferenceMm=discrepancy)))

