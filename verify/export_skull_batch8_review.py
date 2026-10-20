"""Export the reviewed finite scope; never infer types or coordinates from names."""
from pathlib import Path
from collections import Counter
import json,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage5-skull-batch8-2026-10-16'
sys.path.insert(0,str(ROOT/'scripts'))
from head_skull_batch8 import reviewed_decisions, additional_records, PAIRED, TEXT_FIXES

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(name,data):(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
before=read(OUT/'head-baseline.json')
s=(ROOT/'site/pins-head.js').read_text(encoding='utf-8');head=json.loads(s[s.index('push(...')+8:s.rindex(');')])
byid={p['id']:p for p in head};decisions=reviewed_decisions();rows=[]
for old in before:
    d=decisions.get((old['b'],old['c']))
    if not d:continue
    p=byid[old['id']]
    rows.append(dict(id=p['id'],bone=p['b'],code=p['c'],ru=p['ru'],lat=p['lat'],previousKind=old['geometryKind'],
        kind=p['geometryKind'],rationale=d['reason'],refs=p['refs'],confidence='high_for_entity_type_only',
        coordinateAcceptance=False,extentAcceptance=False,remaining='PIN-002/PIN-004/GEO-001/002/003; no exact extent or bilateral specimen coverage accepted'))
assert len(rows)==37 and all(r['previousKind']=='unknown' for r in rows)
save('geometry-kind-review.json',dict(date='2026-10-16',rows=rows,classified=len(rows),kindCounts=dict(Counter(r['kind'] for r in rows)),
    previousExplicitPreserved=484,remaining=[p['id'] for p in head if p['geometryKind']=='unknown'],remainingTarget=[],
    ownSkullCount=521,explicitSkullCount=521,scope='34 mandibular + 2 occipital + 1 ethmoidal; not anatomy/shape completion'))
target=[p for p in head if p['b']=='mandible' or (p['b'],p['c']) in decisions]
save('catalogue-review.json',dict(records=[dict(id=p['id'],bone=p['b'],code=p['c'],ru=p['ru'],lat=p['lat'],kind=p['geometryKind']) for p in target],
    recordCount=len(target),mandibleOwnRecords=37,missingApplicableTA98Codes=[],
    descriptionFixes=[dict(id='head_mandible_A02_1_15_'+f'{n:03}',description=t) for n,t in TEXT_FIXES.items()],
    note='Own TA98 catalogue is present; this is not a complete atlas of all descriptive subdivisions or variants. Additional cards are counted separately.'))
save('bilateral-coverage.json',dict(issue='CO-MANDIBLE-BILATERAL',
    paired=[p['id'] for p in head if p['b']=='mandible' and int(p['c'][-3:]) in PAIRED],
    variableSpines=['head_mandible_A02_1_15_010','head_mandible_A02_1_15_011'],
    coordinateChanges=0,acceptance=False,reason='One preserved representative marker per catalogue entity does not demonstrate both sides or the number of spines.'))
extra=list(additional_records());save('new-cards.json',dict(count=len(extra),records=extra,newCoordinates=0,issue='GEO-MANDIBLE-EXTRA'))
oldshared=read(ROOT/'research/stage5-skull-batch7-2026-10-16/shared-decisions.json')
save('shared-decisions.json',dict(previous=oldshared,remaining=27,newSharedRelations=0,newSharedInstances=0,closedCandidates=0,
    reviewedNotes={
      'SH-024':'Mandibular ramus is a lateral boundary in the existing NBK537034/PMC9180479 evidence; the full role map, including zygomatic contribution and soft-tissue boundaries, remains unresolved. No partial list is promoted to complete ownership.',
      'SH-022':'Coronoid/temporalis continuity does not establish mandibular ownership of every temporal-fossa landmark; existing candidate and role limitations retained.',
      'SH-061':'Palatal incisive canals are anatomically distinct from newly catalogued mandibular incisive canals; no cross-bone owner relation added.',
      'TMJ':'Mandibular head and temporal mandibular fossa remain separate bone features. Joint articulation is not shared ownership of either feature; disc/capsule are a future module.',
      'SYMPHYSIS':'Adult fused mandibular symphysis does not create two new bone owners.'}))
candidates=[]
for key,name,parent in (
 ('body_external_surface','Наружная поверхность тела','002'),('body_internal_surface','Внутренняя поверхность тела','002'),
): candidates.append(dict(candidateId='mandible_'+key,name=name,parentId='head_mandible_A02_1_15_'+parent))
for side in ('right','left'):
    for key,name,parent in (
      ('ramus_lateral_surface','Латеральная поверхность ветви','024'),('ramus_medial_surface','Медиальная поверхность ветви','024'),
      ('ramus_anterior_border','Передний край ветви','024'),('ramus_posterior_border','Задний край ветви','024'),
      ('condylar_articular_surface','Суставная поверхность головки','036'),('incisive_fossa','Резцовая ямка нижней челюсти','002'),
      ('lateral_lingual_foramina','Латеральные язычные отверстия','002'),('facial_artery_groove','Борозда лицевой артерии у нижнего края','003'),
    ): candidates.append(dict(candidateId='mandible_'+side+'_'+key,name=name,side=side,parentId='head_mandible_A02_1_15_'+parent))
candidates.append(dict(candidateId='mandible_median_lingual_foramina',name='Срединные язычные отверстия',parentId='head_mandible_A02_1_15_004'))
assert len(candidates)==19
for c in candidates:
    c.update(status='requires_catalogue_mapping_and_independent_scope_review',issue='CAT-MANDIBLE-EXTRA',
      coordinateAcceptance=False,whyNotAdded='Separate canonical scope/name/representation must be reconciled with existing parent card; not 19 proven absent structures.',
      sourceLead='Gray PDF pp.140–142; Champagne et al. PMID38098242 for lingual foramina; existing addressed mandibular sources. These are leads, not two verified sources for every candidate.')
save('catalogue-candidates.json',dict(count=len(candidates),rows=candidates,previous44FacialCandidatesPreserved=True,
    distinction='19 refinement candidates, not 19 diagnosed anatomical omissions; six independently supported additions are in new-cards.json.'))
print(json.dumps({'classified':37,'kinds':dict(Counter(r['kind'] for r in rows)),'ownCards':len(target),'pairedCoverage':len(PAIRED),'newCards':len(extra),'refinementCandidates':len(candidates)}))
