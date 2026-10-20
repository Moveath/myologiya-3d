"""Presentation semantics from existing explicit extent reviews, never new geometry.

Ambiguous types stay unknown. In particular, a 'landmark' is not necessarily a
point, and a groove/ridge needs more than a line to describe its full shape.
This does not import historical completeFeatureGeometry as current acceptance.
"""
import json
from functools import lru_cache
from pathlib import Path
from head_skull_batch2 import geometry_decisions
from head_skull_batch3 import reviewed_decisions
from head_skull_batch4 import reviewed_decisions as batch4_decisions
from head_skull_batch5 import reviewed_decisions as batch5_decisions
from head_skull_batch6 import reviewed_decisions as batch6_decisions
from head_skull_batch7 import reviewed_decisions as batch7_decisions
from head_skull_batch8 import reviewed_decisions as batch8_decisions

ROOT = Path(__file__).resolve().parents[1]
EXPLICIT_KINDS = {
    'surface': 'area',
    'edge': 'line',
    'suture': 'line',
    'variant_suture': 'line',
    'canal': 'volume',
    'channel': 'volume',
    'cavity': 'volume',
}
POINT_CODES = {'A02.1.04.003', 'A02.1.04.004'}  # Basion, opisthion.


@lru_cache(maxsize=1)
def reviewed_geometry_kinds():
    result = {}
    for region in ('face', 'cranial', 'temporal'):
        path = ROOT / f'research/{region}-feature-extent-review.json'
        for row in json.loads(path.read_text(encoding='utf-8'))['rows']:
            key = (row['bone'], row['code'])
            assert key not in result, ('Duplicate extent review', key)
            kind = EXPLICIT_KINDS.get(row['requiredExtent']['type'], 'unknown')
            if key[0] == 'occipital' and key[1] in POINT_CODES:
                kind = 'point'
            result[key] = kind
    for key, kind in geometry_decisions().items():
        assert key in result, ('Unknown reviewed landmark', key)
        result[key] = kind
    for key, decision in reviewed_decisions().items():
        assert result[key] == 'unknown', ('Previously reviewed kind changed', key)
        result[key] = decision['kind']
    for key, decision in batch4_decisions().items():
        assert result[key] == 'unknown', ('Previously reviewed kind changed', key)
        result[key] = decision['kind']
    for key, decision in batch5_decisions().items():
        assert result[key] == 'unknown', ('Previously reviewed kind changed', key)
        result[key] = decision['kind']
    for key, decision in batch6_decisions().items():
        assert result[key] == 'unknown', ('Previously reviewed kind changed', key)
        result[key] = decision['kind']
    for key, decision in batch7_decisions().items():
        assert result[key] == 'unknown', ('Previously reviewed kind changed', key)
        result[key] = decision['kind']
    for key, decision in batch8_decisions().items():
        assert result[key] == 'unknown', ('Previously reviewed kind changed', key)
        result[key] = decision['kind']
    return result
