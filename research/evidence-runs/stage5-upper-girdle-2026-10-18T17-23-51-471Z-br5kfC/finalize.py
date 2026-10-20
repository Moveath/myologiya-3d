"""One-time additive registry update; never overwrites test evidence."""
import collections, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
REL=OUT.relative_to(ROOT).as_posix(); REPORT='research/stage5-upper-girdle-report-2026-10-18.md'
def write(name,value):
    with (OUT/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def parse(t):
    d={}
    for m in re.finditer(r'^### ([^\n]+)\n([\s\S]*?)(?=^### |\Z)',t,re.M):
        s=re.search(r'Статус: \*\*([^*]+)\*\*',m[2])
        if s:
            assert m[1] not in d
            d[m[1]]=dict(status=s[1],body=m[2])
    return d
issue=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf8')
assert issue==(OUT/'before-ANATOMY_ISSUES.md').read_text(encoding='utf8'),'Concurrent registry change'
old=parse(issue); assert len(old)==225
link=f'[Отчёт]({REPORT}); [по-ID результат]({REL}/reviewed-records-final.json).'
def append_to(id,text):
    global issue
    pattern=r'(^### '+re.escape(id)+r'\n[\s\S]*?)(?=^### |\Z)'
    issue,n=re.subn(pattern,lambda m:m[1].rstrip()+'\n\n- Дополнение LOG-20261018-07: '+text+' '+link+'\n\n',issue,count=1,flags=re.M)
    assert n==1,id
append_to('SRC-001','32 clavicle_left/scapula_left получили предметные определения, Gray/Sobotta/NCBI и пределы геометрии. 28 humerus_left ещё не проверены в этой области. Прежние 106 ID остаются историческим набором; наличие новых refs не закрывает исходный критерий адресной топографической приёмки.')
append_to('SRC-002','У 32 правых записей плечевого пояса появились структурированные refs. Остальные ID прежнего массового набора не объявляются проверенными; статус сохранён.')
append_to('CAT-HAND-SESAMOIDS','Текущий каталог по-прежнему содержит pisiform и упоминания, но не две отдельные кости MCP I. Карточки без модели возможны на этапе 5; при реализации проверить noModel/contextTargets: имеющаяся подсказка контекста говорит «мышцы» и требует корректного костного варианта. Карточки, B/V и UI-приёмка отложены до партии кисти; это не закрытие и не блокировка семантики отсутствием GLB.')
for id in ['GEO-HAND-MCP1-R','GEO-HAND-MCP1-U']:
    append_to(id,'Четыре arm-GLB/base64 совпадают с хешами инвентаризации 15.10. Повторный поиск тех же компонентов не выполнен; прежний Blender-результат не содержит принятого сесамоида. Нужна отдельная лицензированная человеческая сегментация с доказанными стороной/масштабом/контекстом; точка mc1_caput и шеститочечный фрагмент фаланги не замена. Статус заблокирована сохраняется.')

new=[('CAT-UPPER-GIRDLE-CORRECTIONS','Предметные исправления четырёх костей плечевого пояса','проверена',
    'каталог и классификация',
    '64 исходных ID и 4 новых ID — reviewed-records-final.json; обе ключицы, обе лопатки.',
    'Нет предметных определений у левых записей и типов у 64; не представлены spinoglenoid notch и общий AC-сустав; безусловное описание хода артерии.',
    'scripts/upper_girdle_stage5_review.py; scripts/make_pins.py; scripts/make_context_bone_data.py; site/pins.js; site/pins-context-bones.js.',
    'Критерий этой записи: определения/типы 64, подтверждённые дополнения и общий ID на сторону, старые ID/p/n/m сохранены, поиск/карточки/изоляция на 1280 и 390. Выполнен; точная геометрия исключена из этого предметного критерия и учитывается отдельно.',
    '64 исправлены; 4 новые без p/n; 2 общих экземпляра / 4 связи. Node, TA98 (3 прежних расхождения), Playwright обе ширины успешно. Геометрия не принята.'),
   ('GEO-UPPER-GIRDLE-LANDMARKS','Не приняты индивидуальная локализация и протяжённость ориентиров плечевого пояса','требует проверки',
    'анатомическая локализация и геометрия',
    'Все 68 ID reviewed-records-final.json: 32 прежних p справа, 32 левых без p, четыре новые без p.',
    'Blender/Trimesh и шесть ракурсов дают близость, но не анатомическую приёмку или подписанные границы.',
    'pins/ta.json; site/arm-q-glb.txt (только чтение); build_context_bones/arm_extra_hi.glb (только чтение); будущие производные маски.',
    'Этапы 5/6/8: независимая приёмка каждого существующего p; маски/пути/границы 66 протяжённых структур и две точечные локализации. На видимом рельефе возможна экспертная разметка; при недостатке детализации нужны исходник/изображения того же образца. AC-объём требует мягкотканных данных. Не блокирует проверку других костей, но запрещает заявлять точную 3D-полноту при выпуске.',
    'Blender и Trimesh: 4 кости, 32 точки, max 0,242502 мм, согласование 0,000083 мм. Ни одна новая точка или граница не принята; все старые p сохранены.'),
   ('CAT-UPPER-REMAINDER','Оставшаяся предметная проверка плеча, предплечья и кисти','открыта',
    'каталог и научная проверка',
    '31 костная карточка, включая lunate/triquetrum без собственных пинов; 176 исходных записей с двумя soft — remaining-records-final.json.',
    'Инвентаризация 35 костей / 240 исходных записей; первая внутренняя партия обработала только плечевой пояс.',
    'scripts/make_pins.py; scripts/context_bone_cards.py; scripts/ta98.py; текущие карточки руки/референсы; будущие адресные обзоры.',
    'Следующая партия 95 записей плеча/предплечья с перепонкой, затем 81 кисти с удерживателем: предметные определения/применимость/полнота/варианты/связи, тесты и по-ID остаток. CO-ARM-* и CAT-HAND-SESAMOIDS решаются по своим критериям, не дублируются новой задачей. До релиза нельзя заявлять проверку всех верхних конечностей.',
    'Сейчас только инвентаризация и сохранение остатка; эти 176 не считаются анатомически проверенными. Все CO-ARM-* и источниковые блокеры сохранены.')]
index='\n'.join(f'| [{id}](#{id.lower()}) | {title} | 5 | P1 | {status} |' for id,title,status,*_ in new)+'\n\n'
issue=issue.replace('## Карточки задач',index+'## Карточки задач',1)
issue+='\n\n## Верхние конечности — первая предметная партия\n'
for id,title,status,cat,structures,source,files,criteria,proof in new:
    issue+=f'\n### {id}\n\n**{title}**\n\n- Категория: {cat}. Этап: **5**. Приоритет: **P1**. Статус: **{status}**. Научная проверка: да. Обновлено: **2026-10-18**.\n- Структуры и ID: {structures}\n- Источник обнаружения: {source} {link}\n- Затронутые файлы: {files}\n- Решение и критерий закрытия: {criteria}\n- Доказательства исправления и тесты: {proof} {link}\n- История: зарегистрирована LOG-20261018-07; прежние задачи/критерии не заменены.\n'
now=parse(issue);assert len(now)==228
assert all(now[id]['status']==v['status'] for id,v in old.items())
counts=collections.Counter(v['status'] for v in now.values())
assert counts==dict(проверена=56,открыта=35,заблокирована=57,**{'требует проверки':80})
science=sum(v['status']!='проверена' and 'Научная проверка: да' in v['body'] for v in now.values());assert science==136
summary='Всего **228 записей**; подтверждённо закрыто **56**, не закрыто **172**: 35 открыты, 80 требуют проверки, 57 заблокированы. Научной проверки требуют **136** незакрытые записи. Этап 5 — **34/106**. LOG-20261018-07: проверена CAT-UPPER-GIRDLE-CORRECTIONS; GEO-UPPER-GIRDLE-LANDMARKS требует проверки, CAT-UPPER-REMAINDER открыта. Ни одна прежняя нерешённая задача не закрыта. Числа задач не равны числу структур.'
issue,n=re.subn(r'^Всего \*\*225 записей\*\*[^\n]*',summary,issue,count=1,flags=re.M);assert n==1
for oldline,newline in [('| открыта | 34 |','| открыта | 35 |'),('| требует проверки | 79 |','| требует проверки | 80 |'),('| проверена | 55 |','| проверена | 56 |')]:
    assert oldline in issue;issue=issue.replace(oldline,newline,1)
issue=issue.replace('**2073** записи ориентиров. Без p — **747 = 447 исходных + 151 общая + 149 дополнительных собственных**','**2077** записей ориентиров. Без p — **751 = 447 исходных + 153 общие + 151 дополнительная собственная**',1)
intro=f'LOG-20261018-07: плечевой пояс — 4 кости, 64 исходных типа, 4 новые карточки без p; две общие суставные структуры. Вся верхняя конечность ещё не завершена: 31 кость и 176 записей далее. {link}\n\n'
issue=issue.replace('## Как пользоваться',intro+'## Как пользоваться',1)
(ROOT/'ANATOMY_ISSUES.md').write_text(issue,encoding='utf8')

progress=(ROOT/'ANATOMY_PROGRESS.md').read_text(encoding='utf8');assert progress==(OUT/'before-ANATOMY_PROGRESS.md').read_text(encoding='utf8')
progress,n=re.subn(r'^\| 5 \|[^\n]*', '| 5 | Полная проверка и исправление пинов | В работе | LOG-20261018-07: верхние конечности, партия плечевого пояса — 4 кости / 64 типа, 4 новые карточки, 2 общих сустава. Геометрия не принята; следующая партия 95 записей плеча/предплечья, затем 81 кисти. 34/106 задач, не процент анатомической полноты. |',progress,count=1,flags=re.M);assert n==1
progress,n=re.subn(r'^\*\*225 записей:[^\n]*','**228 записей: 56 проверены, 172 не закрыты; 57 заблокированы; 80 имеют статус «требует проверки».** Научная проверка требуется 136 незакрытым записям. Открыта: 35; в работе: 0; исправлена без приёмки: 0. Текущий срез LOG-20261018-07; прежняя история сохранена.',progress,count=1,flags=re.M);assert n==1
progress+=f'''

### LOG-20261018-07 — верхние конечности, плечевой пояс

- Инвентаризация: 35 костных карточек (32 справа, 3 слева), 2 soft; 240 исходных записей (232 TA + 6 att + 2 soft). Полная левая кисть не заявлена. Первая партия: обе ключицы/лопатки, 64 исходных ID; 26 area, 24 volume, 10 line, 2 space, 2 point.
- Реальные исправления: предметные определения и источники 32 левых записей вместо заглушек; 64 типа/обоснования/ограничения; вариабельный ход артерии у incisura, разделение поверхностей/ямок/отростков, контекст рёберного хряща и варианта акромиона. Стабильные ID, названия, p/n/m сохранены. Мышечные сведения не перерабатывались.
- Новые четыре карточки: две spinoglenoid notch без выдуманной латыни/TA-кода; два AC-сустава TA98 A03.5.03.001 с единым ID на сторону и четырьмя связями участия. Все без p/n. 2009 остальных записей, исходные модели и приложение не менялись.
- Источники: FIPAT, Gray, Sobotta OCR, NCBI Bookshelf; API EFetch двух PMID 24902100/24633009 прошёл. Для вариантов прочитаны индексированные аннотации, не полный PMC; электронная/печатная даты разделены. Источники подтверждают сущности, а не точки.
- Blender MCP: четыре кости, 32 старые правые точки, шесть просмотренных ракурсов; сцена сохранена. Trimesh: стороны/трансформации/конечность данных; max distance 0,242502 мм; расхождение с Blender 0,000083 мм. Координаты/маски приняты: 0.
- Python: генераторы и TA98 (762 термина, три старых расхождения). Node: 64 + 4 адресные записи, общие ID, 74 защищённых файла по хешам. Playwright MCP 1280 dark / 390 light: по 68 карточек, ограничения, четыре общих отображения, поиск/выбор/изоляция/прозрачность, реальный canvas-click, по 10 BVH/native лучей, ошибок консоли 0. Две UI-картинки просмотрены; физический телефон/срезы черепа заново не проверялись. После UI дополнены только локатор Gray и научная ссылка о диске; Node final прошёл, прежние свидетельства сохранены.
- Сесамоиды: хеши четырёх arm-ресурсов совпали с инвентаризацией 15.10, новый поиск неизменённых компонентов не нужен. CAT-HAND-SESAMOIDS открыта; GEO-HAND-MCP1-R/U заблокированы исходниками. Карточки без сетки возможны, в партии кисти также устранить мышечную формулировку noModel-контекста для кости. Варианты B/V/Q не объявлены типичными мешами.
- Новые задачи: CAT-UPPER-GIRDLE-CORRECTIONS проверена; GEO-UPPER-GIRDLE-LANDMARKS требует проверки; CAT-UPPER-REMAINDER открыта. SRC-001/002 уточнены частично; ни один прежний статус не изменён. Остаток плеча/предплечья/кисти — точные 176 ID, плюс проверка костей без собственных пинов; предыдущие области/лицензии/CO-ARM-* сохранены.
- Учёт: 228 задач, 56 проверены, 172 незакрыты (35 открыты / 80 требуют проверки / 57 заблокированы), научная проверка 136; этап 5 = 34/106. Проверена одна новая запись реестра, не одна анатомическая структура. В атласе 2077 ориентиров, 751 без p (447 + 153 + 151).
- Доступная партия плечевого пояса завершена. Верхние конечности ещё требуют партий 95 и 81 записей; нижние конечности, цвета и мышцы не затронуты. {link}
'''
(ROOT/'ANATOMY_PROGRESS.md').write_text(progress,encoding='utf8')

baseline=json.loads((ROOT/'research/hand-sesamoid-inventory-2026-10-15.json').read_text(encoding='utf8'))
models=[]
for file,v in baseline['glbs'].items():
    digest=hashlib.sha256((ROOT/file).read_bytes()).hexdigest();assert digest==v['fileSHA256']
    models.append(dict(file=file,sha256=digest,unchangedSince='2026-10-15',sesamoidNameMatches=v['sesamoidNameMatches']))
write('hand-reuse.json',dict(models=models,blenderPrior='research/stage4-2026-10-15/arm-blender.json',newAcceptedSesamoidGeometry=0,newCards=0,catalogueTask='CAT-HAND-SESAMOIDS',geometryTasks=['GEO-HAND-MCP1-R','GEO-HAND-MCP1-U']))
write('registry-final.json',dict(total=len(now),statuses=counts,scienceOpen=science,stage5=dict(verified=34,total=106),previousStatusesUnchanged=True,newIds=[n[0] for n in new]))
write('evidence.json',dict(report=REPORT,data='data-regression-final.json',records='reviewed-records-final.json',remaining='remaining-records-final.json',
    blender='blender-girdle.json',trimesh='trimesh-girdle.json',pubmed='pubmed-verified.json',hand='hand-reuse.json',registry='registry-final.json',
    playwright=['../stage5-upper-girdle-mcp-2026-10-18T17-30-07-162Z-rWzqeU/result.json','../stage5-upper-girdle-mcp-2026-10-18T17-31-22-883Z-taCC8t/result.json'],
    ta98=dict(command='.venv/Scripts/python.exe -X utf8 verify/verify_ta98.py',exitCode=0,terms=762,knownDifferences=['A02.5.10.015','A02.5.10.017','A02.5.11.007'],missing=[],extra=[]),
    acceptedNewCoordinates=0,originalGLBChanged=False,notes='All files uniquely allocated. Initial wrong broad inventory run LnLp2q excluded; corrected scope uses bone group section.'))
print(json.dumps(dict(total=len(now),statuses=counts,previousStatusesUnchanged=True),ensure_ascii=False))
