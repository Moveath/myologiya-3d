"""Verify saved evidence and preservation; does not re-run meshes or browser tests."""
from pathlib import Path
import hashlib,importlib.util,json,re,zipfile
ROOT=Path(__file__).resolve().parents[3]
RUN=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

checkpoint=read(RUN/'checkpoint.json')
assert sha(ROOT/checkpoint['archive'])==checkpoint['archiveSHA256']
site=[r for r in checkpoint['filesManifest'] if r['path'].startswith('site/')]
for r in site:assert sha(ROOT/r['path'])==r['sha256'],r['path']
state=read(ROOT/'research/geometry-recovery-state.json')
valid=load('checkpoint_validator','tools/geometry-recovery-state.py').validate(state)
registry=load('registry_validator','verify/verify_anatomy_registry.py').check()
def issue_fields(text):
    result={}
    for m in re.finditer(r'^### ([A-Za-z0-9_-]+)\n(.*?)(?=^### |\Z)',text,re.M|re.S):
        body=m[2]
        result[m[1]]=(re.search(r'Статус: \*\*([^*]+)\*\*',body)[1],
                      re.search(r'^- Решение и критерий закрытия:.*$',body,re.M)[0])
    return result
with zipfile.ZipFile(ROOT/checkpoint['archive']) as z:
    old=z.read('ANATOMY_ISSUES.md').decode('utf-8-sig').replace('\r\n','\n')
current=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf8')
assert issue_fields(old)==issue_fields(current),'Issue identity/status/acceptance criteria changed'

resource_hashes=[]
for row in state['items']:
    for rec in row['resources']:
        if rec.get('file') and rec.get('sha256'):
            assert sha(ROOT/rec['file'])==rec['sha256'],rec['file']
            resource_hashes.append(rec['file'])
checks={}
paths={
 'mirror':'stage7-interspinales-mirror-candidate-2026-10-22T07-10-51-528Z-2xay0X/node-comparison.json',
 'plane':'stage7-interspinales-local-plane-2026-10-22T07-25-20-358Z-RCXRLB/node-comparison.json',
 'metacarpals':'bonehub-metacarpal-registration-2026-10-22T07-22-32-957Z-wWtQcl/trial-glb-node-checks.json',
 'multifidus':'stage7-targeted-muscle-sources-2026-10-22T07-14-12-363Z-LR6EiF/node-z-multifidus-glb.json'}
for key,path in paths.items():
    d=read(ROOT/'research/evidence-runs'/path)
    count=len(d['checks']) if isinstance(d['checks'],list) else d['checks']
    assert d.get('status')=='passed' or d.get('passed')==count,key
    checks[key]=count
browser={}
for width in [1280,390]:
    d=read(RUN/f'playwright-{width}.json')
    assert d['status']=='passed' and not d['errors'] and not d['productionModified']
    browser[str(width)]=dict(assertions=len(d['checks']),evidence=f'playwright-{width}.json',
                           scope='X=0 interspinales research build; not anatomy acceptance of all candidates')

links=[]
for name in ['ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md','CURRENT_PROJECT_STATUS.md']:
    text=(ROOT/name).read_text(encoding='utf8')
    assert 'LOG-20261022-03' in text
    # Validate all links on new checkpoint lines/section, without re-auditing historical links.
    if name=='ANATOMY_ISSUES.md':selection='\n'.join(l for l in text.splitlines() if 'LOG-20261022-03' in l)
    elif name=='ANATOMY_PROGRESS.md':selection=text.split('### LOG-20261022-03',1)[1]
    else:selection=text.split('## Этапы 6–7 — LOG-20261022-03',1)[1]
    for target in re.findall(r'\]\(([^)]+)\)',selection):
        if re.match(r'https?://',target):continue
        path=target.split('#',1)[0]
        assert (ROOT/path).is_file(),(name,target)
        links.append(path)

result=dict(status='passed',scope='Saved-result consolidation, no new geometry/UI reruns',
            siteFilesUnchanged=len(site),checkpointArchiveHashMatches=True,
            noRegistryStatusOrCriterionChanged=True,registry=registry,
            state=valid,hashedResourceFiles=len(set(resource_hashes)),newDocumentationLinksChecked=len(links),
            savedNodeAssertions=checks,savedNodeTotal=sum(checks.values()),savedBrowserEvidence=browser,
            newlyIntegrated=dict(bones=0,muscles=0,parts=0,masks=0),
            remaining=state['currentCounts'],allMethodsExhausted=False,stage8Started=False)
with (RUN/'completion-validation.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False))
