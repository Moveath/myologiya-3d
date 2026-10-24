"""Bounded, commit-pinned retrieval of new research candidates. No production edits."""
import hashlib, json, pathlib, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
meta = json.loads((ROOT / 'bonehub-api.json').read_text())
SHA = meta['sha']
base = 'https://huggingface.co/datasets/BoneHub/visible-human-3d-models/resolve/' + SHA + '/'
files = ['README.md', 'visible_human_3d_models/CT/Mesh/README.md', 'visible_human_3d_models/CT/metadata.json']
hand = ['METACARPAL_1_LEFT', 'METACARPAL_3_LEFT', 'TRAPEZIUM_LEFT', 'TRAPEZOID_LEFT', 'CAPITATE_LEFT', 'METACARPAL_2_LEFT', 'METACARPAL_4_LEFT', 'PHALANGE_HAND_1_LEFT', 'PHALANGE_HAND_3_LEFT']
foot = ['TALUS_LEFT', 'CALCANEUS_LEFT', 'CUBOID_LEFT', 'LATERAL_CUNEIFORM_LEFT', 'MEDIAL_CUNEIFORM_LEFT', 'INTERMEDIATE_CUNEIFORM_LEFT', 'NAVICULAR_LEFT'] + [f'METATARSAL_{i}_LEFT' for i in range(1, 6)] + ['PHALANGE_FOOT_1_LEFT', 'PHALANGE_FOOT_5_LEFT']
for region, names in [('HAND_LEFT', hand), ('FOOT_LEFT', foot)]:
    files.extend('visible_human_3d_models/CT/Mesh/01_Male/' + region + '/' + n + '.stl' for n in names)

out = ROOT / 'bonehub-candidates'
out.mkdir(exist_ok=False)
records = []
for index, remote in enumerate(files):
    url = base + remote
    name = remote.split('/')[-1]
    if remote == 'README.md': name = 'DATASET_README.md'
    elif remote.endswith('Mesh/README.md'): name = 'MESH_README.md'
    started = time.monotonic()
    record = {'remote': remote, 'url': url, 'commit': SHA, 'local': str((out/name).relative_to(ROOT)), 'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    try:
        with urllib.request.urlopen(url, timeout=25) as response:
            body = response.read(8_000_001)
            if len(body) > 8_000_000: raise RuntimeError('file exceeds 8 MB bounded retrieval limit')
            with (out/name).open('xb') as fh: fh.write(body)
            record.update(status='downloaded', bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), content_type=response.headers.get('Content-Type'))
    except Exception as exc:
        record.update(status='failed', error=str(exc))
    record['elapsed_seconds'] = round(time.monotonic() - started, 3)
    records.append(record)
    with (ROOT / f'bonehub-fetch-{index:02}.json').open('x', encoding='utf8') as fh: json.dump(record, fh, indent=2, ensure_ascii=False)
    print(name, record['status'], record.get('bytes', record.get('error')), flush=True)
with (ROOT/'bonehub-retrieval.json').open('x', encoding='utf8') as fh:
    json.dump({'commit':SHA, 'license':'CC BY 4.0 according to pinned dataset README', 'records':records}, fh, ensure_ascii=False, indent=2)
