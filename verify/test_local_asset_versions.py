"""Regression for mixed cached/fresh JavaScript on the atlas start page."""
from pathlib import Path
import importlib.util,json,re,tempfile,unittest

spec=importlib.util.spec_from_file_location('make_local',Path(__file__).resolve().parents[1]/'scripts/make_local.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class LocalAssetVersions(unittest.TestCase):
    def test_build_revisions_and_import_graph(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as tmp:
            root=Path(tmp)
            self.assertTrue(root.resolve().is_relative_to(Path(__file__).resolve().parent))
            (root/'index.html').write_text('''<script type="importmap">{"imports":{"three":"./vendor/three/build/three.module.js"}}</script>
<script src="data.js"></script><script src="https://example.org/remote.js"></script>
<script type="module">import {controls} from './atlas-controls.js';import {visibility} from './atlas-visibility.js?v=old';</script>''',encoding='utf-8')
            for name,code in {'data.js':'window.DATA=1','atlas-controls.js':'export const controls=1','atlas-visibility.js':"import {sides} from './atlas-model-sides.js';export const visibility=sides",'atlas-model-sides.js':'export const sides=1'}.items():
                (root/name).write_text(code,encoding='utf-8')
            build=module.make_document(root/'index.html')
            self.assertEqual(build,module.make_document(root/'index.html'))
            self.assertRegex(build,r'src="data.js\?v=[a-f0-9]{16}"')
            self.assertIn('src="https://example.org/remote.js"',build)
            self.assertRegex(build,r"from '\./atlas-controls.js\?v=[a-f0-9]{16}'")
            self.assertNotIn('?v=old',build)
            data=json.loads(re.search(r'<script type="importmap">(.*?)</script>',build,re.S)[1])
            self.assertEqual(data['imports']['three'],'./vendor/three/build/three.module.js')
            old=data['imports']['./atlas-model-sides.js']
            self.assertRegex(old,r'\?v=[a-f0-9]{16}$')
            (root/'atlas-model-sides.js').write_text('export const sides=2',encoding='utf-8')
            new=module.make_document(root/'index.html')
            self.assertNotIn('"./atlas-model-sides.js": "'+old+'"',new)
            self.assertIn(data['imports']['./atlas-controls.js'],new)
            (root/'data.js').write_text('window.DATA=2',encoding='utf-8')
            self.assertNotEqual(re.search(r'src="(data.js[^\"]+)"',build)[1],re.search(r'src="(data.js[^\"]+)"',module.make_document(root/'index.html'))[1])

    def test_url_guards_and_query(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as tmp:
            root=Path(tmp);(root/'atlas-controls.js').write_text('export {}',encoding='utf-8')
            self.assertTrue(root.resolve().is_relative_to(Path(__file__).resolve().parent))
            for url in ['https://example.org/x.js','//example.org/x.js','../outside.js','missing.js','image.png']:
                self.assertEqual(url,module.versioned_asset(url,root))
            url=module.versioned_asset('./atlas-controls.js?mode=local&v=old#anchor',root)
            self.assertRegex(url,r'^\./atlas-controls.js\?mode=local&v=[a-f0-9]{16}#anchor$')

if __name__=='__main__':unittest.main()
