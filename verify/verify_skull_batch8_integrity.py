"""Final evidence, registry and original-file protection for skull batch 8."""
from pathlib import Path
import hashlib,json,re
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage5-skull-batch8-2026-10-16'
def read(p):return Path(p).read_text(encoding='utf-8-sig')
def js(p):return json.loads(read(p))
def issues(s):return {k:t for k,t in re.findall(r'^### ([\w-]+)\n(.*?)(?=^### |\Z)',s,re.M|re.S) if 'Статус: **' in t}
baseline=js(OUT/'protected-before.json')
changed=[p for p,h in baseline.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
allowed={'ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md','README.md','site/pins-head.js','scripts/make_pins_head.py',
         'scripts/head_geometry_kind.py','scripts/make_pins_head_extra.py','site/pins-head-extra.js'}
assert set(changed)<=allowed,changed
models=[p for p in baseline if p.endswith('.glb') or p.endswith('-glb.txt')]
assert len(models)==41 and not set(models)&set(changed)
before=issues(read(OUT/'baseline-ANATOMY_ISSUES.md'));now=issues(read(ROOT/'ANATOMY_ISSUES.md'))
assert len(before)==199 and len(now)==202
for key,old in before.items():
    assert key in now
    for field in ['Статус','Этап','Приоритет']:
        a=re.search(field+r': \*\*(.*?)\*\*',old).group(1)
        b=re.search(field+r': \*\*(.*?)\*\*',now[key]).group(1)
        if key=='PIN-SKULL-KIND' and field=='Статус':assert (a,b)==('требует проверки','проверена')
        else:assert a==b,(key,field,a,b)
    for line in old.splitlines():
        if line.startswith('- Решение и критерий закрытия:') or line.startswith('- Дополнение LOG-'):
            assert line in now[key],(key,'lost acceptance/history')
counts=Counter(re.search(r'Статус: \*\*(.*?)\*\*',v).group(1) for v in now.values())
assert dict(counts)=={'проверена':35,'требует проверки':81,'заблокирована':53,'открыта':33},counts
science=sum('Научная проверка: да' in v and 'Статус: **проверена**' not in v for v in now.values());assert science==131
oldlog=read(OUT/'baseline-ANATOMY_PROGRESS.md');newlog=read(ROOT/'ANATOMY_PROGRESS.md')
assert oldlog[oldlog.index('### LOG-'):].strip() in newlog
assert '### LOG-20261016-11' in newlog
assert len(re.findall(r'^\| [1-8] \|',newlog,re.M))==8
data=js(OUT/'data-regression.json');assert data['status']=='passed' and data['classified']==37 and not data['remainingSkull']
for width in (1280,390):
    cases=js(OUT/f'playwright-cards-{width}.json');assert all(c['status']=='passed' and c['width']==width for c in cases)
    ids=[i for c in cases for i in c['testedIDs']];assert len(ids)==len(set(ids))==46
    assert set(ids)=={p['id'] for p in data['cards']}
    assert sum(len(c['links']) for c in cases)==14
for name in ['mcp-kinds-desktop-1280-result.json','mcp-shared-desktop-1280-result.json','playwright-target-1280-retry.json',
             'mcp-kinds-mobile-390-result.json','mcp-shared-mobile-390-result.json','playwright-target-390.json',
             'playwright-shared-regression-1280.json','playwright-shared-regression-390.json','playwright-bvh.json']:
    assert js(OUT/name)['status']=='passed',name
assert js(OUT/'verification-summary.json')['status']=='passed'
assert js(OUT/'shared-decisions.json')['remaining']==27
assert len(js(OUT/'catalogue-candidates.json')['rows'])==19
assert len(js(OUT/'new-cards.json')['records'])==6
for p in OUT.glob('*.json'):js(p)
for path in [ROOT/'research/stage5-skull-batch8-report-2026-10-16.md',ROOT/'ANATOMY_ISSUES.md',ROOT/'ANATOMY_PROGRESS.md']:
    for target in re.findall(r'\]\(([^)]+)\)',read(path)):
        if '://' in target or target.startswith('#'):continue
        target=target.split('#')[0]
        if (path.parent/target).resolve()==(OUT/'final-integrity.json').resolve():continue
        assert (path.parent/target).exists(),(path.name,target)
result=dict(status='passed',protectedBaseline=len(baseline),changed=changed,originalModelsUnchanged=41,oldIssueIDsPreserved=199,
    previousStatusesPreservedExceptVerifiedKind=True,oldCriteriaAndHistoryPreserved=True,oldProgressHistoryPreserved=True,roadmapStages=8,
    totalIssues=202,statuses=dict(counts),sciencePending=science,newIssues=sorted(set(now)-set(before)),closedThisBatch=1,
    classified=37,remainingSkull=0,addedCards=6,newCoordinates=0,allCurrentCardsTestedAtWidths=[1280,390],sharedCandidatesRemaining=27)
(OUT/'final-integrity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
