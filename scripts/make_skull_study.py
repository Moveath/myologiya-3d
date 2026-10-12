"""Reuse the reviewed TA98 variant cards without introducing new anatomy."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
text = (root / 'site/pins-head.js').read_text(encoding='utf-8')
pins = json.loads(text.split('push(...', 1)[1].rsplit(');', 1)[0])
rows = [{key: p[key] for key in ('id', 'b', 'c', 'ru', 'lat', 'g', 'x', 'modelNote', 'refs')}
        for p in pins if p.get('loc') == 'variant']
assert len(rows) == 14
(root / 'site/skull-study-variants.json').write_text(
    json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Study catalogue:', len(rows), 'variant locations; no added geometry')
native = json.loads((root / 'pins_head/openear-native.json').read_text(encoding='utf-8'))
(root / 'site/skull-openear-landmarks.json').write_text(
    json.dumps(native, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('OpenEar native markers:', len(native['markers']))
