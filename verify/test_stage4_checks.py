"""Regression: builders must not silently decimate bones; topology flags are diagnostic."""
from pathlib import Path
import hashlib, json, os, subprocess, sys, tempfile, unittest
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from mesh_build_policy import bone_settings, bone_target
from geometry_export_guard import bone_mesh, stable_vertex_normals, validate_bone_roundtrip
from audit_stage4_topology import topology

class BoneBuildTests(unittest.TestCase):
    def test_policy(self):
        ratio,cap=bone_settings({})
        self.assertEqual(ratio,1)
        self.assertEqual(bone_target(500000,cap),500000)
        for env in ({'BONE_RATIO':'0.15'},{'BONE_RATIO':'nan'},{'BONE_MAX':'0'}):
            with self.assertRaises(ValueError):bone_settings(env)
        with self.assertRaises(ValueError):bone_target(12001,12000)
    def test_actual_builder_preserves_bone_and_rejects_caps(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.venv') as tmp:
            tmp=Path(tmp)
            source=trimesh.creation.icosphere(subdivisions=4,radius=10)
            source.export(tmp/'fixture.stl')
            before=hashlib.sha256((tmp/'fixture.stl').read_bytes()).hexdigest()
            (tmp/'fixture_manifest.py').write_text("MUSCLES={}\nBONES={'fixture':['fixture']}\nOTHER={}\nCONTEXT=[]\n")
            env=os.environ.copy()
            for key in ('BONE_RATIO','BONE_MAX'):env.pop(key,None)
            command=[sys.executable,'-X','utf8',str(ROOT/'scripts/build_glb.py'),str(tmp),str(tmp),str(tmp/'output.glb'),str(tmp/'meta.json'),'fixture_manifest']
            run=subprocess.run(command,env=env,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr[-1200:])
            loaded=trimesh.load(tmp/'output.glb',force='scene',process=False)
            self.assertEqual(sum(len(m.faces) for m in loaded.geometry.values()),len(source.faces))
            np.testing.assert_allclose(loaded.bounds,source.bounds/1000,atol=1e-8)
            self.assertEqual(hashlib.sha256((tmp/'fixture.stl').read_bytes()).hexdigest(),before)
            exported=hashlib.sha256((tmp/'output.glb').read_bytes()).hexdigest()
            for setting in ({'BONE_RATIO':'0.15'},{'BONE_MAX':'1200'}):
                run=subprocess.run(command,env={**env,**setting},capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0)
                self.assertIn('Bone decimation' if 'BONE_RATIO' in setting else 'BONE_MAX',run.stderr)
                self.assertEqual(hashlib.sha256((tmp/'output.glb').read_bytes()).hexdigest(),exported)

    def test_exact_welding_preserves_close_bone_vertices(self):
        # process=True merges these distinct positions at trimesh's default tolerance.
        vertices=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1e-9]],dtype=float)
        faces=np.array([[0,1,2],[3,2,1]])
        mesh=bone_mesh(vertices,faces)
        np.testing.assert_array_equal(mesh.triangles,vertices[faces])
        self.assertEqual(len(mesh.vertices),4)

    def test_normals_on_small_valid_mesh_and_ambiguous_duplicate(self):
        tiny=trimesh.creation.icosphere(subdivisions=1,radius=1e-6)
        normals=stable_vertex_normals(tiny.vertices,tiny.faces)
        np.testing.assert_allclose(np.linalg.norm(normals,axis=1),1)
        with self.assertRaisesRegex(ValueError,'Undefined normals'):
            stable_vertex_normals(np.array([[0,0,0],[1,0,0],[0,1,0]]),np.array([[0,1,2],[0,2,1]]))

    def test_float32_collapse_is_rejected(self):
        mesh=trimesh.Trimesh(vertices=[[1,0,0],[1+1e-9,0,0],[1,1,0]],faces=[[0,1,2]],process=False)
        scene=trimesh.Scene();scene.add_geometry(mesh,node_name='b|tiny',geom_name='b|tiny')
        with self.assertRaisesRegex(ValueError,'collapsed'):
            validate_bone_roundtrip(scene,scene.export(file_type='glb'))

class TopologyTests(unittest.TestCase):
    def test_closed_and_open_surface(self):
        mesh=trimesh.creation.box()
        result,_=topology(mesh.vertices,mesh.faces,np.empty((0,3)),np.eye(4))
        self.assertEqual((result['boundary_edges'],result['inconsistent_two_face_edges'],result['duplicate_faces']),(0,0,0))
        result,_=topology(mesh.vertices,mesh.faces[:-1],np.empty((0,3)),np.eye(4))
        self.assertEqual(result['boundary_edges'],3)
    def test_duplicate_and_flipped_face(self):
        mesh=trimesh.creation.box()
        faces=np.vstack([mesh.faces,mesh.faces[0]])
        result,_=topology(mesh.vertices,faces,np.empty((0,3)),np.eye(4))
        self.assertEqual(result['duplicate_faces'],1)
        faces=mesh.faces.copy();faces[0]=faces[0][::-1]
        result,_=topology(mesh.vertices,faces,np.empty((0,3)),np.eye(4))
        self.assertEqual(result['inconsistent_two_face_edges'],3)
if __name__=='__main__':unittest.main()

