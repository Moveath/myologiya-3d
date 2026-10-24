"""Context check and neutral Blender preview for candidate omohyoid sections.
Does not assign belly labels, anatomical boundaries, masks or production assets.
"""
from pathlib import Path
import json
import sys
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import manifest_neck
from diagnose_omohyoid_parts import sha


def nearest(point, mesh):
    points, distances, triangles = trimesh.proximity.closest_point_naive(mesh, np.asarray([point]))
    return dict(distance_mm=float(distances[0]), point_mm=points[0].tolist(), triangle=int(triangles[0]))


def axis_intersections(point, mesh):
    # Intersect original triangle projection with the anterior/posterior Y ray.
    # This tests relative position only, never histological tissue identity.
    triangles = mesh.triangles
    uv = triangles[:, :, [0, 2]]
    p = np.asarray(point)[[0, 2]]
    a, b = uv[:, 1] - uv[:, 0], uv[:, 2] - uv[:, 0]
    d = p - uv[:, 0]
    det = a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    ok = np.abs(det) > 1e-10
    u = np.zeros(len(det)); v = np.zeros(len(det))
    u[ok] = (d[ok, 0]*b[ok, 1] - d[ok, 1]*b[ok, 0])/det[ok]
    v[ok] = (a[ok, 0]*d[ok, 1] - a[ok, 1]*d[ok, 0])/det[ok]
    ok &= (u >= 0) & (v >= 0) & (u+v <= 1)
    values = triangles[ok, 0, 1]*(1-u[ok]-v[ok]) + triangles[ok, 1, 1]*u[ok] + triangles[ok, 2, 1]*v[ok]
    return sorted(set(np.round(values, 6).tolist()))


run = Path(sys.argv[1]).resolve()
profiles = json.loads((run/'source-shape-profiles.json').read_text())
out = dict(status='diagnostic_only_not_admitted', rows=[], context_sources=[])
for row in profiles['rows']:
    side = row['name'].split('_')[-1]
    context = {}
    for part in ('scapula', 'clavicle', 'sternocleidomastoid'):
        fid = manifest_neck.NAME2ID[side+' '+part]
        path = ROOT/'stl_neck'/(fid+'.stl')
        mesh = trimesh.load(path, force='mesh')
        context[part] = mesh
        out['context_sources'].append(dict(name=side+' '+part, path=str(path.relative_to(ROOT)), sha256=sha(path)))
    c = row['candidate_internal_minimum']['center_mm']
    hits = axis_intersections(c, context['sternocleidomastoid'])
    out['rows'].append(dict(name=row['name'], distal_to_scapula=nearest(row['opposite_endpoint_mm'], context['scapula']),
        candidate_to_clavicle=nearest(c, context['clavicle']), candidate_to_scm=nearest(c, context['sternocleidomastoid']),
        candidate_anterior_posterior_coordinate_mm=c[1], scm_Y_ray_intersections_mm=hits,
        candidate_posterior_to_all_scm_ray_hits=bool(len(hits) and c[1] > max(hits)),
        interpretation='Endpoint adjacency and gross deep-to-SCM relation can support orientation. They do not identify the intermediate tendon or its boundaries.'))
with (run/'context-check.json').open('x', encoding='utf8') as f:
    json.dump(out, f, indent=2)
print(json.dumps(out['rows'], indent=2))
