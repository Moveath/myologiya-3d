"""Analytic regression for millimetre-scale features; no anatomical fixtures."""
import unittest
import numpy as np
import trimesh
from geometry_distance import SurfaceQuery


class SurfaceDistanceTests(unittest.TestCase):
    def setUp(self):
        self.mesh = trimesh.Trimesh(vertices=[[0, 0, 0], [.0001, 0, 0], [0, .0001, 0]],
                                    faces=[[0, 1, 2]], process=False)

    def test_interior_projection_uses_face_not_edge(self):
        closest, distances, faces = SurfaceQuery(self.mesh).closest([[.00002, .00002, .000001]])
        np.testing.assert_allclose(distances, [.001], atol=1e-10)
        np.testing.assert_allclose(closest, [[.00002, .00002, 0]], atol=1e-14)
        self.assertEqual(faces.tolist(), [0])

    def test_outside_projection_uses_edge(self):
        closest, distances, _ = SurfaceQuery(self.mesh).closest([[.00008, .00008, .000001]])
        np.testing.assert_allclose(closest, [[.00005, .00005, 0]], atol=1e-14)
        np.testing.assert_allclose(distances, [np.sqrt(2 * .03**2 + .001**2)], atol=1e-10)

    def test_world_translation_and_source_arrays_preserved(self):
        self.mesh.vertices += [0, 1.5, -.08]
        vertices, faces = self.mesh.vertices.copy(), self.mesh.faces.copy()
        _, distances, _ = SurfaceQuery(self.mesh).closest([[.00002, 1.50002, -.079999]])
        np.testing.assert_allclose(distances, [.001], atol=1e-9)
        np.testing.assert_array_equal(self.mesh.vertices, vertices)
        np.testing.assert_array_equal(self.mesh.faces, faces)


if __name__ == '__main__':
    unittest.main()
