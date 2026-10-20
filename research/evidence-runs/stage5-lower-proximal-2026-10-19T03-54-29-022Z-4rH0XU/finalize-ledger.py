"""One-shot reconciler for this evidence set; refuses a changed baseline or rerun."""
from pathlib import Path
import json,re,sys
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
BASE=str(OUT.relative_to(ROOT)).replace('\\','/')
REPORT='research/stage5-lower-proximal-report-2026-10-19.md'
issues=(ROOT/'ANATOMY_ISSUES.md').read_text('utf8'); progress=(ROOT/'ANATOMY_PROGRESS.md').read_text('utf8')
assert issues==(OUT/'before-ANATOMY_ISSUES.md').read_text('utf8')
assert progress==(OUT/'before-ANATOMY_PROGRESS.md').read_text('utf8')
decisions=[
 dict(candidateId='LOW-PROX-C01',structures=['patella','patella_left'],topic='Детализация суставных фасеток надколенника',status='requires_review',existing=['pat_facies_articularis','context_patella_left_A02_5_05_004'],needed='Согласованная современная карта основных и добавочной фасеток; устранить противоречивое anterior в NBK519534; отдельно решить уровень карточек и маски конкретного образца.'),
 dict(candidateId='LOW-PROX-C02',structures=['patella','patella_left'],topic='Двухчастный надколенник: объём представления варианта',status='requires_review',existing=[],needed='Две независимые адресные опоры по классификации варианта; не считать вариант обязательным и не трактовать артефакт/перелом как вариант. Для модели нужны снимки/сегментация данного образца.'),
 dict(candidateId='LOW-PROX-C03',structures=['knee_right','knee_left'],topic='Fabella: объём отдельной вариабельной сесамовидной кости',status='requires_review',existing=[],needed='Адресная проверка номенклатуры и морфологических исследований; отдельная карточка варианта после подтверждения объёма, индивидуальный меш/снимки и права для 3D. Не включать автоматически в типичный скелет.')]
with (OUT/'remaining-decisions.json').open('x',encoding='utf8') as f:json.dump(decisions,f,ensure_ascii=False,indent=2)
records=[
 ('CAT-LOWER-PROXIMAL','Первая партия бедра и голени: каталог, стороны и типы',5,'проверена',
  '86 исходных ID и 87 добавленных записей перечислены в reviewed-records-accepted.json; femur_left/patella_left/tibia_left/fibula_left.',
  'Критерий этой партии: 86 обоснованных типов, сохранение прежних ID/p/n/m и нецелевых данных; четыре отдельные левые карточки noModel, 71 левый TA98-термин, восемь дополнительных собственных и восемь общих записей без p/n; 18 проверенных компонентных связей; исправленные описания/предупреждения, API и регрессия 1280/390. Критерий не включает полноту стопы, все варианты или приёмку геометрии.',
  'Node passed; TA98 762/три прежних расхождения; Blender и trimesh; Playwright по 71 проверке/173 карточки на каждой ширине плюс финальные 14 описаний/кодов. Геометрические ограничения отдельно не закрыты.'),
 ('GEO-LOWER-LEFT-PROXIMAL','Отсутствуют модели левых бедренной, надколенника и костей голени',6,'заблокирована',
  'femur_left (FMA24475), patella_left (FMA24487), tibia_left (FMA24478), fibula_left (FMA24481).',
  'Получить четыре лицензированных индивидуальных левых исходника/сегментации с образцом, стороной, единицами, осями и регистрацией; создать отдельные производные, проверить импорт/экспорт, выбор, масштаб и анатомию. Словарь FMA и зеркальная правая модель не закрывают задачу. Этап 6 — подключение, 8 — приёмка; не блокирует проверку стопы, блокирует заявление полной двусторонней 3D-остеологии до релиза.',
  'Все 69 доступных GLB/base64-ресурсов сверены по хешам и списку; соответствующих имён и исходных файлов не найдено. Четыре noModel-карточки работают; это не восстановление моделей.'),
 ('PIN-LOWER-PROXIMAL','Топография и протяжённость ориентиров бедра и голени не приняты',5,'требует проверки',
  '173 ID в reviewed-records-accepted.json; 86 исходных p/n, включая fem_trochanter_tertius; 87 новых без p/n. Пятнадцать прикреплений не смешиваются с 71 TA98.',
  'Анатомически идентифицировать каждый маркер на данном образце, принять точки/трассы/маски/объёмы; для третьего вертела сначала доказать наличие варианта. Для суставов нужны хрящи/капсула/связки, для левой стороны GEO-LOWER-LEFT-PROXIMAL. Данные — исходная сегментация/снимки или воспроизводимая экспертная разметка с хешами и идентичностью образца. Перенос геометрии на 6/8 не закрывает этот критерий. Не блокирует независимую партию стопы, блокирует заявление точных пинов/границ до релиза.',
  'Blender и trimesh: 86 точек близки к четырём правым сеткам, max≈0,04445 мм, расхождение <0,00006 мм; это не топографическая приёмка. Код выбора третьего вертела найден в build_leg/landmarks_ta.js:229; маркер скрыт, p/n сохранены. Принятых координат/масок — 0.'),
 ('CAT-LOWER-DETAIL','Адресные вопросы детализации надколенника и вариантов колена',5,'требует проверки',
  'LOW-PROX-C01/C02/C03 в remaining-decisions.json; patella/patella_left, варианты области колена. Это три исследовательских вопроса, не три доказанно отсутствующие обязательные кости.',
  'Для каждой строки решить отдельная карточка/существующая часть/вариант/не требуется, подтвердить независимыми источниками, сохранить отсутствие геометрии. C01: карта фасеток; C02: bipartite patella; C03: fabella. Не добавлять обязательность по референсу или одному обзору. Каталожное решение возможно на этапе 5; модель/маска — 6 и приёмка 8. Не блокирует стопу; до релиза нельзя обещать полный охват вариантов без решения.',
  'Основная pat_facies_articularis и левый TA98-экземпляр уже есть; нижний несуставной участок добавлен. Ошибочная формулировка anterior в NBK519534 не перенесена; спорные детальные карточки/меши не созданы.'),
 ('CAT-LOWER-FOOT','Предметная проверка стоп и двустороннего покрытия',5,'открыта',
  '27 прежних правых карточек и 118 записей в foot-remainder-accepted.json; sesamoid_pedis — один групповой ID. Отдельных левых карточек стопы нет.',
  'В следующей партии этапа 5 проверить обе стороны по каталогу и реальным ресурсам: 26 обычных костей на сторону, отдельное исследование сесамоидов/вариантов, типы, общие суставы и отношения. Проверить пригодные левые ресурсы; при отсутствии — noModel и конкретный блокер 6. Сохранять CO-001, SHX-tarsal-canal-vs-sinus, SHX-hand-foot-interosseous-spaces и три расхождения TA98. Завершение только по-ID доказательствам и тестам, не автоматическому зеркалу.',
  'В этой партии выполнена только инвентаризация: 27 владельцев b| в правом leg-q, 118 исходных записей. Они не переклассифицированы и не объявлены анатомически принятыми.')]
table='\n'.join(f'| [{id}](#{id.lower()}) | {title} | {stage} | P1 | {status} |' for id,title,stage,status,*_ in records)+'\n'
index_end=issues.index('\n## ',issues.index('## Указатель задач')+4)
issues=issues[:index_end].rstrip()+'\n'+table+'\n'+issues[index_end:]
issues+='\n\n## Нижние конечности — первая партия, LOG-20261019-06\n'
for id,title,stage,status,structures,criterion,evidence in records:
 issues+=f'''\n### {id}

**{title}**

- Категория: {'геометрия' if id.startswith(('GEO','PIN')) else 'каталог и научная проверка'}. Этап: **{stage}**. Приоритет: **P1**. Статус: **{status}**. Научная проверка: да. Обновлено: **2026-10-19**.
- Структуры и ID: {structures} [По-ID результат]({BASE}/reviewed-records-accepted.json); [остаток]({BASE}/remaining-decisions.json); [стопа]({BASE}/foot-remainder-accepted.json).
- Источник обнаружения: текущая инвентаризация/научная сверка, [отчёт]({REPORT}); [ресурсы]({BASE}/resources-lower-proximal.json).
- Затронутые файлы: scripts/lower_proximal_stage5_review.py, scripts/make_pins_leg.py, scripts/make_context_bone_data.py, scripts/ta98.py; site/pins-leg.js, site/data-context-bones.js, site/pins-context-bones.js; исходные pins_leg и leg-q только читаются.
- Решение и критерий закрытия: {criterion}
- Доказательства исправления и тесты: {evidence} [Node]({BASE}/data-regression-accepted.json); [тесты и источники]({REPORT}).
'''
cards=lambda s:{m[1]:m[2] for m in re.finditer(r'^### ([A-Za-z0-9_-]+)\n(.*?)(?=^### |\Z)',s,re.M|re.S)}
old=cards((OUT/'before-ANATOMY_ISSUES.md').read_text('utf8'));new=cards(issues)
assert len(old)==239 and len(new)==244
for id,body in old.items():
 assert re.search(r'Статус: \*\*([^*]+)\*\*',body)[1]==re.search(r'Статус: \*\*([^*]+)\*\*',new[id])[1]
 for line in body.splitlines():
  if line.startswith('- Решение и критерий закрытия:'):assert line in new[id]
counts=Counter();stages=defaultdict(lambda:[0,0]);science=0
for body in new.values():
 status=re.search(r'Статус: \*\*([^*]+)\*\*',body)[1];stage=int(re.search(r'Этап: \*\*(\d+)\*\*',body)[1]);counts[status]+=1
 stages[stage][1]+=1;stages[stage][0]+=status=='проверена';science+=status!='проверена' and 'Научная проверка: да.' in body
assert dict(counts)=={'проверена':64,'требует проверки':86,'заблокирована':60,'открыта':34},counts
assert science==144,science
summary='LOG-20261019-06: **244 задачи / 64 проверено / 180 не закрыто**: 34 открыты, 86 требуют проверки, 60 заблокированы. Научная проверка — 144. Новая CAT-LOWER-PROXIMAL проверена в ограниченном объёме; четыре новые задачи открыты/требуют проверки/заблокированы. Все прежние 239 ID/статусов/критериев сохранены. [Отчёт]('+REPORT+').\n\n'
issues=issues.replace('## Сводка\n\n','## Сводка\n\n'+summary,1)
start=issues.index('## Сводка');end=issues.index('## Указатель задач')
segment=issues[start:end]
for status in ('открыта','в работе','требует проверки','заблокирована','исправлена','проверена'):
 segment=re.sub(r'\| '+status+r' \| \d+ \|',f'| {status} | {counts[status]} |',segment)
issues=issues[:start]+segment+issues[end:]
progress=re.sub(r'\*\*239 записей: 63 проверено, 176 не закрыто;[^\n]+',
 '**244 записи: 64 проверено, 180 не закрыто; 60 заблокированы; 86 имеют статус «требует проверки».** Научная проверка требуется 144 незакрытым записям. Открыта: 34; в работе: 0; исправлена без приёмки: 0. Текущий срез LOG-20261019-06; история сохранена.',progress,count=1)
# Registry checker deliberately uses the common word form "записей".
progress=progress.replace('**244 записи:','**244 записей:',1)
for stage,(done,total) in stages.items():
 lines=progress.splitlines()
 for i,line in enumerate(lines):
  if line.startswith(f'| {stage} |'):
   lines[i]=re.sub(r'\d+ проверено / \d+ всего',f'{done} проверено / {total} всего',line)
   if stage==5:lines[i]=lines[i].replace('Нижние конечности ещё не начаты.','LOG-20261019-06: первая нижняя партия — 86 типов, четыре левые noModel-карточки, 87 записей без p/n. Стопа (27/118) далее; геометрия и три адресных вопроса открыты.')
   if stage==6:lines[i]=lines[i].replace('VIS-001…012:', 'GEO-LOWER-LEFT-PROXIMAL: ещё четыре левых исходника заблокированы. VIS-001…012:')
 progress='\n'.join(lines)+'\n'
progress+='''
### LOG-20261019-06 — бедро, надколенник и голень

- Проверены четыре исходные правые костные карточки/86 записей: 71 TA98 и 15 областей прикреплений. Типы: 24 volume, 39 area, 21 line, 1 space, 1 point. Добавлены четыре левые noModel-карточки и 87 записей без p/n (71 TA98, 8 собственных дополнений, 8 общих экземпляров/18 связей); теперь партия 173, атлас 2450, без p 1124.
- Исправлены пять описаний поверхностей/менисков/переднего края tibia, обозначены стороны, скрыт неподтверждённый маркер третьего вертела с сохранением p/n. Исправлен дрейф прежней даты TA98 кисти при пересборке; остальные данные, мышцы и прежние p/n/m сохранены.
- Официальный NCBI EFetch: четыре реальных PMID. FIPAT, Gray, Sobotta, NCBI/OpenStax сверены адресно, противоречивые утверждения не перенесены. Координаты не извлекались из текста или средних размеров.
- Blender MCP: четыре правых меша/86 точек/8 снимков, сохранение сцены и моделей. Trimesh: преобразования, конечность, сторона и расстояния, max≈0,04445 мм, согласование <0,00006 мм. 69 прежних ресурсов повторно проверены по хешам: новых именованных левых проксимальных костей нет. Анатомически принятых координат 0; новых координат 0.
- Node: passed; TA98 762/три прежних расхождения. Playwright MCP 1280/light и 390/dark: по 71 проверке, 173 карточки, 18 связей, поиск, noModel, стороны, изоляция, прозрачность, реальные клики, BVH/native faceIndex. Финальные 14 описаний/кодов проверены на обеих ширинах. Активные срезы головы не перезапускались: код неизменён, прежние доказательства SYS-SIDE-ISOLATION сохранены.
- Учёт: добавлены пять постоянных ID, CAT-LOWER-PROXIMAL проверена только в оговорённом объёме. Прежних задач не закрыто. 244 задачи: 64 проверены, 180 не закрыты (34 открыты, 86 требуют проверки, 60 заблокированы), научный остаток 144. Все 239 прежних ID/статусов/критериев сохранены.
- Остаток: GEO-LOWER-LEFT-PROXIMAL; PIN-LOWER-PROXIMAL; CAT-LOWER-DETAIL (LOW-PROX-C01–03); CAT-LOWER-FOOT (27 карточек/118 исходных записей и левая сторона). Сохранены CO-001, SHX-tarsal-canal-vs-sinus, три TA98, GEO-UPPER-LEFT-FOREARM, GEO-HAND-LEFT-MODELS, сесамоиды кисти и все прежние блокеры. Можно отдельно продолжать стопу, но вся нижняя конечность и её геометрия не завершены. Этап 6 не начат.
'''+f'\n- [Полный отчёт, источники, изменённые файлы и проверки]({REPORT}); [по-ID решения]({BASE}/reviewed-records-accepted.json).\n'
for marker in re.findall(r'^### (LOG-[^\n]+)',(OUT/'before-ANATOMY_PROGRESS.md').read_text('utf8'),re.M):assert '### '+marker in progress
(ROOT/'ANATOMY_ISSUES.md').write_text(issues,'utf8');(ROOT/'ANATOMY_PROGRESS.md').write_text(progress,'utf8')
sys.path.insert(0,str(ROOT/'verify'));from verify_anatomy_registry import check
result=check();result.update(previousIdsPreserved=len(old),previousStatusesPreserved=True,previousCriteriaPreserved=True)
with (OUT/'ledger-check.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False))
