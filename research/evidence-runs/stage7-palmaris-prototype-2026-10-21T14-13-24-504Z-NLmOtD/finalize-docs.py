from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[3];RUN=Path(__file__).resolve().parent
report='research/stage7-palmaris-prototype-2026-10-22.md'
plan='research/stage7-reconstruction-method-plan-2026-10-22.json'
old=json.loads((ROOT/'research/stage7-muscle-batch2-decisions-2026-10-21.json').read_text(encoding='utf8'))
rows=[]
for row in old['rows']:
    issue=row['issue'];method='';needed='';same=False
    if issue=='MG-palmaris_brevis':
        method='parametric_closed_lamina_test_only';same=True
        needed='Согласованные кожа/апоневроз, контуры начала и прикрепления, толщина и состояние мышцы; устранение конфликтов на основании этих данных, затем анатомическая приёмка.'
    elif issue.startswith('MG-auricularis'):
        method='thin_lamina_or_fan_after_boundary_annotation';same=True
        needed='Идентифицированная ушная раковина, фасция и область начала/прикрепления того же образца; отдельные границы конкретной передней/верхней/задней мышцы. Допущенная исходная сторона перед отражением.'
    elif issue.startswith('MG-depressor_supercilii'):
        method='volumetric_segmentation_or_registered_microanatomical_loft'
        needed='Глубинная граница с соседними мышцами у медиальной брови; толщина, траектория и подтверждённые площадки прикреплений, а не маска наружной кожи.'
    elif issue in ['MG-transversus_menti','MG-thorax_sternalis']:
        method='documented_individual_variant_only'
        needed='Конкретный вариант с анатомическим описанием, изображениями, правами, стороной и масштабом. Не генерировать обязательную симметричную структуру.'
    elif issue.startswith('MG-'):
        method='level_labelled_bundle_loft'
        needed='Разметка уровней рёбер/позвонков, стороны и границ каждого мышечного пучка, области начала/прикрепления и относительная глубина.'
    elif issue.startswith('MP-orbicularis_oculi'):
        method='deep_or_ciliary_segmentation_not_surface_mask'
        needed='Локальные гистологические/объёмные данные глубокой или ресничной части, границы и толщины; наружный меш целой мышцы недостаточен.'
    elif issue.startswith(('MP-nasalis','MP-orbicularis_oris')):
        method='reviewed_face_index_mask_on_continuous_parent'
        needed='Подтверждённое покрытие родительского меша и анатомические границы частей; индексы граней без искусственного разрыва.'
    elif issue.startswith('MP-omohyoid'):
        method='two_belly_masks_with_tendon_transition'
        needed='Размеченная зона промежуточного сухожилия и границы обоих брюшек; сохранить непрерывность общего меша.'
    elif issue.startswith('MP-thorax_diaphragm'):
        method='attachment_territory_masks'
        needed='Территории прикреплений и границы центрального сухожилия того же образца; не делить по осевым плоскостям.'
    else:
        method='vertebral_level_and_fascicle_annotation'
        needed='Метки позвонков и непрерывных пучков, подтверждённое число перекрытых уровней; общая длина меша не определяет часть.'
    rows.append(dict(issue=issue,structure=row['structure'],part=row.get('part'),status=row['status'],method=method,
        uses_lamina_family=same,ready_for_automatic_anatomical_admission=False,
        prototype_created=issue=='MG-palmaris_brevis',requiredData=needed,
        originalAcceptanceCriterion=row['existingAcceptanceCriterion'],priorSourceAssessment=row['sourceAssessment'],
        priorSourceLinks=row.get('links',[]),priorReport='stage7-muscle-batch2-report-2026-10-21.md'))
assert len(rows)==34 and len({r['issue']for r in rows})==34
with (ROOT/plan).open('x',encoding='utf8') as f:json.dump(dict(date='2026-10-22',scope='1 detailed pilot; method triage of 12 other muscles and 21 parts, not a repeated scientific audit',pilotAdmitted=False,rows=rows),f,ensure_ascii=False,indent=2)

issues=(ROOT/'ANATOMY_ISSUES.md').read_text(encoding='utf8')
assert 'LOG-20261022-01' not in issues
intro=f'Срез состояния: **2026-10-22**, LOG-20261022-01: создан параметрический тестовый palmaris brevis (1650 вершин / 3296 треугольников); учебного допуска нет. 13 исходных MG / 21 MP, дополнительная левая межостистая группа и 20 костных noModel сохранены. Производственная геометрия и каталог не менялись. [{"Отчёт"}]({report}), [план34 ID]({plan}).\n\n'
issues=issues.replace('Срез состояния: **2026-10-21**, LOG-20261021-07:',intro+'Предыдущий срез: **2026-10-21**, LOG-20261021-07:',1)
start=issues.index('### MG-palmaris_brevis\n');end=issues.index('\n### ',start+1)
block=issues[start:end].replace('Обновлено: **2026-10-15**','Обновлено: **2026-10-22**',1)
block+=f'\n- Дополнение LOG-20261022-01: самостоятельный параметрический прототип по запросу пользователя создан через Blender Python; отдельная тестовая сборка, noModel основного атласа сохранён. 3296 треугольников; самопересечений не найдено, но119/58/37 пар пересечений с abductor digiti minimi / flexor digiti minimi brevis / удерживателем. Нет зарегистрированных кожи, края апоневроза и границ PB. 65/221 опорных проб требуют экстраполяции; отступ, контур и плановые размеры — допущения. Нужны размеченные контуры и толщина в той же системе координат, затем устранение конфликтов без произвольной подгонки. Успешные технические проверки не дают учебного или полного анатомического допуска. [Прототип, источники и тесты]({report}). Исходный критерий и статус сохранены; этап8 не начат.\n'
issues=issues[:start]+block+issues[end:]
(ROOT/'ANATOMY_ISSUES.md').write_text(issues,encoding='utf8')

p=ROOT/'ANATOMY_PROGRESS.md';text=p.read_text(encoding='utf8')
text=text.replace('Обновлено: **2026-10-21**.','Обновлено: **2026-10-22**.',1)
text=text.replace('Текущий срез LOG-20261021-07; история сохранена.','Текущий срез LOG-20261022-01; история сохранена.',1)
text=text.replace('| 7 | Восстановление 13 мышц и 21 части | В работе: две puborectalis и частичный правый набор interspinales подключены | LOG-20261021-07:', '| 7 | Восстановление 13 мышц и 21 части | В работе: 3 дополнительных меша; PB только тестовый | LOG-20261022-01: воспроизводимый PB-прототип, без допуска; 21 Python / 34 Node / 56 MCP. Каталог не изменён. Предыдущий LOG-20261021-07:',1)
text+=f'''\n\n### LOG-20261022-01 — самостоятельный прототип palmaris brevis\n\n- Продолжена задача21.10 после прерывания. Подробно проверена1 мышца; для остальных12 MG и21 MP сохранён [план по существующим ID]({plan}), без повторного поиска всех исходников. Применены anatomy-validator, medical-literature-research, mesh-auditor.\n- Реализован конвейер: точная выборка40 контекстных мешей руки → измеренная система отсчёта → параметрическая замкнутая пластинка → Blender MCP/GLB → trimesh/Node/BVH → отдельная браузерная сборка. Параметры, допущения, происхождение, CC BY-SA2.1 Japan и научные ссылки сохранены.\n- Прототип1650 вершин /3296 треугольников. Нет самопересечений;119/58/37 пар пересечений с двумя мышцами гипотенара и удерживателем. Кожи/апоневроза и подтверждённых границ нет;65/221 проб без прямой опоры. Смещения ради допуска не выполнялись. **Учебный допуск не получен, в основном атласе noModel не удалён.**\n- Исправлены только технические инструменты/тестовая сборка: исключение чужих сцен при экспорте, каноническое имя без суффикса Blender, обработка точности Float32, явный тестовый старт после перезагрузки. Исходники и производственные файлы неизменны по6 контрольным хешам. Старые неудачные попытки не перезаписаны.\n- Проверки:13 trimesh +8 воспроизводимости/параметров;34 Node с24 лучами;Blender MCP и3 ракурса;56 итоговых Playwright MCP на1280/light и390/dark, фазы≤35с с промежуточным сохранением. Физическое устройство не проверялось. [{"Отчёт"}]({report}).\n- **0 закрытых /0 новых задач.255 всего,73 проверены,182 не закрыты,61 заблокирована;30 открыты,5 в работе,86 требуют проверки; научный остаток146.** Этап7:0/45 задач проверено. Каталог259 мышц /304 подключённых меша;14 noModel мышц (13 исходных +1 дополнительная),21 часть и20 костных noModel сохранены.\n- Следующий шаг: зарегистрированные мягкотканные границы PB либо разметка частей существующих мышц. Метод подготовки и проверок переиспользуется; автоматического анатомического допуска и массовой генерации нет. Этап8 не начат. Локальная тестовая сборка127.0.0.1:8785, публикации нет.\n'''
p.write_text(text,encoding='utf8')

p=ROOT/'CURRENT_PROJECT_STATUS.md';text=p.read_text(encoding='utf8')
text=text.replace('**21.10.2026 · этап 7: первая учебная интеграция мышц.**','**22.10.2026 · этап 7: процедурный прототип PB, без нового допуска.**',1)
text=text.replace('Размеченные лицензированные исходники; по каждому ID указаны нужные границы/уровни. Кандидат palmaris brevis требует доступа/лицензии.','PB: есть тестовый GLB, но нет допуска (пересечения, кожа/апоневроз и границы). [План34 ID]('+plan+'); нужны зарегистрированные границы/уровни. Кандидат Physiome остаётся отдельным недоступным исходником.',1)
text=text.replace('## Этап 7 — LOG-20261021-07, текущий результат','## Этап 7 — LOG-20261021-07, предыдущий результат',1)
text+=f'''\n\n## Этап 7 — LOG-20261022-01, текущий результат\n\nСоздан воспроизводимый [прототип palmaris brevis]({report}):1650 вершин /3296 треугольников, отдельный Blender и браузерная сборка. **Учебного допуска нет**: остаются пересечения с соседними тканями и неизвестные границы кожи/апоневроза. Основной атлас не изменён.21 Python,34 Node,56 Playwright MCP-утверждений1280/390 пройдены; геометрическая анатомическая приёмка ими не заменена.\n\nИз исходных13 мышц и21 части по-прежнему восстановлено0. Всего14 мышечных noModel с дополнительной левой межостистой группой;20 костных noModel сохранены. **255 задач /73 проверены /182 не закрыты /61 заблокирована; закрыто0.** Следующий шаг — мягкотканные границы PB или подтверждённые маски частей по [плану34 ID]({plan}). Поиск готовых моделей не является единственным способом; неподтверждённые поверхности не интегрировать. Этап8 не начинать.\n'''
p.write_text(text,encoding='utf8')

p=ROOT/'ANATOMY_SOURCES_AUDIT.md'
with p.open('a',encoding='utf8') as f:f.write(f'\n\n### Адресное дополнение22.10.2026 — palmaris brevis\n\n[Пилот и таблица утверждений]({report}): FIPAT TA98 A04.6.02.053; UAMS; NCBI NBK546622; Moore & Rice2017, PMID28786108 / DOI10.1111/joa.12675; Nam et al.2022, PMID35037581 / DOI10.1142/S2424835522500084; Anatomy Atlases Plate4.30. ESearch/EFetch метаданные реально получены; аннотация/индексированный текст отделены от доступного полного текста. IMAIOS, ссылающийся на StatPearls, не считается независимой второй выборкой. Средняя толщина не подтверждает форму конкретной кисти. Иллюстрации NC/чужого приложения не импортированы. Новый GLB — самостоятельный технический прототип, не принятая PB-сегментация DBCLS; происхождение, допущения и ShareAlike сохранены.\n')

# Correct the count from actual saved tests, not a hand-maintained claim.
p=ROOT/report;text=p.read_text(encoding='utf8').replace('Python/trimesh: **12 проверок**','Python/trimesh: **13 проверок**')
text=text.replace('- Node/r170/BVH0.8.3:', '- Повторная генерация и параметры: **8 проверок** — идентичные исходному рецепту вершины/грани, влияние толщины, стабильная система координат, запрет отрицательной толщины и сохранение тестового статуса.\n- Node/r170/BVH0.8.3:')
p.write_text(text,encoding='utf8')
print(json.dumps({'plan_rows':len(rows),'registry_statuses_changed':0,'new_issues':0,'report':report}))
