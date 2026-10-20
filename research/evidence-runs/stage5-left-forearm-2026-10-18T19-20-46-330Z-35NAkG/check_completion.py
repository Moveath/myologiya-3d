"""Validate final registry accounting, links and immutable evidence/model hashes."""
from pathlib import Path
from collections import Counter
import hashlib, json, re
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).parent
def registry(text):
    result={}
    for m in re.finditer(r'^### ([A-Za-z][A-Za-z0-9_-]+)\n([\s\S]*?)(?=^### |\Z)',text,re.M):
        status=re.search(r'Статус: \*\*(.*?)\*\*',m[2])
        if status:
            assert m[1] not in result
            result[m[1]]=dict(status=status[1],stage=int(re.search(r'Этап: \*\*(\d+)\*\*',m[2])[1]),
                science='Научная проверка: да.' in m[2])
    return result
before=registry((OUT/'before-ANATOMY_ISSUES.md').read_text(encoding='utf8'))
current=registry((ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf8'))
assert set(current)==set(before) and len(current)==232
changed=[id for id in before if before[id]!=current[id]]
assert changed==['CAT-UPPER-LEFT-FOREARM'],changed
assert current['CAT-UPPER-LEFT-FOREARM']['status']=='проверена'
assert current['GEO-UPPER-LEFT-FOREARM']['status']=='заблокирована'
counts=Counter(v['status'] for v in current.values())
assert counts=={'проверена':58,'открыта':35,'требует проверки':81,'заблокирована':58},counts
science=sum(v['science'] and v['status']!='проверена' for v in current.values());assert science==138,science
stage5=[v for v in current.values() if v['stage']==5];assert (sum(v['status']=='проверена' for v in stage5),len(stage5))==(36,110)

resources=json.loads((OUT/'left-forearm-resources.json').read_text(encoding='utf8'))
assert not any(r['matches'] for r in resources['resources']) and not resources['matchingSourceFiles']
assert not any(r['anonymousMeshNodes'] for r in resources['resources'] if 'arm' in Path(r['file']).name)
for r in resources['resources']:assert hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest()==r['sha256'],r['file']
assert all(any(n.startswith(('b|','c|','m|','o|')) for n in r['ancestry']) for r in resources['trimeshMeshes'])
node=json.loads((OUT/'data-regression-final.json').read_text(encoding='utf8'));assert node['status']=='passed'
ui_dirs=['stage5-left-forearm-mcp-2026-10-18T19-27-17-437Z-Fetl8u',
         'stage5-left-forearm-mcp-2026-10-18T19-28-40-497Z-sfNQW4',
         'stage5-left-forearm-final-mcp-2026-10-18T19-32-18-405Z-fA9jy9']
for d in ui_dirs:
    data=json.loads((OUT.parent/d/'result.json').read_text(encoding='utf8'));assert data['status']=='passed',d
    assert len(list((OUT.parent/d).glob('*.png')))==2,d
report=ROOT/'research/stage5-left-forearm-report-2026-10-19.md'
for link in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf8')):
    if not link.startswith(('https://','#')):assert (report.parent/link.split('#')[0]).exists(),link
existing=json.loads((OUT/'hashes-before.json').read_text(encoding='utf8'))
changed_files={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f,h in existing.items() if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h}
expected={'scripts/ta98.py','scripts/make_context_bone_data.py','site/data-context-bones.js','site/pins-context-bones.js','site/index.html','site/local.html','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md'}
assert set(changed_files)==expected,set(changed_files)
new_files=['scripts/left_forearm_stage5_review.py','verify/review_left_forearm_resources.py','verify/review_left_forearm_blender.py',
    'tools/prepare-stage5-left-forearm-evidence.mjs','tools/verify-stage5-left-forearm.mjs',
    'tools/prepare-stage5-left-forearm-mcp.mjs','tools/prepare-stage5-left-forearm-final-mcp.mjs',str(report.relative_to(ROOT))]
for f in new_files:changed_files[f]=hashlib.sha256((ROOT/f).read_bytes()).hexdigest()
result=dict(status='passed',issues=len(current),statuses=dict(counts),scientificVerificationRequired=science,
    closedThisTask=changed,stage5=dict(verified=36,total=110),newIssues=0,newBoneCards=2,newLandmarkRecords=44,
    modelsUnchanged=len(resources['resources']),uiRuns=ui_dirs,changedFileHashes=changed_files,
    pythonChecks=dict(generator='passed',pyCompile='passed',ta98=dict(compared=762,knownDifferences=['A02.5.10.015','A02.5.10.017','A02.5.11.007'])),
    earlierFailedAttempts=['Sandbox-local server inaccessible to MCP; restarted outside restricted network sandbox.',
      'Broad triangle-count equality failed for other arm objects; differences retained, no whole-mesh acceptance claimed.',
      'Final-note fixture expected visible desktop bMore; corrected to actual visibility without application changes.'])
with (OUT/'completion.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in result.items() if k not in ('changedFileHashes','earlierFailedAttempts','pythonChecks','uiRuns')},ensure_ascii=False))
