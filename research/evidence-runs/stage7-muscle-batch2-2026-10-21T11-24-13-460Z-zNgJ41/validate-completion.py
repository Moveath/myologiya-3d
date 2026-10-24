"""Final consistency only; reuse completed mesh and browser evidence."""
import hashlib,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];RUN=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'verify'))
from verify_anatomy_registry import check
read=lambda name:json.loads((RUN/name).read_text(encoding='utf8'))
registry=check();baseline=read('baseline.json')
for rel,h in baseline['hashes'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
for r in read('derivatives.json'):
    assert hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest()==r['sha256']
    assert hashlib.sha256((ROOT/r['source']['file']).read_bytes()).hexdigest()==r['source']['sha256']
published=read('neck-published.json')
assert hashlib.sha256((ROOT/published['file']).read_bytes()).hexdigest()==published['sha256']
browser=read('cli-neck-v7-summary.json')
assert len(browser)==6 and all(r['status']=='passed'and not r['errors']for r in browser)
assert sum(len(r['checks'])for r in browser)==60
assert set(r['width']for r in browser)=={390,1280}
assert read('node-integration.json')['passed']==37
assert read('node-derivatives-corner-normals.json')['passed']==22
matrix=json.loads((ROOT/'research/stage7-muscle-batch2-decisions-2026-10-21.json').read_text(encoding='utf8'))
assert len(matrix['rows'])==len({r['issue']for r in matrix['rows']})==34
issues=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf8')
for row in matrix['rows']:
    body=re.search(r'^### '+re.escape(row['issue'])+r'\n(.*?)(?=^### |\Z)',issues,re.M|re.S)[1]
    assert 'Статус: **заблокирована**'in body
    assert '- Решение и критерий закрытия: '+row['existingAcceptanceCriterion']in body
    assert 'LOG-20261021-07'in body
links=0
report=ROOT/'research/stage7-muscle-batch2-report-2026-10-21.md'
for target in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf8')):
    if target.startswith(('http','mailto:','#')):continue
    assert (report.parent/target.split('#')[0]).exists(),target
    links+=1
for doc in ['ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md','CURRENT_PROJECT_STATUS.md']:
    text=(ROOT/doc).read_text(encoding='utf8');assert report.name in text and '\ufffd'not in text
assert registry['issues']==255 and registry['status_counts']['проверена']==73
out={'status':'passed','registry':registry,'catalogue':read('node-integration.json')['inventory'],
     'admittedNewModels':1,'newCards':2,'originalMissingMusclesRestored':0,'originalMissingPartsRestored':0,
     'technicalOnlyNormalRepairs':2,'sourceHashesPreserved':True,'baselineFilesPreserved':len(baseline['hashes']),
     'browserLocalPlaywrightAssertions':60,'mcpInitialLoadAssertions':4,'fullMcpRun':'blocked by approval policy; user-authorized local-process fallback used',
     'all34OriginalAcceptanceCriteriaPreserved':True,'reportLocalLinks':links,'closedIssuesThisRun':0,'newIssueIDs':0,
     'reviewedIssueDecisions':35,'next':'Stage 7 source/segmentation work; Stage 8 not started'}
with (RUN/'completion.json').open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in out.items()if k not in ['registry','catalogue']},ensure_ascii=False))
