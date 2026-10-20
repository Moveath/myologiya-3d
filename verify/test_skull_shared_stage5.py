"""Safety invariants for the source-only stage 5 catalogue (no GLB or UI run)."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from skull_shared_stage5 import additional_instances, RIM_REFS


class SkullSharedStage5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = json.loads((ROOT / 'research/skull-whole-scope-audit.json').read_text(encoding='utf-8'))['rows']
        cls.terms = {row['code']: row['latin'] for row in rows}

    def records(self):
        return list(additional_instances(self.terms))

    def test_no_geometry_or_implicit_duplicate_instances(self):
        records = self.records()
        self.assertEqual(len(records), 28)
        self.assertEqual(len({r['id'] for r in records}), 28)
        for record in records:
            self.assertFalse({'p', 'n', 'noModel'} & record.keys())
            self.assertEqual(record['anchors'], [])
            self.assertEqual(record['catalogueBones'], [])
            self.assertEqual(record['relationScope'], 'reference_anatomy')
            self.assertIn(record['geometryKind'], {'area', 'space', 'line', 'volume'})
            self.assertGreaterEqual(len({r['authorGroup'] for r in record['refs']}), 2)
            for source in record['refs']:
                self.assertEqual(source['kind'], 'anatomical')
                self.assertEqual(source['scope'], 'bone_relationships')
                self.assertTrue(source['locator'])
            self.assertEqual({r['id'] for r in record['refs']}, set(record['relations'][0]['refs']))

    def test_paired_unpaired_bones_and_local_scope(self):
        self.assertEqual(len(RIM_REFS), 2)
        self.assertEqual(len({r['authorGroup'] for r in RIM_REFS}), 2)
        self.assertTrue(all(r['scope'] == 'bone_relationships' for r in RIM_REFS))
        records = {r['id']: r for r in self.records()}
        for side in ('right', 'left'):
            canal = records['shared_skull_065_' + side]
            self.assertEqual(canal['side'], side)
            self.assertEqual({r['bone'] for r in canal['relations']}, {'sphenoid', 'vomer'})
            self.assertIn('A02.1.12.006', records['shared_skull_072_' + side]['modelNote'])
            self.assertIn('глазницы', records['shared_skull_073_' + side]['ru'])
            suture = records['shared_temporozygomatic_suture_' + side]
            self.assertEqual(suture['c'], 'A03.1.02.024')
            self.assertEqual(suture['geometryKind'], 'line')
        self.assertEqual(records['shared_skull_088']['side'], None)
        self.assertNotIn('shared_skull_066', records)

    def test_no_shared_mutable_evidence_between_calls_or_instances(self):
        first = self.records()
        first[0]['refs'][0]['title'] = 'mutated by a consumer'
        fresh = self.records()
        self.assertNotEqual(first[0]['refs'][0]['title'], fresh[0]['refs'][0]['title'])
        self.assertNotEqual(first[0]['refs'][0]['title'], first[1]['refs'][0]['title'])


if __name__ == '__main__':
    unittest.main()
