"""Record verified addressed work; preserve every earlier issue and journal entry."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage5-skull-targeted-2026-10-17'
RUN=ROOT/'research/evidence-runs/skull-targeted-data-2026-10-17T06-23-51-232Z-rqCZ6e'
LOG='LOG-20261017-02'
REPORT='research/stage5-skull-targeted-report-2026-10-17.md'

def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(name,obj):
    with (OUT/name).open('x',encoding='utf8') as f:json.dump(obj,f,ensure_ascii=False,indent=2)

def records(text):
    result={}
    for m in re.finditer(r'^### ([^\n]+)\n(.*?)(?=^### |^## |\Z)',text,re.M|re.S):
        status=re.search(r'Статус: \*\*([^*]+)\*\*',m[2])
        stage=re.search(r'Этап: \*\*(\d+)\*\*',m[2])
        if status and stage:result[m[1].strip()]={'status':status[1],'stage':int(stage[1]),'science':'Научная проверка: да' in m[2],'body':m[2]}
    return result

def main():
    data=read(RUN/'result.json');decisions=read(OUT/'decisions.json')
    ui=read(OUT/'playwright-results.json');passed={r['name']:r for r in ui if r.get('result',{}).get('status')=='passed'}
    fixtures=read(OUT/'fixtures.json');assert {r['name'] for r in fixtures}==set(passed)
    assert len(passed)==34
    for width in [1280,390]:
        rs=[r['result'] for name,r in passed.items() if name.startswith(f'shared-{width}-')]
        assert sum(r['instances'] for r in rs)==35
        assert sum(r['relationEdges'] for r in rs)==115
        cs=[r['result'] for name,r in passed.items() if name.startswith(f'cards-{width}-')]
        assert len({id for r in cs for id in r['testedIDs']})==40
    assert all(r['result']['status']=='passed' for r in read(OUT/'playwright-functional.json'))
    assert read(OUT/'playwright-new-shared-retry.json')['status']=='passed'
    assert all(r['exitCode']==0 for r in read(OUT/'python-tests.json'))
    assert all(r['exitCode']==0 for r in read(OUT/'node-syntax.json'))
    collision=read(OUT/'evidence-collision-results.json')
    assert len(collision)==2 and all(r['result']['status']=='passed' for r in collision)
    shots=[p for r in collision for p in r['screenshots']]
    assert len(set(shots))==2 and all(Path(p).exists() for p in shots)
    for r in passed.values():assert all(Path(p).exists() for p in r['screenshots'])
    # All protected originals and historical artefacts must be byte-identical.
    baseline=read(OUT/'before-hashes.json');changed=[];missing=[]
    for name,digest in baseline.items():
        p=ROOT/name
        if not p.exists():missing.append(name)
        elif hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(name)
    allowed={'scripts/make_pins_head_extra.py','scripts/make_shared_landmarks.py','site/pins-head-extra.js','site/pins-shared.js',
        'tools/verify-skull-batch8.mjs','tools/verify-skull-final.mjs','tools/verify-stage5-skull.mjs'}
    assert not missing and set(changed)<=allowed,(changed,missing)
    save('integrity-check.json',dict(status='passed',protectedFiles=len(baseline),originalModelsUnchanged=41,
        historicalShotsUnchanged=sum(n.startswith('shots/') for n in baseline),
        priorFinalEvidenceAndShotsUnchanged=sum(n.startswith(('shots/','research/stage5-skull-final-2026-10-17/')) for n in baseline),
        allowedChanges=changed,missing=missing,historicalFileRestored=False,collisionPaths=shots,
        scope='Full SHA-256 comparison before registry/doc changes. No historical output or original GLB/base64 modified.'))
    issues=(ROOT/'ANATOMY_ISSUES.md').read_text('utf8');progress=(ROOT/'ANATOMY_PROGRESS.md').read_text('utf8')
    before=records(issues);assert len(before)==204 and LOG not in issues
    closed={'PIN-SHARED-KIND','CAT-FACIAL-EXTRA','CAT-MANDIBLE-EXTRA'}
    updates={
        'PIN-SHARED-KIND':'32/32 appId предметно классифицированы: 7 точек, 8 областей, 14 пространств, 3 объёмных образования. Причины и две независимые адресные опоры сохранены по каждому ID. Птерион принят только как краниометрическое представление, не как готовая точка/полный рисунок швов. ID, relations, p/n сохранены; UI всех 32 прошёл 1280/390 px. Геометрическая приёмка не закрыта.',
        'CAT-FACIAL-EXTRA':'Все 44 кандидата получили предметное решение: четыре поверхности слёзных костей приняты ранее; сейчас добавлены 38 описательных частей и один общий гребень по двум кандидатам вкладов. Независимые Gray/Buchanan, справочный номенклатурный статус, отсутствие дублей и UI 1280/390 подтверждены. Координат нет; геометрия 39 новых сущностей отдельно в GEO-SKULL-TARGETED-EXTRA.',
        'CAT-MANDIBLE-EXTRA':'19/19 каталожных кандидатов разобраны: 17 ранее, две предугловые вырезки сейчас как анатомический вариант. Термин борозды лицевых сосудов сопоставлен с antegonial/premasseteric notch по PMID37106571, 26339819, 40603468; это не incisura mandibulae между отростками ветви. Поиск/карточки/переходы 1280/390 прошли. Наличие варианта на обеих сторонах GLB неизвестно, p/n не создавались; GEO-SKULL-TARGETED-EXTRA сохранена.'}
    for r in decisions['shared']:
        updates[r['issueId']]=('Состав подтверждён; ' if r['scientificMembershipConfirmed'] else 'Полный состав не подтверждён; ')+r['remaining']+' Исходный критерий не закрыт. Режим проверки: '+r['reviewMode']+'.'
    blockers=read(OUT/'geometry-blockers.json')
    for r in blockers:
        if r['id'] not in before:continue
        updates[r['id']]='Проверена доступность исходных ресурсов, без повторного поиска контура. '+r['required']+' '+r['possibleNow']+' Следующая работа: '+r['nextStage']+' Статус и исходный критерий сохранены; адресная таблица — geometry-blockers.json.'
    def change(m):
        id=m[1].strip();body=m[2]
        if id not in updates:return m[0]
        if id in closed:
            body=re.sub(r'Статус: \*\*[^*]+\*\*','Статус: **проверена**',body,count=1)
            body=body.replace('Научная проверка: да','Научная проверка: нет',1)
        body=re.sub(r'Обновлено: \*\*[^*]+\*\*','Обновлено: **2026-10-17**',body,count=1)
        body=body.rstrip()+f'\n- Дополнение {LOG}: '+updates[id]+f' [Поимённые решения](research/stage5-skull-targeted-2026-10-17/decisions.md), [условия геометрии](research/stage5-skull-targeted-2026-10-17/geometry-blockers.md), [проверки]({REPORT}).\n\n'
        return '### '+id+'\n'+body
    issues=re.sub(r'^### ([^\n]+)\n(.*?)(?=^### |^## |\Z)',change,issues,flags=re.M|re.S)
    issues+='''
### SYS-EVIDENCE-PATH
**Повторный запуск проверочного сценария перезаписывал исторический вспомогательный снимок**

- Категория: проверочные инструменты и доказательства. Этап: **5**. Приоритет: **P1**. Статус: **проверена**. Научная проверка: нет. Обновлено: **2026-10-17**.
- Структуры и ID: не анатомическая структура; исторический `shots/stage5-skull-batch8/1280-dark-batch-0.png` был заменён в прошлой задаче. Утраченное прежнее содержимое не восстановлено и не используется как прежнее доказательство.
- Источник обнаружения: research/stage5-skull-final-report-2026-10-17.md и test-notes.json; LOG-20261017-02.
- Затронутые файлы: tools/evidence-run.mjs, prepare-evidence-mcp.mjs, verify-evidence-run.mjs, verify-stage5-skull.mjs, verify-skull-batch6.mjs, verify-skull-batch7.mjs, verify-skull-batch8.mjs, verify-skull-final.mjs; AGENTS.md.
- Решение и критерий закрытия: новые результаты получают отдельный атомарно созданный каталог; JSON пишется с wx; новые PNG имеют UUID на каждый запуск. Исторические MCP-сценарии запускаются через обёртку, перенаправляющую page.screenshot. Проверить два повторных запуска с прежним путём и SHA-256 исторических файлов. Не восстанавливать потерянный файл выдуманным изображением.
- Доказательства исправления и тесты: verify-evidence-run.mjs — параллельные каталоги различны, повторная запись отклонена, содержимое сохранено, выход из каталога запрещён. MCP collision-results: два запуска одного сценария создали два разных существующих PNG. integrity-check.json: 686 исторических снимков, предыдущие доказательства и 41 модель без изменений. Все 34 текущих MCP-партии использовали новые каталоги. Новый guard защищает page.screenshot; при применении locator.screenshot требуется тот же явный новый путь, универсальной перехват всех файловых операций не заявлен.
- Проверки: [протокол защиты](research/stage5-skull-targeted-2026-10-17/evidence-collision-results.json), [хеши](research/stage5-skull-targeted-2026-10-17/integrity-check.json). Закрыта причина повторной перезаписи текущими проверочными средствами, не историческая утрата изображения.

### GEO-SKULL-TARGETED-EXTRA
**Не приняты границы и геометрия 43 новых адресных дополнений черепа**

- Категория: геометрическая приёмка. Этап: **5**. Приоритет: **P1**. Статус: **требует проверки**. Научная проверка: да. Обновлено: **2026-10-17**.
- Структуры и ID: все 43 appId и refs в [new-records.json](research/stage5-skull-targeted-2026-10-17/new-records.json). 38 внешних частей, один общий гребень носовых костей, два варианта предугловой вырезки, задняя черепная ямка и костная перегородка носа. Не дублирует старые наборы GEO-FACIAL-EXTRA / GEO-MANDIBLE-EXTRA / GEO-SKULL-FINAL-EXTRA.
- Источник обнаружения: адресные каталожные решения LOG-20261017-02; источники подтверждают сущность, не геометрию проекта.
- Затронутые файлы: scripts/skull_targeted_review.py, site/pins-head-extra.js, site/pins-shared.js; будущая независимая разметка.
- Решение и критерий закрытия: для каждого appId принять нужную линию/поверхность/объём/пространство того же образца либо доказать отсутствие варианта. Сохранять хеши, стороны, координатную систему, provenance граней/полилиний/масок и анатомическую приёмку. Для двух вырезок сначала подтвердить наличие по каждой стороне; для составных структур — полный набор согласованных костных участков. Близость к мешу и добавление карточки не являются закрытием.
- Доказательства исправления и тесты: каталожные записи прошли проверки, у всех отсутствуют p/n. Новых координат/контуров/размеров не принято; задача не закрыта.
- Следующий шаг: этап 5 — адресная разметка/доказательства; этап 6 — отображение принятого; этап 8 — независимая приёмка. Не препятствует ограниченному справочному каталогу, запрещает выдавать эти карточки за точную геометрическую карту. [Условия по ресурсам](research/stage5-skull-targeted-2026-10-17/geometry-blockers.md).
'''
    after=records(issues);assert set(before)<=set(after) and len(after)==206
    for id,r in before.items():
        if id not in closed:assert after[id]['status']==r['status'],id
        oldcriterion=re.search(r'^- Решение и критерий закрытия:.*$',r['body'],re.M)
        if oldcriterion:assert oldcriterion[0] in after[id]['body'],id+' criterion changed'
    counts=Counter(r['status'] for r in after.values());unclosed=len(after)-counts['проверена']
    scientific=sum(r['science'] and r['status']!='проверена' for r in after.values())
    stage5=[r for r in after.values() if r['stage']==5]
    stats=dict(total=len(after),verified=counts['проверена'],unclosed=unclosed,statuses=dict(counts),scientific=scientific,
        stage5Verified=sum(r['status']=='проверена' for r in stage5),stage5Total=len(stage5),closedThisTask=[*sorted(closed),'SYS-EVIDENCE-PATH'])
    assert stats['total']==206 and stats['verified']==40 and stats['unclosed']==166 and counts['заблокирована']==53
    summary='22 костные карточки, 521 исходная запись, 72 общих экземпляра и 79 дополнительных собственных карточек: 672 ориентира. Адресно классифицированы 32 общие карточки; 42 каталожных кандидата сведены в 41 новую сущность, ещё две общие карточки добавлены из SH-050/087. Все 43 новые записи без p/n. Для 9/27 SH-кандидатов состав подтверждён (два впервые); полные критерии всех 27 остаются открытыми. Геометрическая и окончательная предметная приёмка черепа не завершена.'
    issues=re.sub(r'^Срез состояния:.*$',f'Срез состояния: **2026-10-17**. Журнал: [ANATOMY_PROGRESS.md](ANATOMY_PROGRESS.md). Этап 5 в работе. {summary}',issues,count=1,flags=re.M)
    issues=re.sub(r'^Всего \*\*204 записи\*\*.*$',f'Всего **206 записей**; подтверждённо закрыто **40**, не закрыто **166**: 33 открыты, 80 требуют проверки, 53 заблокированы. Научной проверки требуют **{scientific}** незакрытых записей. Этап 5 — **{stats["stage5Verified"]}/{stats["stage5Total"]}**. В этой задаче закрыты PIN-SHARED-KIND, CAT-FACIAL-EXTRA, CAT-MANDIBLE-EXTRA и новый SYS-EVIDENCE-PATH; добавлена незакрытая GEO-SKULL-TARGETED-EXTRA. Числа задач не равны числу структур.',issues,count=1,flags=re.M)
    issues=issues.replace('## Сводка\n','## Сводка\n\n'+LOG+': '+summary+f' [Отчёт]({REPORT}).\n',1)
    issues=issues.replace('| требует проверки | 82 |','| требует проверки | 80 |',1).replace('| проверена | 36 |','| проверена | 40 |',1)
    issues=re.sub(r'^Актуальные числа:.*$','Актуальные числа: 141 костная карточка + 9 хрящевых/мягкотканных записей; 255 мышечных карточек; **1922** записи ориентиров. Без p — **596 = 447 исходных + 70 общих + 79 дополнительных собственных**. Исходный набор PIN-002 из 67 общих ID сохранён; три новые общие без p учтены в GEO-SKULL-TARGETED-EXTRA. Три старых неподтверждённых p остаются с отключёнными маркерами. Все наборы других регионов, 13 мышц и 21 часть без геометрии сохранены; их повторной научной проверки не было.',issues,count=1,flags=re.M)
    oldJournal=progress.split('## Записи журнала',1)[1]
    progress=re.sub(r'^\| 5 \|.*$',f'| 5 | Полная проверка и исправление пинов | В работе | {LOG}: 32/32 общих типов, 42/42 каталожных решения, 43 новые записи без координат. 672 ориентира черепа; все 27 SH-критериев и геометрические ограничения сохранены. {stats["stage5Verified"]} проверено / {stats["stage5Total"]} всего; это не процент готовности анатомии. |',progress,count=1,flags=re.M)
    progress=re.sub(r'^\*\*202 записи:.*$',f'**206 записей: 40 проверено, 166 не закрыто; 53 заблокированы; 80 имеют статус «требует проверки».** Научная проверка требуется {scientific} незакрытым записям. Открыта: 33; в работе: 0; исправлена без приёмки: 0. Текущий срез {LOG}. Исторические числа сохранены в датированных записях и снимке before-ANATOMY_PROGRESS.md текущей партии.',progress,count=1,flags=re.M)
    progress=progress.replace('Текущий срез LOG-20261017-01:','Исторический срез LOG-20261017-01:',1)
    progress+='\n\n### '+LOG+' — адресное завершение каталожных вопросов черепа\n\n'+summary+'\n\n'+f'''[Отчёт]({REPORT}), [42 решения и 27 остатков](research/stage5-skull-targeted-2026-10-17/decisions.md), [условия геометрии](research/stage5-skull-targeted-2026-10-17/geometry-blockers.md).

- Классифицированы 32/32 прежние общие карточки (7 точек, 8 областей, 14 пространств, 3 объёма); прежние ID, связи, координаты и 521 собственная запись сохранены. Это принятие типа, не локализации.
- 40 лицевых кандидатов: 38 описательных частей + один общий носовой гребень по двум вкладам. Два кандидата нижней челюсти: справочные предугловые вырезки как вариант, без ложного отождествления с incisura mandibulae. Новые независимые источники Buchanan и PubMed PMID37106571/26339819/40603468; библиография проверена через официальный EFetch.
- SH-050/087: добавлены два канонических объекта с шестью/десятью костными вкладами; ещё два вклада у общего носового гребня. Всего 18 новых связей. Исходные задачи не закрыты: иерархия локальных частей и прочие критерии сохранены. 7 прежних частично подтверждённых SH-семейств повторно не выдаются за новую работу; 18 составов остаются неподтверждёнными.
- Закрыты PIN-SHARED-KIND, CAT-FACIAL-EXTRA, CAT-MANDIBLE-EXTRA; новый SYS-EVIDENCE-PATH исправлен и проверен. GEO-SKULL-TARGETED-EXTRA добавлена с 43 appId и критериями геометрии. Все старые нерешённые ID и критерии сохранены.
- Исправлен протокол: атомарные уникальные каталоги, wx для новых JSON, UUID для PNG; исторические MCP-сценарии через prepare-evidence-mcp.mjs. Два повторных вызова с историческим путём создали разные PNG; 686 исторических снимков и 41 модель byte-identical. Ранее утраченный снимок не восстановлен выдуманными данными.
- Проверки: verify_head.py passed (22 кости/521 TA98); verify_ta98.py — 762 термина, те же три известные расхождения вне черепа; три unittest passed; адресная Node-регрессия passed; девять JS-синтаксических проверок passed; тест сохранности результатов passed. Playwright MCP: 34 адресные партии, по 35 общих карточек/115 костных переходов и 40 новых собственных карточек на каждой ширине 1280/390; светлая и тёмная темы, поиск и реальные клики. Дополнительно старый функциональный сценарий общих ориентиров/изоляции/прозрачности/срезов прошёл на обеих ширинах; три новых общих объекта прошли поиск/изоляцию/прозрачность с сохранением всех костных вкладов. BVH/raycast код, индексы, GLB и координаты неизменны; тяжёлый прежний BVH-протокол использован по неизменности кода/моделей. Новая геометрическая приёмка в Blender не заявляется.
- Непрошедшие первые запуски сохранены: sandbox-сервер не был доступен браузеру; после локального запуска вне sandbox повтор прошёл. В новом тесте неверно ожидалась изоляция одной кости общего объекта; проверка исправлена по существующему механизму contributingBoneIds и прошла. Это дефект теста, не исправление анатомии. Снимки 1280/390 просмотрены: ограничения и источники читаемы, горизонтального переполнения нет.
- Итог реестра: **206 задач / 40 проверено / 166 не закрыто**, из них **53 заблокированы**, **80 требуют проверки**, **33 открыты**; научная проверка — **{scientific}**. Этап 5 — **{stats['stage5Verified']}/{stats['stage5Total']}**. В задаче закрыты четыре записи учёта, а не четыре анатомические структуры.

Адресная каталожная партия завершена на указанном уровне доказательств; окончательная приёмка черепа остаётся открытой. Переход к костям шеи возможен как следующая независимая партия этапа 5 с сохранением всех черепных ID и запретов точного отображения неподтверждённых структур. Это не закрытие SH/GEO и не разрешение релиза. В текущей задаче другие области не обрабатывались.
'''
    assert oldJournal in progress
    for n in [1,2,3,4,6,7,8]:
        oldrow=next(l for l in (OUT/'before-ANATOMY_PROGRESS.md').read_text('utf8').splitlines() if l.startswith(f'| {n} |'))
        assert oldrow in progress
    (ROOT/'ANATOMY_ISSUES.md').write_text(issues,encoding='utf8')
    (ROOT/'ANATOMY_PROGRESS.md').write_text(progress,encoding='utf8')
    save('registry-validation.json',dict(status='passed',**stats,oldIDsPreserved=204,originalCriteriaPreserved=True,oldJournalPreserved=True,roadmapOrderPreserved=True))
    remaining=read(ROOT/'research/stage5-skull-final-2026-10-17/remaining-skull-issues.json')['rows']
    remaining=[r for r in remaining if after[r['id']]['status']!='проверена']
    remaining.append({'id':'GEO-SKULL-TARGETED-EXTRA','status':'требует проверки','source':'geometry-blockers.json'})
    for r in remaining:
        if r['id'] in updates:r['currentUpdate']=updates[r['id']]
    save('remaining-skull-issues.json',dict(rows=remaining,count=len(remaining),note='Prior questions retained with currentUpdate; original acceptance criteria remain authoritative.'))
    save('verification-summary.json',dict(status='passed',dataRun=str(RUN.relative_to(ROOT)).replace('\\','/'),
        uiPassedBatches=34,uiInitialConnectionFailure=1,uiInitialWrongExpectationFailure=1,
        sharedPerWidth=35,relationEdgesPerWidth=115,newOwnCardsPerWidth=40,extraSharedInteractionCases=6,
        historicalFunctionalWidths=[1280,390],newGeometryAccepted=0,sourceModelsChanged=0,
        previousBvhEvidence='research/stage5-skull-final-2026-10-17/playwright-bvh-1280.json; playwright-bvh.json; relevant code/models hashes unchanged',
        anatomyNotAcceptedByUITests=True,statistics=stats))
    print(json.dumps(stats,ensure_ascii=False))

if __name__=='__main__':main()
