"""Collect current evidence; run only lightweight Python checks not saved earlier."""
from pathlib import Path
import json, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/stage5-skull-final-2026-10-17'

def load(name):
    return json.loads((OUT / name).read_text(encoding='utf-8-sig'))

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

python_results = []
for script in ['verify_head.py', 'verify_ta98.py', 'test_skull_shared_stage5.py']:
    result = subprocess.run([sys.executable, str(ROOT / 'verify' / script)], cwd=ROOT,
                            capture_output=True, text=True, encoding='utf-8')
    row = dict(script=script, exitCode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    python_results.append(row)
    assert result.returncode == 0, row
save('python-checks.json', python_results)
assert '762 terms compared, 3 differences' in python_results[1]['stdout']
assert 'Ran 3 tests' in python_results[2]['stderr']

data = load('data-regression.json')
assert data['status'] == 'passed' and data['skullLandmarks'] == 629
ids = {row['id'] for row in load('new-cards.json')['records']}
pending = {row['id'] for row in load('shared-kind-pending.json')['rows']}
assert len(ids) == 25 and len(pending) == 32
browser = []
for width in [1280, 390]:
    tested, links = [], []
    for offset in range(0, 25, 5):
        r = load(f'playwright-cards-{width}-{offset}.json')
        assert r['status'] == 'passed' and r['width'] == width and not r['errors']
        tested += r['testedIDs']; links += r['links']
    assert len(tested) == len(set(tested)) == 25 and set(tested) == ids
    for name in [f'playwright-load-{width}.json', f'playwright-shared-{width}.json', f'playwright-target-{width}.json']:
        r = load(name)
        assert r['status'] == 'passed' and not r.get('errors'), name
    target = load(f'playwright-target-{width}.json')
    assert len(target['results']) == 5
    assert all(r['realRaySelection'] and r['isolation'] and r['transparency'] for r in target['results'])
    bvh_name = 'playwright-bvh-1280.json' if width == 1280 else 'playwright-bvh.json'
    bvh = load(bvh_name)
    assert bvh['status'] == 'passed' and bvh['width'] == width and not bvh.get('errors')
    assert len(bvh['cases']) == 3 and sum(len(r['rays']) for r in bvh['cases']) == 54
    browser.append(dict(width=width, newCardIDs=tested, relatedLinkClicks=len(links),
        realRayBones=5, bvhDifferentialCases=54, sharedJugularRegression=True,
        scope='Desktop/mobile viewport emulation; no physical-device or GPU benchmark claim.'))
kind = load('playwright-shared-kind-retry.json')
assert kind['status'] == 'passed' and not kind['errors']
assert {r['width'] for r in kind['results']} == {1280, 390}
assert all(len(r['testedIDs']) == 32 and set(r['testedIDs']) == pending for r in kind['results'])
mesh = load('blender-review.json')
assert mesh['status'] == 'passed' and mesh['sourceUnchanged'] and mesh['originalScenePreserved']
assert len(mesh['bones']) == 22 and len(mesh['records']) == 521
assert not any(r['anatomicalLocalizationAccepted'] or r['extentAccepted'] for r in mesh['records'])
notes = load('test-notes.json')
notes['sharedKindInitialFailure'] = ('First 32-card check failed because the existing browser page used an older cached pins-shared.js. '
    'Fresh served content independently contained all 32 unknown fields. Retried with a cache-busting request for that same file; '
    'all 32 passed at both widths. Initial failure is retained in playwright-shared-kind.json; not counted as pass.')
save('test-notes.json', notes)
save('verification-summary.json', dict(status='passed', date='2026-10-17',
    python=dict(evidence='python-checks.json', tests=3, sharedUnitTests=3,
        ta98KnownDifferences=3, ta98Compared=762,
        positions='Prior batch8 Python positions result reused: own data and GLB unchanged; current Blender separately checked all 521.'),
    node=dict(evidence='data-regression.json', ownUnchanged=521, sharedIDsAndRelationsPreserved=69,
        sharedMetadataOnlyUnknownAdded=32, oldExtraUnchanged=14, newExtra=25),
    blender=dict(evidence='blender-review.json', bones=22, anchors=521, diagnosticViews=3,
        maxSurfaceDistanceMm=max(r['surfaceDistanceMm'] for r in mesh['records']),
        newAnatomicalCoordinateAcceptances=0, newContourAcceptances=0),
    playwright=browser, unknownTypeWarningChecks=kind['results'],
    limitations=['Three TA98 differences already documented outside skull.',
        'Anatomical localization is not inferred from surface distance or UI success.',
        'First cached warning check failed; fresh retry passed. See test-notes.json.',
        'One historical auxiliary PNG was superseded by bootstrap; not historical evidence. See test-notes.json.']))
print(json.dumps({'status': 'passed', 'pythonScripts': 3, 'newCardsPerWidth': 25,
                  'unknownWarningsPerWidth': 32, 'rayCasesPerWidth': 54}, ensure_ascii=False))
