"""Topography review of the decimated abdominal muscles (ABD-MUSCLES) against the bones of the atlas.

Each side is its own BodyParts3D source (no mirroring). Bones come from the atlas geometry cache
(tools/export-atlas-geometry.mjs: trunk = ribs, sternum, costal cartilages; leg = L1-L5, sacrum, hip
bones), whose source hashes are checked first. All sections share the BodyParts3D frame.
Checks per muscle: technical mesh state; side; reflected-pair similarity (diagnostic); proximity to the
bones named by the card sources; depth of vertices inside bones; and, for the three flat muscles,
their layer order around the body axis (external > internal > transversus).
v2 (abdomen-topography-v2.json) reviews the mesh exactly as published (abdomen_muscles.published_mesh:
no zero-volume flaps or unused vertices), measures bone depth only within 10 mm of a bone surface and
compares every entry >2 mm with the original STL: an entry already present in the source is recorded,
not corrected. v1 (abdomen-topography.json) used the raw decimated arrays and a 30 mm window; v2 kept one
zero-area opposite-winding pair of the right rectus whose vertices other specks also use. v3
(abdomen-topography-v3.json) reviews the mesh after the generalised flap rule of published_mesh.
Usage: python verify/verify_abdomen_muscles.py RUN
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'scripts'))
from abdomen_muscles import published_mesh

run = Path(sys.argv[1]).resolve()
CONTACT_MM, INSIDE_MM, WINDOW_M, SOURCE_MARGIN_MM = 5.0, 2.0, 0.01, 0.5
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)
read = lambda name: json.loads((run / name).read_text(encoding='utf8'))
targets = read('decimation-targets.json')
decimated = {r['fma']: r for r in read('blender-decimation.json')['rows']}
# Bones named by the attachment fields (Kenhub/UAMS/Loyola/Gray), per side; '' = unpaired.
EXPECTED = {
    'abdomen_rectus_abdominis': ['hip_bone', 'sternum', 'costal_cartilages'],
    'abdomen_pyramidalis': ['hip_bone'],
    'abdomen_obliquus_externus_abdominis': ['rib_5', 'rib_6', 'rib_7', 'rib_8', 'rib_9', 'rib_10', 'rib_11', 'rib_12', 'hip_bone'],
    'abdomen_obliquus_internus_abdominis': ['hip_bone', 'rib_10', 'rib_11', 'rib_12', 'costal_cartilages'],
    'abdomen_transversus_abdominis': ['costal_cartilages', 'hip_bone'],
    'abdomen_quadratus_lumborum': ['rib_12', 'lumbar_1', 'lumbar_2', 'lumbar_3', 'lumbar_4', 'hip_bone'],
}


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
    return nodes, [s['sha256'] for s in index['sources']]


def merged(chunks):
    vs, fs, off = [], [], 0
    for v, f in chunks:
        vs.append(v); fs.append(f + off); off += len(v)
    return np.vstack(vs), np.vstack(fs)


def components(mesh):
    return len(trimesh.graph.connected_components(mesh.face_adjacency, nodes=np.arange(len(mesh.faces)), engine='scipy'))


class Bone:
    """Dense surface sample with outward normals: nearest-sample distance and signed depth."""
    def __init__(self, v, f):
        mesh = trimesh.Trimesh(v, f, process=False)
        points, faces = trimesh.sample.sample_surface_even(mesh, max(20000, len(f) * 2), seed=1)
        self.points, self.normals = np.vstack([points, mesh.vertices]), np.vstack([mesh.face_normals[faces], mesh.vertex_normals])
        self.tree = cKDTree(self.points)

    def query(self, p):
        d, i = self.tree.query(p)
        return d, np.einsum('ij,ij->i', p - self.points[i], self.normals[i])

    def depth(self, p):
        d, signed = self.query(p)
        inside = (signed < 0) & (d < WINDOW_M)
        return (round(float(-signed[inside].min() * 1000), 2) if inside.any() else 0.0,
                int((inside & (-signed > INSIDE_MM / 1000)).sum()), d)


trunk, trunk_hash = section('trunk')
leg, leg_hash = section('leg')
bones = {}
for nodes, sec in ((trunk, 'trunk'), (leg, 'leg')):
    for name, chunks in nodes.items():
        kind, key = name.split('|')[:2]
        if kind not in ('b', 'o') or key.startswith(('toe', 'metatarsal', 'cunei', 'navicular', 'cuboid', 'talus', 'calcaneus', 'tibia', 'fibula', 'patella', 'femur', 'sesamoid')):
            continue
        if kind == 'o' and not key.startswith('thorax_costal_cartilages'):
            continue
        key = key.replace('thorax_costal_cartilages', 'costal_cartilages')
        side = 'left' if key.endswith('_left') else 'right' if key.endswith('_right') or key in ('hip_bone',) else ''
        base = key.removesuffix('_left').removesuffix('_right')
        bones.setdefault((base, side), []).extend(chunks)
bones = {k: Bone(*merged(c)) for k, c in bones.items()}
# Body axis for the layer test: the centre of the L3 vertebral body region (x, z) of the atlas.
l3 = merged(leg['b|lumbar_3'])[0]
axis = np.array([np.median(l3[:, 0]), np.median(l3[:, 2])])

meshes, flaps, rows = {}, {}, []
for t in targets:
    data = np.load(root / decimated[t['fma']]['output'])
    meshes[t['id']], flaps[t['id']] = published_mesh(data['vertices'], data['faces'])
for t in targets:
    key, side = t['id'].rsplit('_', 1)
    mesh = meshes[t['id']]
    weld = mesh.copy()
    weld.merge_vertices()
    labels = trimesh.graph.connected_component_labels(weld.face_adjacency, node_count=len(weld.faces))
    sign = -1 if side == 'right' else 1  # body right is -x
    source = None
    other = meshes[key + '_' + ('left' if side == 'right' else 'right')]
    mirrored = other.vertices * np.array([-1, 1, 1])
    d_ab, d_ba = cKDTree(mirrored).query(mesh.vertices)[0], cKDTree(mesh.vertices).query(mirrored)[0]
    contacts, depths = {}, {}
    for (base, s), bone in bones.items():
        if s not in (side, ''):
            continue
        depth, count, d = bone.depth(mesh.vertices)
        if d.min() * 1000 <= 30:
            contacts[base] = round(float(d.min() * 1000), 2)
        if count:
            if source is None:  # original STL in the same frame, for entries that might be inherited
                stl = trimesh.load(root / 'research/cache/abdomen-muscles' / (t['fma'] + '.stl'), process=False)
                source = np.unique(stl.vertices, axis=0) @ R.T / 1000.0
            source_depth, source_count, _ = bone.depth(source)
            depths[base] = dict(maxDepthMM=depth, verticesDeeperThan2mm=count, ofVertices=len(mesh.vertices),
                                sourceMaxDepthMM=source_depth, sourceVerticesDeeperThan2mm=source_count, ofSourceVertices=len(source),
                                inheritedFromSource=source_depth >= depth - SOURCE_MARGIN_MM and source_count > 0)
    expected = EXPECTED[key]
    missing = [b for b in expected if contacts.get(b, 99) > CONTACT_MM]
    deep = {b: v for b, v in depths.items() if not v['inheritedFromSource']}
    wrong = float((mesh.vertices[:, 0] * sign < -0.005).mean())
    r = dict(id=t['id'], fma=t['fma'], triangles=len(mesh.faces), sourceTriangles=t['sourceTriangles'],
             finite=bool(np.isfinite(mesh.vertices).all()), degenerateFaces=int((mesh.area_faces < 1e-12).sum()),
             removedDecimationFlapTriangles=flaps[t['id']],
             components=components(weld), componentFaces=sorted(np.bincount(labels).tolist(), reverse=True)[:6],
             watertight=bool(weld.is_watertight),
             centroidMM=(mesh.vertices.mean(0) * 1000).round(1).tolist(), extentsMM=(mesh.extents * 1000).round(1).tolist(),
             fractionBeyondMidline5mm=round(wrong, 4),
             pairMedianDistanceMM=round(float(np.median(np.concatenate([d_ab, d_ba])) * 1000), 2),
             pairP95DistanceMM=round(float(np.percentile(np.concatenate([d_ab, d_ba]), 95) * 1000), 2),
             pairExtentRatio=(mesh.extents / (mirrored.max(0) - mirrored.min(0))).round(3).tolist(),
             contactsMM=contacts, expectedBones=expected, missingExpectedContacts=missing, boneDepth=depths,
             boneEntryNotInSource=sorted(deep))
    r['technical'] = r['finite'] and not r['degenerateFaces']
    r['side'] = (mesh.vertices[:, 0].mean() * sign > 0) and wrong < 0.01
    r['relation'] = not missing
    r['noDeepBoneEntry'] = not deep
    rows.append(r)

# Layer order of the flat muscles: angular x height bins around the body axis, median radius per muscle.
layers = {}
for side in ('right', 'left'):
    parts = [meshes[f'abdomen_{k}_{side}'] for k in ('obliquus_externus_abdominis', 'obliquus_internus_abdominis', 'transversus_abdominis')]
    binned = []
    for m in parts:
        v = m.vertices
        ang = np.degrees(np.arctan2(v[:, 0] - axis[0], v[:, 2] - axis[1]))
        rad = np.hypot(v[:, 0] - axis[0], v[:, 2] - axis[1])
        keys = np.stack([np.floor(ang / 10), np.floor(v[:, 1] / 0.02)], 1).astype(int)
        cells = {}
        for k, rr in zip(map(tuple, keys), rad):
            cells.setdefault(k, []).append(rr)
        binned.append({k: float(np.median(x)) for k, x in cells.items() if len(x) >= 5})
    shared = set(binned[0]) & set(binned[1]) & set(binned[2])
    ordered = [k for k in shared if binned[0][k] > binned[1][k] > binned[2][k]]
    layers[side] = dict(sharedCells=len(shared), orderedCells=len(ordered),
                        fraction=round(len(ordered) / max(1, len(shared)), 3),
                        medianGapExternalInternalMM=round(float(np.median([binned[0][k] - binned[1][k] for k in shared])) * 1000, 2),
                        medianGapInternalTransversusMM=round(float(np.median([binned[1][k] - binned[2][k] for k in shared])) * 1000, 2))
for r in rows:
    key, side = r['id'].rsplit('_', 1)
    r['layerOrder'] = layers[side]['fraction'] >= 0.8 if key in ('abdomen_obliquus_externus_abdominis', 'abdomen_obliquus_internus_abdominis', 'abdomen_transversus_abdominis') else None
    r['passed'] = r['technical'] and r['side'] and r['relation'] and r['noDeepBoneEntry'] and r['layerOrder'] is not False

result = dict(contactThresholdMM=CONTACT_MM, insideThresholdMM=INSIDE_MM, geometryCache=dict(trunk=trunk_hash, leg=leg_hash),
              bodyAxisMM=(axis * 1000).round(1).tolist(),
              rule=('technical (finite, no degenerate faces) + side (centroid on its side, <1% of vertices >5 mm past the midline) '
                    '+ every bone named by the attachment fields within 5 mm + no vertices >2 mm inside a bone (within 10 mm of its surface) '
                    'unless the original STL has the same entry (recorded, not corrected) '
                    '+ flat muscles: external > internal > transversus radius in >=80% of shared 10 deg x 2 cm cells'),
              limitation=('Proximity, side and layer order show gross identity and topography only; attachment areas, aponeurotic '
                          'boundaries (how far each source mesh includes the aponeurosis is not established), '
                          'fibre directions and the rectus sheath are not accepted. Costal cartilages of the atlas are partial aggregates.'),
              layers=layers, muscles=rows, passed=sum(r['passed'] for r in rows), total=len(rows))
with (run / 'abdomen-topography-v3.json').open('x', encoding='utf8') as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
sys.stdout.reconfigure(encoding='utf-8')
print(json.dumps(dict(passed=result['passed'], total=result['total'], layers=layers, rows=[
    (r['id'], r['passed'], r['componentFaces'], r['removedDecimationFlapTriangles'], r['fractionBeyondMidline5mm'], r['pairMedianDistanceMM'],
     r['missingExpectedContacts'], r['boneEntryNotInSource'], {b: (v['maxDepthMM'], v['verticesDeeperThan2mm'], v['sourceMaxDepthMM']) for b, v in r['boneDepth'].items()}, {k: v for k, v in r['contactsMM'].items() if v <= 10}) for r in rows]), ensure_ascii=False, indent=0))
