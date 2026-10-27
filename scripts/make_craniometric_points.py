"""Approximate craniometric points as suture junctions of the head bone meshes (PIN-001, LOG-20261026-02).

Nasion, bregma, lambda and asterion are defined as the meeting point of named bones/sutures (Gray 1918,
craniometry; Vigo et al. 2020, suture junctions), and the atlas head has one mesh per bone, so a junction is
measurable instead of guessed. For each record the bones are taken from its own reviewed relations:
  1. dense surface samples of every participating bone; candidate points lie within JUNCTION_MM of all of them;
  2. the ectocranial end of the junction is the candidate farthest from the centre of the cranial vault;
  3. the point is snapped to the record's own bone; the unflipped face normal of the closed, consistently wound
     bone mesh must face away from the vault centre, and the outward segment from 3 to 15 mm must be free of
     every head bone (outer surface, not the endocranial end; the neighbouring bones of the junction itself lie
     within the first millimetres by definition);
  4. midline points must lie within MIDLINE_MM of the vault midline; the two asterions must mirror each other.
A record whose bones have no common junction on the mesh (pterion: H-shaped meeting) stays without a point.
Accepted points are educational approximations (anchorStatus mesh_suture_junction), never accepted annotation.
Writes site/pins-craniometric.js (a by-ID patch loaded after pins-shared.js) and RUN/craniometric-points.json.
Usage: python scripts/make_craniometric_points.py RUN
"""
import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
CACHE = ROOT / 'research/cache/atlas-geometry'
IDS = ['shared_skull_015', 'shared_skull_016', 'shared_skull_017', 'shared_skull_019_right', 'shared_skull_019_left',
       'shared_skull_020_right', 'shared_skull_020_left']
MIDLINE = {'shared_skull_015', 'shared_skull_016', 'shared_skull_017'}
VAULT = ['frontal', 'parietal_right', 'parietal_left', 'occipital', 'temporal_right', 'temporal_left']
JUNCTION_MM = 1.0      # every participating bone within this distance
SEARCH_MM = 3.0        # reported search limit for records without a junction
OUTER_MM = 4.0         # candidates within this of the farthest one form the ectocranial cluster
MIDLINE_MM = 3.0
MIRROR_MM = 3.0
CLEAR_MM = 1.0         # outward segment clearance from all head bones
SAMPLES = 400000
NOTE = ('Ориентировочная точка: вычислена как место встречи сеток участвующих костей этой модели на наружной '
        'поверхности черепа (определение точки — Gray 1918; Vigo et al. 2020). Ход швов на модели анатомически не принят; '
        'точка не размечалась анатомом.')
OLD_NOTE = 'Точка, полный контур и индивидуальные варианты на этой модели не подтверждены; координаты не создавались.'
NEW_NOTE = ('Полный контур и индивидуальные варианты на этой модели не подтверждены; точка вычислена как стык сеток костей '
            'и показана как ориентировочная.')

index = json.loads((CACHE / 'head.json').read_text(encoding='utf8'))
for source in index['sources']:
    if hashlib.sha256((ROOT / source['file']).read_bytes()).hexdigest() != source['sha256']:
        raise SystemExit('Stale geometry cache: run node tools/export-atlas-geometry.mjs head')
raw = (CACHE / 'head.bin').read_bytes()
V = np.frombuffer(raw[:index['vertexBytes']], dtype=np.float32).reshape(-1, 3).astype(np.float64)
F = np.frombuffer(raw[index['vertexBytes']:], dtype=np.uint32).reshape(-1, 3).astype(np.int64)
chunks = {}
for node in index['nodes']:
    if node['name'].startswith('b|'):
        chunks.setdefault(node['name'][2:], []).append((V[node['vertexOffset']:node['vertexOffset'] + node['vertexCount']],
                                                        F[node['faceOffset']:node['faceOffset'] + node['faceCount']]))


def mesh(bone):
    vs, fs, off = [], [], 0
    for v, f in chunks[bone]:
        vs.append(v); fs.append(f + off); off += len(v)
    return trimesh.Trimesh(np.vstack(vs), np.vstack(fs), process=False)


meshes = {b: mesh(b) for b in chunks}
for b, m in meshes.items():
    assert m.is_winding_consistent and m.volume > 0, f'{b}: face normals are not consistently outward'
dense = {b: cKDTree(np.vstack([m.vertices, trimesh.sample.sample_surface(m, SAMPLES, seed=7)[0]])) for b, m in meshes.items()}
all_bones = cKDTree(np.vstack([t.data for t in dense.values()]))
vault = np.vstack([meshes[b].vertices for b in VAULT])
centre = (vault.min(0) + vault.max(0)) / 2
pins = {p['id']: p for p in json.loads(subprocess.check_output(['node', str(ROOT / 'tools/dump-atlas-pins.mjs')], cwd=ROOT,
                                                                encoding='utf8'))['pins']}
rows, patches = [], {}
for pid in IDS:
    pin = pins[pid]
    bones = [r['bone'] for r in pin['relations']]
    assert pin['b'] in bones and not pin.get('p'), pid
    candidates = np.vstack([np.vstack([meshes[b].vertices, trimesh.sample.sample_surface(meshes[b], 20000, seed=1)[0]]) for b in bones])
    distance = np.max([dense[b].query(candidates)[0] for b in bones], axis=0) * 1000
    row = dict(id=pid, lat=pin['lat'], bones=bones, owner=pin['b'], minJunctionMM=round(float(distance.min()), 3))
    joined = candidates[distance <= JUNCTION_MM]
    if not len(joined):
        row.update(status='no_junction', reason=f'Участвующие кости не сходятся в одной точке сетки (минимум {row["minJunctionMM"]} мм > {JUNCTION_MM} мм); '
                   'для H-образного стыка нужен выбор определения точки и анатомическая приёмка.',
                   pairMinimaMM={f'{a}-{b}': round(float(dense[b].query(meshes[a].vertices)[0].min() * 1000), 2)
                                 for a, b in itertools.combinations(bones, 2)})
        rows.append(row)
        continue
    radius = np.linalg.norm(joined - centre, axis=1)
    cluster = joined[radius >= radius.max() - OUTER_MM / 1000]
    target = joined[np.argmax(radius)]
    closest, snap, triangle = trimesh.proximity.closest_point_naive(meshes[pin['b']], [target])
    point, normal = closest[0], meshes[pin['b']].face_normals[triangle[0]]
    outward = bool(np.dot(normal, point - centre) > 0)
    segment = point + np.outer(np.linspace(3, 15, 25) / 1000, normal if outward else -normal)
    clearance = float(all_bones.query(segment)[0].min() * 1000)
    junction = float(max(dense[b].query([point])[0][0] for b in bones) * 1000)
    row.update(point=[round(float(x), 5) for x in point], normal=[round(float(x), 3) for x in normal],
               junctionMM=round(junction, 3), snapMM=round(float(snap[0] * 1000), 3), candidates=int(len(joined)),
               outerClusterSpreadMM=round(float(np.linalg.norm(cluster - cluster.mean(0), axis=1).max() * 1000), 2),
               outwardClearanceMM=round(clearance, 2), outwardNormal=outward)
    reasons = []
    if not outward:
        reasons.append('face normal points into the cranium')
    if junction > JUNCTION_MM + 0.5:
        reasons.append('junction after snap')
    if clearance < CLEAR_MM:
        reasons.append('not on the outer surface')
    if pid in MIDLINE:
        row['midlineOffsetMM'] = round(float(abs(point[0] - centre[0]) * 1000), 2)
        if row['midlineOffsetMM'] > MIDLINE_MM:
            reasons.append('off the midline')
    row['status'] = 'rejected' if reasons else 'accepted_approximate'
    if reasons:
        row['reasons'] = reasons
    rows.append(row)
# The two asterions are independent computations; they must mirror each other on this symmetric skull.
asterion = {r['id']: r for r in rows if r['id'].startswith('shared_skull_020') and r['status'] == 'accepted_approximate'}
if len(asterion) == 2:
    right, left = asterion['shared_skull_020_right'], asterion['shared_skull_020_left']
    mismatch = float(np.linalg.norm(np.array(right['point']) * [-1, 1, 1] - (np.array(left['point']) - [2 * centre[0], 0, 0])) * 1000)
    for r in (right, left):
        r['mirrorMismatchMM'] = round(mismatch, 2)
        if mismatch > MIRROR_MM:
            r['status'] = 'rejected'
            r.setdefault('reasons', []).append('asterions do not mirror')
for row in rows:
    if row['status'] != 'accepted_approximate':
        continue
    pin = pins[row['id']]
    assert OLD_NOTE in pin['modelNote'], row['id']
    patches[row['id']] = dict(p=row['point'], n=row['normal'], anchorStatus='mesh_suture_junction',
                              modelNote=pin['modelNote'].replace(OLD_NOTE, NEW_NOTE), approximateNote=NOTE,
                              approximateReview=dict(method='mesh_suture_junction', coordinateAcceptance=False,
                                                     educationalApproximation=True, bones=row['bones'],
                                                     junctionMM=row['junctionMM'], outwardClearanceMM=row['outwardClearanceMM'],
                                                     report='research/evidence-runs/' + run.name + '/craniometric-points.json'))
summary = dict(records=len(rows), accepted=len(patches), statuses={s: sum(r['status'] == s for r in rows) for s in {r['status'] for r in rows}},
               thresholds=dict(junctionMM=JUNCTION_MM, outerClusterMM=OUTER_MM, midlineMM=MIDLINE_MM, mirrorMM=MIRROR_MM,
                               outwardClearanceMM=CLEAR_MM, samplesPerBone=SAMPLES),
               vaultCentre=[round(float(x), 5) for x in centre], geometry=index['sources'])
with (run / 'craniometric-points.json').open('x', encoding='utf8') as fh:
    json.dump(dict(summary=summary, rows=rows), fh, ensure_ascii=False, indent=1)
text = ('/* Generated by scripts/make_craniometric_points.py; do not edit. Approximate craniometric points (suture junctions). */\n'
        '(()=>{const byId=Object.fromEntries(window.ATLAS.pins.map(p=>[p.id,p]));\n'
        'const patches=' + json.dumps(patches, ensure_ascii=False, separators=(',', ':')) + ';\n'
        'for(const [id,patch] of Object.entries(patches)){const pin=byId[id];\n'
        'if(!pin)throw new Error("Unknown landmark "+id);if(pin.p)throw new Error("Refusing to replace a position: "+id);\n'
        'Object.assign(pin,patch);}})();\n')
(ROOT / 'site/pins-craniometric.js').write_text(text, encoding='utf8')
print(json.dumps(dict(summary={k: v for k, v in summary.items() if k != 'geometry'},
                      rows=[(r['id'], r['status'], r.get('junctionMM'), r.get('outwardClearanceMM'), r.get('midlineOffsetMM'),
                             r.get('mirrorMismatchMM'), r.get('reasons') or r.get('reason', '')[:60]) for r in rows]), ensure_ascii=False, indent=1))
