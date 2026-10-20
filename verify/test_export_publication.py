"""Exercise the real publisher scripts against temporary assets, never site/."""
from pathlib import Path
import json, sys, tempfile, types, unittest
from unittest.mock import patch
import trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))


class PublicationTests(unittest.TestCase):
    def test_rejected_metadata_or_geometry_does_not_publish(self):
        for region in ('neck','thorax'):
            for failure in ('metadata','normal','reference'):
                with self.subTest(region=region,failure=failure), tempfile.TemporaryDirectory(dir=ROOT/'.venv') as folder:
                    root=Path(folder)
                    for directory in ('site','research',f'build_{region}',f'stl_{region}'):
                        (root/directory).mkdir()
                    mesh=trimesh.creation.box()
                    mesh.export(root/f'stl_{region}/fixture.stl')
                    source=mesh.copy()
                    if failure=='reference':source.update_faces(list(range(11)))
                    scene=trimesh.Scene();scene.add_geometry(source,node_name='b|fixture',geom_name='b|fixture')
                    scene.export(root/f'build_{region}/{region}_hi.glb')
                    for name in (region,region+'_q'):
                        bad=source.copy()
                        if failure=='normal':bad.vertex_normals=bad.vertex_normals*0
                        s=trimesh.Scene();s.add_geometry(bad,node_name='b|fixture',geom_name='b|fixture')
                        s.export(root/f'build_{region}/{name}.glb',include_normals=True)
                    meta={'parts':{'b|fixture':{'faces':11 if failure=='metadata' else 12}},'stats':{'faces':12}}
                    (root/f'build_{region}/meta.json').write_text(json.dumps(meta))
                    protected=[root/f'site/{region}-glb.txt',root/f'site/{region}-q-glb.txt',root/f'research/{region}-model-provenance.json']
                    for p in protected:p.write_bytes(b'unchanged')
                    manifest=types.SimpleNamespace(BONES={'fixture':['fixture']},MUSCLES={},CONTEXT=[],OTHER={},all_ids=lambda:['fixture'])
                    code=(ROOT/f'scripts/package_{region}_model.py').read_text(encoding='utf8')
                    code=code.replace('ROOT = Path(__file__).resolve().parents[1]',f'ROOT = Path({str(root)!r})')
                    with patch.dict(sys.modules,{f'manifest_{region}':manifest}):
                        with self.assertRaises((AssertionError,ValueError)):
                            exec(compile(code,f'package_{region}_model.py','exec'),{'__file__':str(ROOT/f'scripts/package_{region}_model.py')})
                    for p in protected:self.assertEqual(p.read_bytes(),b'unchanged')

if __name__=='__main__':unittest.main()
