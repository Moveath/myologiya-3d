"""Scale-stable normals and bone export checks; never repairs source topology."""
import numpy as np
import trimesh
import io


def stable_vertex_normals(vertices, faces):
    vertices = np.asarray(vertices, dtype=np.float64)
    if not np.isfinite(vertices).all():
        raise ValueError('Non-finite mesh coordinates')
    # Trimesh's absolute tolerances are unsafe for tiny triangles in metres.
    # Compute on a temporary, rebased millimetre copy, without changing faces.
    probe = trimesh.Trimesh(vertices=(vertices-vertices.mean(axis=0))*1000,
                            faces=faces, process=False)
    normals = np.asarray(probe.vertex_normals).copy()
    t = probe.triangles
    good = np.any(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]) != 0, axis=1)
    used = np.unique(np.asarray(faces)[good])
    if np.any(np.abs(np.linalg.norm(normals[used],axis=1)-1) > 1e-6):
        raise ValueError('Undefined normals on nondegenerate faces; inspect source before export')
    return normals


def bone_mesh(vertices, faces):
    """Exact welding only: never round positions or discard bone triangles."""
    unique, inverse = np.unique(vertices,axis=0,return_inverse=True)
    mesh = trimesh.Trimesh(vertices=unique,faces=inverse[faces],process=False)
    mesh.vertex_normals = stable_vertex_normals(mesh.vertices,mesh.faces)
    return mesh


def validate_bone_roundtrip(scene, exported):
    """Check each bone's face order/corners after float32 GLB serialization."""
    loaded = trimesh.load(io.BytesIO(exported),file_type='glb',force='scene',process=False)
    for name, source in scene.geometry.items():
        if not name.startswith('b|'):
            continue
        if name not in loaded.geometry:
            raise ValueError(f'{name}: lost bone during export')
        actual = loaded.geometry[name]
        if len(source.faces) != len(actual.faces):
            raise ValueError(f'{name}: bone triangle count changed')
        expected = source.triangles.astype(np.float32).astype(np.float64)
        if not np.array_equal(actual.triangles,expected):
            raise ValueError(f'{name}: bone triangle coordinates/order changed')
        def zero(t):
            return np.all(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]) == 0,axis=1)
        if np.any(zero(actual.triangles) & ~zero(source.triangles)):
            raise ValueError(f'{name}: float32 export collapsed a bone triangle')
