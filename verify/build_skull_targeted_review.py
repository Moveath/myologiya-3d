"""Freeze addressed decisions, without modifying anatomical data or old evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/stage5-skull-targeted-2026-10-17'
RUN = ROOT / 'research/evidence-runs/skull-targeted-data-2026-10-17T06-23-51-232Z-rqCZ6e'

def read(p):
    return json.loads(p.read_text(encoding='utf8'))

def save(name, value):
    with (OUT/name).open('x', encoding='utf8') as f:
        if isinstance(value, str): f.write(value)
        else: json.dump(value, f, ensure_ascii=False, indent=2)

def main():
    data=read(RUN/'result.json'); now=read(RUN/'inventory.json')
    old=read(ROOT/'research/stage5-skull-final-2026-10-17/candidate-decisions.json')
    lookup={}
    for p in data['added']:
        for cid in ([p['candidateId']] if p.get('candidateId') else p.get('candidateIds',[])):
            lookup[cid]=p
    catalogue=[]
    for previous in old['catalogue']:
        if previous['appId']: continue
        r=dict(previous); p=lookup[r['candidateId']]
        r.update(appId=p['id'],kind=p['geometryKind'],refs=p['refs'],confidence='high_for_entity_not_specimen',
            decision='anatomical_variant' if p.get('anatomicalVariation') else 'one_shared_entity' if p.get('candidateIds') else 'separate_card_required',
            rationale=p['x'],remaining='Каталог проверяется отдельно от формы, границ и положения данного образца; GEO-SKULL-TARGETED-EXTRA. Латинский код не придуман.')
        r['nomenclature']='Дополнительная описательная карточка; отдельный TA98-код не присвоен, lat пусто. Русское описательное название не объявлено официальным термином FIPAT.'
        catalogue.append(r)
    assert len(catalogue)==42 and len({r['appId'] for r in catalogue})==41
    shared=[]
    for previous in old['shared']:
        r=dict(previous); num=int(r['issueId'].split('-')[-1])
        if num in [50,87]:
            p=next(p for p in data['added'] if p['id']==f'shared_skull_{num:03d}')
            r.update(decision='publish_confirmed_bone_membership',scientificMembershipConfirmed=True,
                existingCanonicalIDs=[p['id']],currentRelations=[{'id':p['id'],'relations':p['relations']}],refs=[p['refs']],
                remaining='Костной состав и роли вкладов подтверждены Gray и независимым Buchanan. Сохранён исходный критерий: нужно завершить связь конкретных локальных частей с общим объектом (partOf), не переназначая старые одиночные координаты. Геометрия и индивидуальные границы не приняты.')
            if num==87:r['remaining']+=' Общий гребень носовых костей уже связан partOf; основные пластинки и остальные гребни ещё не сведены в полную иерархию.'
            r['newRelations']=p['relations']
        elif num==49:
            r['remaining']+=' Buchanan описывает боковые швы, но его краткий список костей ямки не даёт второго столь же явного подтверждения теменных вкладов. Не публикуется неполный перечень под видом целой области.'
        elif num==46:
            r['remaining']+=' В Buchanan найдено описание spheno-petrosal synchondrosis; его нельзя автоматически приравнять к открытому пространству щели или к соседнему каналу.'
        elif num in [60,61,62]:
            r['remaining']+=' Историческая схема Buchanan с четырьмя апертурами не принята как фиксированное количество у взрослого образца. Для .061/.062 сохраняются собственные maxilla-карточки, независимые дубликаты не созданы.'
        r['reviewMode']='new_addressed_evidence' if num in [46,49,50,60,61,62,87] else 'existing_addressed_evidence_reused_no_new_basis'
        r['closed']=False
        shared.append(r)
    assert len(shared)==27 and sum(r['scientificMembershipConfirmed'] for r in shared)==9
    decisions=dict(date='2026-10-17',catalogue=catalogue,shared=shared,classified=data['changedShared'],
        catalogueCandidates=42,catalogueEntitiesAdded=41,newSharedCandidates=2,newRecords=43,
        membershipConfirmed=9,newMembershipConfirmed=2,notConfirmed=18,rejected=0,sharedIssuesClosed=0,
        anatomyNotGeometry=True,sourceScope='No new full audit of 629 records. Existing FIPAT/TA98 and addressed refs reused; new Buchanan and verified NCBI studies supplement, not replace them.')
    save('decisions.json',decisions)
    lines=['# Поимённые решения текущей партии','',
        '42 кандидата → 41 структура: два вклада в гребень носовых костей сведены в одну общую карточку. Ещё две структуры добавлены из 27 кандидатов связей. Координаты не добавлялись.','',
        '| Candidate ID | Решение | appId | Тип |','|---|---|---|---|']
    for r in catalogue:lines.append(f"| {r['candidateId']} | {r['decision']} | {r['appId']} | {r['kind']} |")
    lines+=['','## Общие связи','', '| ID | Подтверждён состав | Решение / точный остаток |','|---|---|---|']
    for r in shared:lines.append(f"| {r['issueId']} | {'да' if r['scientificMembershipConfirmed'] else 'нет'} | {r['remaining']} |")
    lines+=['','## Типы 32 общих карточек','', '| appId | Тип | Обоснование |','|---|---|---|']
    for r in data['changedShared']:lines.append(f"| {r['id']} | {r['kind']} | {r['reason']} |")
    save('decisions.md','\n'.join(lines)+'\n')
    save('new-records.json',data['added'])
    save('inventory-current.json',now)
    # Read-only resource inventory, not repeated mesh/contour computation.
    previous=read(ROOT/'research/stage4-closure-2026-10-16/source-availability.json')
    resources={'priorReport':'research/stage4-closure-2026-10-16/source-availability.json',
        'paths':[{'path':r['path'],'existsNow':(ROOT/r['path']).exists()} for r in previous['missing_inputs'] if any(s in r['path'] for s in ['skull','temporal'])],
        'existingEvidence':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'existsNow':p.exists()} for p in [
            ROOT/'research/stage4-closure-2026-10-16/head-bones-source-extract.glb',
            ROOT/'research/stage4-closure-2026-10-16/head-bones-source-extract.provenance.json',
            ROOT/'research/stage4-closure-2026-10-16/Ear-CT-256.nrrd.header',
            ROOT/'research/stage4-closure-2026-10-16/Ear-seg-256.nrrd.header',
            ROOT/'research/stage4-closure-2026-10-16/Model_140_Malleus_Bone.vtk',
            ROOT/'research/stage4-closure-2026-10-16/Model_17_Stapes_Bone.vtk']],
        'GLBRecoveryLimit':previous['GLB_recovery_limit'],
        'newCTOrSegmentation':False,'newBlenderContourSearch':False}
    save('resource-availability.json',resources)
    rows=read(ROOT/'research/stage5-skull-final-2026-10-17/remaining-skull-issues.json')['rows']
    blockers=[]
    for r in rows:
        if not r['id'].startswith(('GEO','CO','PIN')) or r['id']=='PIN-SHARED-KIND':continue
        q={k:r[k] for k in ['id','title','status','originalAcceptanceCriterion']}
        q.update(existingResources='Опубликованные меши, исходные p/n, типы и прежние протоколы; декодирование GLB восстанавливает только сохранённую сетку.',
            required='Адресная анатомическая разметка того же образца: хеш ресурса, сторона, система координат, идентификаторы граней/вершин или полилиния/маска, принятые анатомом.',
            possibleNow='Подготовить адресное задание и экспертную разметку доступной внешней поверхности; автоматическая близость не закрывает анатомическую приёмку.',
            nextStage='5: разметка и доказательства; 6: визуализация только принятой разметки; 8: независимая приёмка.',
            releaseLimit='Не представлять непроверенную форму/положение как точную геометрию; справочный просмотр с ограничением допустим.',closed=False)
        if r['id'] in ['CO-JUG-right','CO-JUG-left']:
            q.update(required='Согласованные occipital/temporal того же образца с различимой полной апертурой; при недостатке сетки — исходная КТ/сегментация, регистрационная матрица и калибровка. Две стороны принять раздельно, контур согласовать с анатомом.',
                existingResources='Два ранее принятых ограниченных височных якоря; затылочный вклад и полный контур не подтверждены. Нового образца/сегментации нет.',
                possibleNow='Нет для достоверного полного контура/размеров. Повторное вычисление ближайшей поверхности доказательств не добавляет.')
        elif r['id'] in ['GEO-004','GEO-005','GEO-MANDIBLE-EXTRA']:
            q.update(required='КТ/микроКТ или сегментационные маски нужных каналов/полостей того же образца, стороны, разрешение и матрицы; проверить костные стенки, ветвление и входы/выходы отдельно.',
                existingResources='Внешние GLB и частичные дополнительные модели; заголовки SPL NRRD не содержат вокселей. Недостающие Halle/temporal источники перечислены в resource-availability.json.',
                possibleNow='Нет для стенок/ветвей, отсутствующих в сетке. Декодирование, срез поверхности и чужая КТ их не восстанавливают.')
        elif r['id']=='GEO-003':
            q.update(required='Идентифицированный образец каждого варианта из 14-ID перечня, открытая совместимая лицензия, изображение/сегментация и отдельная анатомическая приёмка.',possibleNow='Нет для отсутствующих вариантов; карточки остаются справочными без утверждения наличия в GLB.')
        elif r['id']=='GEO-006':
            q.update(required='Полноразмерные исходные VTK/сегментации всех нужных слуховых косточек и подтверждённая микроморфология; разрешение исходных данных и проверка экспорта.',existingResources='Два оригинальных SPL VTK (malleus/stapes) восстановлены и доступны; это не полный набор и не достаточная детализация всех поверхностей.',possibleNow='Частично: сохранённые VTK пригодны для сопоставления. Полный объём критерия без остальных исходников/микроданных не принят.')
        elif r['id']=='GEO-008':
            q.update(required='Разрешение на отдельную производную обработку, резервные исходники, доказательство анатомической допустимости удаляемых вырожденных элементов и проверка сохранения идентификаторов/экспорта.',possibleNow='Аудит уже выполнен. Без разрешения на обработку оригиналов и принятого метода их не исправлять; исходники защищены.',nextStage='4: производный безопасный конвейер после разрешения; 8: приёмка. Не задача раскраски.')
        elif r['id']=='GEO-009':
            q.update(required='Для оставшихся копланарных/неоднозначных контактов — строгие геометрические предикаты или независимый валидатор и разбор анатомически допустимых контактов. Повтор того же ограниченного алгоритма не является полной проверкой.',possibleNow='Нужны дополнительные алгоритмические доказательства/экспертная оценка; ранее проверенные пары и ограничения сохранены.',nextStage='4: расширение валидатора; 8: итоговая приёмка сетки.')
        elif r['id']=='GEO-010':
            q.update(required='Документированная цепочка исходного MRML/NRRD → VTK → GLB с единицами, осевыми матрицами, стороной и независимыми контрольными расстояниями того же образца.',existingResources='Оригинальный SPL MRML, два VTK и заголовки CT/label NRRD доступны. Сравнение масштаба уже проведено; прежние критерии полной ориентационной/экземплярной приёмки сохраняются.',possibleNow='Частично: цепочка метаданных доступна; не менять масштаб по визуальному сходству или усреднённому литературному размеру.')
        elif r['id']=='GEO-012':
            q.update(required='Независимый анатомический обзор моделей по принятой спецификации; идентифицированные источники, реперные изображения, допустимые размеры и документированная вариабельность.',possibleNow='Техническая подготовка возможна. Независимая экспертная приёмка отсутствует; UI/хеши её не заменяют.',nextStage='8: внешняя приёмка; локальные исправления после адресных замечаний в 5/6.')
        elif r['id'].startswith(('CO-ZYGOTEMP','CO-00')):
            q['required']+=' Для шва — разметка на обеих участвующих костях, не один близкий маркер; для ската — оба костных участка.'
        elif r['id'] in ['PIN-004','CO-VOMER-BILATERAL','CO-MANDIBLE-BILATERAL']:
            q['required']+=' Раздельная правая/левая приёмка каждого ID; не зеркалировать одиночный якорь и не принимать двусторонность по одному p.'
        elif r['id']=='PIN-005':
            q.update(required='По-ID происхождение старого p без loc, явный статус неопределённости и адресная проверка отображения. Нельзя массово присвоить surface.',possibleNow='Да для технического обозначения неизвестности; анатомическое подтверждение p отдельно. Не исправлялось в данной адресной партии.')
        elif r['id']=='PIN-002':
            q.update(required='Сохранить исходный набор 67 общих ID; для каждого определить нужную форму представления и доказанную разметку вместо массовой генерации точек.',existingResources='Исходный список 67 сохранён; три новые общие записи добавлены отдельным набором GEO-SKULL-TARGETED-EXTRA, не подменяют исходные 67.')
        if r['id']=='GEO-SKULL-FINAL-EXTRA':q['required']+=' Для трёх групп язычных отверстий требуется видимость отверстий/каналов в исходнике; 22 внешних образования можно размечать адресно на существующей сетке.'
        if r['id']=='GEO-FACIAL-EXTRA':q['required']+=' Поимённо сохранить восемь старых дополнений; для отверстий/каналов при отсутствии стенок нужны изображения/сегментация, а не проекция на кость.'
        blockers.append(q)
    blockers.append(dict(id='GEO-SKULL-TARGETED-EXTRA',title='Разметка 43 новых записей',status='требует проверки',
        originalAcceptanceCriterion='По каждому appId принять нужную линию/поверхность/объём/пространство того же образца либо доказать отсутствие варианта; хранить хеши, стороны, научную и геометрическую приёмку раздельно.',
        existingResources='Внешние меши девяти лицевых костей, нижней челюсти и составных общих структур доступны; ни одной новой координаты не принято.',
        required='Для 38 внешних описательных частей и общего носового гребня — адресная разметка граней/краёв. Для двух предугловых вырезок — сначала подтвердить наличие на образце независимо по сторонам. Для задней ямки и перегородки — согласованные области каждого костного вклада.',
        possibleNow='Подготовка задания возможна; опубликованная новая карточка не является принятием геометрии.',nextStage='5: разметка/приёмка; 6: отображение; 8: внешний контроль.',releaseLimit='Не выводить точный маркер или полную форму до приёмки.',closed=False,
        appIds=[p['id'] for p in data['added']]))
    save('geometry-blockers.json',blockers)
    lines=['# Адресные условия разблокировки геометрии','',
        'Новых исходников и анатомической разметки не появилось. Повторный поиск контуров в Blender не выполнялся. Проверено наличие ресурсов, а не восстановление утраченной геометрии. Результаты прежнего Blender-аудита остаются действующими в прежнем объёме.','',
        '| ID | Ресурсы сейчас | Что получить / сделать | Возможно сейчас / этап |','|---|---|---|---|']
    for q in blockers:lines.append(f"| {q['id']} | {q['existingResources']} | {q['required']} | {q['possibleNow']} {q['nextStage']} |")
    save('geometry-blockers.md','\n'.join(lines)+'\n')
    print(json.dumps(dict(catalogue=42,newRecords=43,classified=32,confirmedShared=9,pendingShared=18,geometryRows=len(blockers)),ensure_ascii=False))

if __name__=='__main__':main()
