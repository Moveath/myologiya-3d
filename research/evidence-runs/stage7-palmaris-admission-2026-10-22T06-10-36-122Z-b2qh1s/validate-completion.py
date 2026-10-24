"""Verify saved evidence, source preservation and registry; no repeated rendering."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[3];RUN=Path(__file__).resolve().parent
OTHER=ROOT/'research/evidence-runs/stage7-omohyoid-mask-feasibility-2026-10-22T06-10-37-586Z-A5PssF'
PRIOR=ROOT/'research/evidence-runs/stage7-palmaris-prototype-2026-10-21T14-13-24-504Z-NLmOtD'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(ROOT/'verify'))
from verify_anatomy_registry import check
registry=check();checks=[]
def require(v,name):
    assert v,name
    checks.append(name)
for path,h in read(PRIOR/'baseline.json')['hashes'].items():require(sha(ROOT/path)==h,'Production unchanged: '+path)
for path,h in read(RUN/'layer-review.json')['hashes'].items():require(sha(ROOT/path)==h,'PB source unchanged: '+path)
shape=read(OTHER/'shape-summary.json')
for row in shape['rows']:require(sha(ROOT/row['source'])==row['source_sha256'],'Original STL unchanged: '+row['name'])
require(sha(ROOT/shape['hyoid_source'])==shape['hyoid_sha256'],'Original hyoid STL unchanged')
arrays=read(OTHER/'blender-review-arrays.json')
require(sha(ROOT/arrays['source'])==arrays['sha256'],'Neck GLB unchanged')
layer=read(RUN/'layer-review.json');contact=read(RUN/'contact-review.json');node=read(OTHER/'node-review.json')
require(layer['status']=='passed' and len(layer['checks'])==6,'PB layer checks')
require(contact['status']=='passed' and len(contact['checks'])==14,'PB contact/BVH checks')
require(node['status']=='passed' and len(node['checks'])==24,'Omohyoid Node/BVH checks')
require(node['inventory']==dict(muscles=259,muscleNoModel=14,partsNoModel=21,boneNoModel=20),'Current inventory')
diagnostic=read(OTHER/'diagnostic-checks.json')['checks']
require(len(diagnostic)==17 and all(x['pass']for x in diagnostic),'17 independent diagnostic checks')
require(all(x['positions_equal']and x['indices_equal']for x in read(OTHER/'current-array-validation.json')['checks']),'Three exact context comparisons')
for p,views in [(RUN/'blender-contact-review.json',3),(OTHER/'blender-review.json',2)]:
    d=read(p);require(d['status']=='passed'and d['views']==views,'Blender evidence '+p.name)
pb=[read(RUN/n)for n in ['mcp-palmaris-admission-1280.json','mcp-palmaris-admission-v2-390.json']]
require(all(d['status']=='passed'and len(d['checks'])==12 and not d['errors']for d in pb),'24 final PB browser assertions')
mobile=read(OTHER/'mcp-omohyoid-390.json');desktop=read(OTHER/'mcp-omohyoid-1280.json');capture=read(OTHER/'mcp-omohyoid-1280-capture.json')
require(mobile['status']=='passed'and len(mobile['checks'])==24 and not mobile['errors'],'24 mobile omohyoid assertions')
require(desktop['status']=='failed'and 'exceeded 40 seconds' in desktop['error']and len(desktop['checks'])==24 and not desktop['errors'],'Desktop assertions retained, screenshot deadline accurately recorded')
require(capture['status']=='passed'and capture['state']['width']==1280,'Desktop capture recovered without repeating completed clicks')
for p in [RUN/'palmaris-admission-1280.png',RUN/'palmaris-admission-v2-390.png',OTHER/'omohyoid-390.png',OTHER/'omohyoid-1280-capture.png']:
    require(p.exists()and p.stat().st_size>1000,'Actual screenshot: '+p.name)
report=ROOT/'research/stage7-palmaris-admission-and-omohyoid-2026-10-22.md'
for link in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf8')):
    if not link.startswith(('http:','https:','#')):require((report.parent/link).exists(),'Report link '+link)
for path in ['ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md','CURRENT_PROJECT_STATUS.md']:
    require('LOG-20261022-02' in (ROOT/path).read_text(encoding='utf8'),'Documentation '+path)
require(registry['issues']==255 and registry['status_counts']['проверена']==73 and registry['status_counts']['заблокирована']==61,'Registry counts and IDs retained')
result=dict(status='passed_with_documented_browser_capture_recovery',checks=checks,
    registry=registry,reviewedExistingIssues=5,newIssues=0,closedIssues=0,newModels=0,newPartMasks=0,
    inventory=node['inventory'],pythonChecks=23,exactArrayComparisons=3,nodeChecks=38,
    completedFunctionalBrowserAssertions=72,fullDesktopOmohyoidRun='timed_out_after_24_assertions_at_capture',
    recoveredDesktopCapture=True,blenderViews=5,sourceHashesChecked=14,stage8Started=False)
with (RUN/'completion.json').open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in result.items()if k not in ['registry','checks']},ensure_ascii=False))
