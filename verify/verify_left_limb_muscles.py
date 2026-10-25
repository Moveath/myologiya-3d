"""Per-muscle identity/side/scale/relation diagnostics of the decimated left BP3D limb muscles.

Compares each left part with the reflected accepted right part (x -> -x in the atlas frame, which
is only a diagnostic reference, never published) and compares the set of bones that each muscle
approaches on its own side. Bone proximity is a nearest-vertex distance on the live meshes; it is
evidence of gross topographic consistency, not of an attachment area.
"""
import json
from pathlib import Path
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
CONTACT_MM = 2.5
MARGIN_MM = 0.5  # a one-sided contact counts only when the other side is clearly farther
NEAR_MM = 6.0
read = lambda name: json.loads((run / name).read_text(encoding='utf8'))
targets = read('decimation-targets.json')
decimated = {r['leftFMA']: r for r in read('blender-decimation.json')['rows']}
right_arrays = read('right-limb-arrays.json')
left_bones = read('left-bone-arrays.json')
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)


def vertices(row):
    return np.array(row['vertices'], dtype=float).reshape(-1, 3)


right_bones, shared = {}, {}
for key, row in right_arrays.items():
    if row['name'].startswith('b|'):
        bid = row['name'].split('|')[1]
        (shared if bid == 'sacrum' else right_bones)[bid] = vertices(row)
for bid, row in left_bones.items():
    if bid.startswith('lumbar_'):
        shared[bid] = vertices(row)
left_bone_v = {bid: vertices(row) for bid, row in left_bones.items() if bid.endswith('_left')}
trees = {('right', b): cKDTree(v) for b, v in right_bones.items()}
trees.update({('left', b.removesuffix('_left')): cKDTree(v) for b, v in left_bone_v.items()})
trees.update({('shared', b): cKDTree(v) for b, v in shared.items()})


def contacts(points, side):
    found = {}
    for (s, bone), tree in trees.items():
        if s not in (side, 'shared'):
            continue
        d = tree.query(points, distance_upper_bound=NEAR_MM / 1000)[0]
        if np.isfinite(d).any():
            found[bone] = round(float(d.min() * 1000), 3)
    return found


muscles = {}
for row in targets:
    data = np.load(root / decimated[row['leftFMA']]['output'])
    v, f = data['vertices'] @ R.T / 1000.0, data['faces']
    left = trimesh.Trimesh(v, f, process=False)
    rv = vertices(right_arrays[row['rightKey']])
    mirrored = rv * np.array([-1, 1, 1])
    d_lr = cKDTree(mirrored).query(left.vertices)[0]
    d_rl = cKDTree(left.vertices).query(mirrored)[0]
    weld = left.copy()
    weld.merge_vertices()
    part = dict(part=row['part'], leftFMA=row['leftFMA'], rightFMA=row['rightFMA'], triangles=len(f),
                rightTriangles=row['rightTriangles'], finite=bool(np.isfinite(v).all()),
                degenerateFaces=int((left.area_faces < 1e-12).sum()),
                duplicateFaces=int(len(weld.faces) - len(np.unique(np.sort(weld.faces, axis=1), axis=0))),
                components=len(weld.split(only_watertight=False)), centroidX=float(left.vertices[:, 0].mean()),
                fractionPositiveX=float((left.vertices[:, 0] > 0).mean()),
                centroidOffsetFromMirroredRightMM=float(np.linalg.norm(left.vertices.mean(0) - mirrored.mean(0)) * 1000),
                extentRatio=(left.extents / (mirrored.max(0) - mirrored.min(0))).round(4).tolist(),
                medianSymmetricDistanceMM=float(np.median(np.concatenate([d_lr, d_rl])) * 1000),
                p95SymmetricDistanceMM=float(np.percentile(np.concatenate([d_lr, d_rl]), 95) * 1000),
                leftContacts=contacts(left.vertices, 'left'), rightContacts=contacts(rv, 'right'))
    muscles.setdefault((row['region'], row['right'], row['left']), []).append(part)

rows = []
for (region, right, left), parts in muscles.items():
    near = lambda key: {b: min(p[key][b] for p in parts if b in p[key]) for p in parts for b in p[key]}
    ln, rn = near('leftContacts'), near('rightContacts')
    lc = {b for b, d in ln.items() if d <= CONTACT_MM}
    rc = {b for b, d in rn.items() if d <= CONTACT_MM}
    # Threshold noise: contact on one side and within MARGIN on the other is not a topographic difference.
    clear = lambda mine, other: sorted(b for b in mine if other.get(b, NEAR_MM + 1) > mine.get(b) + MARGIN_MM and other.get(b, NEAR_MM + 1) > CONTACT_MM)
    technical = all(p['finite'] and not p['degenerateFaces'] for p in parts)
    side = all(p['centroidX'] > 0 for p in parts)
    shape = all(p['medianSymmetricDistanceMM'] <= 3.0 and all(0.8 <= e <= 1.25 for e in p['extentRatio']) for p in parts)
    missing, extra = clear({b: rn[b] for b in rc}, ln), clear({b: ln[b] for b in lc}, rn)
    relation = not missing and not extra
    rows.append(dict(region=region, right=right, left=left, parts=parts, leftBones=sorted(lc), rightBones=sorted(rc),
                     thresholdNoise=sorted((lc ^ rc) - set(missing) - set(extra)),
                     missingOnLeft=missing, extraOnLeft=extra, technical=technical, side=side,
                     shape=shape, relation=relation, passed=technical and side and shape and relation))
result = dict(contactThresholdMM=CONTACT_MM, rule='technical + left centroid + shape vs reflected right (median <=3 mm, extents 0.8-1.25) + no clear one-sided bone contact (<=2.5 mm on one side and >0.5 mm farther and >2.5 mm on the other)',
              marginMM=MARGIN_MM,
              limitation='Nearest-vertex proximity and reflected-right similarity show gross identity/topography only; attachment areas, fibre directions and part boundaries are not accepted.',
              muscles=rows, passed=sum(r['passed'] for r in rows), total=len(rows))
with (run / 'left-muscle-review-v2.json').open('x', encoding='utf8') as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print(json.dumps(dict(passed=result['passed'], total=result['total'],
                      failed=[(r['left'], {k: r[k] for k in ('technical', 'side', 'shape', 'relation')}, r['missingOnLeft'], r['extraOnLeft'])
                              for r in rows if not r['passed']]), ensure_ascii=False))
