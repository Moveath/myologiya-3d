"""Fetch author-published CT/mandible files with Figshare MD5 verification."""
from pathlib import Path
import hashlib
import json
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'research/cache/mandible-channels'
CACHE.mkdir(parents=True, exist_ok=True)
record = json.load(urllib.request.urlopen('https://api.figshare.com/v2/articles/6167726'))
assert record['license']['name'] == 'CC BY 4.0'
(CACHE / 'figshare-record.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf8')
requested = set(sys.argv[1:] or ['STLs.zip'])
for item in record['files']:
    if item['name'] not in requested:
        continue
    target = CACHE / item['name']
    if not target.exists():
        temporary = target.with_suffix(target.suffix + '.part')
        with urllib.request.urlopen(item['download_url'], timeout=120) as response, temporary.open('wb') as output:
            while block := response.read(4 * 1024 * 1024):
                output.write(block)
        temporary.replace(target)
    with target.open('rb') as source:
        digest = hashlib.file_digest(source, 'md5').hexdigest()
    assert digest == item['computed_md5'], (target, digest)
    print(item['name'], target.stat().st_size, 'MD5 verified', flush=True)
