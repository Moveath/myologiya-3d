"""Bounded validation of the new prototype, not an anatomical admission."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import trimesh
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1];build=ROOT/sys.argv[1];run=ROOT/sys.argv[2]
spec=json.loads((build/'recipe.json').read_text(encoding='utf8'))
scene=trimesh.load(build/'palmaris_brevis-trial.glb',force='scene',process=False)
assert len(scene.geometry)==1
mesh=scene.to_geometry(); source=trimesh.Trimesh(np.array(spec['positions']).reshape(-1,3),np.array(spec['indices']).reshape(-1,3),process=False)
dist,match=cKDTree(source.triangles_center).query(mesh.triangles_center)
corner_error=max(float(cKDTree(source.triangles[i]).query(t)[0].max()) for t,i in zip(mesh.triangles,match))
checks={
 'single_mesh':len(scene.geometry)==1,'triangles_preserved':len(mesh.faces)==3296,
 'all_triangle_corners_preserved':len(np.unique(match))==len(source.faces) and corner_error<1e-7,
 'finite_vertices':bool(np.isfinite(mesh.vertices).all()),'right_body_side':bool((mesh.vertices[:,0]<0).all()),
 'no_zero_area':bool((mesh.area_faces>1e-14).all()),'watertight':bool(mesh.is_watertight),
 'consistent_winding':bool(mesh.is_winding_consistent),'positive_volume':bool(mesh.volume>0),
 'single_component':mesh.body_count==1,'no_duplicate_triangles':len(np.unique(np.sort(mesh.faces,axis=1),axis=0))==len(mesh.faces),
 'explicit_test_status':spec['status']=='technical_prototype_not_admitted',
 'originals_unchanged':all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in json.loads((run/'baseline.json').read_text())['hashes'].items())}
result=dict(status='passed' if all(checks.values()) else 'failed',checks=checks,vertices=len(mesh.vertices),triangles=len(mesh.faces),bounds_m=mesh.bounds.tolist(),volume_mm3=float(mesh.volume*1e9),surface_mm2=float(mesh.area*1e6),max_corner_error_m=corner_error,tolerance_m=1e-7,anatomical_admission=False)
with (run/'trimesh-prototype-v2.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(result));assert all(checks.values())
