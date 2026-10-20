"""One-time, guarded documentation update; preserves historical entries and criteria."""
from pathlib import Path
import json,re
from collections import Counter,defaultdict
root=Path.cwd()
report='research/stage5-foot-report-2026-10-19.md'
evidence='research/evidence-runs/stage5-foot-closure-2026-10-19T18-00-05-369Z-abKECx'
source='research/evidence-runs/stage5-foot-2026-10-19T09-33-56-218Z-lia0LB'
snap=json.loads((root/'research/evidence-runs/stage5-foot-resume-2026-10-19T17-48-01-945Z-hnJyWZ/before-documents.json').read_text('utf-8'))
formats={}
def read(name):
    raw=(root/name).read_bytes();formats[name]=(raw.startswith(b'\xef\xbb\xbf'),b'\r\n' in raw)
    text=raw.decode('utf-8-sig').replace('\r\n','\n')
    assert text==snap[name].lstrip('\ufeff').replace('\r\n','\n'),name+' changed since snapshot'
    return text
issues=read('ANATOMY_ISSUES.md');progress=read('ANATOMY_PROGRESS.md');current=read('CURRENT_PROJECT_STATUS.md')
old_issues=issues;old_progress=progress
def edit_card(ident,fn):
    global issues
    pattern=rf'(^### {re.escape(ident)}\n)(.*?)(?=^### |\Z)'
    match=re.search(pattern,issues,re.M|re.S);assert match,ident
    issues=issues[:match.start()]+match[1]+fn(match[2])+issues[match.end():]
def foot_card(body):
    body=body.replace('Статус: **открыта**','Статус: **проверена**',1)
    body=re.sub(r'^- Структуры и ID:.*$',f'- Структуры и ID: 54 владельца (27 справа и 27 слева), 299 записей: 118 исходных + 181 новая. sesamoid_pedis и sesamoid_pedis_left — групповые владельцы; четыре дочерние сесамовидные карточки входят в 299. [Все ID]({source}/reviewed-records-final.json); [левые noModel-карточки]({source}/left-cards-final.json).',body,flags=re.M)
    body=body.replace('В этой партии выполнена только инвентаризация:','Исторический срез нижней проксимальной партии: только инвентаризация —').replace('Они не переклассифицированы и не объявлены анатомически принятыми.','На тот момент записи ещё не были переклассифицированы; этот старый результат не означает текущего отсутствия левых карточек.')
    return body.rstrip()+f'\n- Завершение LOG-20261019-11: 118 типов, 27 левых карточек, 181 новая запись, 46 суставных экземпляров и две пазухи/126 связей; все новые p/n null. Node и мобильные 299 карточек/126 связей, адресные шесть последних карточек/18 связей на ПК — passed. [Отчёт]({report}); [сверка и тесты]({evidence}/consistency.json). Предметный каталог и оформление ограничений приняты; координаты/маски — 0 новых приёмок. Отдельные PIN-LOWER-FOOT, GEO-LOWER-LEFT-FOOT, GEO-FOOT-SESAMOID-PARTS и прежние CO/SHX/DATA сохраняют полные критерии.\n\n'
edit_card('CAT-LOWER-FOOT',foot_card)
updates={
 'CO-001':f'Левая описательная запись context_calcaneus_left_A02_5_11_009 теперь существует (p/n null, talus_left + calcaneus_left), но левой модели нет. Правая cal_sinus_tarsi сохраняет прежнюю скрытую координату, без анатомической приёмки. Исторические сведения об отсутствии левого ID относятся к прежним срезам. [Текущий по-ID остаток]({evidence}/remaining-evidence.json).',
 'SHX-tarsal-canal-vs-sinus':f'В партии стопы типы борозд и пространства уточнены; отдельный канал не создан, борозды с пазухой не слиты. Связи двух sinus не закрывают вопрос терминологических границ и геометрической протяжённости. [Отчёт]({report}).',
 'DATA-MUSCLE-BONE-LINKS':f'Семь исходных прикреплений стопы: calc_dorsal_anterior, calc_plantar, cuboid_groove, cuneiform_med_plantar, att_cuneiform_int_plantar, cuneiform_lat_plantar, sesamoid_plantar. geometryKind=area не подтверждает старые m, прямое/сухожильное или частеспецифическое прикрепление. Требуются независимые источники/полный текст и область применимости; m сохранены. [Перечень и необходимые доказательства]({evidence}/remaining-evidence.json).',
}
for ident,paragraph in updates.items():edit_card(ident,lambda b,p=paragraph:b.rstrip()+'\n- Дополнение LOG-20261019-11: '+p+'\n\n')
new=[
 ('PIN-LOWER-FOOT','Локализация и протяжённость ориентиров стопы',5,'требует проверки','топография и геометрическая разметка',
  '299 записей, перечисленных по ID; 118 прежних координат, 181 новая запись без координат. Типы point/line/area/space/volume не являются приёмкой локализации.',
  'Независимо принять локализацию на конкретном образце и анатомически подходящую геометрию: точки, линии, поверхности, пространства и объёмы. Сохранить хеш модели, сторону, систему координат, источники, маску/якорь и результаты проверки. Не заменять область случайной точкой; CO-001 и сесамоиды имеют отдельные связанные критерии. Приёмка в этапе 5, реализация разметки в 6, внешняя проверка в 8. Не блокирует итоговую инвентаризацию этапа 5; блокирует заявление точной топографии при публикации.'),
 ('GEO-LOWER-LEFT-FOOT','Отсутствующая принятая геометрия левой стопы',6,'заблокирована','исходная 3D-геометрия',
  '27 левых владельцев noModel из left-cards-final.json, включая групповой sesamoid_pedis_left. Количество владельцев не равно числу физических сесамоидов.',
  'Получить лицензированные левые исходники с идентификацией образца, масштабом, осями и регистрацией. Проверить все именованные структуры, стороны и принадлежность, затем принятие в Blender/trimesh и UI. Словарные ID, безымянные фрагменты и зеркальная копия не заменяют исходник. Оригинальные GLB не менять без разрешения. Геометрия в этапе 6, приёмка в 8; не блокирует сверку каталога 5, блокирует заявление полного двустороннего 3D.'),
 ('GEO-FOOT-SESAMOID-PARTS','Раздельная идентификация и выделение сесамоидов стопы',6,'требует проверки','идентификация компонент и маски',
  'Четыре дочерние карточки: extra_sesamoid_pedis_medial_hallux_sesamoid, extra_sesamoid_pedis_lateral_hallux_sesamoid и соответствующие extra_sesamoid_pedis_left_*; справа общий ресурс содержит две компоненты, слева моделей нет.',
  'Независимо установить медиальную/латеральную идентичность правых компонент в анатомической системе стопы, сохранить маски треугольников/компонент и хеш исходника, проверить отдельный выбор. Нельзя устанавливать сторону по одному экранному/global X. Левые исходники учитываются в GEO-LOWER-LEFT-FOOT, не восстанавливаются повторно здесь; после их получения принять индивидуальные связи с карточками. Этап 6/8; не блокирует сверку 5, блокирует заявление раздельной геометрической готовности сесамоидов.'),
]
for ident,title,stage,status,category,structures,criterion in new:
    assert f'### {ident}\n' not in issues
    issues+=f'''\n### {ident}

**{title}**

- Категория: {category}. Этап: **{stage}**. Приоритет: **P1**. Статус: **{status}**. Научная проверка: да. Обновлено: **2026-10-19**.
- Структуры и ID: {structures} [Поимённый список]({evidence}/remaining-evidence.json).
- Источник обнаружения: [предметная партия стопы]({report}); прежние Blender/trimesh и ресурсная проверка, подтверждённые текущей сверкой каталога.
- Затронутые файлы: scripts/foot_stage5_review.py, scripts/make_pins_leg.py, scripts/make_context_bone_data.py; site/pins-leg.js, site/pins-context-bones.js, site/data-context-bones.js; модели leg-glb/leg-extra-glb — только чтение до отдельного разрешения.
- Решение и критерий закрытия: {criterion}
- Доказательства исправления и тесты: ограничения/noModel и карточки проверены, но критерии геометрической приёмки **не выполнены**. [Сверка]({evidence}/consistency.json); [Blender]({source}/blender-foot.json); [ресурсы]({source}/resource-review.json). Ни UI-тест, ни расстояние до поверхности не закрывают эту задачу.
'''
    index=f'| [{ident}](#{ident.lower()}) | {title} | {stage} | P1 | {status} |'
    anchor=next(l for l in issues.splitlines() if l.startswith('| [CAT-LOWER-FOOT]'))
    issues=issues.replace(anchor,anchor+'\n'+index,1)
issues=re.sub(r'(^\| \[CAT-LOWER-FOOT\].*\| )открыта( \|$)',r'\1проверена\2',issues,flags=re.M)
cards=list(re.finditer(r'^### ([A-Za-z0-9_-]+)\n(.*?)(?=^### |\Z)',issues,re.M|re.S));counts=Counter();stages=defaultdict(lambda:[0,0]);science=0
for m in cards:
    stage=int(re.search(r'Этап: \*\*(\d+)\*\*',m[2])[1]);status=re.search(r'Статус: \*\*([^*]+)\*\*',m[2])[1]
    counts[status]+=1;stages[stage][1]+=1;stages[stage][0]+=status=='проверена';science+=status!='проверена' and 'Научная проверка: да.' in m[2]
assert len(cards)==250 and counts==Counter({'проверена':68,'открыта':33,'требует проверки':88,'заблокирована':61}),counts
for status in ['открыта','в работе','требует проверки','заблокирована','исправлена','проверена']:
    issues=re.sub(rf'^\| {status} \| \d+ \|$',f'| {status} | {counts[status]} |',issues,flags=re.M)
issues=issues.replace('LOG-20261019-10: [CURRENT_PROJECT_STATUS.md]',f'LOG-20261019-11: **250 задач / 68 проверено / 182 не закрыто**: 33 открыты, 88 требуют проверки, 61 заблокирована. CAT-LOWER-FOOT проверена в доступном предметном объёме; три геометрические задачи зарегистрированы, все старые блокеры сохранены. [Отчёт]({report}); [актуальные ограничения по 299 ID]({evidence}/remaining-evidence.json).\n\nLOG-20261019-10: [CURRENT_PROJECT_STATUS.md]',1)
issues=re.sub(r'^Актуальные числа LOG-20261019-10:.*$',f'Актуальные числа LOG-20261019-11: **205 костных карточек + 9 хрящевых/мягкотканных; 2631 запись, 1305 без p; 255 мышечных карточек**. Стопа: 54 владельца / 299 записей, 27 левых владельцев noModel. Наличие карточки не доказывает геометрию. [Сверка]({evidence}/consistency.json).',issues,flags=re.M)
progress=re.sub(r'\*\*247 записей: 67 проверено, 180 не закрыто;.*?Текущий срез LOG-20261019-10; история сохранена\.',f'**250 записей: 68 проверено, 182 не закрыто; 61 заблокирована; 88 имеют статус «требует проверки».** Научная проверка требуется {science} незакрытым записям. Открыта: 33; в работе: 0; исправлена без приёмки: 0. Текущий срез LOG-20261019-11; история сохранена.',progress)
for stage,(done,total) in stages.items():
    line=next(l for l in progress.splitlines() if l.startswith(f'| {stage} |'))
    updated=re.sub(r'\d+ проверено / \d+ всего',f'{done} проверено / {total} всего',line)
    if stage==5:updated=updated.replace('Стопа (27/118) далее;','Стопа: LOG-20261019-11 — 54 владельца/299 записей, доступная предметная партия завершена;')
    if stage==6:updated=updated.replace('VIS-001…012:', 'GEO-LOWER-LEFT-FOOT: 27 владельцев без принятых моделей; GEO-FOOT-SESAMOID-PARTS: раздельная идентификация/маски не приняты. VIS-001…012:')
    progress=progress.replace(line,updated,1)
progress+=f'''

### LOG-20261019-11 — завершение CAT-LOWER-FOOT после остановки

- Продолжено сохранённое состояние: генераторы и прежняя анатомическая сверка не повторялись. 118 исходных типов, 27 левых noModel-карточек и 181 новая запись сохранены; всего 54 костных владельца / 299 записей стопы. 46 новых суставных экземпляров и два sinus, 126 связей. Новых/принятых координат и масок — 0.
- Мобильный Playwright MCP 390 px: 299 карточек, 126 связей, поиск, стороны, noModel, изоляция/прозрачность и предупреждения — passed. ПК 1280 px: только шесть последних карточек/18 связей, их изоляция/прозрачность/noModel и адресный workflow — passed. Старые 341 проверки не повторялись. Ошибок console/page в принятых фазах нет; снимки просмотрены, физический телефон не проверялся.
- Добавлены ограничение 45 с на фазу и сохранение каждого результата отдельно. Неуспешный workflow сохранён: после изоляции требовалось вновь открыть мобильную карточку перед нажатием прозрачности. Исправлен тест, успешно повторён только workflow, приложение не менялось. Прерванный старый мобильный прогон не объявлен прошедшим.
- Лёгкая Node-сверка: уникальность всех 2631 ID, сохранность 181 новой записи, однократные общие связи, совпадение с прежним final-снимком, неизменность прежних p/n/m и мышц — passed. Актуальный по-ID остаток построен заново из 299 записей; прежний снимок 293 не перезаписан.
- Закрыта только CAT-LOWER-FOOT. Добавлены PIN-LOWER-FOOT (требует проверки), GEO-LOWER-LEFT-FOOT (заблокирована), GEO-FOOT-SESAMOID-PARTS (требует проверки). Дополнены CO-001, SHX-tarsal-canal-vs-sinus, DATA-MUSCLE-BONE-LINKS (семь прикреплений), без закрытия. Все остальные прежние ID/статусы/критерии и история сохранены.
- Учёт: **250 задач / 68 проверено / 182 не закрыто**: 33 открыты, 88 требуют проверки, 61 заблокирована; научный остаток {science}. Из прежних задач закрыта 1, новых незакрытых 3. Число задач не равно числу анатомических структур.
- [Отчёт]({report}); [сверка и принятые фазы]({evidence}/consistency.json); [актуальные ограничения по ID]({evidence}/remaining-evidence.json). Изменены два проверочных инструмента и документы; данные, приложение, оригинальные GLB и старые координаты в продолжении не менялись. Этап 5 готов к итоговой сверке областей и адресного остатка, но не объявлен полностью принятым. Этап 6 и публикация не начинались.
'''
current=current.replace('**247 задач: 67 проверены, 180 не закрыты** — 34 открыты, 86 требуют проверки, 60 заблокированы.','**250 задач: 68 проверены, 182 не закрыты** — 33 открыты, 88 требуют проверки, 61 заблокирована.')
oldline=next(l for l in current.splitlines() if l.startswith('| CAT-LOWER-FOOT |'))
newlines=f'''| CAT-LOWER-FOOT | Стопа | ГОТОВО | 118 исходных типов; 27 левых noModel-карточек и 181 новая запись; всего 54 владельца/299 записей. Мобильные 299 карточек/126 связей и шесть последних суставных карточек на ПК проверены [D]. | Доступный предметный объём принят; координаты и геометрия — отдельные задачи ниже. | 5 |
| PIN-LOWER-FOOT | Пины и поверхности стопы | ТРЕБУЕТ ПРОВЕРКИ | Все 299 ID перечислены; 118 старых координат, 181 новая запись без координат. | Независимая локализация и разметка протяжённости на конкретном образце. | 5 → 6/8 |
| GEO-LOWER-LEFT-FOOT | 3D левой стопы | ЗАБЛОКИРОВАНО | 27 карточек есть; пригодных именованных исходников не найдено. | Лицензированные левые модели, масштаб/оси/регистрация и приёмка. | 6/8 |
| GEO-FOOT-SESAMOID-PARTS | Раздельная геометрия сесамоидов стопы | ТРЕБУЕТ ПРОВЕРКИ | Четыре дочерние карточки; справа две компоненты общего ресурса, идентичность/маски не приняты. | Принять правые компоненты; слева исходники через GEO-LOWER-LEFT-FOOT. | 6/8 |'''
current=current.replace(oldline,newlines)
current=current.replace('Научно проверить и оформить связи. Это показатель метаданных, не 216 доказанных анатомических ошибок.','Научно проверить и оформить связи, включая семь прикреплений стопы [D]. Это показатель метаданных, не 216 доказанных анатомических ошибок.')
current=current.replace('Общий ориентир и исследования сохранены.','Правый общий ориентир/скрытый маркер сохранён; левый ID добавлен без координат и модели.')
current=re.sub(r'^\*\*Этап 5: CAT-LOWER-FOOT.*$', '**Этап 5: итоговая сверка всех костных областей и адресного остатка.** Предметная партия стопы завершена на доступном уровне. Проверить реестр и доказательства, включая три вопроса колена и четыре вопроса FDS кисти; не повторять уже принятые классификации. Геометрические блокеры сохраняются; этап 6 автоматически не начинается.',current,flags=re.M)
current=current.replace('178 костных + 9 мягкотканных карточек, 255 мышц, 2450 ориентиров; 1124 без p','205 костных + 9 мягкотканных карточек, 255 мышц, 2631 ориентир; 1305 без p')
current=current.replace('карточки предплечья/кисти/бедра/голени добавлены.','карточки предплечья/кисти/бедра/голени/стопы добавлены.')
current=current.replace('- [Машинная сверка текущего состояния]', '- Историческая [сверка до партии стопы]')
current=current.replace('код/данные совпали с checkout проверенной публикации;','на тот момент код/данные совпали с checkout проверенной публикации;')
current+=f'\n- [D: завершённая предметная партия стопы]({report}); [сверка текущих данных и новых UI-проверок]({evidence}/consistency.json). Стопа дополнена локально после версии 21; автоматическая синхронизация с публичным сайтом не предполагается.\n'
# Preserve every old issue, status except the explicitly accepted CAT, and criterion text.
oldcards={m[1]:m[2] for m in re.finditer(r'^### ([A-Za-z0-9_-]+)\n(.*?)(?=^### |\Z)',old_issues,re.M|re.S)}
newcards={m[1]:m[2] for m in re.finditer(r'^### ([A-Za-z0-9_-]+)\n(.*?)(?=^### |\Z)',issues,re.M|re.S)}
for ident,body in oldcards.items():
    assert ident in newcards
    for prefix in ['- Решение и критерий закрытия:']:
        line=next(l for l in body.splitlines() if l.startswith(prefix));assert line in newcards[ident],ident
    if ident!='CAT-LOWER-FOOT':assert re.search(r'Статус: \*\*([^*]+)',body)[1]==re.search(r'Статус: \*\*([^*]+)',newcards[ident])[1],ident
oldjournal=old_progress.split('## Записи журнала',1)[1];assert oldjournal in progress
for name,text in [('ANATOMY_ISSUES.md',issues),('ANATOMY_PROGRESS.md',progress),('CURRENT_PROJECT_STATUS.md',current)]:
    bom,crlf=formats[name];data=text.replace('\n','\r\n') if crlf else text
    (root/name).write_bytes((b'\xef\xbb\xbf' if bom else b'')+data.encode('utf-8'))
print(json.dumps({'updated':3,'issues':len(cards),'counts':dict(counts),'science':science,'stages':dict(stages),'old_ids_and_criteria_preserved':len(oldcards),'old_journal_preserved':True},ensure_ascii=False))
