"""Approximate left limb landmarks by contralateral transfer (BONES-MUSCLES-AUDIT, GEO-LEFT-LIMB-MUSCLES).

Every left limb landmark record was published without a position or muscle link because the left
bones had no models. All of them now have native left BodyParts3D 3.0 meshes from the same body.
For each left record paired with a reviewed right record (template ID, unique TA98 code, unique
Latin term or ID) this script:
  1. reflects the whole right bone (x -> -x) and registers it rigidly to the native left bone
     (ICP, no scale or reflection), because limb posture differs between the sides;
  2. moves the right point and normal with that transform;
  3. snaps a surface point to the left mesh and accepts it only if the snap, the local shape
     residual, the normal angle and the nearest-bone test pass the thresholds below;
  4. adds the paired left muscle to the attachment links (anatomy of the named landmark is
     side-independent; the left muscle cards already copy the reviewed right text) and measures
     whether the native left muscle reaches the point as closely as the right muscle reaches its point.
  5. (LOG-20261026-02) a point rejected only for the local shape residual of the whole-bone fit is
     refined by a rigid fit of the 20 mm neighbourhood, started from the whole-bone fit; it is accepted
     only if the same residual threshold then passes, the point moves at most 3 mm and the rotation
     changes at most 5 degrees against the whole-bone fit, and the snap/normal/nearest-bone tests pass.
Accepted points are educational approximations (anchorStatus contralateral_transfer), never
independent left-side annotation. Rejected points keep p=None. Right records are never changed.
Writes site/pins-left-transfer.js (a by-ID patch loaded after pins-shared.js) and RUN/transfer-report.json.
Usage: python scripts/make_left_limb_landmarks.py RUN
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'verify'))
from geometry_distance import SurfaceQuery  # noqa: E402
from left_limb_muscles import table  # noqa: E402

run = Path(sys.argv[1]).resolve()
CACHE = ROOT / 'research/cache/atlas-geometry'
SECTIONS = ['arm', 'leg', 'trunk', 'neck']
# Acceptance thresholds (mm / degrees).
SNAP_MM = 2.0          # transferred surface point to the left surface
RESIDUAL_MM = 1.5      # median local shape residual within 8 mm after registration
NORMAL_DEG = 60.0      # transferred normal versus left face normal
OFFSURFACE_MM = 1.5    # change of the distance to the surface for off-surface points
RADIUS_MM = 8.0
LOCAL_FIT_MM = 20.0    # neighbourhood of the local refinement
LOCAL_SHIFT_MM = 3.0   # local versus whole-bone transfer of the point
LOCAL_ROT_DEG = 5.0
MIRROR = np.diag([-1.0, 1.0, 1.0])
NOTE = ('Ориентировочная точка: перенесена с проверенного правого ориентира той же модели BodyParts3D 3.0 '
        '(отражение, жёсткое совмещение всей кости и проекция на собственную левую сетку). '
        'Самостоятельно на левой стороне не размечалась и не подтверждена анатомом.')
NOTE_LOCAL = ('Ориентировочная точка: перенесена с проверенного правого ориентира той же модели BodyParts3D 3.0 '
              '(отражение, жёсткое совмещение всей кости, уточнённое по окрестности 20 мм, и проекция на собственную левую сетку). '
              'Самостоятельно на левой стороне не размечалась и не подтверждена анатомом.')
TRANSFERRED = 'показана ориентировочная точка, перенесённая с правой стороны той же модели'
# Only the statements that a transfer makes false; every other limit of the record stays verbatim.
TEXT_FIXES = [
    ('Подтверждённой координаты нет; точка с противоположной стороны не переносилась.', f'Подтверждённой координаты нет; {TRANSFERRED}.'),
    ('Координат нет; отражение другой стороны не применялось.', f'Подтверждённой координаты нет; {TRANSFERRED}.'),
    ('Координаты и протяжённость этого образования не приняты.', f'Координаты как разметка левой стороны и протяжённость образования не приняты; {TRANSFERRED}.'),
    ('координаты левого экземпляра отдельно не проверены.', f'координаты левого экземпляра отдельно не проверены; {TRANSFERRED}.'),
    ('Координаты, контуры и площади ориентиров не назначены.', f'Контуры и площади ориентиров не назначены; {TRANSFERRED}.'),
    ('Координаты пинов, контуры, площади и индивидуальные маски сесамоидов не переносились.',
     'Контуры, площади и индивидуальные маски сесамоидов не переносились; точка — отражение проверенной правой (ориентировочно).'),
    ('Левый экземпляр: координаты правой стороны не переносились.', 'Левый экземпляр: точка ориентировочно перенесена с правой стороны.'),
]
STALE = ('не переносил', 'Координат нет', 'не назначены.', 'отражение другой стороны не применялось')


def fix_text(text):
    for old, new in TEXT_FIXES:
        text = text.replace(old, new)
    return text


def section_geometry():
    for sec in SECTIONS:
        index = json.loads((CACHE / f'{sec}.json').read_text(encoding='utf8'))
        for source in index['sources']:
            if hashlib.sha256((ROOT / source['file']).read_bytes()).hexdigest() != source['sha256']:
                raise SystemExit(f'Stale geometry cache for {sec}: run node tools/export-atlas-geometry.mjs {sec}')
        raw = (CACHE / f'{sec}.bin').read_bytes()
        V = np.frombuffer(raw[:index['vertexBytes']], dtype=np.float32).reshape(-1, 3).astype(np.float64)
        F = np.frombuffer(raw[index['vertexBytes']:], dtype=np.uint32).reshape(-1, 3).astype(np.int64)
        for node in index['nodes']:
            kind, key, *_ = node['name'].split('|')
            if kind in ('b', 'm', 'o'):
                v = V[node['vertexOffset']:node['vertexOffset'] + node['vertexCount']]
                f = F[node['faceOffset']:node['faceOffset'] + node['faceCount']]
                yield sec, kind, key, v, f


meshes = {}
for sec, kind, key, v, f in section_geometry():
    store = meshes.setdefault((kind, key), {'sec': sec, 'chunks': []})
    if store['sec'] == sec:
        store['chunks'].append((v, f))


def mesh(kind, key):
    chunks = meshes[(kind, key)]['chunks']
    vs, fs, off = [], [], 0
    for v, f in chunks:
        vs.append(v); fs.append(f + off); off += len(v)
    return trimesh.Trimesh(vertices=np.vstack(vs), faces=np.vstack(fs), process=False)


data = json.loads(subprocess.check_output(['node', str(ROOT / 'tools/dump-atlas-pins.mjs')], cwd=ROOT, encoding='utf8'))
pins, muscles, bones = data['pins'], data['muscles'], data['bones']
by_id = {p['id']: p for p in pins}
LIMB_LEFT = {b for b in bones if b.endswith('_left') and ('b', b) in meshes and meshes[('b', b)]['sec'] in ('arm', 'leg')}


def right_bone(bone):
    return bone[:-5]


def pair(left):
    rb = right_bone(left['b'])
    if left.get('templateRecord'):
        r = by_id.get(left['templateRecord'])
        return r if r and r['b'] == rb else None
    if left.get('c'):
        found = [r for r in pins if r['b'] == rb and r.get('c') == left['c']]
        if len(found) > 1:
            found = [r for r in found if r['lat'] == left['lat']]
        if len(found) == 1:
            return found[0]
    if left.get('lat'):
        found = [r for r in pins if r['b'] == rb and r['lat'] == left['lat'] and r['t'] == left['t']]
        if len(found) == 1:
            return found[0]
    r = by_id.get(left['id'].replace('_left', ''))
    return r if r and r['b'] == rb else None


cross = {r['right']: r['left'] for r in table()}


def left_muscle(right):
    for candidate in [cross.get(right), right[:-6] + '_left' if right.endswith('_right') else None, right + '_left']:
        if candidate and candidate in muscles:
            return candidate
    return None


registrations, report, patches = {}, [], {}


def register(bone):
    if bone in registrations:
        return registrations[bone]
    L, R = mesh('b', bone), mesh('b', right_bone(bone))
    src = np.asarray(R.vertices) @ MIRROR.T
    rng = np.random.default_rng(20261025)
    sample = src[rng.choice(len(src), size=min(4000, len(src)), replace=False)]
    init = np.eye(4)
    init[:3, 3] = np.asarray(L.vertices).mean(axis=0) - src.mean(axis=0)
    matrix, _, _ = trimesh.registration.icp(sample, np.asarray(L.vertices), initial=init, threshold=1e-9,
                                            max_iterations=80, reflection=False, scale=False)
    moved = trimesh.transform_points(src, matrix)
    tree = cKDTree(np.asarray(L.vertices))
    residual = tree.query(moved)[0] * 1000
    registrations[bone] = dict(matrix=matrix, moved=moved, movedTree=cKDTree(moved), residual=residual, left=L, right=R,
                               leftQuery=SurfaceQuery(L), rightQuery=SurfaceQuery(R),
                               stats=dict(medianMM=round(float(np.median(residual)), 3), p95MM=round(float(np.percentile(residual, 95)), 3),
                                          rotationDeg=round(float(np.degrees(np.arccos(np.clip((np.trace(matrix[:3, :3]) - 1) / 2, -1, 1)))), 2)))
    return registrations[bone]


def refine_locally(reg, p_r):
    """Rigid fit of the reflected right neighbourhood, started from the whole-bone fit (step 5)."""
    M = reg['matrix']
    src = np.asarray(reg['right'].vertices) @ MIRROR.T
    pm = MIRROR @ p_r
    idx = np.where(np.linalg.norm(src - pm, axis=1) <= LOCAL_FIT_MM / 1000)[0]
    q0 = trimesh.transform_points([pm], M)[0]
    left_v = np.asarray(reg['left'].vertices)
    targets = left_v[np.linalg.norm(left_v - q0, axis=1) <= (LOCAL_FIT_MM + 10) / 1000]
    if len(idx) < 50 or len(targets) < 50:
        return None
    matrix, _, _ = trimesh.registration.icp(src[idx], targets, initial=M, threshold=1e-9, max_iterations=60,
                                            reflection=False, scale=False)
    q1 = trimesh.transform_points([pm], matrix)[0]
    moved = trimesh.transform_points(src[idx], matrix)
    near = np.linalg.norm(moved - q1, axis=1) <= RADIUS_MM / 1000
    residual = cKDTree(left_v).query(moved[near])[0] * 1000 if near.any() else None
    delta = matrix[:3, :3] @ M[:3, :3].T
    return dict(matrix=matrix, point=q1, residualMM=float(np.median(residual)) if residual is not None else None,
                shiftMM=float(np.linalg.norm(q1 - q0) * 1000),
                rotationDeg=float(np.degrees(np.arccos(np.clip((np.trace(delta) - 1) / 2, -1, 1)))), neighbours=int(len(idx)))


# Nearest-bone test uses all limb bones of the same side.
side_bones = sorted(LIMB_LEFT)
side_vertices = [np.asarray(mesh('b', b).vertices) for b in side_bones]
side_tree = cKDTree(np.vstack(side_vertices))
side_owner = np.concatenate([np.full(len(v), i) for i, v in enumerate(side_vertices)])
muscle_trees = {}


def muscle_distance(key, point):
    if key not in meshes:
        return None
    if key not in muscle_trees:
        muscle_trees[key] = cKDTree(np.asarray(mesh(*key).vertices))
    return float(muscle_trees[key].query(point)[0]) * 1000


def left_attachment(right):
    """Left counterpart of a reviewed right attachment area (t=att): same text, side words swapped."""
    record = {k: right[k] for k in ('t', 'lat', 'x', 'refs', 'geometryKind', 'geometryKindReason', 'anatomicalDefinition', 'note') if k in right}
    for key in ('x', 'note', 'anatomicalDefinition', 'geometryKindReason'):
        if key in record:
            record[key] = record[key].replace('справа', 'слева').replace('правой', 'левой').replace('правая', 'левая')
    record.update(id='left_' + right['id'], b=right['b'] + '_left', ru=right['ru'] + ' слева', side='left', p=None, n=None, m=[],
                  templateRecord=right['id'],
                  modelNote='Левое место прикрепления создано по проверенной правой записи; координаты левого экземпляра — см. ниже.')
    return record


work = [left for left in pins if left['b'] in LIMB_LEFT and not left.get('p')]
existing = {p['id'] for p in pins}
additions = []
for right in pins:
    if right['t'] == 'att' and right['b'] + '_left' in LIMB_LEFT and right.get('m'):
        record = left_attachment(right)
        assert record['id'] not in existing, record['id']
        additions.append(record)
        work.append(record)
by_id.update({r['id']: r for r in additions})

for left in work:
    right = pair(left)
    row = dict(id=left['id'], bone=left['b'], right=right['id'] if right else None)
    if not right:
        row['status'] = 'no_paired_right_record'
        report.append(row)
        continue
    links = []
    for entry in right.get('m') or []:
        muscle, role, part = (list(entry) + [None])[:3]
        target = left_muscle(muscle)
        if not target:
            row.setdefault('linkProblems', []).append(f'{muscle}: no left card')
            continue
        keep_part = part if part and part in muscles[target]['parts'] else None
        if part and not keep_part:
            # Cross-region cards name the same TA98 parts with other keys (clav/clavicular).
            same = [k for k, lat in muscles[target]['parts'].items() if lat == muscles[muscle]['parts'].get(part)]
            keep_part = same[0] if len(same) == 1 else None
        if part and not keep_part:
            row.setdefault('linkProblems', []).append(f'{muscle}:{part} -> {target}: part not on the left card, linked to whole muscle')
        links.append([target, role, keep_part] if keep_part else [target, role])
    patch = {}
    if links:
        patch['m'] = links
    if not right.get('p') or right.get('anchorStatus') == 'unverified':
        row['status'] = 'right_record_without_reviewed_position'
    else:
        reg = register(left['b'])
        M = reg['matrix']
        p_r, n_r = np.array(right['p'], float), np.array(right.get('n') or [0, 0, 0], float)
        q = trimesh.transform_points([MIRROR @ p_r], M)[0]
        n_q = M[:3, :3] @ (MIRROR @ n_r)
        n_q = n_q / np.linalg.norm(n_q) if np.linalg.norm(n_q) else n_q
        d_right = float(reg['rightQuery'].closest([p_r])[1][0])
        closest, d_left, tri = reg['leftQuery'].closest([q])
        near = reg['movedTree'].query_ball_point(q, RADIUS_MM / 1000)
        local = float(np.median(reg['residual'][near])) if near else None
        normal_deg = None
        if np.linalg.norm(n_q):
            face_n = reg['left'].face_normals[tri[0]]
            normal_deg = float(np.degrees(np.arccos(np.clip(np.dot(face_n, n_q), -1, 1))))
        surface = d_right <= 0.5
        point = closest[0] if surface else q
        _, nearest = side_tree.query(q, k=48)
        others = {side_bones[side_owner[i]] for i in nearest} - {left['b']}
        closer = []
        for other in sorted(others)[:3]:
            d = float(SurfaceQuery(mesh('b', other)).closest([q])[1][0])
            if d + 0.25 < float(d_left[0]):
                closer.append([other, round(d, 3)])
        row.update(rightSurfaceMM=round(d_right, 3), snapMM=round(float(d_left[0]), 3), localResidualMM=round(local, 3) if local is not None else None,
                   normalDeg=round(normal_deg, 1) if normal_deg is not None else None, closerBones=closer, registration=reg['stats'])
        reasons = []
        if surface and d_left[0] > SNAP_MM:
            reasons.append('snap')
        if not surface and abs(float(d_left[0]) - d_right) > OFFSURFACE_MM:
            reasons.append('surface distance changed')
        if local is None or local > RESIDUAL_MM:
            reasons.append('local shape residual')
        if surface and normal_deg is not None and normal_deg > NORMAL_DEG:
            reasons.append('normal')
        if closer:
            reasons.append('closer to another bone')
        if reasons == ['local shape residual']:
            local_fit = refine_locally(reg, p_r)
            if local_fit:
                M = local_fit['matrix']
                q = local_fit['point']
                n_q = M[:3, :3] @ (MIRROR @ n_r)
                n_q = n_q / np.linalg.norm(n_q) if np.linalg.norm(n_q) else n_q
                closest, d_left, tri = reg['leftQuery'].closest([q])
                normal_deg = None
                if np.linalg.norm(n_q):
                    normal_deg = float(np.degrees(np.arccos(np.clip(np.dot(reg['left'].face_normals[tri[0]], n_q), -1, 1))))
                point = closest[0] if surface else q
                _, nearest = side_tree.query(q, k=48)
                closer = []
                for other in sorted({side_bones[side_owner[i]] for i in nearest} - {left['b']})[:3]:
                    d = float(SurfaceQuery(mesh('b', other)).closest([q])[1][0])
                    if d + 0.25 < float(d_left[0]):
                        closer.append([other, round(d, 3)])
                row['localRefinement'] = dict(residualMM=round(local_fit['residualMM'], 3) if local_fit['residualMM'] is not None else None,
                                              shiftMM=round(local_fit['shiftMM'], 3), rotationDeg=round(local_fit['rotationDeg'], 2),
                                              neighbours=local_fit['neighbours'], snapMM=round(float(d_left[0]), 3),
                                              normalDeg=round(normal_deg, 1) if normal_deg is not None else None, closerBones=closer)
                local_reasons = []
                if local_fit['residualMM'] is None or local_fit['residualMM'] > RESIDUAL_MM:
                    local_reasons.append('local shape residual')
                if local_fit['shiftMM'] > LOCAL_SHIFT_MM or local_fit['rotationDeg'] > LOCAL_ROT_DEG:
                    local_reasons.append('local fit departs from whole-bone fit')
                if surface and d_left[0] > SNAP_MM:
                    local_reasons.append('snap')
                if not surface and abs(float(d_left[0]) - d_right) > OFFSURFACE_MM:
                    local_reasons.append('surface distance changed')
                if surface and normal_deg is not None and normal_deg > NORMAL_DEG:
                    local_reasons.append('normal')
                if closer:
                    local_reasons.append('closer to another bone')
                if not local_reasons:
                    reasons = []
                    row['method'] = 'local_refinement'
                else:
                    row['localRefinement']['reasons'] = local_reasons
        if reasons:
            row['status'] = 'rejected'
            row['reasons'] = reasons
        else:
            row['status'] = 'accepted_approximate'
            patch.update(p=[round(float(x), 5) for x in point], n=[round(float(x), 3) for x in n_q], anchorStatus='contralateral_transfer')
            for key in ('x', 'modelNote'):
                if left.get(key):
                    fixed = fix_text(left[key])
                    stale = [s for s in STALE if s in fixed and not ('сесамоидов не переносились' in fixed and s == 'не переносил')]
                    assert not stale, (left['id'], key, stale)
                    if fixed != left[key]:
                        patch[key] = fixed
            if right.get('loc') and not left.get('loc'):
                patch['loc'] = right['loc']
            checks = []
            for entry in right.get('m') or []:
                muscle, role, part = (list(entry) + [None])[:3]
                target = left_muscle(muscle)
                d_r, d_l = muscle_distance(('m', muscle), p_r), muscle_distance(('m', target), point) if target else None
                if d_r is not None and d_l is not None:
                    checks.append(dict(right=muscle, left=target, role=role, rightMM=round(d_r, 2), leftMM=round(d_l, 2),
                                       consistent=abs(d_l - d_r) <= 5.0))
            if checks:
                row['muscleChecks'] = checks
    if left in additions:
        row['created'] = True
        patch = {**left, **patch}
    if patch:
        patch['transferReview'] = dict(method='contralateral_local_rigid_transfer' if row.get('method') == 'local_refinement' else 'contralateral_rigid_transfer',
                                       template=right['id'], status=row['status'],
                                       coordinateAcceptance=False, educationalApproximation=row['status'] == 'accepted_approximate',
                                       linksFromPairedRecord=bool(links), report='research/BONES_MUSCLES_FULL_AUDIT.md',
                                       **{k: row[k] for k in ('snapMM', 'localResidualMM', 'normalDeg', 'localRefinement') if k in row})
        if row['status'] == 'accepted_approximate':
            patch['transferNote'] = NOTE_LOCAL if row.get('method') == 'local_refinement' else NOTE
        patches[left['id']] = patch
    report.append(row)

statuses = {}
refined = [r for r in report if r.get('method') == 'local_refinement']
for r in report:
    statuses[r['status']] = statuses.get(r['status'], 0) + 1
accepted = [r for r in report if r['status'] == 'accepted_approximate']
checks = [c for r in accepted for c in r.get('muscleChecks', [])]
summary = dict(records=len(report), created=len(additions), statuses=statuses, bones=len({r['bone'] for r in report}),
               withLinks=sum('m' in p for p in patches.values()), links=sum(len(p.get('m', [])) for p in patches.values()),
               leftMusclesLinked=len({m[0] for p in patches.values() for m in p.get('m', [])}),
               muscleChecks=len(checks), muscleChecksConsistent=sum(c['consistent'] for c in checks),
               acceptedByLocalRefinement=len(refined),
               thresholds=dict(snapMM=SNAP_MM, localResidualMM=RESIDUAL_MM, normalDeg=NORMAL_DEG, offSurfaceMM=OFFSURFACE_MM, radiusMM=RADIUS_MM,
                               localFitMM=LOCAL_FIT_MM, localShiftMM=LOCAL_SHIFT_MM, localRotationDeg=LOCAL_ROT_DEG))
with (run / 'transfer-report.json').open('x', encoding='utf8') as fh:
    json.dump(dict(summary=summary, registrations={b: r['stats'] for b, r in registrations.items()}, rows=report), fh, ensure_ascii=False, indent=1)
text = ('/* Generated by scripts/make_left_limb_landmarks.py; do not edit. Approximate left limb landmarks and links. */\n'
        '(()=>{const byId=Object.fromEntries(window.ATLAS.pins.map(p=>[p.id,p]));\n'
        'const created=' + json.dumps([i for i in patches if i in {a["id"] for a in additions}]) + ';\n'
        'const patches=' + json.dumps(patches, ensure_ascii=False, separators=(',', ':')) + ';\n'
        'for(const id of created){if(byId[id])throw new Error("Duplicate landmark "+id);window.ATLAS.pins.push(byId[id]={id,m:[]});}\n'
        'for(const [id,patch] of Object.entries(patches)){const pin=byId[id];\n'
        'if(!pin)throw new Error("Unknown landmark "+id);if(pin.p&&patch.p)throw new Error("Refusing to replace a reviewed position: "+id);\n'
        'if(patch.m)patch.m=[...(pin.m||[]),...patch.m];Object.assign(pin,patch);}})();\n')
(ROOT / 'site/pins-left-transfer.js').write_text(text, encoding='utf8')
print(json.dumps(summary, ensure_ascii=False, indent=1))
