"""Durable per-structure execution checkpoint, not a second issue-status registry.

init RUN creates the initial 55-row state from saved evidence (no mesh audit).
append RUN BATCH.json applies addressed updates and writes an immutable revision.
validate checks IDs, evidence links and catalogue counts in the saved inventory.
"""
from pathlib import Path
import argparse, copy, hashlib, json, re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT/'research/geometry-recovery-state.json'
BONES = 'research/evidence-runs/geometry-recovery-bone-methods-2026-10-22T07-10-36-377Z-kDATcr/bone-method-decisions.json'
PLAN = 'research/stage7-reconstruction-method-plan-2026-10-22.json'
RECENT = 'research/stage7-palmaris-admission-and-omohyoid-2026-10-22.md'
MIRROR = 'research/evidence-runs/stage7-interspinales-mirror-candidate-2026-10-22T07-10-51-528Z-2xay0X/decision.json'

def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def now(): return datetime.now(timezone.utc).isoformat()
def relative(path): return Path(path).resolve().relative_to(ROOT).as_posix()
def key(kind, row): return f"{kind}:{row['id']}" + (f":{row['part']}" if kind=='part' else '')
def method(code, status, summary, evidence):
    return dict(code=code,status=status,summary=summary,evidence=evidence)

def init(run):
    assert not STATE.exists(), 'Existing checkpoint must be resumed, never reinitialized'
    inventory = read(run/'inventory.json')
    plans = {(r['structure'], r['part']): r for r in read(PLAN)['rows']}
    bones = {r['id']:r for r in read(BONES)['structures']}
    items=[]
    for plural,kind in [('bones','bone'),('muscles','muscle'),('parts','part')]:
        for row in inventory['missing'][plural]:
            item=dict(key=key(kind,row),kind=kind,catalogueId=row['id'],part=row.get('part'),
                      ru=row['ru'],lat=row['lat'],sideInCatalogue=row.get('side'),
                      initialNoModel=True,currentNoModel=True,status='research_only_not_admitted',
                      admitted=False,fullAnatomicalAcceptance=False,integratedFile=None,
                      evidence=[relative(run/'inventory.json')],resources=[],history=[])
            if kind=='bone':
                old=bones[row['id']]
                item.update(issueIds=[old['issueId']],methods=old['methods'],resources=old['resources'],
                            blocker=old['blocker']+' '+old.get('newBlocker',''),nextStep=old['nextStep'])
                item['evidence'].append(BONES)
            elif row['id']=='interspinales_cervicis_left':
                old=read(MIRROR)
                item.update(issueIds=['ANAT-002'],resources=[dict(file=old['candidateFile'],sha256=old['candidateSHA256'],license=old['license'])],
                            blocker=old['reason'],nextStep='Подтвердить локальную среднюю плоскость и двусторонние площадки прикрепления; C7–T1 отдельно отсутствует.')
                item['methods']=[method(c,s,t,[MIRROR]) for c,s,t in [
                    ('A','completed_candidate_not_admitted','Исходный левый набор: выборочные проникновения до 1,647 мм.'),
                    ('B','prior_named_source_assessed','BP3D FMA71309: пять левых пучков, учебный допуск не выдан.'),
                    ('C','completed_candidate_not_admitted','Отражение принятой правой группы X=0: разрывы концов 1,237–2,984 мм.'),
                    ('D','completed_partial_extraction','Пять пучков C2–C7 выделены; C7–T1 отсутствует.'),
                    ('E','blocked_missing_constraints','Нет зарегистрированных площадок прикрепления; произвольные сдвиги не выполнены.'),
                    ('F','not_attempted','Нужны лицензированные изображения с различимыми пучками и совместимая регистрация.')]]
                item['evidence'].extend([MIRROR,str(Path(MIRROR).parent/'blender-review.json').replace('\\','/')])
            else:
                old=plans[(row['id'],row.get('part'))]
                ev=[PLAN,'research/'+old['priorReport']]
                item.update(issueIds=[old['issue']],blocker=old['requiredData'],nextStep=old['requiredData'])
                item['methods']=[
                    method('A','prior_inventory_reused',old['priorSourceAssessment'],ev),
                    method('B','prior_source_search_reused',old['priorSourceAssessment'],ev),
                    method('C','blocked_no_admitted_counterpart','Нет принятого отдельного экземпляра противоположной стороны; отражение не создаёт отсутствующие границы.',ev),
                    method('D','assessed_boundaries_missing',old['requiredData'],ev),
                    method('E','prototype_research_only' if old.get('prototype_created') else 'assessed_not_generated',old['method']+'; '+old['requiredData'],ev),
                    method('F','not_attempted','Нужны лицензированные изображения с различимой структурой, сегментацией и регистрацией; доступность не заявлена.',ev)]
                if row['id']=='palmaris_brevis' or row['id'].startswith('omohyoid_'):
                    item['evidence'].append(RECENT)
                    item['doNotRepeatWithout']='Новые границы/исходник или новый обоснованный метод; предыдущие PB/omohyoid проверки завершены.'
                item['evidence'].extend(ev)
            item['allApplicableMethodsExhausted']=False
            item['history']=[dict(at=now(),event='seed_from_existing_evidence',evidence=item['evidence'])]
            items.append(item)
    return dict(schemaVersion=1,revision=0,createdAt=now(),updatedAt=now(),
                scope='Execution checkpoint for 20 bone owners, 14 muscles and 21 parts. ANATOMY_ISSUES.md remains the only task-status registry.',
                issueRegistry='ANATOMY_ISSUES.md',inventory=relative(run/'inventory.json'),checkpoint=relative(run/'checkpoint.json'),
                initialCounts=inventory['counts'],currentCounts=inventory['counts'],items=items,
                dependentOpenIssueIds=['GEO-THORAX-CARTILAGE-COVERAGE','GEO-FOOT-SESAMOID-PARTS','GEO-007','GEO-011','GEO-012','LIC-001','LIC-004','SRC-009'],
                admissionPolicy=dict(educational='Identity, side, scale, major relations and rights verified; no known major conflict; real loading/selection/BVH/browser evidence required.',
                                     full='Separate confirmed geometry/attachments/regions and scientific acceptance; educational admission never closes it.'),
                resume=dict(activeBatch='new_z_anatomy_parts_and_bonehub_metacarpals',
                            next='Read this state and newest batch evidence; do not repeat unchanged baseline, PB or omohyoid checks.',
                            stage8Started=False),batches=[])

def validate(state):
    issues=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf8')
    inventory=read(state['inventory'])
    expected={key(k,r) for plural,k in [('bones','bone'),('muscles','muscle'),('parts','part')] for r in inventory['missing'][plural]}
    keys=[r['key'] for r in state['items']]
    assert len(keys)==55 and len(set(keys))==55
    assert {r['key'] for r in state['items'] if r['currentNoModel']}==expected
    assert state['currentCounts']==inventory['counts']
    checks=0
    for row in state['items']:
        expected_key=key(row['kind'],dict(id=row['catalogueId'],part=row['part']))
        assert row['key']==expected_key, 'Checkpoint key does not match catalogue identity'
        assert row['issueIds'], 'A checkpoint row must refer to the issue registry'
        for issue in row['issueIds']:
            assert re.search(r'(?<![\w-])'+re.escape(issue)+r'(?![\w-])',issues),issue
        assert len(row['methods'])==6 and {m['code'] for m in row['methods']}==set('ABCDEF')
        for p in row['evidence']+[p for m in row['methods'] for p in m['evidence']]:
            assert (ROOT/p).is_file(),p
        if row['admitted']:
            assert not row['currentNoModel'] and (ROOT/row['integratedFile']).is_file()
            assert all(row['admissionChecks'].get(k) for k in ['rights','anatomicalBasics','Blender','Node','BVH','browser1280','browser390'])
        else:
            assert row['currentNoModel'] and row['integratedFile'] is None
        checks+=1
    for issue in state['dependentOpenIssueIds']: assert issue in issues,issue
    return dict(valid=True,rows=checks,counts=state['currentCounts'],revision=state['revision'])

def save(state,run,batch):
    state['revision']+=1;state['updatedAt']=now();state['batches'].append(batch)
    validate(state)
    raw=(json.dumps(state,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    snap=run/f"state-{state['revision']:04d}.json"
    with snap.open('xb')as f:f.write(raw)
    temporary=STATE.with_suffix('.json.tmp')
    with temporary.open('xb')as f:f.write(raw)
    temporary.replace(STATE)
    print(json.dumps(dict(snapshot=relative(snap),sha256=hashlib.sha256(raw).hexdigest(),**validate(state))))

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['init','append','validate']);p.add_argument('run',nargs='?');p.add_argument('batch',nargs='?');a=p.parse_args()
    if a.command=='validate': print(json.dumps(validate(read(STATE))));return
    run=(ROOT/a.run).resolve();assert run.is_dir()
    if a.command=='init':
        save(init(run),run,dict(id='initial-consolidation',at=now(),evidence=[relative(run/'inventory.json')],integrated=0));return
    state=read(STATE);batch=read(a.batch);bykey={r['key']:r for r in state['items']}
    assert batch['id'] not in {b['id'] for b in state['batches']}
    for update in batch.get('updates',[]):
        row=bykey[update['key']];previous=copy.deepcopy(row)
        row.update({k:v for k,v in update.items() if k not in ['history','key']})
        row['history']=previous['history']+[dict(at=now(),event=batch['id'],previousStatus=previous['status'],evidence=batch['evidence'])]
    if batch.get('inventory'):
        state['inventory']=batch['inventory'];state['currentCounts']=read(batch['inventory'])['counts']
    if batch.get('resume'):state['resume']=batch['resume']
    save(state,run,{k:v for k,v in batch.items() if k!='updates'})

if __name__=='__main__':main()
