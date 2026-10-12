"""Fit and audit the source-derived Z skull against BodyParts3D.

This fits only one orientation-preserving similarity transform, never a
per-point deformation. Fit statistics are not evidence that small anatomical
formations exist. Anatomical review and proposed use are recorded separately.
"""
from pathlib import Path
import json
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build_head/complete_cranial'
OUT.mkdir(exist_ok=True)
BONES = ['frontal', 'occipital', 'sphenoid', 'ethmoid', 'parietal_left', 'parietal_right']
SOURCE = ROOT / 'research/cache/z-detail'
scene = trimesh.load(ROOT / 'build_head/head_hi.glb', force='scene')
bp = {}
for node in scene.graph.nodes_geometry:
    if not node.startswith('b|'):
        continue
    matrix, name = scene.graph[node]
    mesh = scene.geometry[name].copy()
    mesh.apply_transform(matrix)
    bp[node[2:]] = mesh
z = {}
for bone in BONES:
    raw = json.loads((SOURCE / f'{bone}.json').read_text())
    z[bone] = trimesh.Trimesh(raw['vertices'], raw['faces'], process=False)

# Equal numbers of source samples per bone prevent large flat parietal surfaces
# from dominating the fit. Fixed random seeds make sampling reproducible.
src = [trimesh.sample.sample_surface(z[b], 6000, seed=i)[0] for i,b in enumerate(BONES)]
dst = [trimesh.sample.sample_surface(bp[b], 100000, seed=i)[0] for i,b in enumerate(BONES)]
trees = [cKDTree(p) for p in dst]
ratio = np.median([bp[b].extents.max()/z[b].extents.max() for b in BONES])
translation = np.median([bp[b].bounds.mean(0)-ratio*z[b].bounds.mean(0) for b in BONES], axis=0)
transform = np.eye(4)
transform[:3,:3] *= ratio
transform[:3,3] = translation
iterations = []
for iteration in range(70):
    matched_a, matched_b = [], []
    errors = []
    for points, target, tree in zip(src,dst,trees):
        moving = trimesh.transform_points(points,transform)
        distance, index = tree.query(moving)
        # Exclude the largest 20% residuals: Z contains edited geometry and
        # bilateral symmetrization. These differences are not to be deformed.
        valid = distance <= np.quantile(distance,.8)
        matched_a.append(points[valid]); matched_b.append(target[index[valid]])
        errors.append(float(np.median(distance))*1000)
    transform, _, cost = trimesh.registration.procrustes(
        np.concatenate(matched_a),np.concatenate(matched_b),reflection=False,
        translation=True,scale=True)
    iterations.append({'iteration':iteration,'bone_median_mm':errors,'cost':float(cost)})

rows=[]
combined=trimesh.Scene()
for i,b in enumerate(BONES):
    transformed=z[b].copy(); transformed.apply_transform(transform)
    # Bidirectional surface statistics include all samples, not just inliers.
    zs=trimesh.sample.sample_surface(transformed,40000,seed=i+20)[0]
    bs=trimesh.sample.sample_surface(bp[b],40000,seed=i+30)[0]
    zd=cKDTree(dst[i]).query(zs)[0]*1000
    bd=cKDTree(trimesh.sample.sample_surface(transformed,100000,seed=i+40)[0]).query(bs)[0]*1000
    stats=lambda a:{str(q):round(float(np.quantile(a,q)),4) for q in [0,.25,.5,.75,.9,.95,.99,1]}
    rows.append({'bone':b,'z_to_bp_sampled_distance_mm':stats(zd),'bp_to_z_sampled_distance_mm':stats(bd),
                 'bp_vertices':len(bp[b].vertices),'z_vertices':len(z[b].vertices)})
    combined.add_geometry(transformed,node_name='b|z_'+b,geom_name='b|z_'+b)
    combined.add_geometry(bp[b],node_name='b|bp_'+b,geom_name='b|bp_'+b)
for name in ['frontal_sinus','sphenoidal_sinus']+[f'ethmoid_cells_{g}_{s}' for g in ['anterior','middle','posterior'] for s in ['left','right']]:
    raw=json.loads((SOURCE/f'{name}.json').read_text())
    mesh=trimesh.Trimesh(raw['vertices'],raw['faces'],process=False)
    mesh.apply_transform(transform)
    combined.add_geometry(mesh,node_name='o|'+name,geom_name='o|'+name)
(OUT/'comparison.glb').write_bytes(combined.export(file_type='glb'))
report={'method':'Single robust orientation-preserving similarity; sampled nearest surfaces; trimmed 20% during fit; all samples in reported residuals',
    'transform_z_to_bp':transform.tolist(),'fit_bones':BONES,'iterations':iterations,'distances':rows,
    'limitations':['No local deformation or transfer of landmark claims.','Distances to sampled surfaces are approximate and slightly overestimate nearest-triangle distance.','Morphologic agreement must additionally be inspected at named anatomical landmarks.']}
(OUT/'registration-fit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'transform':transform.tolist(),'distances':rows}))
