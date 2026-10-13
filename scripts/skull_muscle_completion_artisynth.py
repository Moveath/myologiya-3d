"""Download and inspect authored ArtiSynth face elements; never infer TA98 parts.

Outputs stay in ignored build_head/muscle_completion. This is a source review,
not an accepted replacement for the atlas's missing anatomical geometry.
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/new-muscles/artisynth'
OUT = ROOT / 'build_head/muscle_completion'
COMMIT = 'e37be3f1b4831f347c055cbf7124b6bd57414f98'
BASE = f'https://raw.githubusercontent.com/artisynth/artisynth_models/{COMMIT}/'
GEOM = 'src/artisynth/models/face/geometry/refmodel/'
FILES = ['LICENSE', 'README', 'src/artisynth/models/face/BadinFaceDemo.java',
         'src/artisynth/models/face/RefFemMuscleFaceDemo.java'] + [
             GEOM + n for n in ['newface.node', 'newface.elem',
                                 'OOM_active_node.node', 'OOM_active_elements.elem',
                                 'OOP_active_node.node', 'OOP_active_elements.elem']]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def nodes(path):
    # ANSYS fixed-width output may place the node id next to a negative value.
    rows = [[float(v) for v in re.findall(r'[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?', line)]
            for line in path.read_text().splitlines() if line.strip()]
    assert all(len(row) == 4 for row in rows)
    result = {int(row[0]): np.asarray(row[1:]) for row in rows}
    assert len(rows) == len(result)
    return result


def boundary(node_map, element_rows):
    """Boundary of the exact supplied 8-node solids, including collapsed cells."""
    # ANSYS SOLID45 corner ordering; repeated corners encode wedge/pyramid cells.
    hex_faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
                 (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    face_map = defaultdict(list)
    for row in element_rows:
        ids = [int(x) for x in row[:8]]
        assert all(n in node_map for n in ids), (row[-1], ids)
        center = np.mean([node_map[n] for n in dict.fromkeys(ids)], axis=0)
        for face in hex_faces:
            poly = list(dict.fromkeys(ids[k] for k in face))
            if len(poly) < 3:
                continue
            coords = np.array([node_map[n] for n in poly])
            normal = np.cross(coords[1] - coords[0], coords[2] - coords[0])
            if np.dot(normal, coords.mean(axis=0) - center) < 0:
                poly.reverse()
            face_map[tuple(sorted(poly))].append(poly)
    assert all(len(x) <= 2 for x in face_map.values()), 'non-manifold cell adjacency'
    outside = [v[0] for v in face_map.values() if len(v) == 1]
    used = sorted({i for p in outside for i in p})
    lookup = {n: i for i, n in enumerate(used)}
    vertices_mm = np.array([node_map[n] for n in used])
    # Axis rotation only; retain the source frame, never register/mirror to BP3D.
    vertices = vertices_mm[:, [0, 2, 1]] * [0.001, 0.001, -0.001]
    triangles = []
    for p in outside:
        for i in range(1, len(p) - 1):
            tri = [lookup[p[0]], lookup[p[i]], lookup[p[i + 1]]]
            v = vertices[tri]
            if np.linalg.norm(np.cross(v[1]-v[0], v[2]-v[0])) > 1e-15:
                triangles.append(tri)
    mesh = trimesh.Trimesh(vertices=vertices, faces=triangles, process=False)
    return mesh, used


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source_files = []
    for rel in FILES:
        path = CACHE / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(urllib.request.urlopen(BASE + rel, timeout=60).read())
        b = path.read_bytes()
        source_files.append({'path': str(path.relative_to(ROOT)).replace('\\', '/'),
                             'url': BASE + rel, 'bytes': len(b), 'sha256': sha(b)})
    scene = trimesh.Scene()
    review = []
    element_sets = {}
    reference_nodes = nodes(CACHE / GEOM / 'newface.node')
    for name, color in [('face_context', [190, 192, 204, 95]),
                        ('OOM', [231, 111, 81, 255]), ('OOP', [57, 166, 155, 255])]:
        if name == 'face_context':
            npth, epth = CACHE / GEOM / 'newface.node', CACHE / GEOM / 'newface.elem'
        else:
            npth = CACHE / GEOM / (name + '_active_node.node')
            epth = CACHE / GEOM / (name + '_active_elements.elem')
        nm = nodes(npth)
        max_node_difference = max(float(np.linalg.norm(p-reference_nodes[n])) for n, p in nm.items())
        assert max_node_difference == 0, 'active source node differs from reference model'
        rows = np.loadtxt(epth, dtype=int)
        # The OOM export includes 151 four-node auxiliary elements (zero padding).
        # They are not solid muscle volume and are not converted to artificial bulk.
        solids = rows[np.all(rows[:, :8] != 0, axis=1)]
        element_sets[name] = set(int(x) for x in solids[:, -1])
        mesh, original_ids = boundary(nm, solids)
        mesh.visual.face_colors = color
        scene.add_geometry(mesh, node_name=name, geom_name=name)
        review.append({'id': name, 'source_node_file': npth.name,
                       'source_element_file': epth.name,
                       'input_nodes': len(nm), 'input_elements': len(rows),
                       'included_solid_elements': len(solids),
                       'excluded_zero_padded_auxiliary_elements': len(rows)-len(solids),
                       'unique_corners': dict(Counter(len(set(r[:8])) for r in solids)),
                       'vertices': len(mesh.vertices), 'triangles': len(mesh.faces),
                       'watertight': mesh.is_watertight,
                       'winding_consistent': mesh.is_winding_consistent,
                       'max_difference_from_same_reference_node_mm': max_node_difference,
                       'bounds_m': mesh.bounds.tolist(),
                       'source_vertex_ids': original_ids,
                       'source_solid_element_ids': sorted(element_sets[name])})
    glb = scene.export(file_type='glb', include_normals=True)
    (OUT / 'artisynth-authored-elements.glb').write_bytes(glb)
    (OUT / 'LICENSE-ARTISYNTH.txt').write_text((CACHE/'LICENSE').read_text(), encoding='utf-8')
    report = {
        'reviewed': '2026-10-13', 'source': 'ArtiSynth Models / reference face',
        'source_commit': COMMIT, 'source_files': source_files,
        'license': 'ArtiSynth Models license: redistribution of code and data permitted, with notices and citation',
        'attribution': 'Contributing authors and organizations; reference face: Nazari, Perrier, Chabanas, Payan; ArtiSynth integration: Stavness, Flynn, Lloyd, Fels.',
        'citation': {'url': 'https://www.artisynth.org/Models/Citations',
                     'title': 'Stavness et al. (2014), Coupled Biomechanical Modeling of the Face, Jaw, Skull, Tongue, and Hyoid Bone, pp.253–274'},
        'anatomical_references': [
            {'url': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2631558/',
             'title': 'Rogers et al. (2009), Comparative microanatomy of the orbicularis oris muscle between chimpanzees and humans',
             'locator': 'Introduction, Fig.1; Results, Fig.2: anatomical marginalis and peripheralis layers; these do not establish the boundary of a given FE element set'},
            {'url': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5754395/',
             'title': 'Eskes et al. (2018), Simulation of facial expressions using person-specific sEMG signals controlling a biomechanical face model',
             'locator': 'Materials and methods, Biomechanical model: reference face and manually selected orbicularis muscle elements; OOP/OOM in muscle list'}],
        'method': 'Граница точных исходных объёмных элементов ANSYS; удалены общие внутренние грани, четырёхугольники триангулированы. Координаты [x,y,z] мм → [x,z,-y] м. Геометрия не сглажена, не отражена и не дополнена.',
        'finding': 'Источник содержит авторские конечные элементы OOM/OOP, а не две независимо сегментированные TA98-части. Форма мягких тканей опирается на КТ, мышечные пути и активные элементы заданы в биомеханической модели авторами. Списки OOM/OOP пересекаются; экспорт одного полулица не доказывает полноту мышцы.',
        'shared_solid_element_ids': sorted(element_sets['OOM'] & element_sets['OOP']),
        'ta98_parts_confirmed': [], 'published': False,
        'missing_atlas_records_closed': 0,
        'visual_review': {
            'date': '2026-10-13',
            'images': ['both_context_0_0_-1.png', 'OOM_0.35_0.2_-1.png', 'OOP_0.35_0.2_-1.png'],
            'finding': 'Осмотр совместно с исходной поверхностью лица и по отдельности: два блочных полукольца одного полулица; ступенчатые края соответствуют конечным элементам. Это не отдельные полные поверхности двух частей TA98.',
            'publication_decision': 'Локальный технический образец. Не добавлять как подтверждённые анатомические части в учебный атлас.'
        },
        'source_model_geometry_only': True,
        'model': {'path': str((OUT/'artisynth-authored-elements.glb').relative_to(ROOT)).replace('\\', '/'),
                  'sha256': sha(glb), 'bytes': len(glb)},
        'objects': review,
    }
    (OUT/'artisynth-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'objects': [{k: x[k] for k in ['id','vertices','triangles','watertight','winding_consistent']} for x in review],
                      'shared_OOM_OOP_elements': len(report['shared_solid_element_ids']),
                      'glb_bytes': len(glb)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
