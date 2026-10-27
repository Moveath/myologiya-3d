"""Fetch the twelve abdominal muscle STLs (BodyParts3D 3.0) and write their decimation targets.

The STL mirror commit is the one already used for the left limb muscles; cached files are never replaced.
Face budget: the default muscle rule of scripts/build_glb.py (abdomen_muscles.target_faces).
Usage: python scripts/prepare_abdomen_muscles.py RUN
"""
import hashlib
import json
import struct
import sys
import time
import urllib.request
from pathlib import Path
from abdomen_muscles import MUSCLES, NAME2ID, target_faces

ROOT = Path(__file__).resolve().parents[1]
COMMIT = 'f0eeb6e843380cfe6b83797cf8c3e1af74de5e61'
URL = 'https://raw.githubusercontent.com/Kevin-Mattheus-Moerman/BodyParts3D/' + COMMIT + '/assets/BodyParts3D_data/stl/{}.stl'
CACHE = ROOT / 'research/cache/abdomen-muscles'
ID2NAME = {v: k for k, v in NAME2ID.items()}
run = Path(sys.argv[1]).resolve()
CACHE.mkdir(parents=True, exist_ok=True)


def fetch(fma):
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
    return dict(fma=fma, name=ID2NAME[fma], url=URL.format(fma), bytes=len(data), triangles=triangles,
                sha256=hashlib.sha256(data).hexdigest())


sources, targets = [], []
for key, parts in MUSCLES.items():
    for fma, part in parts:
        source = fetch(fma)
        sources.append(dict(source, id=key, side=key.rsplit('_', 1)[1]))
        targets.append(dict(id=key, part=part or '', fma=fma, sourceTriangles=source['triangles'],
                            target=target_faces(source['triangles'])))
for name, value in (('sources.json', dict(commit=COMMIT, release='BodyParts3D 3.0 (DBCLS) via STL mirror of Kevin-Mattheus-Moerman',
                                          license='CC BY-SA 2.1 Japan', rows=sources)),
                    ('decimation-targets.json', targets)):
    with (run / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=1)
print(json.dumps([(t['id'], t['sourceTriangles'], t['target']) for t in targets]))
