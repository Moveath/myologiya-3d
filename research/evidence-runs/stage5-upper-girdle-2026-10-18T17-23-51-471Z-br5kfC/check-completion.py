"""Final document/link/hash check, plus last-updated dates of amended issues."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
target=ROOT/'ANATOMY_ISSUES.md'; text=target.read_text(encoding='utf8')
for id in ['SRC-001','SRC-002','CAT-HAND-SESAMOIDS','GEO-HAND-MCP1-R','GEO-HAND-MCP1-U']:
    pattern=r'(^### '+re.escape(id)+r'\n[\s\S]*?)(?=^### |\Z)'
    text,n=re.subn(pattern,lambda m:re.sub(r'Обновлено: \*\*\d{4}-\d\d-\d\d\*\*','Обновлено: **2026-10-18**',m[1],count=1),text,count=1,flags=re.M)
    assert n==1
target.write_text(text,encoding='utf8')
report=ROOT/'research/stage5-upper-girdle-report-2026-10-18.md'
links=[]
for url in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf8')):
    if url.startswith(('http','#')):continue
    p=(report.parent/url.split('#')[0]).resolve(); assert p.is_file(),url;links.append(url)
def parse(t):
    result={}
    for m in re.finditer(r'^### ([^\n]+)\n([\s\S]*?)(?=^### |\Z)',t,re.M):
        s=re.search(r'Статус: \*\*([^*]+)\*\*',m[2])
        if s:assert m[1] not in result;result[m[1]]=s[1]
    return result
old=parse((OUT/'before-ANATOMY_ISSUES.md').read_text(encoding='utf8'));now=parse(text)
assert len(old)==225 and len(now)==228 and all(now[k]==v for k,v in old.items())
for log in ['LOG-20261018-06','LOG-20261018-07']:
    assert log in (ROOT/'ANATOMY_PROGRESS.md').read_text(encoding='utf8')
files=['scripts/upper_girdle_stage5_review.py','scripts/make_pins.py','scripts/make_context_bone_data.py',
 'site/pins.js','site/pins-context-bones.js','tools/prepare-stage5-upper-evidence.mjs',
 'tools/verify-stage5-upper-girdle.mjs','tools/prepare-stage5-upper-girdle-mcp.mjs',
 'verify/review_upper_girdle.py','verify/review_upper_girdle_blender.py',
 'research/stage5-upper-girdle-report-2026-10-18.md','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md']
hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
baseline=json.loads((OUT/'hashes-before.json').read_text(encoding='utf8'));protected=[]
for f,h in baseline.items():
    if f not in files:assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f;protected.append(f)
rows=json.loads((OUT/'reviewed-records-final.json').read_text(encoding='utf8'))
remaining=json.loads((OUT/'remaining-records-final.json').read_text(encoding='utf8'))
assert len(rows)==68 and len(remaining)==176
assert len({p['id'] for p in rows+remaining})==244
e=json.loads((OUT/'evidence.json').read_text(encoding='utf8'))
for ui in e['playwright']:
    d=json.loads((OUT/ui).read_text(encoding='utf8'));assert d['status']=='passed' and len(d['cards'])==68 and not d['consoleErrors']
result=dict(status='passed',registry=len(now),previous225StatusesUnchanged=True,localReportLinks=len(links),
    reviewedRecords=len(rows),remainingRecords=len(remaining),protectedFiles=len(protected),finalFileHashes=hashes,
    acceptedNewCoordinates=0,htmlAndGLBUnchanged=True)
with (OUT/'completion.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='finalFileHashes'}))
