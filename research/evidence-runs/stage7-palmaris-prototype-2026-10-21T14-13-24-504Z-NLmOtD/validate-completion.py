"""Reuse completed evidence; no repeated model import or browser suite."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[3];RUN=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verify'))
from verify_anatomy_registry import check
read=lambda name:json.loads((RUN/name).read_text(encoding='utf8'))
registry=check()
for path,sha in read('baseline.json')['hashes'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
export=read('export-finalization.json')
assert hashlib.sha256((ROOT/export['file']).read_bytes()).hexdigest()==export['sha256']
phases=['mcp-palmaris-v3-1280-setup','mcp-palmaris-v2-1280-cards','mcp-palmaris-v3-1280-sides',
        'mcp-palmaris-v3-390-setup','mcp-palmaris-v3-390-cards','mcp-palmaris-v3-390-sides']
browser=[read(p+'.json')for p in phases]
assert all(r['status']=='passed' and not r['errors'] for r in browser)
assert sum(len(r['checks']) for r in browser)==56
assert 'Errors: 0' in (RUN/'browser-console-errors.txt').read_text()
assert read('trimesh-prototype-v2.json')['status']=='passed'
assert len(read('trimesh-prototype-v2.json')['checks'])==13
assert read('recipe-tests.json')['status']=='passed'
assert len(read('recipe-tests.json')['checks'])==8
node=read('node-prototype.json');assert node['status']=='passed' and len(node['checks'])==34
assert node['inventory']==dict(muscles=259,muscleNoModel=14,partsNoModel=21,boneNoModel=20)
plan=json.loads((ROOT/'research/stage7-reconstruction-method-plan-2026-10-22.json').read_text(encoding='utf8'))
old=json.loads((ROOT/'research/stage7-muscle-batch2-decisions-2026-10-21.json').read_text(encoding='utf8'))
assert {r['issue']for r in plan['rows']}=={r['issue']for r in old['rows']}
assert all(not r['ready_for_automatic_anatomical_admission']for r in plan['rows'])
report=ROOT/'research/stage7-palmaris-prototype-2026-10-22.md'
for link in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf8')):
    if not link.startswith(('http:','https:','#')):assert (report.parent/link).exists(),link
for doc in ['ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md','CURRENT_PROJECT_STATUS.md']:
    assert 'LOG-20261022-01' in (ROOT/doc).read_text(encoding='utf8')
completion=dict(date='2026-10-22',status='technical_prototype_complete_not_admitted',
    registry=registry,closedTasks=0,newTasks=0,detailedAnatomicalPilots=1,otherMethodDecisions=33,
    prototypeVertices=1650,prototypeTriangles=3296,integratedModels=0,
    inventory=node['inventory'],pythonChecks=21,nodeChecks=34,playwrightMCPChecks=56,
    browserEvidence=phases,sourceHashesUnchanged=6,
    contextCrossingTrianglePairs={r['id']:r['crossing'] for r in node['contacts']if r['crossing']},
    selfIntersections=0,limitations=['registered skin/aponeurosis/attachment boundaries absent','65 of 221 envelope samples unsupported','214 context triangle-pair crossings; not 214 independent lesions'],
    next='Registered boundaries for PB or masks of continuous muscles; Stage 8 not started')
with (RUN/'completion.json').open('x',encoding='utf8')as f:json.dump(completion,f,ensure_ascii=False,indent=2)
with (RUN/'attempt-notes.json').open('x',encoding='utf8')as f:json.dump({
 'initial_export':'Rejected: selected objects from foreign scenes. Fixed with use_active_scene.',
 'v2_blender_name':'Scene-global .001 suffix normalized in JSON only; binary chunks preserved.',
 'initial_trimesh_check':'Failed at an excessively strict 2e-8 m tolerance. Final triangle-wise error3.1165e-8 m <1e-7 m; no geometry modified.',
 'mcp_v1':'Wrapper dynamic import failed; completed phase result was not persisted, not counted.',
 'mcp_v2_1280_sides':'Search/side/context assertions passed, reload assertion failed. Test build used unsupported entry query parameters; fixed explicit trial startup in browser-v2.',
 'original_34':'No original MG or MP received admission; procedural preview is not accepted anatomical geometry.'},f,indent=2)
print(json.dumps({k:v for k,v in completion.items()if k not in ['registry','browserEvidence']},ensure_ascii=False))
