"""Read-only geometry audit of every loaded bone and muscle (BONES-MUSCLES-AUDIT).

Input: research/cache/atlas-geometry/<section>.{bin,json} from tools/export-atlas-geometry.mjs
(world space exactly as loadSection() assembles it) and RUN/catalogue-{cards,pins}.json from
tools/audit-bones-muscles-catalogue.mjs. Output: RUN/geometry-audit.json.

Measured: integrity (finite values, index range, zero-area and duplicate faces, normals), scale,
side by position, contralateral pairs (mirror X, centroid offset, area/triangle ratios and
rigid-ICP shape distance), landmark distance to the owner surface versus the nearest other bone,
normal agreement and attachment-to-muscle distance. These are triage signals, not anatomy.
Usage: .venv/Scripts/python.exe verify/audit_bones_muscles_geometry.py RUN
"""
from pathlib import Path
import json
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from geometry_distance import SurfaceQuery

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/atlas-geometry'
run = Path(sys.argv[1]).resolve()
SECTIONS = ['head', 'neck', 'trunk', 'arm', 'leg']
CONTEXT_OWNER = {'neck': {'FMA9165': 'thoracic_1'}, 'trunk': {'FMA12525': 'cervical_7'}}  # as register() in index.html
cards = {(c['kind'], c['id']): c for c in json.loads((run / 'catalogue-cards.json').read_text(encoding='utf8'))}
pins = json.loads((run / 'catalogue-pins.json').read_text(encoding='utf8'))
rng = np.random.default_rng(20261025)


def load(sec):
    idx = json.loads((CACHE / f'{sec}.json').read_text(encoding='utf8'))
    raw = (CACHE / f'{sec}.bin').read_bytes()
    V = np.frombuffer(raw[:idx['vertexBytes']], dtype=np.float32).reshape(-1, 3).astype(np.float64)
    F = np.frombuffer(raw[idx['vertexBytes']:], dtype=np.uint32).reshape(-1, 3)
    out = {}
    for n in idx['nodes']:
        kind, key, *rest = n['name'].split('|')
        if kind == 'c' and key in CONTEXT_OWNER.get(sec, {}):
            kind, key = 'b', CONTEXT_OWNER[sec][key]
        if kind not in ('b', 'm', 'o'):  # o = soft-tissue cards of the bone catalogue
            continue
        v = V[n['vertexOffset']:n['vertexOffset'] + n['vertexCount']]
        f = F[n['faceOffset']:n['faceOffset'] + n['faceCount']].astype(np.int64)
        out.setdefault((kind, key), []).append(dict(part=rest[0] if rest else '', v=v, f=f, normals=n['hasNormals']))
    return idx, out


def combine(chunks):
    vs, fs, off = [], [], 0
    for c in chunks:
        vs.append(c['v']); fs.append(c['f'] + off); off += len(c['v'])
    return np.vstack(vs), np.vstack(fs)


def metrics(chunks):
    v, f = combine(chunks)
    finite = bool(np.isfinite(v).all())
    in_range = bool(f.size == 0 or (f.min() >= 0 and f.max() < len(v)))
    tri = v[f]
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    area = np.linalg.norm(cross, axis=1) / 2
    key = np.sort(f, axis=1)
    duplicate = len(key) - len(np.unique(key, axis=0))
    total = float(area.sum())
    centroid = (tri.mean(axis=1) * area[:, None]).sum(axis=0) / max(total, 1e-30)
    ext = (v.max(axis=0) - v.min(axis=0)) * 1000
    mesh = trimesh.Trimesh(vertices=v * 1000, faces=f, process=False)
    mesh.merge_vertices()
    watertight = bool(mesh.is_watertight)
    return dict(triangles=int(len(f)), vertices=int(len(v)), finite=finite, indicesInRange=in_range,
                zeroAreaFaces=int((area < 1e-12).sum()), duplicateFaces=int(duplicate),
                allNormals=all(c['normals'] for c in chunks), areaMM2=round(total * 1e6, 2),
                centroid=[round(x, 6) for x in centroid], extentMM=[round(x, 2) for x in ext],
                watertight=watertight, volumeMM3=round(float(mesh.volume), 1) if watertight else None,
                windingConsistent=bool(mesh.is_winding_consistent))


def sample(chunks, n=2500):
    v, f = combine(chunks)
    pts, _ = trimesh.sample.sample_surface(trimesh.Trimesh(vertices=v, faces=f, process=False), n, seed=7)
    return np.asarray(pts)


structures, sections_of = {}, {}
for sec in SECTIONS:
    _, items = load(sec)
    for key, chunks in items.items():
        sections_of.setdefault(key, []).append(sec)
        structures.setdefault(key, chunks)  # identical sources across sections are checked below
duplicates_across = {}
for sec in SECTIONS:
    _, items = load(sec)
    for key, chunks in items.items():
        if sections_of[key][0] != sec:
            a, b = combine(structures[key]), combine(chunks)
            duplicates_across[f'{key[0]}|{key[1]}|{sec}'] = bool(a[0].shape == b[0].shape and np.allclose(a[0], b[0]) and np.array_equal(a[1], b[1]))

rows, flags = {}, []
flag = lambda sev, typ, ident, detail: flags.append(dict(severity=sev, type=typ, id=ident, detail=detail))
for (kind, ident), chunks in structures.items():
    m = metrics(chunks)
    card = cards.get(('muscle' if kind == 'm' else 'bone', ident))
    m.update(kind=kind, id=ident, sections=sections_of[(kind, ident)], parts=sorted({c['part'] for c in chunks}),
             catalogueSide=card['side'] if card else None, inCatalogue=bool(card))
    rows[f'{kind}|{ident}'] = m
    if not card:
        flag('P1', 'mesh-without-card', ident, kind)
    if not m['finite'] or not m['indicesInRange']:
        flag('P0', 'mesh-invalid-values', ident, '')
    if m['zeroAreaFaces']:
        flag('P3', 'mesh-zero-area-faces', ident, m['zeroAreaFaces'])
    if m['duplicateFaces']:
        flag('P2', 'mesh-duplicate-faces', ident, m['duplicateFaces'])
    if not m['allNormals']:
        flag('P2', 'mesh-without-normals', ident, '')
    big = max(m['extentMM'])
    if big < 1.5 or big > 750:
        flag('P1', 'mesh-implausible-scale', ident, m['extentMM'])
    x, half = m['centroid'][0] * 1000, m['extentMM'][0] / 2
    side = m['catalogueSide']
    if side == 'right' and x > 0 or side == 'left' and x < 0:
        flag('P0', 'mesh-on-wrong-side', ident, f'side={side}, centroid x={x:.1f} mm')
    if side is None and kind == 'b' and abs(x) > max(10, half):
        flag('P2', 'unsided-mesh-off-midline', ident, f'centroid x={x:.1f} mm, half width {half:.1f}')
    if card and card['noModel']:
        flag('P1', 'noModel-card-has-mesh', ident, kind)

# Cards with a model claim but no loaded mesh.
for (kind, ident), card in cards.items():
    key = f"{'b' if kind == 'bone' else 'm'}|{ident}"
    if kind == 'bone' and key not in rows and f'o|{ident}' in rows:
        key = f'o|{ident}'
    if not card['noModel'] and key not in rows:
        flag('P1', 'card-model-not-loaded', ident, kind)
    for part, p in card['parts'].items():
        if not p['noModel'] and key in rows and part not in rows[key]['parts']:
            flag('P2', 'part-model-not-loaded', f'{ident}:{part}', '')

# Contralateral pairs.
pairs = []
for (kind, ident) in structures:
    if not ident.endswith('_left'):
        continue
    base = ident[:-5]
    right = next((k for k in [(kind, base), (kind, base + '_right')] if k in structures), None)
    if not right:
        continue
    L, R = structures[(kind, ident)], structures[right]
    mL, mR = rows[f'{kind}|{ident}'], rows[f'{kind}|{right[1]}']
    cL, cR = np.array(mL['centroid']), np.array(mR['centroid'])
    offset = (cL - cR * [-1, 1, 1]) * 1000
    pR = sample(R) * [-1, 1, 1]
    vL = combine(L)[0]
    tree = cKDTree(vL)
    raw = tree.query(pR)[0] * 1000
    # Rigid shape agreement (no scale/reflection) after centroid alignment.
    init = np.eye(4); init[:3, 3] = vL.mean(axis=0) - pR.mean(axis=0)
    matrix, aligned, cost = trimesh.registration.icp(pR, vL, initial=init, threshold=1e-7, max_iterations=40, scale=False, reflection=False)
    shape = tree.query(aligned)[0] * 1000
    row = dict(kind=kind, left=ident, right=right[1], centroidOffsetMM=[round(x, 2) for x in offset],
               areaRatio=round(mL['areaMM2'] / mR['areaMM2'], 3), triangleRatio=round(mL['triangles'] / mR['triangles'], 3),
               volumeRatio=round(mL['volumeMM3'] / mR['volumeMM3'], 3) if mL['volumeMM3'] and mR['volumeMM3'] else None,
               mirrorMedianMM=round(float(np.median(raw)), 2), mirrorP95MM=round(float(np.percentile(raw, 95)), 2),
               shapeMedianMM=round(float(np.median(shape)), 2), shapeP95MM=round(float(np.percentile(shape, 95)), 2),
               rotationDeg=round(float(np.degrees(np.arccos(np.clip((np.trace(matrix[:3, :3]) - 1) / 2, -1, 1)))), 2))
    pairs.append(row)
    size = max(mR['extentMM'])
    if row['shapeP95MM'] > max(3.0, 0.08 * size) or not 0.75 <= row['areaRatio'] <= 1.33:
        flag('P1', 'pair-shape-mismatch', ident, row)

# Landmarks: owner surface distance, nearest other bone, normal and attachment-to-muscle distance.
bone_keys = [k for k in structures if k[0] == 'b']
bone_vertices = {k: combine(structures[k])[0] for k in bone_keys}
all_v = np.vstack([bone_vertices[k] for k in bone_keys])
all_owner = np.concatenate([np.full(len(bone_vertices[k]), i) for i, k in enumerate(bone_keys)])
global_tree = cKDTree(all_v)
queries = {}
muscle_trees = {}


def query(key):
    if key not in queries:
        v, f = combine(structures[key])
        queries[key] = (SurfaceQuery(trimesh.Trimesh(vertices=v, faces=f, process=False)), trimesh.Trimesh(vertices=v, faces=f, process=False))
    return queries[key]


pin_rows = []
for pin in pins:
    if not pin['hasP']:
        continue
    owner = ('b', pin['b']) if ('b', pin['b']) in structures else ('o', pin['b'])
    p = np.array(pin['p'], dtype=np.float64)
    row = dict(id=pin['id'], b=pin['b'], c=pin['c'], kind=pin['geometryKind'], loc=pin['loc'], anchor=pin['anchorStatus'])
    if owner not in structures:
        row['ownerMesh'] = False
        pin_rows.append(row)
        flag('P1', 'pin-owner-without-mesh', pin['id'], pin['b'])
        continue
    sq, mesh = query(owner)
    closest, dist, tri = sq.closest([p])
    row['ownerMM'] = round(float(dist[0]), 3)
    if pin.get('n'):
        n = np.array(pin['n'], dtype=np.float64)
        cosine = float(np.dot(n / np.linalg.norm(n), mesh.face_normals[tri[0]]))
        row['normalDeg'] = round(float(np.degrees(np.arccos(np.clip(cosine, -1, 1)))), 1)
        if row['normalDeg'] > 100 and row['ownerMM'] < 3.0:
            flag('P2', 'pin-normal-into-surface', pin['id'], f"{pin['b']} {row['normalDeg']} deg")
    _, near = global_tree.query(p, k=64)
    candidates = []
    for i in near:
        k = bone_keys[all_owner[i]]
        if k != owner and k not in candidates:
            candidates.append(k)
        if len(candidates) == 2:
            break
    others = []
    for k in candidates:
        d = float(query(k)[0].closest([p])[1][0])
        others.append((round(d, 3), k[1]))
    if others:
        row['nearestOther'] = min(others)
    pin_rows.append(row)
    if row['ownerMM'] > 3.0 and pin['loc'] not in ('internal', 'projection'):
        flag('P1', 'pin-off-owner-surface', pin['id'], f"{pin['b']} {row['ownerMM']} mm, kind={pin['geometryKind']}, loc={pin['loc']}")
    if others and row['nearestOther'][0] + 0.5 < row['ownerMM'] and row['ownerMM'] > 1.0:
        flag('P0', 'pin-closer-to-other-bone', pin['id'], f"owner {pin['b']} {row['ownerMM']} mm, {row['nearestOther'][1]} {row['nearestOther'][0]} mm")
    for muscle, role, part in [(list(x) + [None])[:3] for x in pin['m']]:
        key = ('m', muscle)
        if key not in structures:
            continue
        if key not in muscle_trees:
            muscle_trees[key] = cKDTree(combine(structures[key])[0])
        d = float(muscle_trees[key].query(p)[0]) * 1000
        row.setdefault('muscleMM', []).append([muscle, role, part, round(d, 2)])
        if d > 15:
            flag('P2', 'attachment-far-from-muscle', pin['id'], f'{muscle}:{role} {d:.1f} mm from the muscle mesh')

with (run / 'pin-geometry.json').open('x', encoding='utf8') as fh:
    json.dump(pin_rows, fh, ensure_ascii=False)
by_type = {}
for f in flags:
    by_type[f['type']] = by_type.get(f['type'], 0) + 1
dist = np.array([r['ownerMM'] for r in pin_rows if 'ownerMM' in r])
report = dict(method=__doc__.strip().splitlines()[0], sections=SECTIONS, structures=len(rows),
              bones=sum(k.startswith('b|') for k in rows), muscles=sum(k.startswith('m|') for k in rows),
              crossSectionCopiesIdentical=duplicates_across, pinsMeasured=int(len(dist)),
              pinOwnerDistanceMM=dict(median=round(float(np.median(dist)), 3), p95=round(float(np.percentile(dist, 95)), 3),
                                      over1=int((dist > 1).sum()), over3=int((dist > 3).sum()), max=round(float(dist.max()), 2)),
              byType=by_type, flags=flags, pairs=pairs, structuresMetrics=rows)
with (run / 'geometry-audit.json').open('x', encoding='utf8') as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1)
print(json.dumps(dict(structures=len(rows), pairs=len(pairs), pinsMeasured=report['pinsMeasured'],
                      pinOwnerDistanceMM=report['pinOwnerDistanceMM'], byType=by_type,
                      nonIdenticalCopies=[k for k, v in duplicates_across.items() if not v]), ensure_ascii=False, indent=1))
