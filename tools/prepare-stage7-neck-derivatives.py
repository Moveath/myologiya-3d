"""Research derivatives only: corner normals and exact connected components.

No anatomical admission, moving vertices, healing faces or editing original files.
The two C1/C2-adjacent fragments are retained in the source and review manifest.
"""
import hashlib
import json
import pathlib
import sys

import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from geometry_export_guard import stable_vertex_normals

PREVIOUS = ROOT / 'research/evidence-runs/stage7-muscle-recovery-2026-10-21T09-59-41-337Z-J0c1JT'
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(run):
    out = ROOT / 'build_stage7/neck_review_v2'
    out.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((PREVIOUS / 'muscle-inventory-after.json').read_text())
    unchanged = {p: sha(ROOT / p) == h for p, h in inventory['hashes'].items()}
    assert all(unchanged.values()), 'Prior inventory changed; reassess before reuse'
    with (run / 'baseline.json').open('x', encoding='utf8') as f:
        json.dump(dict(hashes=inventory['hashes'], reusedEvidence=str(PREVIOUS.relative_to(ROOT)),
                       matches=unchanged, boneNoModel=inventory['boneNoModel']), f, indent=2)
    records = []

    def export(name, mesh, source, expected, method, **extra):
        scene = trimesh.Scene()
        scene.add_geometry(mesh, node_name=name, geom_name=name)
        data = scene.export(file_type='glb')
        target = out / (name + '.glb')
        if target.exists():
            assert target.read_bytes() == data, 'Refuse to overwrite changed derivative'
        else:
            target.write_bytes(data)
        loaded = trimesh.load(target, force='mesh', process=False)
        assert np.array_equal(loaded.triangles, expected.astype(np.float32).astype(float))
        assert np.isfinite(loaded.vertex_normals).all()
        assert np.allclose(np.linalg.norm(loaded.vertex_normals, axis=1), 1, atol=1e-6)
        assert not np.any(np.all(np.cross(loaded.triangles[:,1]-loaded.triangles[:,0],
                                         loaded.triangles[:,2]-loaded.triangles[:,0]) == 0, axis=1))
        records.append(dict(id=name, source=source, file=target.relative_to(ROOT).as_posix(),
                            sha256=sha(target), triangles=len(loaded.faces),
                            vertices=len(loaded.vertices), method=method,
                            admission='research_only', license='CC BY-SA 2.1 Japan',
                            author='The Database Center for Life Science (DBCLS)',
                            bounds=loaded.bounds.tolist(), **extra))

    for fid in ['FMA71309', 'FMA71442', 'FMA71443']:
        src = ROOT / 'research/cache/stage7-sources' / (fid + '.obj')
        origin = json.loads((PREVIOUS / (fid + '-source.json')).read_text())
        assert sha(src) == origin['sha256']
        raw = trimesh.load(src, force='mesh', process=False)
        v = raw.vertices @ R.T / 1000
        unique, inverse = np.unique(v, axis=0, return_inverse=True)
        faces = inverse[raw.faces]
        if fid != 'FMA71309':
            # Independent corner vertices avoid cancellation on oppositely wound
            # thin plates. Keep every triangle and its winding, including defects.
            corners = v[raw.faces].reshape(-1, 3)
            t = corners.reshape(-1, 3, 3)
            cross = np.cross((t[:,1]-t[:,0])*1000, (t[:,2]-t[:,0])*1000)
            lengths = np.linalg.norm(cross, axis=1)
            assert np.all(lengths > 0)
            normals = np.repeat(cross / lengths[:,None], 3, axis=0)
            mesh = trimesh.Trimesh(corners, np.arange(len(corners)).reshape(-1,3),
                                   vertex_normals=normals, process=False)
            try:
                stable_vertex_normals(unique, faces)
                original_error = None
            except ValueError as e:
                original_error = str(e)
            assert original_error is not None, 'Expected defect must be reproducible'
            export(fid + '-corner-normals', mesh, origin, v[raw.faces],
                   'Independent per-corner flat normals; exact triangle coordinates/order/winding; no face removal, welding, smoothing or healing.',
                   originalSmoothNormalFailure=original_error,
                   unresolved=['segment identity', 'thin plates', 'self intersections',
                               'posterior medial/lateral boundary' if fid == 'FMA71443' else 'attachment boundaries'])
        else:
            mesh = trimesh.Trimesh(unique, faces, process=False)
            edges = mesh.edges_unique
            graph = coo_matrix((np.ones(len(edges)), (edges[:,0],edges[:,1])), shape=(len(unique),)*2)
            count, labels = connected_components(graph, directed=False)
            components = []
            for label in range(count):
                indices = np.where(labels[faces[:,0]] == label)[0]
                coords = unique[np.unique(faces[indices])]
                components.append(dict(sourceFaceIndices=indices.tolist(),
                                       center=coords.mean(0).tolist(), bounds=[coords.min(0).tolist(), coords.max(0).tolist()]))
            components.sort(key=lambda c: -c['bounds'][1][1])
            assert count == 12
            # Explicit reviewed component identities, not coordinate clipping.
            # Endpoint evidence was computed in the earlier run; now reused.
            ends = json.loads((PREVIOUS/'neck-endpoint-diagnostics.json').read_text())['rows']
            assert all(np.allclose(c['bounds'],e['bounds']) for c,e in zip(components, ends))
            for i, c in enumerate(components):
                c['reviewIndex'] = i
                c['nearestEndpointBones'] = {k:v[0] for k,v in ends[i]['ends'].items()}
                c['decision'] = 'excluded-C1-C2-adjacent' if i < 2 else 'candidate-only-C2-C7'
                c['sideCandidate'] = 'right' if c['center'][0] < 0 else 'left'
            for side in ['right', 'left']:
                selected = [c for c in components[2:] if c['sideCandidate'] == side]
                assert len(selected) == 5
                indices = np.sort(np.concatenate([c['sourceFaceIndices'] for c in selected]))
                # Compact only the unused vertices; retains exact per-face corners.
                used, inv = np.unique(faces[indices], return_inverse=True)
                m = trimesh.Trimesh(unique[used], inv.reshape(-1,3), process=False)
                m.vertex_normals = stable_vertex_normals(m.vertices, m.faces)
                export('interspinales-candidate-'+side, m, origin, v[raw.faces][indices],
                       'Five unchanged disconnected components; excluded upper two fragments; compacted unused vertices only. Level labels provisional, not attachment proof.',
                       sourceFaceIndices=indices.tolist(), components=[c['reviewIndex'] for c in selected],
                       unresolved=['individual attachment boundaries', 'C7-T1 pair absent from source', 'C1-C2 fragments excluded, not relabelled'])
            with (run/'interspinales-components.json').open('x',encoding='utf8') as f:
                json.dump(components,f,indent=2)
        assert sha(src) == origin['sha256']
    with (run/'derivatives.json').open('x',encoding='utf8') as f:
        json.dump(records,f,ensure_ascii=False,indent=2)
    print(json.dumps([dict(id=r['id'],triangles=r['triangles'],admission=r['admission']) for r in records]))


if __name__ == '__main__':
    prepare(pathlib.Path(sys.argv[1]).resolve())
