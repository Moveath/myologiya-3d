"""Record accepted side/isolation regressions, retaining all pre-existing issue states."""
import hashlib, json, re, sys
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'verify'))
from verify_anatomy_registry import check

RUNS=[
 'side-isolation-unit-2026-10-19T03-33-06-290Z-uP4KJ9',
 'side-isolation-mcp-2026-10-19T03-25-42-792Z-KUNorW',
 'side-isolation-mcp-2026-10-19T03-29-52-213Z-hghctj',
 'side-isolation-mcp-2026-10-19T03-34-50-244Z-gJqzhw',
 'side-isolation-mcp-2026-10-19T03-34-50-334Z-7p6uGe',
]
for run in RUNS:
    assert json.loads((ROOT/'research/evidence-runs'/run/'result.json').read_text(encoding='utf8'))['status']=='passed',run
for name,h in json.loads((OUT/'hashes-before.json').read_text(encoding='utf8')).items():
    assert hashlib.sha256((ROOT/'site'/name).read_bytes()).hexdigest()==h,name

issues=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf-8-sig')
progress=(ROOT/'ANATOMY_PROGRESS.md').read_text(encoding='utf-8-sig')
old_issues=(OUT/'original-ANATOMY_ISSUES.md').read_text(encoding='utf-8-sig')
old_progress=(OUT/'original-ANATOMY_PROGRESS.md').read_text(encoding='utf-8-sig')
assert issues==old_issues and progress==old_progress,'Registry changed since baseline; reconcile before writing'
report='research/side-isolation-report-2026-10-19.md'
evidence='research/evidence-runs/side-isolation-2026-10-19T03-12-10-723Z-FKtz2V'
coverage='research/evidence-runs/side-isolation-unit-2026-10-19T03-33-06-290Z-uP4KJ9/muscle-bone-context.json'
new_summary=f'LOG-20261019-05: **239 задач / 63 проверено / 176 не закрыто**: 33 открыты, 84 требуют проверки, 59 заблокированы. Научная проверка — 140. SYS-SIDE-ISOLATION проверена; DATA-MUSCLE-BONE-LINKS требует проверки. Прежние 237 ID/статусов сохранены. [Отчёт]({report}).'
issues=issues.replace('## Сводка\n','## Сводка\n\n'+new_summary+'\n',1)
issues=issues.replace('LOG-20261019-04: **237 задач','Исторический срез LOG-20261019-04: **237 задач',1)
issues=issues.replace('| требует проверки | 83 |','| требует проверки | 84 |',1).replace('| проверена | 62 |','| проверена | 63 |',1)
index='| [SYS-SIDE-ISOLATION](#sys-side-isolation) | Фильтр сторон и явный разрешённый состав изоляции | 5 | P1 | проверена |\n| [DATA-MUSCLE-BONE-LINKS](#data-muscle-bone-links) | Неполное структурирование костных связей мышц и частей | 7 | P1 | требует проверки |\n\n'
issues=issues.replace('## Карточки задач',index+'## Карточки задач',1)

def supplement(text, ident, addition):
    pattern=rf'(^### {re.escape(ident)}\n)(.*?)(?=^### |\Z)'
    def repl(m):
        body=re.sub(r'Обновлено: \*\*\d{4}-\d{2}-\d{2}\*\*', 'Обновлено: **2026-10-19**',m[2])
        return m[1]+body.rstrip()+'\n\n- Дополнение LOG-20261019-05: '+addition+'\n\n'
    text,n=re.subn(pattern,repl,text,flags=re.M|re.S);assert n==1,ident
    return text

issues=supplement(issues,'SYS-SHARED-CONTEXT',f'Регрессия 1280/390 подтвердила C7–T1 после разделения служебных фоновых ID: изоляция сохраняет cervical_7 и thoracic_1, выключение общего окружения не убирает участников. Канонические ID и статус сохранены. [Отчёт]({report}).')
issues=supplement(issues,'GEO-011',f'Новый режим костей мышцы читает существующие pin.m → pin.b и не подтверждает площади. Неполнота явных связей вынесена в DATA-MUSCLE-BONE-LINKS; отсутствие связей masseter_left не заполнено зеркалированием или разбором текста. Критерий GEO-011 не выполнен и статус сохранён. [Перечень]({coverage}).')
issues+=f'''
## Стороны и изоляция — адресное техническое исправление

### SYS-SIDE-ISOLATION

**Фильтр сторон и явный разрешённый состав изоляции**

- Категория: видимость и навигация. Этап: **5**. Приоритет: **P1**. Статус: **проверена**. Научная проверка: нет. Обновлено: **2026-10-19**.
- Структуры и ID: biceps_brachii, triceps_brachii и его long/lat, humerus/humerus_left, scapula/scapula_left, radius/ulna; общие extra_humerus_elbow_joint, C7–T1; noModel scaphoid_left. Служебные context:FMA… не меняют анатомические ID.
- Источник обнаружения: обращение пользователя; до исправления изоляция biceps_brachii оставляла 35 костей, межкостную перепонку и 42 фоновых меша. [Воспроизведение]({evidence}/reproduction-before.json).
- Затронутые файлы: site/index.html, site/local.html, site/atlas-visibility.js, site/atlas-model-sides.js, scripts/make_model_sides.py, tools/verify-side-isolation.mjs, tools/prepare-side-isolation-mcp.mjs.
- Решение и критерий закрытия: явный режим обеих/правой/левой стороны; нет противоположных мешей в одностороннем виде; строгая изоляция исключает неразрешённые кости/фон; режим костей мышцы использует только явные отношения с корректным scope части; общие компоненты, выбор, поиск, прозрачность, BVH/срезы и noModel сохраняются на 1280/390. Оригинальные GLB и данные неизменны.
- Доказательства исправления и тесты: Node 10 групп; Blender MCP 143 mesh-объекта и сохранение сцены/хешей; Playwright MCP по 87 проверок плюс по 10 адресных проверок переключения частей на 1280/390, без ошибок консоли. Подтверждены поиск другой стороны, отдельные фоновые ID, реальные клики, BVH/native faceIndex и срезы. [Отчёт и все протоколы]({report}). Отсутствующая геометрия и полнота связей мышц этой задачей не закрываются.

### DATA-MUSCLE-BONE-LINKS

**Неполное структурирование костных связей мышц и частей**

- Категория: анатомические отношения и область доказательств. Этап: **7**. Приоритет: **P1**. Статус: **требует проверки**. Научная проверка: да. Обновлено: **2026-10-19**.
- Структуры и ID: адресно masseter_left (есть текстовые описания, нет явной костной связи), masseter_right (есть только связь с mandible в pin.m); полный перечень 255 мышц и 121 части с sourcePinIds/boneIds — [таблица]({coverage}). Ноль явных связей у 146 мышц и 70 частей — показатель покрытия метаданных, не число доказанных анатомических пропусков.
- Источник обнаружения: регрессия нового режима костей мышцы и сверка текущего ATLAS с site/skull-muscle-attachments.json. Текстовые поля не имеют достаточной формальной привязки к ID костей; нулевое покрытие может быть корректным для мягкотканного прикрепления.
- Затронутые файлы: scripts/*muscles*.py, генераторы pin.m, site/skull-muscle-attachments.json; в текущем исправлении — только потребитель site/atlas-visibility.js и предупреждения site/index.html.
- Решение и критерий закрытия: по каждой предметно выбранной строке проверить начало/прикрепление и стороны по двум независимым источникам, отличить кость/мягкую ткань, оформить явные ID/роли/part и refs без обязательной выдуманной координаты. Для части не наследовать whole_muscle как specific. Проверить полноту разрешённого списка в интерфейсе; при отсутствии доказательств сохранять статус неопределённости. Это отличается от геометрической задачи GEO-011, которая остаётся открытой.
- Доказательства исправления и тесты: сохранён поимённый снимок существующих отношений; предупреждение об отсутствии связей masseter_left проверено на ПК/мобильной ширине. Исправление анатомического покрытия не выполнено; ложный fallback по близости или противоположной стороне не добавлен. Для разблокировки нужен адресный разбор источников и формализация связи, не новая версия Three.js. [Отчёт]({report}).
'''

lines=progress.splitlines()
for i,line in enumerate(lines):
    if line.startswith('| 5 |'):
        lines[i]=f'| 5 | Полная проверка и исправление пинов | В работе | LOG-20261019-05: исправлены стороны/изоляция, костный контекст и переключение частей; SYS-SIDE-ISOLATION проверена. Предыдущая доступная партия верхних конечностей завершена; четыре FDS и геометрический остаток сохранены. Нижние конечности ещё не начаты. Записи учёта: 41 проверено / 115 всего; это не процент полноты. |'
    if line.startswith('| 7 |'):
        lines[i]=line.replace('0 проверено / 44 всего','0 проверено / 45 всего').replace('fieldRefs/fieldScope,','DATA-MUSCLE-BONE-LINKS — отдельная формализация связей и scope, без закрытия GEO-011. fieldRefs/fieldScope,')
progress='\n'.join(lines)+'\n'
old_summary='**237 записей: 62 проверено, 175 не закрыто; 59 заблокированы; 83 имеют статус «требует проверки».** Научная проверка требуется 139 незакрытым записям. Открыта: 33; в работе: 0; исправлена без приёмки: 0. Текущий срез LOG-20261019-04; история сохранена.'
assert old_summary in progress
progress=progress.replace(old_summary,'**239 записей: 63 проверено, 176 не закрыто; 59 заблокированы; 84 имеют статус «требует проверки».** Научная проверка требуется 140 незакрытым записям. Открыта: 33; в работе: 0; исправлена без приёмки: 0. Текущий срез LOG-20261019-05; история сохранена.',1)
progress+=f'''
### LOG-20261019-05 — стороны тела, строгая изоляция и костный контекст

- Запрос: устранить противоположные и неразрешённые объекты при просмотре руки/мышц, сохранив общий двусторонний режим. Это адресная техническая работа этапа 5; новый анатомический регион не начат.
- Причина воспроизведена: при изоляции biceps_brachii оставались 35 костей, 1 мягкотканная структура и 42 фоновых меша. Фильтра сторон не было, c|FMA объединялись в context. Blender подтвердил отдельные левые меши плечевого пояса/плеча.
- Изменения: режим Обе/Справа/Слева с сохранением по разделам; 517 технических метаданных сторон из манифестов/словаря; раздельные служебные ID контекста; явный разрешённый список изоляции; опция Кости мышцы из pin.m → pin.b; для части — только связи с её part. Реальные клики выявили и помогли исправить отсутствие пересчёта видимости при смене части. Поиск противоположной стороны переключает односторонний режим, а «Обе» сохраняется.
- Проверки: Node 10 групп; SHA-256 14 опубликованных пакетов моделей и 14 файлов данных/пинов неизменен; Blender MCP 143 mesh-объекта, оригинальная сцена/хеши сохранены. Playwright MCP 1280/390: по 87 основных проверок и по 10 адресных проверок частей после последнего уточнения. Поиск, карточки, noModel, общие связи, прозрачность, изоляция, реальные клики, BVH/native faceIndex и срезы пройдены; ошибок консоли нет. Снимки обеих тем осмотрены. Python-генераторы успешны; зависимости и Three.js 0.170.0 не менялись. [Отчёт]({report}).
- Остаток: DATA-MUSCLE-BONE-LINKS требует проверки (255 мышц/121 часть в поимённой таблице; нулевые связи не автоматически ошибка). У masseter_left предупреждение заменяет произвольный подбор костей. Срединные/неразделённые модели не разрезаются фильтром. GEO-UPPER-LEFT-FOREARM, GEO-HAND-LEFT-MODELS, GEO-HAND-MCP1-R/U, GEO-011 и все старые блокеры сохранены.
- Учёт: зарегистрирована и проверена SYS-SIDE-ISOLATION; зарегистрирована требует проверки DATA-MUSCLE-BONE-LINKS. Все 237 прежних ID/статусов/критериев сохранены. Итого 239 задач, 63 проверены, 176 не закрыты: 33 открыты / 84 требуют проверки / 59 заблокированы; научная проверка — 140. Принята одна новая техническая задача, прежних анатомических задач не закрыто.
- Следующий шаг: продолжать утверждённую предметную дорожную карту; формализацию костных связей мышц выполнить в соответствующей научной партии этапа 7. Отсутствующие модели не восстановлены и не зеркалились. История и промежуточные результаты не перезаписывались.
'''

pattern=r'^### ([A-Za-z0-9_-]+)\n(.*?)(?=^### |\Z)'
before=dict(re.findall(pattern,old_issues,re.M|re.S));after=dict(re.findall(pattern,issues,re.M|re.S))
assert len(before)==237 and len(after)==239
for id,body in before.items():
    assert id in after
    for p in [r'Статус: \*\*([^*]+)\*\*',r'- Решение и критерий закрытия: ([^\n]+)']:
        assert re.search(p,body)[1]==re.search(p,after[id])[1],id
assert old_progress.split('## Записи журнала',1)[1].strip() in progress
(ROOT/'ANATOMY_ISSUES.md').write_text(issues,encoding='utf8')
(ROOT/'ANATOMY_PROGRESS.md').write_text(progress,encoding='utf8')
result=check();result.update(oldIdsRetained=237,oldStatusesRetained=237,oldClosureCriteriaRetained=237,oldJournalRetained=True)
with (OUT/'ledger-check.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False))
