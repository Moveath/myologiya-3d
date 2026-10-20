"""Lightweight closure checks; no rerun of unchanged geometry or UI."""
from pathlib import Path
import ast, hashlib, json, re, collections
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
report=ROOT/'research/stage5-arm-forearm-report-2026-10-18.md'
changed=['scripts/make_pins.py','scripts/make_context_bone_data.py','scripts/arm_forearm_stage5_review.py',
 'site/pins.js','site/pins-context-bones.js','tools/prepare-stage5-arm-forearm-evidence.mjs',
 'tools/verify-stage5-arm-forearm.mjs','tools/prepare-stage5-arm-forearm-mcp.mjs',
 'verify/review_arm_forearm.py','verify/review_arm_forearm_blender.py',
 'research/stage5-arm-forearm-report-2026-10-18.md','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']
for file in changed:
    assert (ROOT/file).exists(),file
    if file.endswith('.py'):ast.parse((ROOT/file).read_text(encoding='utf-8-sig'))
protected=0
for file,digest in json.loads((OUT/'hashes-before.json').read_text()).items():
    if file not in changed:
        assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest,file
        protected+=1
links=0
for target in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf8')):
    if '://' not in target:
        assert (report.parent/target.split('#')[0]).exists(),target
        links+=1
issues=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf8'); progress=(ROOT/'ANATOMY_PROGRESS.md').read_text(encoding='utf8')
rows={}
for m in re.finditer(r'^### ([^\n]+)\n([\s\S]*?)(?=^### |\Z)',issues,re.M):
    s=re.search(r'Статус: \*\*([^*]+)\*\*',m[2])
    if s:
        assert m[1] not in rows
        rows[m[1]]=(s[1],m[2])
assert len(rows)==232
counts=collections.Counter(v[0] for v in rows.values());assert counts=={'проверена':57,'требует проверки':81,'заблокирована':58,'открыта':36}
stage5=[v for v in rows.values() if 'Этап: **5**' in v[1]]
assert len(stage5)==110 and sum(v[0]=='проверена' for v in stage5)==35
assert '**2092** записи ориентиров. Без p — **766' in issues
assert '| 5 | Полная проверка' in progress and '35/110' in progress
for item in json.loads((OUT/'evidence.json').read_text(encoding='utf8'))['playwright']:
    r=json.loads((OUT/item).read_text(encoding='utf8'));assert r['status']=='passed' and len(r['cards'])==110 and r['sharedEdges']==15
result=dict(status='passed',registryTasks=len(rows),statuses=counts,stage5=[35,110],protectedFiles=protected,localReportLinks=links,
    changedFileHashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in changed},
    note='Only registry, report links, source syntax and protected hashes checked after UI; unchanged heavy checks not repeated.')
with (OUT/'completion.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='passed',protectedFiles=protected,localReportLinks=links,registryTasks=len(rows)),ensure_ascii=False))
