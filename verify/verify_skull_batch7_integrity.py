"""Final batch accounting and original-file protection, no anatomical acceptance."""
from pathlib import Path
import hashlib,json,re
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage5-skull-batch7-2026-10-16'
def read(p):return Path(p).read_text(encoding='utf-8-sig')
def js(p):return json.loads(read(p))
baseline=js(OUT/'protected-before.json')
changed=[p for p,h in baseline.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
allowed={'ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md','README.md','site/index.html','site/local.html','site/pins-head.js','scripts/make_pins_head.py','scripts/head_geometry_kind.py'}
assert set(changed)<=allowed,changed
models=[p for p in baseline if p.endswith('.glb') or p.endswith('-glb.txt')]
assert len(models)==41 and not set(models)&set(changed)
def issues(s):return {k:t for k,t in re.findall(r'^### ([\w-]+)\n(.*?)(?=^### |\Z)',s,re.M|re.S) if 'Статус: **' in t}
before=issues(read(OUT/'baseline-ANATOMY_ISSUES.md'));now=issues(read(ROOT/'ANATOMY_ISSUES.md'))
assert len(before)==195 and len(now)==199
for key,old in before.items():
    assert key in now
    for field in ['Статус','Этап','Приоритет']:
        pattern=field+r': \*\*(.*?)\*\*'
        assert re.search(pattern,old).group(1)==re.search(pattern,now[key]).group(1),(key,field)
    for line in old.splitlines():
        if line.startswith('- Решение и критерий закрытия:') or line.startswith('- Дополнение LOG-'):
            assert line in now[key],(key,'lost acceptance/history')
counts=Counter(re.search(r'Статус: \*\*(.*?)\*\*',v).group(1) for v in now.values())
assert dict(counts)=={'проверена':34,'требует проверки':80,'заблокирована':52,'открыта':33}
science=sum('Научная проверка: да' in v and 'Статус: **проверена**' not in v for v in now.values());assert science==129
oldlog=read(OUT/'baseline-ANATOMY_PROGRESS.md');newlog=read(ROOT/'ANATOMY_PROGRESS.md')
start=oldlog.index('### LOG-');assert oldlog[start:].strip() in newlog
assert '### LOG-20261016-10' in newlog
assert len(re.findall(r'^\| [1-8] \|',newlog,re.M))==8
data=js(OUT/'data-regression.json');assert data['status']=='passed' and data['classified']==34
for filename,width in [('playwright-cards.json',1280),('playwright-cards-mobile.json',390)]:
    cases=js(OUT/filename);assert all(c['status']=='passed' and c['width']==width for c in cases)
    ids=[i for c in cases for i in c['testedIDs']];assert len(ids)==len(set(ids))==48
    assert sum(len(c['links']) for c in cases)==14
for name in ['mcp-kinds-desktop-1280-result.json','mcp-shared-desktop-1280-result.json','playwright-target-1280.json','mcp-kinds-mobile-390-result.json','mcp-shared-mobile-390-result.json','playwright-target-390.json','playwright-bvh.json']:
    assert js(OUT/name)['status']=='passed',name
for p in OUT.glob('*.json'):js(p)
for path in [ROOT/'research/stage5-skull-batch7-report-2026-10-16.md',ROOT/'ANATOMY_ISSUES.md',ROOT/'ANATOMY_PROGRESS.md']:
    for target in re.findall(r'\]\(([^)]+)\)',read(path)):
        if '://' in target or target.startswith('#'):continue
        target=target.split('#')[0]
        # This report is written only after the remaining checks below pass.
        if (path.parent/target).resolve()==(OUT/'final-integrity.json').resolve():continue
        assert (path.parent/target).exists(),(path.name,target)
result=dict(status='passed',protectedBaseline=len(baseline),changed=changed,originalModelsUnchanged=len(models),oldIssueIDsPreserved=195,oldStatusesStagesCriteriaAndHistoryPreserved=True,oldProgressHistoryPreserved=True,roadmapStages=8,totalIssues=len(now),statuses=dict(counts),sciencePending=science,newIssues=sorted(set(now)-set(before)),closedThisBatch=0,classified=34,remainingSkull=37,addedCards=8,newCoordinates=0,allCurrentCardsTestedAtWidths=[1280,390],sharedCandidatesRemaining=27)
(OUT/'final-integrity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
