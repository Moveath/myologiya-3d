import copy, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[3]
RUN=pathlib.Path(__file__).resolve().parent
REPORT='research/stage7-muscle-batch2-report-2026-10-21.md'
MATRIX='research/stage7-muscle-batch2-decisions-2026-10-21.json'
data=copy.deepcopy(json.loads((ROOT/'research/stage7-muscle-blockers-2026-10-21.json').read_text(encoding='utf8')))
data['scope']='34 прежних MG/MP: сверка решений по неизменённым хешам, без повторного полного научного аудита; дополнительная работа ANAT-002 отдельно'
data['evidenceRun']=RUN.relative_to(ROOT).as_posix()
data['currentCatalogue']={'cards':259,'meshes':304,'originalMissingMuscles':13,'additionalMissingMuscles':1,'missingParts':21,'boneNoModel':20}
for row in data['rows']:
    row['reviewMode']='Previous anatomy/source assessment retained; current catalogue integrity checked against 16 prior SHA-256 hashes'
    ident=row['issue']
    if ident=='MG-palmaris_brevis':
        row['newEvidence']='Physiome Git HEAD metadata 185bc97e4ffcb44e8a73ee97296d81cb494f0ca3; clone failed TLS; web 403. No model file or per-resource licence received. Kerkhof et al. DOI 10.1111/joa.12877 points to MorphoSource P419; files/rights/frame not received.'
        row['links']+=['https://onlinelibrary.wiley.com/doi/full/10.1111/joa.12877']
    if ident.startswith('MP-'):
        row['structureType']='Part or fascicle of an existing whole muscle; not an independent missing whole muscle'
        if 'oculi' in ident:
            row['requiredGeometry']='Sample-specific layer/fascicle segmentation; a general outer surface does not establish deep/ciliary coverage'
        elif 'omohyoid' in ident:
            row['requiredGeometry']='Masks of superior/inferior bellies with intermediate tendon boundary; do not cut the continuous parent arbitrarily'
        elif any(s in ident for s in ['nasalis','orbicularis_oris','diaphragm']):
            row['requiredGeometry']='Labelled territory on the existing mesh if actual anatomical coverage is confirmed; separate derivative only if required by layers/shape'
        else:
            row['requiredGeometry']='Identified continuous bundles with vertebral level/attachment metadata; source segmentation before long/short or thoracic assignment'
    row['evidence'] += [RUN.relative_to(ROOT).as_posix()+'/node-integration.json']
data['additionalBatch2']={'issue':'ANAT-002','published':['interspinales_cervicis_right'],
 'newCards':['interspinales_cervicis_right','interspinales_cervicis_left'],
 'coverage':'5 right components C2-C7; C7-T1 missing; source C1-C2 fragments excluded without movement',
 'notAdmitted':['interspinales-candidate-left','FMA71442-corner-normals','FMA71443-corner-normals'],
 'fullAcceptance':False}
with (ROOT/MATRIX).open('x',encoding='utf8') as f:json.dump(data,f,ensure_ascii=False,indent=2)

p=ROOT/'ANATOMY_ISSUES.md';s=p.read_text(encoding='utf8')
assert 'LOG-20261021-07' not in s
s=s.replace('Срез состояния: **2026-10-21**, LOG-20261021-06:',
'''Срез состояния: **2026-10-21**, LOG-20261021-07: 259 мышечных карточек / 304 меша. Подключён частичный правый набор interspinales cervicis C2–C7; левая карточка noModel. Исправлены нормали двух тестовых источников шеи без анатомического допуска. Первоначальные 13 MG / 21 MP остаются; всего 14 мышечных noModel с новой левой группой. 20 костных noModel сохранены. [Отчёт](research/stage7-muscle-batch2-report-2026-10-21.md).

Предыдущий срез: **2026-10-21**, LOG-20261021-06:''',1)
s=s.replace('LOG-20261021-06, текущий срез:',
'''LOG-20261021-07, текущий срез: **255 задач / 73 проверено / 182 не закрыто** — 30 открыты, 5 в работе, 86 требуют проверки, 61 заблокирована. ANAT-002 в работе, не закрыта. 0 закрытых / 0 новых ID; [35 адресных решений и отчёт](research/stage7-muscle-batch2-report-2026-10-21.md).

LOG-20261021-06, предыдущий срез:''',1)
s=s.replace('| в работе | 4 |','| в работе | 5 |',1).replace('| требует проверки | 87 |','| требует проверки | 86 |',1)
old='| [ANAT-002](#anat-002) | Короткие межостистые и межпоперечные шейные группы отсутствуют в каталоге | 7 | P1 | требует проверки |'
new='| [ANAT-002](#anat-002) | Неполный каталог и геометрия коротких шейных мышц | 7 | P1 | в работе |'
assert old in s;s=s.replace(old,new,1)
for row in data['rows']:
    ident=row['issue'];pattern=r'(^### '+re.escape(ident)+r'\n)(.*?)(?=^### |\Z)'
    match=re.search(pattern,s,re.M|re.S);assert match
    note='\n- Дополнение LOG-20261021-07: исходный блокер и критерий закрытия сохранены. Целая мышца/часть не восстановлена; проверена согласованность актуальных данных по неизменённым хешам. [Адресное решение второй партии]('+MATRIX+'); [отчёт]('+REPORT+').\n\n'
    if ident=='MG-palmaris_brevis':note='\n- Дополнение LOG-20261021-07: Physiome даёт Git HEAD как метаданные, но клонирование завершилось TLS-ошибкой; страницы 403. EXnode/EXelem, точный автор и лицензия конкретной сетки не получены. Новый научный указатель — Kerkhof et al., DOI 10.1111/joa.12877 / MorphoSource P419: нужны файлы, права и регистрация левой конечности к нашему образцу. Геометрия не подключена; общий статус ресурса не заменяет лицензию. [Отчёт]('+REPORT+').\n\n'
    s=s[:match.end()]+s[match.end():] if False else s[:match.start(2)]+match[2].rstrip()+'\n'+note+s[match.end():]
match=re.search(r'(^### ANAT-002\n)(.*?)(?=^### |\Z)',s,re.M|re.S);body=match[2]
body=body.replace('**Короткие межостистые и межпоперечные шейные группы отсутствуют в каталоге**','**Неполный каталог и геометрия коротких шейных мышц**')
body=body.replace('Статус: **требует проверки**','Статус: **в работе**',1)
body=body.replace('Структуры и ID: Проектных ID нет.','Структуры и ID: interspinales_cervicis_right/left добавлены; справа 5 учебных пучков, слева noModel. Остальные группы пока без самостоятельных карточек.')
body += '\n- Дополнение LOG-20261021-07: FMA71309 разделён по исходным связным компонентам, без разреза/смещения: 2800 треугольников пяти правых пучков C2–C7 подключены с явным неполным покрытием; C7–T1 отсутствует. Два спорных фрагмента у C1–C2 исключены из производной, исходник сохранён. Левая производная тестовая: выборочные перекрытия с костями до 1,4491 мм; нужна согласованная геометрия/разметка прикреплений, не произвольная подгонка. FMA71442/71443: нормали исправлены на производных с сохранением 8322/8782 треугольников; пластинки/самопересечения и уровни/medial–lateral остаются нерешёнными. Две карточки, один загружаемый меш, три GLB вне допуска. Blender/trimesh, 37 Node интеграционных, 22 Node нормалей, 60 локальных Playwright-проверок 1280/390; MCP подтвердил загрузку, дальнейшие действия блокировала политика разрешений. Полная научная/геометрическая приёмка и исходный критерий четырёх групп не закрыты. [Отчёт]('+REPORT+').\n\n'
s=s[:match.start(2)]+body+s[match.end():];p.write_text(s,encoding='utf8')

p=ROOT/'ANATOMY_PROGRESS.md';s=p.read_text(encoding='utf8');assert 'LOG-20261021-07'not in s
line=next(l for l in s.splitlines() if l.startswith('| 7 |'))
s=s.replace(line,'| 7 | Восстановление 13 мышц и 21 части | В работе: две puborectalis и частичный правый набор interspinales подключены | LOG-20261021-07: 259 карточек / 304 меша; 13 прежних мышц + новая левая группа noModel, 21 часть остаётся. Два межпоперечных исходника технически исправлены, но не допущены. 37 Node интеграционных / 22 нормалей / 60 локальных Playwright, Blender/trimesh. Записи учёта: 0 проверено / 45 всего; это не процент готовности анатомии. |',1)
s=s.replace('61 заблокирована; 87 имеют статус','61 заблокирована; 86 имеют статус',1).replace('Открыта: 30; в работе: 4;','Открыта: 30; в работе: 5;',1).replace('Текущий срез LOG-20261021-06','Текущий срез LOG-20261021-07',1)
s+='''

### LOG-20261021-07 — адресная работа с мышечными исходниками и частичное покрытие шеи

- Продолжена исходная задача этапа 7. Повторного полного аудита нет: 16 сохранённых SHA совпали; проверены новые производные. По 34 прежним MG/MP сохранены критерии и [поимённые решения](research/stage7-muscle-batch2-decisions-2026-10-21.json). Новые указатели palmaris brevis не дали доступного файла с подтверждёнными правами/регистрацией; произвольная реконструкция не выполнена.
- ANAT-002 переведена в работу. Добавлены две карточки interspinales_cervicis_right/left; справа подключены пять исходных пучков C2–C7 (2800 треугольников) с явным предупреждением неполного учебного покрытия. C7–T1 отсутствует. Фрагменты у C1–C2 не переименованы и не передвинуты. Левая производная не подключена: выборочные перекрытия с костными мешами до 1,4491 мм; это не медицинский порог и не точный максимум.
- FMA71442/71443: исправлены нормали отдельных углов, все треугольники и winding сохранены. 20/19 пластинок, самопересечения и неразмеченные сегменты/подгруппы не устранены; обе модели исследовательские. Из прежних 13 мышц / 21 части восстановлено 0; новая группа учитывается отдельно.
- Каталог: 259 карточек / 304 мышечных меша. Всего 14 мышечных noModel (13 исходных + новая левая межостистая группа), 21 часть без отдельной геометрии. 20 костных noModel, ограничения этапа 6 и puborectalis сохранены. Оригинальные OBJ/GLB и пины не менялись; лицензионная атрибуция и ShareAlike сохранены.
- Проверки: Python/trimesh, Blender MCP (4 производные, 3 вида), 37 Node интеграционных / 22 нормалей, адресная проверка BVH/лучей и выборка костных перекрытий. TA98: 762 термина / 3 прежних расхождения. Playwright: 60 утверждений на 1280/light и 390/dark, поиск/карточки/реальный выбор/изоляция/стороны/прозрачность/связи; фазы до 35 с, результаты сохранены отдельно. MCP выполнил начальную загрузку (4 утверждения), затем действия блокировала политика approval policy is never. С отдельным разрешением выполнен локальный Playwright через установленный Chrome; это не выдано за полный MCP-прогон.
- **0 закрытых / 0 новых задач. 255 всего, 73 проверены, 182 не закрыты, 61 заблокирована**; 30 открыты, 5 в работе, 86 требуют проверки; научный остаток 146. Этап 7: 0 проверено / 45 всего. [Отчёт](research/stage7-muscle-batch2-report-2026-10-21.md).
- Контрольная точка: доступный лицензированный palmaris brevis; согласованная левая interspinales и C7–T1; сегментная разметка intertransversarii; границы тонких частей/брюшек. Полная приёмка мышц остаётся открыта; этап 8 не начат. Локальный сервер 8783; публикации нет.
''';p.write_text(s,encoding='utf8')

p=ROOT/'CURRENT_PROJECT_STATUS.md';s=p.read_text(encoding='utf8');assert 'LOG-20261021-07'not in s
s=s.replace('30 открыты, 4 в работе, 87 требуют проверки','30 открыты, 5 в работе, 86 требуют проверки',1)
line=next(l for l in s.splitlines()if l.startswith('| ANAT-002 |'))
s=s.replace(line,'| ANAT-002 | Короткие шейные мышцы | ЧАСТИЧНО | Две карточки; справа учебная модель пяти пучков C2–C7. Нормали двух межпоперечных источников исправлены, но они тестовые. | Левая модель, C7–T1, спорные C1–C2, сегменты/medial–lateral и точные прикрепления не приняты. | 7/8 |',1)
s=s.replace('Этап 7 начат: две puborectalis подключены, 13 MG/21 MP остаются; три коротких шейных источника не допущены.', 'Этап 7 в работе: две puborectalis и частичный правый набор interspinales подключены. 13 прежних MG/21 MP остаются; дополнительно левая interspinales noModel; две межпоперечные производные тестовые.',1)
s+='''

## Этап 7 — LOG-20261021-07, текущий результат

**259 мышечных карточек / 304 меша.** Добавлены карточки межостистых мышц шеи обеих сторон и один учебный меш справа: пять пучков C2–C7, без C7–T1. Слева модель остаётся тестовой. У двух межпоперечных исходников исправлены нормали, но сегментная анатомия не принята. [Отчёт](research/stage7-muscle-batch2-report-2026-10-21.md).

Из исходных 13 мышц и 21 части восстановлено 0; все их критерии сохранены. Всего мышечных noModel теперь 14 — добавлена левая межостистая группа. 20 костных noModel неизменны. Подтверждены 37 Node интеграционных, 22 нормалей, Blender/trimesh и 60 локальных Playwright-утверждений на 1280/390. Полный MCP-прогон заблокирован политикой разрешений, поэтому не заявлен.

**255 задач / 73 проверены / 182 не закрыты / 61 заблокирована.** Закрыто 0, новых ID нет; ANAT-002 в работе. Следующий шаг — получить пригодные лицензированные исходники и сегментную разметку оставшихся мышц/частей. К этапу 8 пока не переходить.
''';p.write_text(s,encoding='utf8')
print(json.dumps({'matrixRows':len(data['rows']),'newModels':1,'newCards':2,'docs':3}))
