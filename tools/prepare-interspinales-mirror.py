"""Research-only reflection of the admitted right cervical group; no production writes."""
import hashlib
import json
import pathlib
import sys

import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUN = pathlib.Path(sys.argv[1]).resolve()
OUT = ROOT / 'build_stage7/interspinales_mirror_v1'
OUT.mkdir(exist_ok=False)
PREVIOUS = ROOT / 'research/evidence-runs/stage7-muscle-recovery-2026-10-21T09-59-41-337Z-J0c1JT'
source = ROOT / 'site/models/bodyparts3d-3.0/neck-stage7/interspinales_cervicis_right.glb'
left_source = ROOT / 'build_stage7/neck_review_v2/interspinales-candidate-left.glb'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
provenance = json.loads((source.parent / 'provenance.json').read_text())
assert sha(source) == provenance['sha256']
inventory = json.loads((PREVIOUS / 'muscle-inventory-after.json').read_text())
assert sha(ROOT / 'site/neck-glb.txt') == inventory['hashes']['site/neck-glb.txt']
original = trimesh.load(source, force='mesh', process=False)
v = original.vertices.copy()
v[:, 0] *= -1
f = original.faces[:, [0, 2, 1]].copy()
n = original.vertex_normals.copy()
n[:, 0] *= -1
mirrored = trimesh.Trimesh(v, f, vertex_normals=n, process=False)
scene = trimesh.Scene()
owner = 'm|interspinales_cervicis_left|'
scene.add_geometry(mirrored, node_name=owner, geom_name=owner)
target = OUT / 'interspinales_cervicis_left-mirrored-trial.glb'
with target.open('xb') as h:
    h.write(scene.export(file_type='glb'))
back = trimesh.load(target, force='mesh', process=False)
assert np.array_equal(back.faces, f)
assert np.array_equal(back.vertices, v.astype(np.float32).astype(float))
assert np.allclose(back.vertex_normals, n, atol=1e-7)
assert np.allclose(back.area, original.area, rtol=1e-12)
assert np.isclose(back.volume, original.volume, rtol=1e-12)
assert back.is_winding_consistent and back.is_watertight
assert (back.vertices[:, 0] > 0).all()
edges = back.edges_unique
graph = coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(len(v),) * 2)
count, labels = connected_components(graph, directed=False)
assert count == 5
components = []
for label in range(count):
    ids = np.where(labels[back.faces[:, 0]] == label)[0]
    points = back.vertices[np.unique(back.faces[ids])]
    components.append(dict(faceIndices=ids.tolist(), bounds=[points.min(0).tolist(), points.max(0).tolist()], center=points.mean(0).tolist()))
components.sort(key=lambda c: -c['bounds'][1][1])
for i, c in enumerate(components):
    c['provisionalLevel'] = f'C{i+2}-C{i+3}'
checks = dict(exactReflectedVertices=True, reverseWinding=True, reflectedNormals=True,
              areaPreserved=True, signedVolumePreserved=True, watertight=True,
              windingConsistent=True, fiveComponents=True, allVerticesOnLeft=True,
              originalSourceUnchanged=sha(source) == provenance['sha256'],
              currentNeckContextHashMatches=True)
record = dict(id='interspinales-mirror-candidate-left', file=target.relative_to(ROOT).as_posix(),
              sourceFile=source.relative_to(ROOT).as_posix(), sourceSHA256=sha(source), sha256=sha(target),
              sourceProvenance=provenance, originalLeftTestFile=left_source.relative_to(ROOT).as_posix(),
              originalLeftTestSHA256=sha(left_source), triangles=len(back.faces), vertices=len(back.vertices),
              components=components, checks=checks, plane=dict(axis='X', offset=0, units='metres',
              basis='BodyParts3D/atlas coordinate convention; prior stage6 plane screen. Not independently segmented patient midsagittal plane.'),
              method='x -> -x, winding [0,2,1], normal x -> -x; exact admitted right subset; no translation, scaling, deformation, pin modification or new fascicles.',
              admission='research_only_not_admitted', license='CC BY-SA 2.1 Japan', author='DBCLS',
              notice='Mirrored educational candidate, five C2-C7 bundles only. C7-T1 absent; exact attachment boundaries and individual asymmetry not accepted.',
              reusedContext=str((PREVIOUS / 'context-arrays.json').relative_to(ROOT)))
with (RUN / 'mirror-preparation.json').open('x', encoding='utf8') as h:
    json.dump(record, h, ensure_ascii=False, indent=2)
with (OUT / 'provenance.json').open('x', encoding='utf8') as h:
    json.dump(record, h, ensure_ascii=False, indent=2)
with (OUT / 'ATTRIBUTION.txt').open('x', encoding='utf8') as h:
    h.write('BodyParts3D 3.0, archive 20110915, OBJ95%, FMA71309. Copyright DBCLS.\n'
            'Derivative by Myology 3D, 2026-10-22: exact reflection of five admitted right components, reversed winding and reflected normals.\n'
            'CC BY-SA 2.1 Japan: https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en\n'
            'Source terms: https://lifesciencedb.jp/bp3d/info_en/license/index.html\n'
            'Attribution and ShareAlike apply to distribution and adaptation; commercial use subject to licence.\n'
            'RESEARCH ONLY, not anatomical admission. Original data untouched. C7-T1 absent.\n')
print(json.dumps(dict(file=record['file'], sha256=record['sha256'], triangles=len(back.faces), checks=len(checks))))
