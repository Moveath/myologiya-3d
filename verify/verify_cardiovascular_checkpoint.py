"""Bounded final consistency check; does not repeat geometry or anatomy review."""
from pathlib import Path
from collections import Counter
import hashlib, json, re, sys
from verify_anatomy_registry import check as registry_check

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'research/evidence-runs/cardiovascular-first-integration-2026-10-22T11-41-39-801Z-wDXHnD'
UI = ROOT / 'research/evidence-runs/cardiovascular-ui-r2-2026-10-22T12-24-27-891Z-4dzKc9'
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def tool_result(path):
    data = read(path)
    if 'content' in data:
        text = next(c['text'] for c in data['content'] if c.get('type') == 'text')
        data = json.JSONDecoder().raw_decode(text[text.index('{'):])[0]
    return data

def main(run):
    checks = 0
    def require(value, message):
        nonlocal checks
        assert value, message
        checks += 1

    baseline = read(run / 'before-finalization.json')
    for name, digest in baseline['hashes'].items():
        require(sha(ROOT / name) == digest, 'Previously tested UI/data/recovery state changed: ' + name)
    snapshot = read(MAIN / 'checkpoint.json')
    originals = [r for r in snapshot['filesManifest'] if re.match(r'^site/(?:.*-glb\.txt|pins.*\.js|data-(?!cardiovascular).*\.js|models/.*\.glb)$', r['path'])]
    for row in originals:
        require(sha(ROOT / row['path']) == row['sha256'], 'Original changed: ' + row['path'])

    inventory = read(ROOT / 'research/cardiovascular-state.json')
    records = inventory['structures']
    require(len(records) == 98 and len({r['id'] for r in records}) == 98, 'Inventory IDs')
    require(Counter(r['system'] for r in records) == {'heart':11,'arteries':49,'veins':38}, 'System distribution')
    require(Counter(r['system'] for r in records if not r['noModel']) == {'heart':4,'arteries':27,'veins':19}, 'Model distribution')
    require(inventory['counts'] == dict(cards=98, educational=50, noModel=48, fullAnatomicalAcceptance=0, proceduralReconstructions=0), 'Admission counts')
    ids = {r['id'] for r in records}
    model_paths = []
    triangles = 0
    for row in records:
        require(all(ref in ids for ref in row['relations'].values()), 'Dangling typed relation: ' + row['id'])
        require(len(row['refs']) >= 2 and bool(row['nextAction']), 'Missing sources or next action: ' + row['id'])
        require('CV-CATALOG-SOURCES' in row['issueIds'], 'Missing source issue')
        if row['noModel']:
            require(row['modelFile'] is None and row['admission'] is None and 'CV-GEO-MISSING' in row['issueIds'], 'False admission: ' + row['id'])
        else:
            candidate = row['candidate']; admission = row['admission']
            model_paths.append(row['modelFile']); triangles += candidate['triangles']
            require(admission['status'] == 'educational_limited' and 'CV-GEO-ACCEPTANCE' in row['issueIds'], 'Admission status')
            require(sha(ROOT / 'site' / row['modelFile']) == candidate['sha256'] == admission['sha256'], 'Model hash changed')
            require(sha(ROOT / candidate['source']['file']) == candidate['source']['sha256'], 'OBJ changed')
            require(candidate['source']['version'] == '3.0' and candidate['source']['license'] == 'CC BY-SA 2.1 Japan', 'Source license/version')
            for evidence in admission['evidence']:
                require((ROOT / evidence).is_file(), 'Missing admission evidence: ' + evidence)
    require(len(model_paths) == len(set(model_paths)) == 50 and triangles == 704246, 'Unique models / triangles')
    for evidence in inventory['checkpoint']['evidence']:
        require((ROOT / evidence).is_file(), 'Missing checkpoint evidence: ' + evidence)
    node = read(MAIN / 'node-production.json')
    require(node['status'] == 'passed' and node['checks'] == 1459 and len(node['models']) == 50, 'Production proof')
    require(node['oldCounts'] == {'boneNoModel':20,'muscleNoModel':14,'partNoModel':21}, 'Legacy counts proof')
    browser_paths = [MAIN / 'cv-heart-1280-result.json', *[UI / n for n in ('cv-vessels-1280-result.json','cv-regression-1280-result.json','cv-vessels-390-result.json','cv-regression-390-result.json','cv-heart-390-completion.json','canvas-raycast.json')]]
    for path in browser_paths:
        result = tool_result(path)
        require(result['status'] == 'passed', 'Unfinished browser proof: ' + path.name)
        require(all(c['passed'] for c in result.get('checks', [])), 'Failed browser assertion')
    timeout = read(UI / 'cv-heart-390-result.json')
    require(timeout['status'] == 'failed' and timeout['error'] == '45s scenario budget' and len(timeout['checks']) == 12 and all(c['passed'] for c in timeout['checks']), 'Preserve actual mobile timeout result')
    require(read(run / 'systems-unit.json')['status'] == 'passed', 'System unit checks missing')

    text = (ROOT / 'ANATOMY_ISSUES.md').read_text(encoding='utf-8-sig')
    bodies = {m[1]:m[2] for m in re.finditer(r'^### ([A-Za-z0-9_-]+)\n(.*?)(?=^### |\Z)', text, re.M|re.S)}
    for ident, old in baseline['issueBodies'].items():
        require(ident in bodies, 'Lost issue: ' + ident)
        if ident != 'FUT-005':
            require(bodies[ident].strip() == old.strip(), 'Old status/criteria changed: ' + ident)
    require(set(bodies) - set(baseline['issueBodies']) == {'CV-GEO-MISSING','CV-GEO-ACCEPTANCE','CV-CATALOG-SOURCES'}, 'Unexpected new issue IDs')
    registry = registry_check()
    require(registry['issues'] == 258 and registry['status_counts']['проверена'] == 73 and registry['status_counts']['заблокирована'] == 62, 'Registry counts')
    status = (ROOT / 'CURRENT_PROJECT_STATUS.md').read_text(encoding='utf8')
    require('**258 задач: 73 проверены, 185 не закрыты**' in status, 'Current status count')
    report = ROOT / inventory['checkpoint']['report']
    require(report.is_file(), 'Missing final report')
    local_links = 0
    for target in re.findall(r'\]\(([^)]+)\)', report.read_text(encoding='utf8')):
        if re.match(r'^(https?:|#)', target):
            continue
        require((report.parent / target.split('#')[0]).exists(), 'Broken report link: ' + target)
        local_links += 1
    sys.path.insert(0, str(ROOT / 'scripts'))
    from make_local import make_document
    require((ROOT / 'site/local.html').read_text(encoding='utf8') == make_document(ROOT / 'site/index.html'), 'Local wrapper stale')
    result = dict(status='passed', checks=checks, scope='File/data/evidence consistency only; no repeated mesh scan or new scientific acceptance', cards=98, educationalModels=50, noModel=48, triangles=triangles, retainedOriginalFiles=len(originals), preservedPreviousIssues=254, changedExistingIssue='FUT-005', newIssues=3, closedIssues=0, reportLinks=local_links, registry=registry)
    with (run / 'completion-validation.json').open('x', encoding='utf8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps({k:v for k,v in result.items() if k != 'registry'}, ensure_ascii=False))

if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
