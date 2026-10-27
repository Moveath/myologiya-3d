"""Fetch the left (and, for the record, right) BP3D STL of the six soft tissues and write decimation targets.

The STL mirror commit is the one already used for the left limb muscles; cached files are never replaced.
The face budget of every left file is the face count of the accepted right node in the published atlas.
Usage: python scripts/prepare_left_soft_tissues.py RUN
"""
import hashlib
import json
import struct
import sys
import time
import urllib.request
from pathlib import Path
from left_soft_tissues import table

ROOT = Path(__file__).resolve().parents[1]
COMMIT = 'f0eeb6e843380cfe6b83797cf8c3e1af74de5e61'
URL = 'https://raw.githubusercontent.com/Kevin-Mattheus-Moerman/BodyParts3D/' + COMMIT + '/assets/BodyParts3D_data/stl/{}.stl'
CACHE = ROOT / 'research/cache/left-soft-tissues'
run = Path(sys.argv[1]).resolve()
CACHE.mkdir(parents=True, exist_ok=True)


def fetch(fma, name):
    target = CACHE / (fma + '.stl')
    if not target.exists():
        for attempt in range(5):
            try:
                with urllib.request.urlopen(URL.format(fma), timeout=120) as response:
                    data = response.read()
                break
            except Exception:
                time.sleep(3 * (attempt + 1))
        else:
            raise RuntimeError(fma)
        with target.open('xb') as f:
            f.write(data)
    data = target.read_bytes()
    triangles = struct.unpack('<I', data[80:84])[0]
    assert len(data) == 84 + 50 * triangles, 'Binary STL size mismatch ' + fma
    return dict(fma=fma, name=name, url=URL.format(fma), bytes=len(data), triangles=triangles,
                sha256=hashlib.sha256(data).hexdigest())


published = {}
for sec in ('arm', 'leg'):
    index = json.loads((ROOT / f'research/cache/atlas-geometry/{sec}.json').read_text(encoding='utf8'))
    for node in index['nodes']:
        if node['name'].startswith('o|'):
            published[node['name'][2:]] = node['faceCount']
sources, targets = [], []
for row in table():
    assert row['leftFMA'], row
    left, right = fetch(row['leftFMA'], row['leftName']), fetch(row['rightFMA'], row['rightName'])
    sources += [dict(left, side='left', id=row['left']), dict(right, side='right', id=row['right'])]
    targets.append(dict(region=row['region'], right=row['right'], left=row['left'], part='', leftFMA=row['leftFMA'],
                        rightFMA=row['rightFMA'], rightSourceTriangles=right['triangles'], leftSourceTriangles=left['triangles'],
                        rightTriangles=published[row['right']], target=published[row['right']]))
for name, value in (('left-sources.json', dict(commit=COMMIT, release='BodyParts3D 3.0 (DBCLS) via STL mirror of Kevin-Mattheus-Moerman',
                                               license='CC BY-SA 2.1 Japan', rows=sources)),
                    ('decimation-targets.json', targets)):
    with (run / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=1)
print(json.dumps([(t['left'], t['leftSourceTriangles'], t['target']) for t in targets]))
