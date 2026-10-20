"""Reproducible addressed review inventory; no inferred coordinates."""
from pathlib import Path
from collections import Counter
import json, sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage5-skull-batch7-2026-10-16'
sys.path.insert(0,str(ROOT/'scripts'))
from head_skull_batch7 import BONES, reviewed_decisions, additional_records, decision_sources
from ta98 import BONE,T
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
head=json.loads((ROOT/'site/pins-head.js').read_text(encoding='utf-8').split('push(...',1)[1].rsplit(');',1)[0])
before={p['id']:p for p in read(OUT/'head-baseline.json')}
decisions=reviewed_decisions();records=[];catalogue=[]
for p in head:
    if p['b'] not in BONES: continue
    assert p['c'] in BONE[p['b']]
    assert p['ru']==T[p['c']][1] and p['lat']==T[p['c']][0].split(';')[0].strip()
    row=dict(id=p['id'],bone=p['b'],code=p['c'],ru=p['ru'],latin=p['lat'],definition=p['x'],kind=p['geometryKind'],refs=p['refs'],coordinateAcceptance=False,extentAcceptance=False)
    catalogue.append(row)
    if (p['b'],p['c']) in decisions:
        row=dict(row,beforeKind=before[p['id']]['geometryKind'],rationale=decisions[p['b'],p['c']]['reason'])
        records.append(row)
remaining=[dict(id=p['id'],bone=p['b'],code=p['c'],ru=p['ru']) for p in head if p['geometryKind']=='unknown']
write('geometry-kind-review.json',dict(records=records,byKind=dict(Counter(r['kind'] for r in records)),byBone=dict(Counter(r['bone'] for r in records)),explicit=len(head)-len(remaining),remaining=remaining,remainingTarget=[]))
write('catalogue-review.json',dict(records=catalogue,recordCount=len(catalogue),uniqueCodes=len({r['code'] for r in catalogue}),missingApplicableTA98Codes=[],note='Own TA98 bone lists complete. This is not exhaustive educational anatomy. RU/Latin matched reconciled local table; five official parent lists consulted live.'))
extras=list(additional_records());pending=[]
def candidate(bone,key,ru,scope):
    pending.append(dict(candidateId='candidate_'+bone+'_'+key,bone=bone,ru=ru,scope=scope,status='requires_review',appId=None,p=None,
        acceptance='Independent addressed description, nomenclature/part mapping, no existing equivalent, educational scope; geometry accepted separately.'))
for bone in BONES:
    group=bone.removesuffix('_right').removesuffix('_left')
    if group not in ('nasal','lacrimal','inferior_concha','vomer'):continue
    faces={'nasal':[('external','Наружная'),('internal','Внутренняя')],'lacrimal':[('lateral','Латеральная'),('medial','Медиальная')],'inferior_concha':[('medial','Медиальная'),('lateral','Латеральная')],'vomer':[('right','Правая боковая'),('left','Левая боковая')]}[group]
    for key,label in faces:candidate(bone,'surface_'+key,label+' поверхность','surface subdivision')
    borders=[('superior','Верхний'),('inferior','Нижний')]
    if group=='nasal':borders += [('lateral','Латеральный'),('medial','Медиальный')]
    elif group in ('lacrimal','vomer'):borders += [('anterior','Передний'),('posterior','Задний')]
    for key,label in borders:candidate(bone,'border_'+key,label+' край','border, not automatically an independent landmark')
    if group=='inferior_concha':
        for key,label in [('anterior','Передний'),('posterior','Задний')]:candidate(bone,'end_'+key,label+' конец','extremity')
    if group=='nasal':candidate(bone,'septal_crest_contribution','Вклад в перегородочный гребень носовых костей','must resolve paired contributions versus single shared crest; SH-087 scope')
assert len(pending)==44
write('completeness-review.json',dict(added=extras,pending=pending,counts=dict(added=8,pendingCandidates=44),
    evidenceLimit='44 descriptive subdivisions are candidates for catalogue scope, not 44 proven anatomical errors. Gray-family atlas derivatives are not two independent confirmations. No coordinates, TA codes or geometry invented.',
    duplicateReview='Zygomatic apertures are not intrabony canals; maxillary process of zygoma is not zygomatic process of maxilla. Descending lacrimal process is not hamulus or conchal lacrimal process. No new whole bones.',
    geometryIssue='GEO-FACIAL-EXTRA',catalogueIssue='CAT-FACIAL-EXTRA'))
refs={r['id']:r for d in decisions.values() for r in decision_sources(d)}
for p in extras:
    for r in p['refs']:refs[r['id']]=r
pubmed=[]
for name in ['pubmed-targeted.json','pubmed-kawata.json','pubmed-lacrimal.json']:pubmed+=read(OUT/name)['records']
write('source-review.json',dict(sources=list(refs.values()),pubmedRecords=pubmed,
    terminology=[dict(code=code,url='https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/Entity%20TA98%20EN/'+code[1:]+'%20Entity%20TA98%20EN.htm') for code in ['A02.1.14.001','A02.1.10.001','A02.1.09.001','A02.1.08.001','A02.1.11.001']],
    api='Official ESearch/EFetch: 6 requests including exploratory search; five addressed publication records verified. Metadata alone is not claim confirmation.',
    independence='Kim 2013 and Kawata 2024: independent original micro-CT samples. Elsevier and IMAIOS cite Gray 2016; not counted as independent confirmations of the same Gray-derived statement. Basrah handout repeats Gray; excluded as independent evidence.',
    accessLimits=['Gray 1918 and Palacky open text read; older process taxonomy not substituted for TA98.', 'Bookshelf NBK544257/NBK532870 and direct PMC blocked by CAPTCHA; indexed snippets not claimed as full reading.', 'Liu 2020: indexed English abstract; direct PMC/PubMed CAPTCHA. Kawata publisher full text available.', 'Buchanan returned 403; prior addressed source pairs retained, no new full reading claimed.', 'No new lawful access to complete modern Russian/Sobotta/Netter editions; no copying licensed illustrations.'],
    reused='All old per-record source pairs retained; scientific support for entity type separate from disputed localization and geometry.',geometryAccepted=False))
b=read(OUT/'blender-review.json')
paired=[r for r in b['records'] if '_right_' in r['id'] or '_left_' in r['id']]
side_sign_mismatches=[r['id'] for r in paired if ('_right_' in r['id'] and r['p'][0]>=0) or ('_left_' in r['id'] and r['p'][0]<=0)]
write('geometry-observations.json',dict(tool='Blender MCP',recordCount=40,viewedImages=[i['file'] for i in b['images']],
    pairedCoordinateSignCheck=dict(records=len(paired),mismatches=side_sign_mismatches,note='Project coordinate convention only; not independent anatomical acceptance.'),
    maxNearestSurfaceMm=max(d for r in b['records'] for d in r['nearestSurfaceMm'].values()),transformation='Three (x,y,z) -> Blender (x,-z,y)',
    observations=['Nine named bone meshes present. Major plates and processes visible in 18 views; some old glyphs occluded in individual views.', 'Fine zygomatic aperture boundaries/intrabony courses and nasal apertures not established from smoothed external meshes.', 'Lacrimal crest/hamulus and conchal processes have relief, but precise boundaries and the new descending process extent are not accepted.', 'Vomer alae and lateral grooves have only one stored point each; bilateral coverage unconfirmed. Crista/pars terminology disagreement retained.'],
    coordinateAcceptance=False,extentAcceptance=False,sourceUnchanged=b['sourceUnchanged'],originalScenePreserved=b['originalScenePreserved'],
    note='Small nearest-surface distance only verifies projection. Red 0.8 mm glyphs are display markers, not anatomical dimensions.'))
shared=read(ROOT/'research/stage5-skull-batch6-2026-10-16/shared-decisions.json')
notes={
 'SH-022':'Zygomatic contribution to temporal fossa distinguished from its own temporal surface; previous partial boundary map remains.',
 'SH-024':'Zygomatic arch/adjacency does not by itself establish membership of every infratemporal-fossa boundary.',
 'SH-065':'Vomer-related variant canal: name/adjacency not evidence of a complete continuous lumen and all bone roles.',
 'SH-066':'Own vomer alae do not establish vomerorostral canal boundaries or independent geometry.',
 'SH-081':'Own lacrimal groove, maxillary groove, sac fossa and bony nasolacrimal canal remain distinct; no silent merging.',
 'SH-086':'Nasal cavity needs complete defined wall/floor/roof scope; no new relation from proximity.',
 'SH-087':'Gray detailed bony septum includes nasal/frontal/sphenoid contributions, while modern core descriptions focus on ethmoid/vomer/maxillary/palatine crests. Resolve scope before accepting a purported exhaustive six-instance relation.',
 'SH-090':'Concha contribution to lower boundary not evidence for all middle-meatus walls or aperture membership.',
 'SH-091':'Inferior concha roofs inferior meatus; floor/lateral wall scope still needs addressed exhaustive mapping.',
 'SH-092':'Nasolacrimal duct opening is not the entire bony canal; soft-tissue versus bone landmark scope unresolved.',
 'SH-093':'Common meatus space between septum and conchae: local bone surfaces are not independent duplicate spaces.',
 'SH-095':'Nasopharyngeal meatus scope and relationship to posterior conchal ends require independent addressed definition.'}
for row in shared['rows']:
    key=row.get('issueId',row.get('id'))
    if key in notes:row['batch7Review']=notes[key]
write('shared-decisions.json',dict(previous=shared,reviewedNotes=notes,newSharedRelations=0,newSharedInstances=0,closedCandidates=0,remaining=27,
    distinction='relatedLandmarks in eight supplemental cards are navigation references, not new co-ownership relations. Existing SH-082/085 and skull sutures remain unchanged.'))
print(json.dumps(dict(classified=len(records),catalogue=len(catalogue),additional=len(extras),pendingCatalogue=len(pending),remaining=len(remaining),kinds=dict(Counter(r['kind'] for r in records)))))
