"""Generate an actionable skull view of the existing registry; do not change statuses."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/stage5-skull-final-2026-10-17'
s=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf-8')
issues={k:v for k,v in re.findall(r'^### ([\w-]+)\n(.*?)(?=^### |^## |\Z)',s,re.M|re.S) if 'Статус: **' in v}
shared={r['issueId']:r for r in json.loads((OUT/'candidate-decisions.json').read_text(encoding='utf-8'))['shared']}
global_ids={'SRC-008','GEO-008','GEO-009','GEO-012','LIC-001','LIC-002','LIC-003',
            'QA-003','QA-004','QA-005','QA-006','VIS-001','VIS-002','VIS-007','VIS-008','VIS-009','VIS-010',
            'PIN-005','PIN-002','GEO-001','GEO-002','GEO-003','GEO-004','GEO-005','GEO-006','GEO-010',
            'SHX-sigmoid-groove-parts','PIN-SHARED-KIND'}
rows=[]
def field(body,key):
    m=re.search(re.escape(key)+r': \*\*(.*?)\*\*',body);return m.group(1) if m else None
def line(body,key):
    m=re.search(r'^- '+re.escape(key)+r': (.*)$',body,re.M);return m.group(1) if m else ''
for key,body in issues.items():
    if field(body,'Статус')=='проверена':continue
    initial=body.split('- Дополнение LOG-')[0]
    if key.startswith(('MG-','MP-')) or key in {'SRC-003','SRC-004','SRC-005','SRC-006','SRC-007','SRC-010','GEO-011','LIC-004','ANAT-001','ANAT-002','FUT-001','FUT-003','VIS-011'}:continue
    if not (key in global_ids or key in shared or re.search(r'череп|скул|затылоч|решётчат|носов|слёзн|сошник|нижн[ею].?челюст|верхн[ею].?челюст|височн|head_|skull|SPL Ear',initial,re.I)):continue
    title=re.search(r'^\*\*(.*?)\*\*',body,re.M).group(1)
    stage=field(body,'Этап');criteria=line(body,'Решение и критерий закрытия')
    missing=criteria
    now='Частично: уточнение доказательств/разметки доступно; закрывать только по исходному критерию.'
    future='Этап '+stage+'; перенос не закрывает задачу.'
    impact='Ограничивает соответствующую структуру и заявление полноты; не запрещает весь справочный просмотр.'
    if key in shared:
        missing=shared[key]['remaining']
        now='Да для адресного поиска/сверки scope; нет для неподтверждённой геометрии. Уже существующие связи сохранены.'
        future='5: факт/вклад/сторона; 6: отображение только принятой разметки; 8: независимая приёмка.'
    elif key in {'CO-JUG-right','CO-JUG-left','GEO-004','GEO-003','GEO-010','GEO-MANDIBLE-EXTRA'}:
        now='Нет для полного геометрического закрытия: нужны идентифицированные данные того же образца или калибровка и адресная анатомическая приёмка.'
        future='5: получить/идентифицировать нужную геометрию; 8: приёмка. Не заменять чужой КТ или литературным размером.'
        impact='Не допускает точного учебного утверждения о ходе, размерах или наличии варианта на этой модели.'
    elif key=='PIN-SHARED-KIND':
        missing='32 общие канонические карточки имели отсутствующее geometryKind; теперь unknown и видимое предупреждение. Нужны предметные определения типа по адресным источникам, отдельно от состава костей и координат.'
        now='Да: адресно классифицировать по анатомической сущности; готовые refs на отношения нельзя автоматически считать доказательством типа.'
        future='5; PIN-SKULL-KIND закрыта только для 521 собственных записей и не переоткрывается.'
    elif key=='GEO-SKULL-FINAL-EXTRA':
        missing='25 по-ID образований: 22 требуют принятой поверхностной/краевой/объёмной разметки; три группы язычных отверстий требуют идентификации апертур на том же образце. Снимок сглаженного меша их не подтверждает.'
        now='Для 22 доступна адресная работа на существующей геометрии с анатомической проверкой; для трёх групп отверстий пока недостаточно исходных данных.'
        future='5: локализация/границы; 6: визуальное выделение после приёмки; 8: внешняя проверка.'
    elif key=='CAT-FACIAL-EXTRA':
        missing='Из 44 кандидатов четыре поверхности слёзных костей добавлены. Для остальных 40 не принята независимая адресная пара и/или scope отдельной карточки; Gray-производные не независимы. Точные candidateId в candidate-decisions.json.'
        now='Да: продолжить адресный поиск и номенклатурное сопоставление. Недостаток доказательств не равен отсутствию анатомической структуры.'
        future='5; не передавать неоконченный каталог в цветовую систему.'
    elif key=='CAT-MANDIBLE-EXTRA':
        missing='17/19 кандидатов стали карточками. Два оставшихся: mandible_right_facial_artery_groove и mandible_left_facial_artery_groove; нужен независимый источник о вариабельном костном ложе, не только о ходе артерии.'
        now='Да для научного поиска; текущий GLB не подтверждает отдельную борозду.'
        future='5; геометрия отдельно после подтверждения сущности.'
    elif key.startswith('VIS-') or key=='CO-004':
        now='Техническая реализация возможна после принятия соответствующих областей; в этой задаче не выполняется.'
        future='6: визуализация; анатомическую разметку принять в 5; проверка выпуска в 8.'
        impact='Снижает удобство и различимость; отсутствие цвета не создаёт новых анатомических доказательств.'
    elif key.startswith('LIC-'):
        now='Документальная сверка доступна; недостающие лицензии/версии нужно получить у источника.'
        future='Исходный этап '+stage+'; права на конкретный публикуемый набор должны быть приняты до релиза этапа 8.'
        impact='Может блокировать публикацию соответствующего ресурса; не разрешает заменять лицензию предположением.'
    elif key.startswith('QA-') or key=='GEO-012' or key=='SRC-008':
        now='Автоматическая часть доступна; внешняя экспертная приёмка и реальные устройства требуют отдельного протокола.'
        future='8; предварительные технические проверки возможны на 5. Не выдавать эмуляцию за телефон или экспертизу.'
        impact='Блокирует окончательную приёмку/релиз, а не весь ограниченный исследовательский просмотр.'
    elif key.startswith('FUT-'):
        now='Отдельный модуль за границами текущей остеологии; сам по себе не препятствует проверке костных поверхностей сейчас.'
        future='8 или отдельный согласованный модуль; костные суставные поверхности остаются в 5.'
    rows.append(dict(id=key,title=title,status=field(body,'Статус'),stage=stage,
        whatRemains=missing,canFixNow=now,nextStage=future,useImpact=impact,
        originalAcceptanceCriterion=criteria,source=line(body,'Источник обнаружения'),
        registryLink='../../ANATOMY_ISSUES.md#'+key.lower()))
assert set(shared)<=set(r['id'] for r in rows)
(OUT/'remaining-skull-issues.json').write_text(json.dumps({'rows':rows,'count':len(rows),
    'scope':'Skull-specific plus applicable global release/UI dependencies; muscles and other regional work excluded. Registry retains every issue.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=['# Незакрытые вопросы черепа и зависимости выпуска','',
    'Эта таблица — представление ANATOMY_ISSUES.md, не второй реестр. ID, статусы и исходные критерии сохранены. Каталожная, научная и экземплярная геометрическая приёмка различаются.','',
    '| ID / статус | Что отсутствует | Можно ли сейчас | Следующий этап | Влияние на использование |','|---|---|---|---|---|']
for r in rows:
    vals=[f"[{r['id']}]({r['registryLink']}) — {r['status']}",r['whatRemains'],r['canFixNow'],r['nextStage'],r['useImpact']]
    md.append('| '+' | '.join(v.replace('|','/').replace('\n',' ') for v in vals)+' |')
(OUT/'remaining-skull-issues.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({'remainingSkullAndGlobalDependencies':len(rows),'ids':[r['id'] for r in rows]}))
