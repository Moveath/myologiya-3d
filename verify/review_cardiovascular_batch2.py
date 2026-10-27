"""Topographic review of the second BodyParts3D cardiovascular batch (LOG-20261026-03).

For each new heart part: distance to the BodyParts3D heart wall, share of vertices inside the myocardial wall
(signed distance with the outward wall normals) and inside the heart's convex hull, and the nearest existing
coronary vessels and atrioventricular valves. Expected relations come from the cited sources: branches and
cardiac veins run on the epicardial surface next to their parent vessels, septal branches inside the wall,
papillary muscles in the ventricular cavity next to the chordae of their valve. Usage: python verify/review_cardiovascular_batch2.py RUN
"""
import json
import sys
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
BUILD = ROOT / 'build_cardiovascular/bp3d-3.0-v1'
CV = ROOT / 'site/models/bodyparts3d-3.0/cardiovascular'
EXPECT = {
    'cv_a_coronary_right_marginal': ('surface', ['cv_a_coronary_right']),
    'cv_a_coronary_posterior_interventricular': ('surface', ['cv_a_coronary_right']),
    'cv_a_coronary_right_posterolateral': ('surface', ['cv_a_coronary_right']),
    'cv_a_coronary_septal_right': ('wall', []),
    'cv_a_coronary_septal_left': ('wall', ['cv_a_coronary_anterior_interventricular']),
    'cv_v_cardiac_great': ('surface', ['cv_a_coronary_anterior_interventricular', 'cv_a_coronary_circumflex']),
    'cv_v_cardiac_middle': ('surface', []),
    'cv_v_ventricle_left_posterior': ('surface', ['cv_a_coronary_circumflex']),
    'cv_v_cardiac_anterior': ('surface', ['cv_a_coronary_right']),
    'cv_papillary_rv_anterior': ('cavity', []),
    'cv_papillary_rv_posterior': ('cavity', ['cv_valve_tricuspid']),
    'cv_papillary_rv_septal': ('cavity', ['cv_valve_tricuspid']),
    'cv_papillary_lv_posterior': ('cavity', ['cv_valve_mitral']),
    'cv_papillary_lv_unspecified': ('cavity', []),
}
NEIGHBOURS = ['cv_a_coronary_right', 'cv_a_coronary_left', 'cv_a_coronary_anterior_interventricular', 'cv_a_coronary_circumflex',
              'cv_valve_tricuspid', 'cv_valve_mitral', 'cv_valve_pulmonary']
heart = trimesh.load(CV / 'cv_heart.glb', force='mesh', process=False)
pts, faces = trimesh.sample.sample_surface(heart, 400000, seed=3)
wall_tree, wall_normals = cKDTree(pts), heart.face_normals[faces]
from scipy.spatial import Delaunay
hull = Delaunay(heart.convex_hull.vertices)
near = {k: cKDTree(trimesh.load(CV / f'{k}.glb', force='mesh', process=False).vertices) for k in NEIGHBOURS}
rows, passed = [], 0
for card, (kind, expected) in EXPECT.items():
    record = json.loads((BUILD / f'{card}.json').read_text(encoding='utf8'))
    mesh = trimesh.load(ROOT / record['trial'], force='mesh', process=False)
    d, i = wall_tree.query(mesh.vertices)
    in_wall = float((np.einsum('ij,ij->i', mesh.vertices - pts[i], wall_normals[i]) < 0).mean())
    in_hull = float((hull.find_simplex(mesh.vertices) >= 0).mean())
    contacts = {k: round(float(t.query(mesh.vertices)[0].min() * 1000), 2) for k, t in near.items()}
    checks = {'side': record['boundsM'] is not None}
    if kind == 'surface':
        checks['onEpicardium'] = float(np.median(d * 1000)) <= 1.0
    elif kind == 'wall':
        checks['insideWall'] = in_wall >= 0.7
    else:
        checks['inCavity'] = in_hull >= 0.99 and in_wall <= 0.6
    checks['parentContact'] = all(contacts[k] <= 1.0 for k in expected)
    ok = all(checks.values())
    passed += ok
    rows.append(dict(id=card, fma=record['source']['fma'], triangles=record['triangles'], expected=kind, expectedContacts=expected,
                     wallDistanceMedianMM=round(float(np.median(d) * 1000), 2), wallDistanceMaxMM=round(float(d.max() * 1000), 2),
                     insideWallShare=round(in_wall, 3), insideHullShare=round(in_hull, 3), nearestMM=contacts, checks=checks, passed=ok,
                     degenerate=record['degenerate'], duplicateFaces=record['duplicateFaces']))
result = dict(rule='surface: median distance to the heart wall <= 1 mm; wall: >=70% of vertices inside the myocardial wall; '
                   'cavity: >=99% inside the heart hull and <=60% inside the wall; expected parent vessels/valves within 1 mm',
              limitation='Signed distance and convex hull are coarse topographic tests on one specimen; course, branching pattern and dominance are not accepted.',
              rows=rows, passed=passed, total=len(rows))
with (run / 'batch2-topography.json').open('x', encoding='utf8') as fh:
    json.dump(result, fh, ensure_ascii=False, indent=1)
print(json.dumps(dict(passed=passed, total=len(rows), failed=[(r['id'], r['checks'], r['nearestMM']) for r in rows if not r['passed']]), ensure_ascii=False, indent=1))
