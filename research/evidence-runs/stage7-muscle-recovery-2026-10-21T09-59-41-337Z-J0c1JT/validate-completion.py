"""Small final consistency pass; does not repeat geometry or browser tests."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[3];RUN=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verify'))
from verify_anatomy_registry import check
registry=check()
read=lambda name:json.loads((RUN/name).read_text(encoding='utf-8'))
before,after=read('muscle-inventory-before.json'),read('muscle-inventory-after.json')
assert after['cards']==257 and len(after['rows'])==303
assert len(after['missing'])==13 and len(after['parts'])==21 and not after['mismatch']
assert set(after['boneNoModel'])==set(before['boneNoModel']) and len(after['boneNoModel'])==20
for rel,h in before['hashes'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
for row in read('puborectalis-export.json'):
    p=ROOT/row['derivedFile'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    src=ROOT/'research/cache/stage7-sources'/f"{row['source']['fma']}.obj"
    assert hashlib.sha256(src.read_bytes()).hexdigest()==row['source']['sha256']
accepted=['browser-v4-1280-'+part+'.json'for part in ['setup','card-right','card-left','sides']]
accepted+=['browser-v4-390-setup.json']+['browser-v5-390-'+part+'.json'for part in ['card-right','card-left','sides']]
browser=[read(name)for name in accepted]
assert all(r['status']=='passed'and not r['errors']for r in browser)
assert sum(len(r['checks'])for r in browser)==74
assert read('production-clean.json')['probeAbsent']
assert read('node-integration.json')['checks']==323
docs=['research/stage7-muscle-recovery-2026-10-21.md','research/stage7-muscle-blockers-2026-10-21.md']
links=0
for doc in docs:
    content=(ROOT/doc).read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)]+)\)',content):
        if target.startswith(('http','mailto:','#')):continue
        p=(ROOT/doc).parent/target.split('#')[0];assert p.exists(),f'{doc}: {target}';links+=1
    assert '\ufffd'not in content
matrix=json.loads((ROOT/'research/stage7-muscle-blockers-2026-10-21.json').read_text(encoding='utf-8'))
assert len(matrix['rows'])==34
issues=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf-8')
for row in matrix['rows']:
    body=re.search(r'^### '+re.escape(row['issue'])+r'\n(.*?)(?=^### |\Z)',issues,re.M|re.S)[1]
    assert 'Статус: **заблокирована**'in body
    assert '- Решение и критерий закрытия: '+row['existingAcceptanceCriterion']in body
    assert 'LOG-20261021-05'in body
for file in ['ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md','CURRENT_PROJECT_STATUS.md']:
    content=(ROOT/file).read_text(encoding='utf-8');assert 'stage7-muscle-recovery-2026-10-21.md'in content
out={'status':'passed','registry':registry,'catalogue':{'muscles':257,'meshes':303,'missingMuscles':13,'missingParts':21,'boneNoModel':20},'newModels':2,'closedIssuesThisRun':0,'newIssueIDs':0,'protectedOriginalFiles':len(before['hashes']),'sourceAndDerivedHashesPreserved':True,'nodeChecks':323,'browserAssertions':74,'acceptedBrowserResults':accepted,'localReportLinks':links,'all34OriginalAcceptanceCriteriaRetained':True,'nextStage':'Continue stage 7; do not start stage 8'}
with(RUN/'completion.json').open('x',encoding='utf-8')as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in out.items()if k!='acceptedBrowserResults'},ensure_ascii=False))
