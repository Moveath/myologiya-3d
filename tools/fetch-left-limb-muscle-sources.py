"""Download the left BodyParts3D STL of every mapped limb-muscle part; never replace a cached file."""
import hashlib
import json
import pathlib
import struct
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'scripts'))
from left_limb_muscles import table

COMMIT = 'f0eeb6e843380cfe6b83797cf8c3e1af74de5e61'
URL = 'https://raw.githubusercontent.com/Kevin-Mattheus-Moerman/BodyParts3D/' + COMMIT + '/assets/BodyParts3D_data/stl/{}.stl'
run = pathlib.Path(sys.argv[1])
cache = root / 'research/cache/left-limb-muscles'
cache.mkdir(parents=True, exist_ok=True)
parts = [p for r in table() if not r['crossRegion'] for p in r['parts']]


def fetch(part):
    target = cache / (part['leftFMA'] + '.stl')
    if not target.exists():
        for attempt in range(5):
            try:
                with urllib.request.urlopen(URL.format(part['leftFMA']), timeout=120) as response:
                    data = response.read()
                break
            except Exception:
                time.sleep(3 * (attempt + 1))
        else:
            raise RuntimeError(part['leftFMA'])
        with target.open('xb') as f:
            f.write(data)
    data = target.read_bytes()
    triangles = struct.unpack('<I', data[80:84])[0]
    assert len(data) == 84 + 50 * triangles, 'Binary STL size mismatch ' + part['leftFMA']
    return dict(fma=part['leftFMA'], name=part['leftName'], url=URL.format(part['leftFMA']), bytes=len(data),
                triangles=triangles, sha256=hashlib.sha256(data).hexdigest())


with ThreadPoolExecutor(max_workers=4) as pool:
    rows = list(pool.map(fetch, parts))
with (run / 'left-sources.json').open('x', encoding='utf8') as f:
    json.dump(dict(commit=COMMIT, release='BodyParts3D 3.0 (DBCLS) via STL mirror of Kevin-Mattheus-Moerman',
                   license='CC BY-SA 2.1 Japan', rows=rows), f, ensure_ascii=False, indent=2)
print(json.dumps(dict(parts=len(rows), triangles=sum(r['triangles'] for r in rows), megabytes=round(sum(r['bytes'] for r in rows) / 1e6, 1))))
