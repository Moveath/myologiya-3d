"""Bounded source-preserving omohyoid shape diagnostic, not an anatomical mask.

Usage: .venv/Scripts/python.exe verify/diagnose_omohyoid_parts.py <new evidence dir>
Longitudinal positions are intrinsic edge-distance coordinates. Cross-sections
are level sets of that coordinate, not planes selected to manufacture bellies.
Neither a narrow section nor a change of direction identifies tendon tissue.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import manifest_neck


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph(v, f):
    edges = np.sort(np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), axis=1)
    edges = np.unique(edges, axis=0)
    weights = np.linalg.norm(v[edges[:, 0]] - v[edges[:, 1]], axis=1)
    return coo_matrix((np.r_[weights, weights], (np.r_[edges[:, 0], edges[:, 1]], np.r_[edges[:, 1], edges[:, 0]])), shape=(len(v), len(v))).tocsr()


def contours(v, f, t, level):
    segments = []
    for face in f[(t[f].min(axis=1) < level) & (t[f].max(axis=1) > level)]:
        p = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            a, b = face[i], face[j]
            if (t[a] - level) * (t[b] - level) < 0:
                alpha = (level - t[a]) / (t[b] - t[a])
                p.append(v[a] + alpha * (v[b] - v[a]))
        if len(p) == 2:
            segments.append(p)
    seg = np.array(segments)
    if not len(seg):
        return None
    points, index = np.unique(np.round(seg.reshape(-1, 3), 7), axis=0, return_inverse=True)
    edges = index.reshape(-1, 2)
    adjacency = coo_matrix((np.ones(len(edges) * 2), (edges.T.ravel(), edges[:, ::-1].T.ravel())), shape=(len(points), len(points))).tocsr()
    n_components, labels = connected_components(adjacency)
    center = points.mean(axis=0)
    _, _, vh = np.linalg.svd(points - center, full_matrices=False)
    uv = (points - center) @ vh[:2].T
    ranges = np.ptp(uv, axis=0)
    perimeter = np.linalg.norm(seg[:, 1] - seg[:, 0], axis=1).sum()
    # Oriented area requires ordered loops: report only stable width/perimeter.
    return dict(level=float(level), center_mm=center.tolist(), widths_mm=ranges.tolist(), perimeter_mm=float(perimeter),
                loops=int(n_components), all_degree_two=bool(np.all(np.diff(adjacency.indptr) == 2)),
                out_of_plane_rms_mm=float(np.sqrt(np.mean(((points - center) @ vh[2]) ** 2))),
                segments_mm=seg.tolist())


def analyse(path, hyoid_points, name, mesh=None):
    if mesh is None:
        mesh = trimesh.load(path, force='mesh', process=True)
    v, f = np.asarray(mesh.vertices), np.asarray(mesh.faces)
    g = graph(v, f)
    nc, labels = connected_components(g)
    face_labels = labels[f[:, 0]]
    counts = np.bincount(face_labels)
    keep = f[face_labels == counts.argmax()]
    ids, inverse = np.unique(keep, return_inverse=True)
    v, f = v[ids], inverse.reshape(-1, 3)
    g = graph(v, f)
    nearest, _ = cKDTree(hyoid_points).query(v)
    a = int(nearest.argmin())
    da = dijkstra(g, indices=a)
    b = int(da.argmax())
    db = dijkstra(g, indices=b)
    length = da[b]
    t = (da - db + length) / (2 * length)
    profiles = [contours(v, f, t, float(s)) for s in np.arange(.025, .976, .025)]
    profiles = [x for x in profiles if x]
    inside = [x for x in profiles if .2 <= x['level'] <= .8]
    ranked = sorted(inside, key=lambda x: x['perimeter_mm'])
    minima = [profiles[i] for i in range(1, len(profiles)-1) if .15 <= profiles[i]['level'] <= .85 and profiles[i]['perimeter_mm'] < min(profiles[i-1]['perimeter_mm'], profiles[i+1]['perimeter_mm'])]
    return dict(name=name, source=str(path.relative_to(ROOT)), source_sha256=sha(path), source_vertices=len(mesh.vertices), source_triangles=len(mesh.faces),
                components_face_counts=sorted(counts.tolist(), reverse=True), used_triangles=len(f),
                endpoint_method='Nearest source vertex to hyoid mesh, then farthest intrinsic vertex; not validated attachment labels',
                superior_endpoint_mm=v[a].tolist(), opposite_endpoint_mm=v[b].tolist(), closest_hyoid_vertex_distance_mm=float(nearest[a]),
                max_edge_distance_mm=float(length), material_tissue_labels=False,
                candidate_internal_minimum={k: val for k,val in ranked[0].items() if k != 'segments_mm'},
                internal_local_minima=[{k: val for k,val in x.items() if k != 'segments_mm'} for x in minima],
                profiles=profiles, vertices_mm=v.tolist(), faces=f.tolist(), longitudinal_coordinate=t.tolist(),
                anatomical_mask_admitted=False, limitation='Shape extrema do not identify myotendinous boundaries. No donor-specific tendon label, texture or volume segmentation is available.')


def main():
    run = Path(sys.argv[1]).resolve()
    if not run.is_relative_to(ROOT / 'research' / 'evidence-runs'):
        raise ValueError('Use an allocated evidence run')
    hpath = ROOT / 'stl_neck' / (manifest_neck.BONES['hyoid'][0] + '.stl')
    h = trimesh.load(hpath, force='mesh')
    out = dict(method='intrinsic-level-set-profile-v1', units='BodyParts3D mm; original source orientation',
               hyoid_source=str(hpath.relative_to(ROOT)), hyoid_sha256=sha(hpath), rows=[])
    for side in ('right', 'left'):
        name = 'omohyoid_' + side
        path = ROOT / 'stl_neck' / (manifest_neck.MUSCLES[name][0][0] + '.stl')
        out['rows'].append(analyse(path, h.vertices, name))
    target = run / 'source-shape-profiles.json'
    with target.open('x', encoding='utf8') as stream:
        json.dump(out, stream, ensure_ascii=False, separators=(',', ':'))
    concise = {**out, 'rows': [{k:v for k,v in row.items() if k not in ('profiles', 'vertices_mm', 'faces', 'longitudinal_coordinate')} for row in out['rows']]}
    with (run / 'shape-summary.json').open('x', encoding='utf8') as stream:
        json.dump(concise, stream, ensure_ascii=False, indent=2)
    print(json.dumps(concise, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
