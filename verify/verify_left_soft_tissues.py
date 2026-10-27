"""Identity/side/scale/relation diagnostics of the decimated left BP3D soft tissues (CAT-SOFT-TISSUE-BILATERAL).

Same rule as verify_left_limb_muscles.py: each left structure is compared with the reflected
accepted right node of the published atlas (x -> -x, diagnostic only) and the set of bones it
approaches on its own side is compared with the right structure's set. Geometry comes from the
atlas geometry cache (tools/export-atlas-geometry.mjs), whose source hashes are checked first.
Usage: python verify/verify_left_soft_tissues.py RUN
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
CONTACT_MM, MARGIN_MM, NEAR_MM = 2.5, 0.5, 6.0
SHARED = ('sacrum', 'lumbar_')
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)
read = lambda name: json.loads((run / name).read_text(encoding='utf8'))
targets = read('decimation-targets.json')
decimated = {r['leftFMA']: r for r in read('blender-decimation.json')['rows']}


def section(sec):
    cache = root / 'research/cache/atlas-geometry'
    index = json.loads((cache / f'{sec}.json').read_text(encoding='utf8'))
    for source in index['sources']:
        if hashlib.sha256((root / source['file']).read_bytes()).hexdigest() != source['sha256']:
            raise SystemExit(f'Stale geometry cache for {sec}: run node tools/export-atlas-geometry.mjs {sec}')
    raw = (cache / f'{sec}.bin').read_bytes()
    V = np.frombuffer(raw[:index['vertexBytes']], dtype=np.float32).reshape(-1, 3).astype(np.float64)
    F = np.frombuffer(raw[index['vertexBytes']:], dtype=np.uint32).reshape(-1, 3).astype(np.int64)
    nodes = {}
    for node in index['nodes']:
        v = V[node['vertexOffset']:node['vertexOffset'] + node['vertexCount']]
        f = F[node['faceOffset']:node['faceOffset'] + node['faceCount']]
        nodes.setdefault(node['name'], []).append((v, f))
    return nodes


def components(mesh):
    # Face-adjacency components (scipy); trimesh split() would try to fill holes of open sheets.
    return len(trimesh.graph.connected_components(mesh.face_adjacency, nodes=np.arange(len(mesh.faces)), engine='scipy'))


def merged(chunks):
    vs, fs, off = [], [], 0
    for v, f in chunks:
        vs.append(v); fs.append(f + off); off += len(v)
    return np.vstack(vs), np.vstack(fs)


rows = []
for sec in ('arm', 'leg'):
    nodes = section(sec)
    bones = {}
    for name, chunks in nodes.items():
        kind, key = name.split('|')[:2]
        if kind != 'b':
            continue
        side = 'shared' if key.startswith(SHARED) else 'left' if key.endswith('_left') else 'right'
        bones[(side, key.removesuffix('_left'))] = cKDTree(merged(chunks)[0])

    def contacts(points, side):
        found = {}
        for (s, bone), tree in bones.items():
            if s in (side, 'shared'):
                d = tree.query(points, distance_upper_bound=NEAR_MM / 1000)[0]
                if np.isfinite(d).any():
                    found[bone] = round(float(d.min() * 1000), 3)
        return found

    for row in (t for t in targets if t['region'] == sec):
        data = np.load(root / decimated[row['leftFMA']]['output'])
        left = trimesh.Trimesh(data['vertices'] @ R.T / 1000.0, data['faces'], process=False)
        rv, rf = merged(nodes['o|' + row['right']])
        right = trimesh.Trimesh(rv, rf, process=False)
        mirrored = rv * np.array([-1, 1, 1])
        d_lr, d_rl = cKDTree(mirrored).query(left.vertices)[0], cKDTree(left.vertices).query(mirrored)[0]
        weld = left.copy()
        weld.merge_vertices()
        rweld = right.copy()
        rweld.merge_vertices()
        ln, rn = contacts(left.vertices, 'left'), contacts(rv, 'right')
        lc, rc = {b for b, d in ln.items() if d <= CONTACT_MM}, {b for b, d in rn.items() if d <= CONTACT_MM}
        clear = lambda mine, other: sorted(b for b in mine if other.get(b, NEAR_MM + 1) > mine[b] + MARGIN_MM and other.get(b, NEAR_MM + 1) > CONTACT_MM)
        missing, extra = clear({b: rn[b] for b in rc}, ln), clear({b: ln[b] for b in lc}, rn)
        r = dict(region=sec, right=row['right'], left=row['left'], leftFMA=row['leftFMA'], rightFMA=row['rightFMA'],
                 triangles=len(left.faces), rightTriangles=len(right.faces), finite=bool(np.isfinite(left.vertices).all()),
                 degenerateFaces=int((left.area_faces < 1e-12).sum()),
                 duplicateFaces=int(len(weld.faces) - len(np.unique(np.sort(weld.faces, axis=1), axis=0))),
                 components=components(weld), rightComponents=components(rweld),
                 centroidX=float(left.vertices[:, 0].mean()), fractionPositiveX=float((left.vertices[:, 0] > 0).mean()),
                 centroidOffsetFromMirroredRightMM=float(np.linalg.norm(left.vertices.mean(0) - mirrored.mean(0)) * 1000),
                 extentRatio=(left.extents / (mirrored.max(0) - mirrored.min(0))).round(4).tolist(),
                 areaRatio=round(float(left.area / right.area), 4),
                 medianSymmetricDistanceMM=float(np.median(np.concatenate([d_lr, d_rl])) * 1000),
                 p95SymmetricDistanceMM=float(np.percentile(np.concatenate([d_lr, d_rl]), 95) * 1000),
                 leftContacts=ln, rightContacts=rn, leftBones=sorted(lc), rightBones=sorted(rc),
                 thresholdNoise=sorted((lc ^ rc) - set(missing) - set(extra)), missingOnLeft=missing, extraOnLeft=extra)
        r['technical'] = r['finite'] and not r['degenerateFaces']
        r['side'] = r['centroidX'] > 0 and r['fractionPositiveX'] > 0.99
        r['shape'] = r['medianSymmetricDistanceMM'] <= 3.0 and all(0.8 <= e <= 1.25 for e in r['extentRatio'])
        r['relation'] = not missing and not extra
        r['passed'] = r['technical'] and r['side'] and r['shape'] and r['relation']
        rows.append(r)
result = dict(contactThresholdMM=CONTACT_MM, marginMM=MARGIN_MM,
              rule='technical + left side (centroid x>0, >99% vertices x>0) + shape vs reflected right (median <=3 mm, extents 0.8-1.25) '
                   '+ no clear one-sided bone contact (<=2.5 mm on one side and >0.5 mm farther and >2.5 mm on the other)',
              limitation='Proximity and reflected-right similarity show gross identity/topography only; ligament/tendon boundaries, '
                         'attachment areas and fibre directions are not accepted.',
              structures=rows, passed=sum(r['passed'] for r in rows), total=len(rows))
with (run / 'left-soft-tissue-review.json').open('x', encoding='utf8') as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print(json.dumps(dict(passed=result['passed'], total=result['total'], rows=[
    (r['left'], r['passed'], round(r['medianSymmetricDistanceMM'], 2), r['extentRatio'], r['areaRatio'], r['leftBones'], r['rightBones'],
     r['missingOnLeft'], r['extraOnLeft'], r['components'], r['rightComponents']) for r in rows]), ensure_ascii=False, indent=0))
