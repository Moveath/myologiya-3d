"""Verify the final skull ledger, immutable assets and evidence links against snapshots."""
from pathlib import Path
from collections import Counter
from urllib.parse import unquote
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/stage5-skull-final-2026-10-17'

def read(path):
    return path.read_text(encoding='utf-8-sig')

def load(name):
    return json.loads(read(OUT / name))

def issues(text):
    return {key: body for key, body in re.findall(r'^### ([\w-]+)\n(.*?)(?=^### |^## |\Z)', text, re.M | re.S)
            if 'Статус: **' in body}

def status(body):
    return re.search(r'Статус: \*\*(.*?)\*\*', body)[1]

protected = load('protected-before.json')
changed = []
for name, expected in protected.items():
    path = ROOT / name
    assert path.is_file(), name
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        changed.append(name)
allowed = {'ANATOMY_ISSUES.md', 'ANATOMY_PROGRESS.md', 'README.md',
           'scripts/make_pins_head_extra.py', 'site/pins-head-extra.js',
           'scripts/make_shared_landmarks.py', 'site/pins-shared.js'}
assert set(changed) == allowed, changed
models = [name for name in protected if name.endswith('.glb') or name.endswith('-glb.txt')]
assert len(models) == 41 and not set(models).intersection(changed)
current = issues(read(ROOT / 'ANATOMY_ISSUES.md'))
before = issues(read(OUT / 'baseline-ANATOMY_ISSUES.md'))
assert len(before) == 202 and len(current) == 204
assert set(current) - set(before) == {'GEO-SKULL-FINAL-EXTRA', 'PIN-SHARED-KIND'}
status_changes = [key for key in before if status(current[key]) != status(before[key])]
assert status_changes == ['CAT-MAXILLA-EXTRA'], status_changes
assert status(current['CAT-MAXILLA-EXTRA']) == 'проверена'
for key, body in before.items():
    for line in body.splitlines():
        if line.startswith(('- Решение и критерий закрытия:', '- Дополнение LOG-')):
            assert line in current[key], (key, 'Lost acceptance criterion or history')
counts = Counter(status(body) for body in current.values())
assert dict(counts) == {'проверена': 36, 'требует проверки': 82, 'заблокирована': 53, 'открыта': 33}
science = sum(status(body) != 'проверена' and 'Научная проверка: да' in body for body in current.values())
assert science == 132
stage5 = [body for body in current.values() if 'Этап: **5**' in body]
assert len(stage5) == 82 and sum(status(body) == 'проверена' for body in stage5) == 14
old_history = read(OUT / 'baseline-ANATOMY_PROGRESS.md').split('## Записи журнала', 1)[1].rstrip()
new_history = read(ROOT / 'ANATOMY_PROGRESS.md').split('## Записи журнала', 1)[1]
assert new_history.startswith(old_history), 'Old log entries changed'
assert len(re.findall(r'^### LOG-20261017-01', new_history, re.M)) == 1
for phase in range(1, 9):
    assert re.search(r'^\| '+str(phase)+r' \|', read(ROOT / 'ANATOMY_PROGRESS.md'), re.M)

data = load('data-regression.json')
assert data['status'] == 'passed' and data['skullLandmarks'] == 629
assert data['newCoordinates'] == 0 and data['newCards'] == 25
inventory = load('inventory-current.json')
baseline = load('inventory-before-complete.json')
assert inventory['bones'] == baseline['bones'] and inventory['own'] == baseline['own']
assert len(inventory['shared']) == 69 and len(inventory['extras']) == 39
old_shared = {p['id']: p for p in baseline['shared']}
pending = {p['id'] for p in load('shared-kind-pending.json')['rows']}
assert len(pending) == 32
for record in inventory['shared']:
    expected = dict(old_shared[record['id']])
    if record['id'] in pending:
        assert 'geometryKind' not in expected
        expected['geometryKind'] = 'unknown'
    assert record == expected, record['id']
assert len(load('unlocated-shared-ids.json')) == 67
assert len(load('landmark-evidence.json')['documentedLimitedSharedAnchors']) == 2
assert len(load('landmark-evidence.json')['midlineSignFlags']) == 9
decision = load('candidate-decisions.json')
assert len(decision['catalogue']) + len(decision['shared']) == 94
assert decision['catalogueAdded'] == 25 and decision['cataloguePending'] == 42 and decision['sharedPending'] == 27
assert load('verification-summary.json')['status'] == 'passed'
remaining = load('remaining-skull-issues.json')
for row in remaining['rows']:
    assert row['status'] == status(current[row['id']]) != 'проверена'
    assert all(row[key] for key in ['whatRemains', 'canFixNow', 'nextStage', 'useImpact', 'originalAcceptanceCriterion'])

# Check only this task's addressed local Markdown links; existing unrelated broken links are not repaired here.
checked_links = 0
paths = [ROOT / 'research/stage5-skull-final-report-2026-10-17.md',
         OUT / 'source-review.md', OUT / 'candidate-decisions.md', OUT / 'remaining-skull-issues.md']
for path in paths:
    for target in re.findall(r'\]\(([^)]+)\)', read(path)):
        if re.match(r'\w+://', target) or target.startswith('#'):
            continue
        target_path = target.split('#', 1)[0]
        resolved = (path.parent / unquote(target_path)).resolve()
        if resolved == OUT / 'integrity-check.json':
            continue  # Written by this check only after the assertions succeed.
        assert resolved.is_file(), (str(path), target)
        checked_links += 1
for path in OUT.glob('*.json'):
    json.loads(read(path))

result = dict(status='passed', date='2026-10-17', protectedFiles=len(protected),
    protectedModelHashesUnchanged=len(models), changedProtectedFiles=changed,
    oldIssueIDsPreserved=len(before), acceptanceCriteriaAndOldAddendaPreserved=True,
    progressHistoryPreserved=True, changedStatuses=status_changes,
    issueCount=len(current), statusCounts=dict(counts), unresolved=168, scientificReviewNeeded=science,
    stage5Total=len(stage5), stage5Verified=14, linkedRemainingQuestions=remaining['count'],
    skullLandmarks=629, oldOwnRecordsPreserved=521, sharedIDsAndRelationsPreserved=69,
    explicitUnknownAdded=32, newCards=25, newCoordinates=0, checkedLocalLinks=checked_links,
    exception='Historical auxiliary PNG superseded as explicitly documented in test-notes.json; not included among unchanged evidence.')
(OUT / 'integrity-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: result[key] for key in ['status', 'issueCount', 'unresolved', 'protectedModelHashesUnchanged', 'checkedLocalLinks']}, ensure_ascii=False))
