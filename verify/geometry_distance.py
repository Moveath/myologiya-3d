"""Stable surface queries for atlas inputs in metres; report distances in mm.

Trimesh's closest-point algorithm uses absolute numerical tolerances. On small
triangles, querying in metres can classify an interior point as an edge point.
Rebase and scale only an in-memory query copy; preserve faces and source arrays.
"""
import numpy as np
import trimesh


class SurfaceQuery:
    def __init__(self, mesh):
        self.origin = np.asarray(mesh.bounds, dtype=np.float64).mean(axis=0)
        self.mesh_mm = trimesh.Trimesh(
            vertices=(np.asarray(mesh.vertices, dtype=np.float64) - self.origin) * 1000,
            faces=np.asarray(mesh.faces).copy(), process=False)

    def closest(self, points_m):
        points_mm = (np.asarray(points_m, dtype=np.float64) - self.origin) * 1000
        closest_mm, distance_mm, triangles = trimesh.proximity.closest_point_naive(
            self.mesh_mm, points_mm)
        return closest_mm / 1000 + self.origin, distance_mm, triangles
