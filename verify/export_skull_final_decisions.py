"""Reconcile all named candidates and evidence scopes, without mass anatomy inference."""
from pathlib import Path
import json, re
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage5-skull-final-2026-10-17'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(name,d):(OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inv=load(OUT/'inventory-current.json');before=load(OUT/'inventory-before.json')
new=[p for p in inv['extras'] if p['id'] not in {q['id'] for q in before['extras']}]
bycandidate={p['candidateId']:p for p in new}
facial=load(ROOT/'research/stage5-skull-batch7-2026-10-16/completeness-review.json')['pending']
mandible=load(ROOT/'research/stage5-skull-batch8-2026-10-16/catalogue-candidates.json')['rows']
maxilla=[dict(candidateId=f'maxilla-{side}-{key}',bone=f'maxilla_{side}',ru=ru,issue='CAT-MAXILLA-EXTRA')
         for side in ('right','left') for key,ru in [('facial-incisive-fossa','Лицевая резцовая ямка'),('canine-eminence','Клыковое возвышение')]]
rows=[]
for group,candidates,issue in [('facial',facial,'CAT-FACIAL-EXTRA'),('mandible',mandible,'CAT-MANDIBLE-EXTRA'),('maxilla',maxilla,'CAT-MAXILLA-EXTRA')]:
    for c in candidates:
        key=c['candidateId'];p=bycandidate.get(key)
        row=dict(candidateId=key,issue=issue,group=group,name=c.get('ru',c.get('name')),bone=c.get('bone','mandible'),
                 existingParent=c.get('parentId'),coordinateAcceptance=False,extentAcceptance=False)
        if p:
            row.update(decision='added_distinct_card',appId=p['id'],kind=p['geometryKind'],refs=p['refs'],
                rationale='Уточнение имеет самостоятельный анатомический смысл. Родительская кость/часть и соседняя структура не эквивалентны; старые ID сохранены. Источники подтверждают сущность, не границы GLB.',
                confidence='high_for_entity_only',remaining='Геометрическая приёмка в GEO-SKULL-FINAL-EXTRA; не назначать p по соседнему маркеру.')
        else:
            why='Описательная часть подтверждается Gray; найденная страница Complete Anatomy ссылается на Gray/Standring, поэтому не засчитана независимой второй опорой. Новая карточка пока не принята; существование родительской кости не считается эквивалентом отдельной части.'
            if 'septal_crest' in key:
                why+=' Сначала согласовать локальные вклады обеих носовых костей с одним общим гребнем; две независимые карточки общего гребня недопустимы.'
            elif '_end_' in key:
                why='Gray описывает передний/задний концы раковины. Найденное современное краткое определение перечисляет поверхности и края, но не даёт независимой адресной проверки границ концов и необходимости отдельной карточки.'
            elif 'facial_artery_groove' in key:
                why='Gray описывает иногда присутствующую борозду у нижнего края. Ход лицевой артерии сам по себе не доказывает обязательную костную борозду; независимое адресное описание вариабельности и наличие на этом образце не приняты.'
            row.update(decision='requires_independent_scope_confirmation',appId=None,kind=None,rationale=why,
                confidence='insufficient_for_new_card',remaining='Этап 5: независимый адресный атлас/исследование, название, иерархия и решение о самостоятельном отображении; затем регрессия. Не переносится в этап окраски.',
                sourceLeads=['Gray/Lewis, Osteology: corresponding bone section',
                    'Elsevier Complete Anatomy: corresponding bone, Key Features & Anatomical Relations (Gray-based; not independent)'] if group=='facial' else ['Gray/Lewis, PDF pp.140–142, inferior border of mandible'])
        rows.append(row)
assert len(rows)==67 and sum(r['decision']=='added_distinct_card' for r in rows)==25
previous=load(ROOT/'research/stage5-skull-batch8-2026-10-16/shared-decisions.json')
while isinstance(previous.get('previous'),dict):previous=previous['previous']
shared=[]
for c in previous['rows']:
    num=c['issueId'].split('-')[1];instances=[p for p in inv['shared'] if p.get('c')==c['code']]
    reason=c['retainedReason']
    if num=='083':
        reason='Связи sphenoid/frontal уже реализованы в партии 3 по Gray и независимой главе Rootman. Старая причина об отсутствии второй опоры устарела. Не приняты сторона прежнего собственного маркера, его partOf и полный контур конкретного образца.'
    shared.append(dict(issueId=c['issueId'],code=c['code'],name=c['name'],
        existingCanonicalIDs=[p['id'] for p in instances],currentRelations=[{'id':p['id'],'relations':p['relations']} for p in instances],
        decision='retain_confirmed_partial_representation' if instances else 'do_not_publish_unconfirmed_relationship',
        remaining=reason,refs=[p['refs'] for p in instances],scientificMembershipConfirmed=bool(instances),
        coordinateAcceptance=False,extentAcceptance=False,nextStage=5,
        releaseEffect='Не использовать как точную карту стенок/каналов; справочное отображение допустимо с ограничением.',
        priorEvidence='research/stage5-skull-batch8-2026-10-16/shared-decisions.json; original source review and registry criteria retained'))
assert len(shared)==27
save('candidate-decisions.json',dict(date='2026-10-17',totalCandidates=94,catalogue=rows,shared=shared,
    catalogueAdded=25,cataloguePending=42,sharedPending=27,sharedPreviouslyPublishedFamilies=sum(bool(r['existingCanonicalIDs']) for r in shared),
    newSharedRelations=0,scope='All 94 screened and reconciled; not 94 accepted scientific claims. 42 catalogue decisions and 27 shared acceptance criteria remain unresolved.'))
extent=load(ROOT/'site/skull-geometry-review.json');byextent={r['pinId']:r for r in extent['rows']}
geometry=[]
for p in inv['own']:
    old=byextent[p['id']]
    geometry.append(dict(id=p['id'],bone=p['b'],code=p['c'],name=p['ru'],kind=p['geometryKind'],p=p['p'],
        localization=p.get('loc'),currentCoordinateAcceptance=p.get('geometryReview',{}).get('coordinateAcceptance'),
        formalCoordinateAcceptancePresent=p.get('geometryReview',{}).get('coordinateAcceptance') is True,
        historicalExtentStatus=old['status'],historicalCriterion=old['criterion'],
        historicalExpertValidation=extent['independentExpertValidation'],
        representationNeeded=p['geometryKind'],extentIsNotDefinedByMarker=p['geometryKind']!='point',
        laterality=p.get('lateralityReview'),sourceRefs=p.get('refs',[]),
        nextAction='Адресная анатомическая и экземплярная приёмка; использовать прежние наблюдения, не выводить название из расстояния до сетки.'))
save('landmark-evidence.json',dict(rows=geometry,counts=dict(Counter(p['geometryKind'] for p in inv['own'])),
    localizationCounts=dict(Counter(p.get('loc') for p in inv['own'])),
    formalAcceptedCoordinateCount=sum(r['formalCoordinateAcceptancePresent'] for r in geometry),
    warning='0 формальных coordinateAcceptance=true не означает 521 доказанную ошибку. 325 surface, 182 projection, 14 variant — прежние уровни доказательств, не число независимо принятых точек.',
    historicalExtentCounts=extent['counts'],historicalExtentExpertValidation=False,
    documentedLimitedSharedAnchors=[dict(id=p['id'],anchors=p.get('anchors')) for p in inv['shared'] if p.get('anchors')],
    midlineSignFlags=[dict(id=p['id'],bone=p['b'],x=p['p'][0],interpretation='Near-midline sign flag only; owner-mesh proximity passed. Not a diagnosed side error.') for p in inv['own'] if p['b'].endswith('_left') and p['p'][0]<0 or p['b'].endswith('_right') and p['p'][0]>0],
    currentDataNoNewCoordinates=True))
save('shared-kind-pending.json',dict(issue='PIN-SHARED-KIND',rows=[dict(id=p['id'],name=p['ru'],code=p['c'],relations=p['relations'],refs=p['refs'],geometryKind=p['geometryKind']) for p in inv['shared'] if p.get('geometryKind')=='unknown'],
    reason='32 old canonical skull cards had no representation field and no UI warning. Unknown is explicit now; it is not an anatomical classification. Own 521 records remain classified.'))
save('unlocated-shared-ids.json',[p['id'] for p in inv['shared'] if not p.get('p')])
save('new-cards.json',dict(records=new,count=len(new),newCoordinates=0,issue='GEO-SKULL-FINAL-EXTRA'))
boneRows=[]
for b in inv['bones']:
    own=[p for p in inv['own'] if p['b']==b['id']]
    boneRows.append(dict(id=b['id'],ru=b['ru'],lat=b['lat'],code=b['code'],ownIDs=[p['id'] for p in own],
        kinds=dict(Counter(p['geometryKind'] for p in own)),unknown=0,
        supplementaryIDs=[p['id'] for p in inv['extras'] if p['b']==b['id']],
        sharedIDs=[p['id'] for p in inv['shared'] if any(r['bone']==b['id'] for r in p['relations'])],
        fullTA98ApplicableCataloguePresent=True,fullOsteologyAccepted=False,
        evidence='Eight preserved batch reports plus current candidate/evidence ledgers. TA98 presence is not exhaustive descriptive anatomy.'))
save('bone-review.json',dict(bones=boneRows,count=22,own=521,shared=69,extras=len(inv['extras']),
    liveSkullLandmarks=521+69+len(inv['extras']),boneCardsCountedSeparately=22,
    wholeSkullTeachingCatalogueCount=97,wholeSkullCatalogueNotAddedToLiveCount=True))
lines=['# Поимённые решения итоговой проверки черепа','',
       '94 кандидата рассмотрены. Приняты 25 новых карточек; 42 каталожных уточнения и 27 общих критериев остаются открытыми. Это не счётчик геометрической приёмки. Подробные ссылки: [JSON](candidate-decisions.json).','',
       '| Кандидат | Структура | Решение / appId | Следующий шаг |','|---|---|---|---|']
for r in rows:lines.append('| '+r['candidateId']+' | '+str(r['name'])+' | '+(r['appId'] or 'Требует независимой проверки')+' | '+r['remaining']+' |')
lines+=['','## Общие структуры','','| ID | Уже опубликованные объекты | Что не принято |','|---|---|---|']
for r in shared:lines.append('| '+r['issueId']+' | '+(', '.join(r['existingCanonicalIDs']) or 'Нет общего экземпляра')+' | '+r['remaining']+' |')
(OUT/'candidate-decisions.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'catalogueCandidates':67,'added':25,'cataloguePending':42,'shared':27,'publishedPartialSharedFamilies':sum(bool(r['existingCanonicalIDs']) for r in shared),'allSkullOwn':len(geometry)}))
