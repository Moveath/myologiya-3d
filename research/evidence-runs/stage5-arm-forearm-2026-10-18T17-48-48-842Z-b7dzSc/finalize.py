"""One-time additive registry update; evidence is created with exclusive writes."""
import collections, hashlib, json, re, base64, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
REL=OUT.relative_to(ROOT).as_posix(); REPORT='research/stage5-arm-forearm-report-2026-10-18.md'
def write(name,value):
    with (OUT/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def parse(text):
    result={}
    for m in re.finditer(r'^### ([^\n]+)\n([\s\S]*?)(?=^### |\Z)',text,re.M):
        status=re.search(r'Статус: \*\*([^*]+)\*\*',m[2])
        if status:
            assert m[1] not in result
            result[m[1]]=dict(status=status[1],body=m[2])
    return result
issue=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf8')
assert issue==(OUT/'before-ANATOMY_ISSUES.md').read_text(encoding='utf8')
old=parse(issue);assert len(old)==228
link=f'[Отчёт]({REPORT}); [110 ID]({REL}/reviewed-records.json); [проверки]({REL}/evidence.json).'
def append_to(id,text):
    global issue
    pattern=r'(^### '+re.escape(id)+r'\n[\s\S]*?)(?=^### |\Z)'
    def add(m):
        body=re.sub(r'Обновлено: \*\*[^*]+\*\*','Обновлено: **2026-10-19**',m[1],count=1)
        return body.rstrip()+'\n\n- Дополнение LOG-20261019-01: '+text+' '+link+'\n\n'
    issue,n=re.subn(pattern,add,issue,count=1,flags=re.M);assert n==1,id
append_to('SRC-001','28 humerus_left получили предметные определения и независимые академические опоры. Исходный набор 106 записей не удалён: наличие refs не доказывает топографию/геометрию данного образца. Статус и полный критерий сохраняются.')
append_to('SRC-002','67 исходных правых записей плеча/предплечья, включая 3 att и 1 soft, получили структурированные источники и пределы. Исторический массовый набор сохраняется; не объявлен целиком проверенным.')
append_to('CAT-UPPER-REMAINDER','95 записей текущей партии классифицированы и предметно разобраны; добавлены 15 карточек. Остаток исходного набора — 81 ID кисти в remaining-records.json, плюс полнота карточек кисти без собственных пинов. Левые radius/ulna отсутствуют: отдельные CAT-UPPER-LEFT-FOREARM и GEO-UPPER-LEFT-FOREARM, не смешивать с исходными 176. Статус открыта сохранён.')
for i in range(1,7):
    append_to('CO-ARM-'+str(i),'Blender и независимый trimesh повторно согласовали расстояния при адресной проверке новой партии. Исходная координата сохранена; близость к сетке не восстанавливает её происхождение и не подтверждает анатомическую локализацию. Прежний блокер не закрыт; нужна независимая приёмка данного образца и исходной разметки.')
new=[
 ('CAT-UPPER-ARM-CORRECTIONS','Предметные исправления 95 записей плеча и предплечья','проверена','каталог и связи',
  'humerus/humerus_left/radius/ulna: 91 TA; hum_body_ant/rad_supinator/uln_distal_anterior: 3 att; membrane_mid: 1 soft; 15 новых ID в reviewed-records.json.',
  'Неуточнённые типы, заглушки левой плечевой, неверное число краёв тела, смешение дна борозды и медиальной губы, неточное описание запястной площадки и непроверенное присутствие варианта.',
  'scripts/arm_forearm_stage5_review.py; scripts/make_pins.py; scripts/make_context_bone_data.py; site/pins.js; site/pins-context-bones.js.',
  'Критерий: 95 предметных определений/типов, подтверждённые дополнения/связи; стабильные ID/p/n, без дублей; проверка поиска/карточек/участников/BVH на двух ширинах. Выполнено. Геометрия и отсутствующие две левые кости исключены из этого узкого критерия и зарегистрированы отдельно.',
  '95 классифицированы, 15 добавлены без p/n, 7 суставов/15 связей; Node, генераторы, TA98 с 3 прежними расхождениями, Playwright 1280/390 пройдены. 1982 прежние записи неизменны; геометрия не принята.'),
 ('GEO-UPPER-ARM-LANDMARKS','Не приняты локализация и границы ориентиров плеча и предплечья','требует проверки','геометрия и анатомическая локализация',
  'Все 110 ID reviewed-records.json: 67 прежних p, 28 прежних без p, 15 новых без p. CO-ARM-1…6 учитываются по своим постоянным ID.',
  'Blender: 5 объектов, 9 ракурсов; max distance 0,675519 мм не доказывает анатомию. Нет масок поверхности, трасс, объёмной сегментации суставов и подтверждения надмыщелкового отростка на экземплярах.',
  'pins/ta.json; pins/old_hi.json; site/arm-q-glb.txt; build_context_bones/arm_extra_hi.glb (исходники только для чтения); будущая разметка.',
  'Этап 5: независимая по-ID приёмка точек/наличия варианта на этом образце; маски/контуры/сегменты с хешем и ракурсами. Для неразличимых отверстий нужны исходные изображения/сегментация того же образца, для суставов — мягкие ткани. Этап 6 только отображает принятые области, 8 — финальная приёмка. Кисть проверять можно; точную 3D-полноту до релиза не заявлять.',
  'Blender/trimesh согласование 0,0000888 мм; 0 анатомически принятых координат/контуров. Правый пин варианта скрыт через anchorStatus, исходные p/n сохранены; все ограничения видимы в UI.'),
 ('CAT-UPPER-LEFT-FOREARM','Отсутствуют карточки левой лучевой и локтевой костей','открыта','неполнота каталога',
  'Будущие radius_left/ulna_left; словарь BodyParts3D FMA23465/FMA23468. Сейчас нет действующих карточек и их собственных ориентиров.',
  'Заявленный пользователем двусторонний объём сопоставлен с фактическими четырьмя костями в исходных 95 записях.',
  'scripts/context_bone_cards.py; scripts/ta98.py; генераторы/карточки руки; будущие тесты noModel.',
  'Следующая адресная партия этапа 5: добавить научно подтверждённые костные карточки и применимый каталог без p, проверить костный noModel-контекст, поиск/выбор на 1280/390. Технически возможно сейчас; отсутствие GLB не блокирует семантические карточки. До заявления двусторонней полноты требуется реализация; проверке правой кисти не мешает.',
  'В этой внутренней партии не реализовано; это незавершённая работа каталога, не научная невозможность и не закрытие переносом.'),
 ('GEO-UPPER-LEFT-FOREARM','Нет доступных индивидуальных моделей левого предплечья','заблокирована','исходная геометрия',
  'FMA23465 (left radius), FMA23468 (left ulna); будущие radius_left/ulna_left.',
  'bp/all_named.tsv содержит имена; локальные stl*/FMA23465.stl и FMA23468.stl отсутствуют; в проверенных arm-сборках соответствующие именованные узлы не найдены.',
  'bp/all_named.tsv; site/arm*-glb.txt; build_context_bones/arm_extra*.glb; будущие новые производные, без перезаписи оригиналов.',
  'Нужны реальные лицензированные исходные файлы или человеческая сегментация с подтверждённой стороной, масштабом, системой координат и происхождением; затем Blender/trimesh и анатомическая приёмка. Правые сетки нельзя зеркалировать как доказательство левого образца. Этапы 5/6/8; блокирует достоверное левое 3D-предплечье, но не его текстовые карточки или проверку кисти.',
  'Новые сетки/координаты не созданы. Поиск сохранён в left-forearm-resources.json; словарь не считается геометрией.'),
]
issue=issue.replace('## Карточки задач','\n'.join(f'| [{id}](#{id.lower()}) | {title} | 5 | P1 | {status} |' for id,title,status,*_ in new)+'\n\n## Карточки задач',1)
issue+='\n\n## Верхние конечности — плечо и предплечье, LOG-20261019-01\n\n'
for id,title,status,category,structures,discovery,files,criteria,evidence in new:
    issue+=f'''### {id}
**{title}**

- Категория: {category}. Этап: **5**. Приоритет: **P1**. Статус: **{status}**. Научная проверка: да. Обновлено: **2026-10-19**.
- Структуры и ID: {structures}
- Источник обнаружения: {discovery} {link}
- Затронутые файлы: {files}
- Решение и критерий закрытия: {criteria}
- Доказательства и проверки: {evidence}

'''
now=parse(issue);assert len(now)==232 and all(now[id]['status']==v['status'] for id,v in old.items())
counts=collections.Counter(v['status'] for v in now.values())
assert counts==dict(проверена=57,открыта=36,заблокирована=58,**{'требует проверки':81})
science=sum(v['status']!='проверена' and 'Научная проверка: да' in v['body'] for v in now.values());assert science==139
summary='Всего **232 записи**; подтверждённо закрыто **57**, не закрыто **175**: 36 открыты, 81 требует проверки, 58 заблокированы. Научной проверки требуют **139** незакрытых записей. Этап 5 — **35/110**. LOG-20261019-01: CAT-UPPER-ARM-CORRECTIONS проверена; геометрия и левое предплечье остаются. Ни один прежний нерешённый вопрос не закрыт. Числа задач не равны числу структур.'
issue,n=re.subn(r'^Всего \*\*228 записей\*\*[^\n]*',summary,issue,count=1,flags=re.M);assert n==1
for status,number in counts.items():
    issue,n=re.subn(r'^\| '+re.escape(status)+r' \| \d+ \|',f'| {status} | {number} |',issue,count=1,flags=re.M);assert n==1
issue=issue.replace('**2077** записей ориентиров. Без p — **751 = 447 исходных + 153 общие + 151 дополнительная собственная**','**2092** записи ориентиров. Без p — **766 = 447 исходных + 160 общих + 159 дополнительных собственных**',1)
issue=issue.replace('Срез состояния: **2026-10-18**','Срез состояния: **2026-10-19**',1)
issue=issue.replace('## Как пользоваться',f'LOG-20261019-01: 4 существующие костные карточки и перепонка, 95 исходных записей классифицированы; 15 новых без p, 7 суставов/15 связей. Две отсутствующие левые кости учтены отдельно; кисть (81 запись) ещё не проверена. {link}\n\n## Как пользоваться',1)
progress=(ROOT/'ANATOMY_PROGRESS.md').read_text(encoding='utf8');assert progress==(OUT/'before-ANATOMY_PROGRESS.md').read_text(encoding='utf8')
progress=progress.replace('Обновлено: **2026-10-18**','Обновлено: **2026-10-19**',1)
progress,n=re.subn(r'^\| 5 \|[^\n]*','| 5 | Полная проверка и исправление пинов | В работе | LOG-20261019-01: плечо/предплечье — 4 существующие кости / 95 типов, 15 новых карточек, 7 суставов и 15 связей. Геометрия не принята. Следующая партия: 81 запись кисти; две левые кости предплечья — отдельные незакрытые каталог/геометрия. 35/110 задач, не процент полноты. |',progress,count=1,flags=re.M);assert n==1
progress,n=re.subn(r'^\*\*228 записей:[^\n]*','**232 записи: 57 проверены, 175 не закрыты; 58 заблокированы; 81 имеет статус «требует проверки».** Научная проверка требуется 139 незакрытым записям. Открыта: 36; в работе: 0; исправлена без приёмки: 0. Текущий срез LOG-20261019-01; история сохранена.',progress,count=1,flags=re.M);assert n==1
progress+=f'''

### LOG-20261019-01 — плечо и предплечье, 95 исходных записей

- Работа 18–19 октября. Фактически 4 костные карточки (две плечевые, правые radius/ulna), 91 TA + 3 att + 1 soft = 95; 67 прежних p, 28 без p. Типы: 32 volume, 29 line, 34 area. Ни кисть, ни мышцы не проверялись новой партией.
- Исправлены три края humerus, типичная связь latissimus_dorsi с дном борозды вместо медиальной губы, описание радиальной запястной площадки; отмечено расхождение источников. Надмыщелковый отросток — вариант с неподтверждённым присутствием, старый правый p сохранён и скрыт. 28 левых заглушек заменены предметными определениями. Старые ID/p/n сохранены, m изменены только в двух оговорённых записях; мышечные карточки неизменны.
- Добавлены 15 карточек без p/n: 2 передних края, 4 категории питательных отверстий, 2 дистальных образования ulna, 7 суставов с 15 связями component. Сустав и собственные костные площадки различены; 3 компонента локтевого комплекса имеют partOf. Межкостная перепонка не дублируется.
- Источники: FIPAT/TA98, Gray 1918, Sobotta 1914 OCR, NCBI Bookshelf, UAMS. NCBI EFetch трёх PMID прошёл; авторы/названия/DOI сверены, отсутствие DOI не заполнено выдуманным значением. Современные лицензированные атласы и полные статьи без доступа не заявлены прочитанными. Референсы использованы по существующему анализу, не как научное доказательство.
- Blender MCP: 4 кости + мягкотканная перепонка, 67 точек, 9 просмотренных изображений; начальная ошибка измерителя o|/b| исправлена в проверочных скриптах, повтор прошёл. Trimesh независимо подтвердил расстояния: max 0,675519 мм, расхождение 0,0000888 мм. 0 анатомически принятых координат/масок; исходная сцена/GLB сохранены.
- Проверки: генераторы; TA98 — 762 термина и 3 старых расхождения, новых нет; Node — 95+15, 1982 прежние записи неизменны, 74 защищённых файла совпали по хешам. Playwright MCP 1280 dark / 390 light: по 110 карточек, 15 общих отображений, поиск/выбор/изоляция/прозрачность, скрытый непроверенный вариант, реальный canvas-click, по 10 BVH/native лучей; ошибок консоли 0, переполнения нет. Два UI-снимка просмотрены. Физический телефон, повторные самопересечения и срезы неизменённого черепа не проверялись.
- Левые radius/ulna отсутствуют; FMA23465/23468 есть в словаре, STL и именованных мешей в рассматриваемых arm-ресурсах нет. CAT-UPPER-LEFT-FOREARM открыта: карточки без модели технически возможны, эта отдельная реализация ещё не сделана. GEO-UPPER-LEFT-FOREARM заблокирована исходниками. Не считать отсутствие модели блокировкой текста; не зеркалировать правые кости.
- Реестр: новая CAT-UPPER-ARM-CORRECTIONS проверена; GEO-UPPER-ARM-LANDMARKS требует проверки; две задачи левого предплечья сохранены. SRC-001/002, CO-ARM-1…6 и CAT-UPPER-REMAINDER уточнены без изменения статусов. Кисть — 81 исходный ID плюс полнота её карточек; все сесамоидные и прежние региональные блокеры сохранены.
- Учёт: 232 задачи; 57 проверены, 175 незакрыты (36 открыты / 81 требуют проверки / 58 заблокированы), научная проверка 139; этап 5 = 35/110. Проверена 1 новая задача, ни один прежний блокер не закрыт. В атласе 2092 ориентира, 766 без p (447 + 160 + 159); в руке 259.
- Существующий набор 95 предметно завершён на доступном уровне; двусторонний раздел из шести костей ещё не завершён. Переход к предметной проверке кисти допустим, отдельная партия левого предплечья и геометрическая приёмка обязательны до заявления полноты. {link}
'''

# Read only GLB JSON, no mesh loading/rewriting, to distinguish names from assets.
models=[]
files=sorted((ROOT/'site').glob('arm*-glb.txt'))+sorted((ROOT/'build_context_bones').glob('arm_extra*.glb'))
for file in files:
    raw=file.read_bytes(); glb=base64.b64decode(raw) if file.suffix=='.txt' else raw
    size=struct.unpack_from('<I',glb,12)[0]; data=json.loads(glb[20:20+size])
    names=[n.get('name','') for n in data.get('nodes',[])]
    matches=[s for s in names if any(term in s.lower() for term in ('radius_left','ulna_left','left radius','left ulna','fma23465','fma23468'))]
    assert not matches,matches
    models.append(dict(file=file.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),leftForearmMatches=matches))
sources={fid:[p.relative_to(ROOT).as_posix() for p in ROOT.glob('stl*/'+fid+'.stl')] for fid in ('FMA23465','FMA23468')}
assert not any(sources.values())
write('left-forearm-resources.json',dict(dictionary='bp/all_named.tsv',sourceIds={'FMA23465':'left radius','FMA23468':'left ulna'},localSTL=sources,models=models,claim='No corresponding named node in these resources; no claim to infer identity of arbitrary anonymous components.'))
write('failed-attempt.json',dict(tool='Blender MCP',message='Code execution error: interosseous_membrane',cause='Initial addressed script resolved only b| owners; actual soft object is o|interosseous_membrane.',resolution='Both addressed readers now accept b| and o|; successful repeated run in blender-arm-forearm.json; source meshes unchanged.'))
write('registry-final.json',dict(total=len(now),statuses=counts,scienceOpen=science,stage5=dict(verified=35,total=110),previousStatusesUnchanged=True,newIds=[n[0] for n in new]))
write('evidence.json',dict(report=REPORT,data='data-regression.json',records='reviewed-records.json',remaining='remaining-records.json',blender='blender-arm-forearm.json',trimesh='trimesh-arm-forearm.json',pubmed='pubmed-verified.json',leftForearm='left-forearm-resources.json',registry='registry-final.json',
    playwright=['../stage5-arm-forearm-mcp-2026-10-18T18-56-16-271Z-dDj8c5/result.json','../stage5-arm-forearm-mcp-2026-10-18T18-58-01-739Z-1GUYNJ/result.json'],
    ta98=dict(command='.venv/Scripts/python.exe -X utf8 verify/verify_ta98.py',exitCode=0,terms=762,knownDifferences=['A02.5.10.015','A02.5.10.017','A02.5.11.007'],missing=[],extra=[]),acceptedNewCoordinates=0,originalGLBChanged=False))
(ROOT/'ANATOMY_ISSUES.md').write_text(issue,encoding='utf8');(ROOT/'ANATOMY_PROGRESS.md').write_text(progress,encoding='utf8')
print(json.dumps(dict(total=len(now),statuses=counts,scienceOpen=science,previousStatusesUnchanged=True),ensure_ascii=False))
