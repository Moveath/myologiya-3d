"""Read reviewed head landmarks, preserving surface/projection distinctions.

The original ray-cast file is kept as a reproducible baseline. Supplement files
override individual bone/code pairs after a new review; they never fill missing
coordinates algorithmically from an unreviewed list of names.
"""
from pathlib import Path
import importlib
import json

ROOT = Path(__file__).resolve().parents[1]
PARTS = ('face', 'cranial', 'temporal')
SUPPLEMENTS = [f'pins_head/{name}-extra.json' for name in PARTS] + ['pins_head/face-completion.json', 'pins_head/face-features-bp.json']
KINDS = {'surface', 'projection', 'internal', 'variant'}


def descriptions():
    merged = {}
    for name in PARTS:
        module = importlib.import_module(f'head_{name}_evidence')
        for code, entry in module.DESCRIPTIONS.items():
            assert code not in merged, (code, 'Conflicting evidence modules')
            assert entry.get('x') and len(entry.get('refs', [])) >= 2, code
            merged[code] = {**entry, 'scope': 'anatomy'}
    return merged


def positions():
    baseline = json.loads((ROOT/'pins_head/ta.json').read_text(encoding='utf-8'))
    merged = {}
    for row in baseline:
        if row.get('missing'):
            continue
        merged[row['bone'], row['code']] = {**row, 'localization': 'surface',
                                          'source_file': 'pins_head/ta.json'}
    for filename in SUPPLEMENTS:
        rows = json.loads((ROOT/filename).read_text(encoding='utf-8'))
        seen = set()
        for row in rows:
            key = row['bone'], row['code']
            assert key not in seen, (filename, key, 'Duplicate landmark')
            seen.add(key)
            assert row['localization'] in KINDS, (filename, key)
            assert row.get('modelNote'), (filename, key, 'Missing model limitation')
            assert len(row.get('p', [])) == len(row.get('n', [])) == 3, key
            merged[key] = {**row, 'source_file': filename}
    return merged
