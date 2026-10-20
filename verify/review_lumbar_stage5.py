"""Lightweight lumbar source/export comparison. Not an anatomical acceptance."""
import hashlib, json, sys
from pathlib import Path
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]).resolve()
assert out.is_relative_to(ROOT/'research/evidence-runs') and out.is_dir()
provenance=json.loads((ROOT/'research/context-bone-provenance.json').read_text(encoding='utf8'))['bones']
scene=trimesh.load(ROOT/'build_context_bones/leg_extra_hi.glb',force='scene',process=False)
rows=[]
for i in range(1,6):
    bone=f'lumbar_{i}';meta=provenance[bone];source=ROOT/meta['sourceFile']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==meta['sourceSha256']
    original=trimesh.load(source,process=False)
    world=original.vertices[:,[0,2,1]]/1000;world[:,2]*=-1
    matrix,key=scene.graph['b|'+bone];mesh=scene.geometry[key].copy();mesh.apply_transform(matrix)
    bounds=np.array([world.min(axis=0),world.max(axis=0)])
    error=float(abs(mesh.bounds-bounds).max()*1000)
    assert len(mesh.faces)==meta['sourceTriangles']==len(original.faces)
    assert error<.01,(bone,error)
    assert np.isfinite(mesh.vertices).all() and np.isfinite(mesh.face_normals).all()
    rows.append(dict(bone=bone,source=meta['sourceFile'],sourceSha256=meta['sourceSha256'],
        triangles=len(mesh.faces),boundsMetres=mesh.bounds.tolist(),boundsErrorMm=error,
        transformDeterminant=float(np.linalg.det(matrix[:3,:3])),coordinateCount=0,
        anatomyAccepted=False,acceptedSurfaceMasks=0))
assert all(rows[i]['boundsMetres'][1][1]>rows[i+1]['boundsMetres'][1][1] for i in range(4))
result=dict(status='passed',rows=rows,scope='Source hashes, triangle counts, transformed bounds, level ordering, finite normals. No new full defect scan of unchanged meshes.',
    newCoordinates=0,newMasks=0)
with (out/'trimesh-lumbar.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='passed',bones=5,triangles=sum(r['triangles'] for r in rows),maximumBoundsErrorMm=max(r['boundsErrorMm'] for r in rows))))
