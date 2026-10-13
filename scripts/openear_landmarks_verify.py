"""Check thirteen supplemental pin positions against the original author PLYs.

This verifies numeric correspondence only, not anatomical correctness.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import trimesh
from openear_landmarks_completion import EXPECTED_CODES

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'pins_head/openear-native.json').read_text(encoding='utf-8'))
rotation = np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]])
filenames = {'malleus': '03_Malleus.ply', 'incus': '04_Incus.ply', 'stapes': '05_Stapes.ply'}
checks = []
for bone, filename in filenames.items():
    mesh = trimesh.load(ROOT / 'research/cache/complete-temporal/zeta' / filename, process=False)
    mesh.vertices = mesh.vertices @ rotation.T
    selected = [m for m in data['markers'] if m['b'] == bone]
    # Use mm: trimesh's general degenerate-triangle tolerance is inappropriate
    # for tiny ossicle triangles if their coordinates are expressed in metres.
    points = np.array([m['p'] for m in selected]) * 1000
    _, distances, triangle_ids = trimesh.proximity.closest_point_naive(mesh, points)
    for marker, distance, triangle_id in zip(selected, distances, triangle_ids):
        assert distance < .003, (marker['id'], distance)
        checks.append({'id': marker['id'], 'original_ply': filename,
                       'original_ply_sha256': hashlib.sha256((ROOT / 'research/cache/complete-temporal/zeta' / filename).read_bytes()).hexdigest(),
                       'distance_to_original_surface_mm': float(distance),
                       'nearest_original_triangle': int(triangle_id)})
assert len(checks) == 13
assert {m['c'] for m in data['markers']} == EXPECTED_CODES
for bone, suffixes in {'stapes': (34,35,36,37), 'incus': (39,40,41,42), 'malleus': (44,45,46,47,48)}.items():
    assert {m['c'] for m in data['markers'] if m['b']==bone} == {f'A15.3.02.{n:03d}' for n in suffixes}
actual_sha=hashlib.sha256((ROOT / 'site/skull-openear.glb').read_bytes()).hexdigest()
assert actual_sha==data['geometry_sha256']
report = {'tolerance_mm': .003,
          'native_published_geometry_sha256': actual_sha,
          'required_ta98_subterms': sorted(EXPECTED_CODES),
          'comparison_units': 'millimetres, to avoid metre-scale near-degeneracy tolerance in trimesh triangle projection',
          'anatomical_validity_not_proved_by_distance': True, 'checks': checks}
(ROOT / 'build_head/openear_landmarks/geometry-check.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'13 native OpenEar points checked; max original-surface distance {max(c["distance_to_original_surface_mm"] for c in checks):.6f} mm')
