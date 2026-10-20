import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
report='research/stage5-lumbopelvic-targeted-report-2026-10-18.md';rel=OUT.relative_to(ROOT).as_posix()
link=f' [Отчёт]({report}); [доказательства]({rel}/evidence.json).'
text=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf8')
notes={
 'GEO-PELVIS-LANDMARKS':'Теперь 143 тазовые костные/составные записи (140 + 3), 75 без p; 68 старых костных p не приняты. В Blender нет именованных масок/меток границ в трёх мешах; хеши неизменны, прежний trimesh переиспользован. Для SI и костных краёв можно начать адресную ручную разметку текущей сетки с независимой приёмкой; для хрящевых/связочных просветов нужны данные того же образца. Переход к верхним конечностям не блокирует. Этап 5 — доказательства, 6 — показ, 8 — приёмка; точная геометрическая публикация до приёмки ограничена.',
 'GEO-LUMBAR-LANDMARKS':'Добавлены 5 групп базивертебральных отверстий, теперь 117 поясничных записей без принятой геометрии. Нужны поуровневые отверстия/внутренние каналы, стороны и принятие вариантов. Новых p/контуров 0; прежние STL/GLB неизменны. Не препятствует проверке верхних конечностей; этапы 5/6/8, обязательна приёмка перед точным пространственным показом.',
 'GEO-007':'Доступность ресурсов проверена адресно: FMA16202 остаётся единым исходником, в GLB нет принятой маски Co1; тазовых DICOM/NIfTI/NRRD не найдено. Два прежних вида переиспользованы, новый разрез не выполнялся. Нужна идентифицированная сегментация/изображения того же образца либо независимая приёмка различимой границы. Не мешает верхним конечностям, но блокирует точную самостоятельную геометрию копчика; этапы 5/6/8.',
 'PIN-001':'Исходные 447 неизменны. Добавлены 8 описательных записей без p/n. По атласу 747 без p: 447 исходных + 151 общая + 149 дополнительных собственных; 2 прежних дополнительных отверстия стали общими через relations без координат. Это не 8 исправленных координат; новые ID в candidate-decisions/targeted-records.'}
for id,note in notes.items():
    pat=re.compile(r'(^### '+re.escape(id)+r'\n)([\s\S]*?)(?=^### |\Z)',re.M);m=pat.search(text);assert m
    body=re.sub(r'- Дополнение LOG-20261018-06:[^\n]*','- Дополнение LOG-20261018-06: '+note+link,m[2]);text=text[:m.start(2)]+body+text[m.end(2):]
text=text.replace('modelNote записей с geometryRequirements.status=unverified_extent; адресная проверка31изменённой/новойкарточки.','modelNote записей с geometryRequirements.status=unverified_extent; адресная проверка 31 изменённой/новой карточки.')
text=text.replace('снимки MCP1280/390этойпартии: «Принятые границы…» безявногозаголовкатребований.','снимки MCP 1280/390 этой партии: «Принятые границы…» без явного заголовка требований.')
text=text.replace('добавленаусловнаяподпись «Геометрия не принята. Ограничения и необходимые доказательства»;31/31на1280и390,снимокпроверен. Наличие подписи не закрываетгеометрическиезадачи.','добавлена условная подпись «Геометрия не принята. Ограничения и необходимые доказательства»; 31/31 на 1280 и 390, снимок проверен. Наличие подписи не закрывает геометрические задачи.')
(ROOT/'ANATOMY_ISSUES.md').write_text(text,encoding='utf8')
progress=(ROOT/'ANATOMY_PROGRESS.md').read_text(encoding='utf8')
line=next(l for l in progress.splitlines() if l.startswith('| 5 |'))
progress=progress.replace(line,'| 5 | Полная проверка и исправление пинов | В работе | LOG-20261018-06: 7 адресных вопросов поясницы/таза, 6 каталожных решений; переходная нумерация образца остаётся в проверке. 8 новых без p, 23 исправленные записи. Предметный критерий CAT-PELVIS-REVIEW выполнен; геометрия открыта. Можно переходить к верхним конечностям. 33/103 задачи, не процент полноты. |')
progress=progress[:progress.index('### LOG-20261018-06')]+'''### LOG-20261018-06 — адресное завершение поясницы и таза

- Семь прежних K-кандидатов двух CAT-задач разобраны; шесть каталожных решений приняты. Применимость переходной нумерации к BP3D остаётся неподтверждённой; источник FMA и уровни сохранены.
- Добавлены 8 записей без координат: 2 вариантные предушковидные борозды, 1 парная группа Co1, 5 групп базивертебральных отверстий. Исправлены 23 прежних описания/связи, остальные 2042 пина неизменны. Новых принятых координат, контуров и масок 0; 6 att не переоценивались как миология.
- Задний запирательный бугорок: анатомический partOf=ischium при отдельно сохранённой TA98-группе pubis. Два больших седалищных отверстия сохранили ID и доступны у крестца; 2 новых членства / 4 явных связи. Для mamillo-accessory размещён вариантный текст в 10 прежних карточках, без десяти фиктивных отверстий.
- Источники: официальная TA98, Gray, Sobotta 1914 (законно доступный текст), NCBI Bookshelf NBK549870, OpenStax, Dartmouth, Anatomy Standard. Новые метаданные 6 PMID проверены EFetch. Первый широкий поиск предушных структур отклонён; уточнённый ESearch успешен. Доступ аннотации/индексированного текста не выдан за полный текст.
- Blender MCP: 3 меша, технические атрибуты без анатомических масок, хеши/исходная сцена сохранены. Переиспользованы 74 расстояния trimesh после проверки хешей и 2 прежних нужных ракурса; тяжёлый повтор не запускался. Отсутствие сегментации/мягкотканных границ — конкретный блокер.
- Python: оба изменённых генератора, TA98 (762 / 3 известных расхождения), пересборка local.html. Node: 31 адресная запись, старые ID/координаты/мышцы/кости/оригиналы сохранены. Playwright MCP 1280 dark / 390 light: по 31 карточке, по 4 общих отображения, поиск/выбор/изоляция/прозрачность/canvas/BVH (10 лучей), 0 ошибок консоли.
- После обнаруженной двусмысленности modelNote добавлен явный UI-статус «Геометрия не принята»; ещё 31/31 проверки обоих размеров и снимок. Исторические снимки не перезаписывались. Ошибки первого запуска генератора без CLI-аргументов и доступа к sandbox socket сохранены; исправленные повторы завершились успешно.
- CAT-PELVIS-REVIEW: требует проверки → проверена (предметный критерий, не GEO). Новая SYS-GEOMETRY-NOTE-STATUS: проверена. CAT-LUMBAR-DETAIL, оба региональных GEO, GEO-007, SHX-pelvic-outlet, вся очередь черепа/шеи/груди/лицензий сохранены. Других прежних статусов не изменяли.
- Учёт: 225 задач, 55 проверены, 170 незакрыты (34 открыты / 79 требуют проверки / 57 заблокированы), научная проверка 134; этап 5 = 33/103. За эту задачу проверены 2 записи реестра, из них 1 новая. В атласе 2073 ориентира, 747 без p; в области 117 поясничных + 143 тазовых костных/составных записи, 6 att отдельно.
- Доступная предметная партия завершена. Можно планировать верхние конечности, без перехода в этой задаче. До 3D-публикации точных границ нужны принятые маски/исходники; неизвестные варианты и нумерация не объявляются подтверждёнными.
'''+link+'\n'
prior=(OUT/'before-ANATOMY_PROGRESS.md').read_text(encoding='utf8');assert prior.split('## Записи журнала',1)[1] in progress
(ROOT/'ANATOMY_PROGRESS.md').write_text(progress,encoding='utf8')
hashes=json.loads((OUT/'hashes-before.json').read_text(encoding='utf8'))
allowed={'scripts/pelvis_stage5_review.py','scripts/lumbar_stage5_review.py','site/pins-leg.js','site/pins-context-bones.js','site/index.html','site/local.html','ANATOMY_ISSUES.md','ANATOMY_PROGRESS.md'}
changed=[];protected=[]
for f,sha in hashes.items():
    now=hashlib.sha256((ROOT/f).read_bytes()).hexdigest()
    if now!=sha:assert f in allowed,f;changed.append(f)
    else:protected.append(f)
assert set(changed)==allowed
new_files=['scripts/lumbopelvic_targeted_review.py','tools/prepare-stage5-lumbopelvic-targeted-evidence.mjs','tools/verify-stage5-lumbopelvic-targeted.mjs','tools/prepare-stage5-lumbopelvic-targeted-mcp.mjs','verify/review_lumbopelvic_boundaries_blender.py',report]
all_changed=changed+new_files
checked_links=[]
for target in re.findall(r'\]\(([^)]+)\)',(ROOT/report).read_text(encoding='utf8')):
    if target.startswith('http'):continue
    target=target.split('#')[0]
    if target.endswith('/evidence.json'):continue
    assert (ROOT/'research'/target).exists(),target;checked_links.append(target)
summary=dict(status='passed',changedFiles=all_changed,fileHashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in all_changed},
    protectedFilesUnchanged=len(protected),originalModelsUnchanged=True,oldCoordinatesUnchanged=True,newGeometry=0,
    previousProgressHistoryPreserved=True,localReportLinksChecked=len(checked_links),
    evidence=dict(data='data-regression.json',records='targeted-records.json',decisions='candidate-decisions.json',registry='registry-final.json',blender='blender-boundary-availability.json',pubmed='pubmed-verified.json',uiNote='geometry-label-ui.json',
      desktop='../stage5-lumbopelvic-targeted-mcp-2026-10-18T16-59-17-449Z-8EY5T3/result.json',mobile='../stage5-lumbopelvic-targeted-mcp-2026-10-18T17-00-08-451Z-S5m1z0/result.json',
      failedTransport='../stage5-lumbopelvic-targeted-mcp-2026-10-18T16-58-27-734Z-D0D0hh/transport-error.json',previousTrimesh='../stage5-pelvis-2026-10-18T16-21-31-309Z-EguUlx/trimesh-pelvis-v2.json'),
    incidents=['Public API initially failed inside sandbox; approved official API access succeeded.',
     'Broad ESearch returned unrelated preauricular ear records; excluded, focused query saved separately.',
     'make_pins_leg without three required CLI arguments failed before write; documented invocation succeeded.',
     'Initial sandbox HTTP connection failed; approved loopback server allowed two fresh complete MCP runs.',
     'Final hash verifier initially omitted authorized registry updates from its allow-list; corrected to permit the two requested Markdown files.'])
with (OUT/'evidence.json').open('x',encoding='utf8') as f:json.dump(summary,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='passed',protected=len(protected),changed=len(all_changed),reportLinks=len(checked_links))))
