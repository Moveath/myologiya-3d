"""Export a read-only acceptance inventory; never promote anatomical evidence."""
from collections import Counter
from copy import deepcopy
from html import escape
from pathlib import Path
import json
import subprocess

from head_localization import positions
from head_terms import BONES as BONE_NAMES
from head_muscles import MUSCLE_TEMPLATES, EVIDENCE
from manifest_head import BONES, MUSCLES
from ta98 import T

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def named(key, label):
    return label + (' · правая сторона' if key.endswith('_right') else ' · левая сторона' if key.endswith('_left') else '')

CRITERIA = {
    'surface': 'Проверить характерный рельеф, границы и протяжённость образования на исходной геометрии; маркер одного участка не заменяет эту проверку.',
    'projection': 'Получить и проверить различимую геометрию образования на основном или отдельном исходном образце; сохранить собственную сторону, координаты и ракурс. Проекция сама по себе не проходит приёмку геометрии.',
    'variant': 'Получить подтверждённый 3D-пример варианта соответствующего типа и стороны, если сторона заявлена; сохранить реальный образец. Не требовать присутствия варианта на нормальном основном черепе и не считать фотографию 3D-моделью.',
}

GATES = [
    ('S01', 'Полный состав раздела', 'открыто', 'Сверить 22 кости, 521 запись и отдельные 97 записей «череп как целое». Для каждого термина задать требуемый результат: модель, область, вид, группа или возрастной пример. Ни одного молча исключённого термина.', 'Номенклатурная матрица с русским термином Колесникова, латынью TA98 и критериями; группы и виды не считать отсутствующими сетками.'),
    ('S02', 'Границы соседних разделов', 'разделены после уточнения пользователя', 'Текущий костный модуль: взрослый череп, костные образования и слуховые косточки. Уже начатые мимические/жевательные мышцы принимаются отдельно. Органы чувств, нервы, сосуды, зубные ткани, суставные диски/капсулы/связки, шея и возрастное развитие — самостоятельные будущие модули.', 'Наличие костного канала не объявляет готовым нерв, костной суставной поверхности — весь сустав, альвеолы — зуб. Между модулями сохраняются ссылки; будущие системы не считаются скрытыми дефектами принятого костного модуля.'),
    ('G01', 'Геометрия 22 костей и 521 образования', 'частично', 'Проверить все элементы, включая 325 surface. Закрыть 182 проекции (113 разных терминов) соответствующими реальными объектами; отдельно вести 14 мест вариантов.', 'Исходник, хеш, лицензия, образец/сторона, геометрическое подтверждение всей заявленной области, ракурсы, независимые анатомические источники. Сравнение с КТ, когда исходник — сегментация.'),
    ('G02', 'Каналы, отверстия и сообщения', 'частично', 'Для каждого канала показать вход, выход, непрерывность хода, стенки и перечисленные TA98 ответвления. Край отверстия, просвет или нерв не заменяют стенку. Три новых объекта имеют completeFeatureGeometry=false.', 'Протокол по каждому образованию; обрезка/дефект исходника не принимаются за нормальную стенку. Выделение по сканам допустимо, догадочное заполнение — нет.'),
    ('G03', 'Полости, пазухи и ячейки', 'частично', 'Развести кость, объём воздуха и мягкие ткани; проверить заявленные стенки, перегородки и сообщения. Авторский объём воздуха не доказывает всю окружающую кость.', 'Отдельные исходные объекты и подтверждённые границы; отсутствие мешающих артефактов после исходных Boolean-операций.'),
    ('G04', 'Варианты строения', 'частично', '14 карточек описывают 12 разных типов. Сейчас есть 12 опубликованных изображений и нет отдельных принятых 3D-сеток вариантов.', 'По одному проверенному 3D-примеру каждого включённого типа; сторона примера указана честно. Парные места каталога не выдаются за два просканированных экземпляра.'),
    ('G05', 'Слуховые косточки', 'частично', 'Три косточки есть в правом OpenEar; размечены 8 из 13 подчинённых терминов. Добавить пять перечисленных ниже ориентиров и проверить полную геометрию каждой заявленной части.', 'Все 13 терминов на собственном исходном образце. Для заявления о двух сторонах нужны реальные данные обеих сторон; отражение не считается независимым подтверждением.'),
    ('M01', 'Целые мышцы', 'частично', 'В каталоге 52 экземпляра; у 43 есть модели, у 9 нет. Получить девять проверенных экземпляров и проверить форму/границы уже существующих.', 'Реальный авторский объект или сегментация, верное TA98-название, сторона, анатомическое сопоставление, лицензия для коммерческого распространения.'),
    ('M02', 'Части мышц', 'частично', 'В карточках 26 экземпляров частей: 16 имеют сетки, 10 не имеют. Проверить соответствие каждой границы именно нужной части TA98.', 'Отдельно выбираемые подтверждённые объекты; общая мышца, произвольный разрез и перекрывающиеся расчётные зоны не закрывают часть.'),
    ('M03', 'Начала и прикрепления', 'частично', 'Составить полный реестр для всех мышц и частей, включая мягкие ткани. Текущие 18 маркеров/19 связей для 13 карточек — выборочные ориентиры.', 'Каждая заявленная область подтверждена по стороне и источникам; костная точка не подменяет прикрепление к коже, фасции или соседней мышце. Исключить ошибочную одностороннюю привязку.'),
    ('T01', 'Факты и точные ссылки', 'частично', 'Перепроверить поддержку каждого утверждения двумя независимыми источниками с локаторами. Функция и конкретное кровоснабжение transversus menti отмечены как неподтверждённые.', 'Два независимых подтверждения либо документированное расхождение/неопределённость, если это предел научного знания. Нельзя выдумать однозначную норму ради снятия флага.'),
    ('T02', 'Карточки частей и русский язык', 'частично', 'Проверить наследование начала, прикрепления, функции, иннервации, кровоснабжения. Явно подписывать сведения всей мышцы; выполнить русскоязычную анатомическую вычитку.', 'TA98 и Колесников сверены по точным местам; у каждой части понятна область действия текста. Номенклатурные справочники не считаются двумя анатомическими источниками.'),
    ('Q01', 'Координаты и качество геометрии', 'частично', 'Проверить собственные координаты, единицы, сторону, нормали, обрезки, отверстия и сохранение мелких структур при упрощении. Для рамки КТ проверить углы по center/u/v/field и очистку при смене серии.', 'Машинная проверка плюс визуальный протокол; попадание точки в сетку не доказывает анатомическое имя. Ошибка измерена относительно исходника, а не выведена из размера вокселя.'),
    ('Q02', 'Учебные функции и ошибки', 'базовые проверки пройдены', 'Сохранить цветовой режим, легенду, выбор, изоляцию, прозрачность, срез, поиск, восемь групп, прямые переходы, возврат, тест и сброс. Проверить каждую новую структуру.', '390/1280 px и обе темы; правильная карточка/модель/КТ, обработка ошибок загрузки, отсутствие устаревшего изображения. Тест по костным точкам в README — отдельная ещё не выполненная функция.'),
    ('Q03', 'Реальные телефоны и ресурсы', 'не подтверждено', 'Проверить touch-жесты, память, скорость загрузки и устойчивость на реальных iOS/Android; отказ WebGL/CDN. Headless Chromium с мобильной шириной не заменяет эти проверки.', 'Протокол с устройством/ОС/браузером, измерениями и результатами. Автономная работа не заявляется: текущий сайт использует CDN.'),
    ('L01', 'Коммерчески совместимые права', 'текущий набор проверен', 'Для каждого нового исходника проверить происхождение и условия; сохранить авторство, лицензии, изменения и условия ShareAlike. NC не включать в публикуемый набор.', 'Реестр всех реально публикуемых файлов и разрешений; отдельная проверка упаковки и условий распространения будущего платного приложения.'),
    ('R01', 'Внешняя анатомическая приёмка', 'не проведена', 'Нужен независимый специалист по анатомии для учебной приёмки формы, сторон, подписей, связей и текстов. Автотесты и внутреннее сопоставление с источниками не являются такой рецензией.', 'Подписанный протокол рецензента с перечнем просмотренных структур и исправлением замечаний. Это критерий предлагаемой строгой приёмки, а не утверждение о юридической обязанности.'),
    ('R02', 'Один финальный выпуск', 'текущая версия опубликована', 'После закрытия обязательных пунктов пересобрать все наборы, повторить проверки, обновить обе публичные ссылки, исходники и папку «учеба».', 'Одна зафиксированная версия; опубликованные файлы совпадают с принятыми по хешам. Ноль обязательных пунктов со статусом «источник не получен», «не проверено» или «нужно решить объём».'),
]

def export():
    status = read('research/skull-completion-status.json')
    native = read('site/skull-native-features.json')
    catalogue = {x['c']: x for x in read('site/skull-feature-catalogue.json')['features']}
    bone_rows=[]
    for (bone,code),p in positions().items():
        base=bone.removesuffix('_right').removesuffix('_left')
        lat,ru,_=T[code]
        item=catalogue.get(code,{})
        bone_rows.append(dict(id=f'{bone}:{code}',bone=bone,bone_ru=named(bone,BONE_NAMES[base]['ru']),code=code,ru=ru,lat=lat,
            current_localization=p['localization'],current_model_note=p.get('modelNote',''),position_source=p.get('source_file'),
                owner_module='skull_osteology',closure_status='requires_full_feature_review',acceptance=CRITERIA[p['localization']],
            supplemental_marker_views=[dict(mode=v.get('mode'),id=v.get('id'),scope=v.get('scope')) for v in item.get('views',[])],
            supplemental_channel_views=item.get('channel_views',[]),has_published_image=bool(item.get('example'))))
    muscle_rows=[]; part_rows=[]
    for base,m in MUSCLE_TEMPLATES.items():
        for mid in ([base] if base in ('orbicularis_oris','transversus_menti') else [base+'_right',base+'_left']):
            muscle_rows.append(dict(id=mid,ru=named(mid,m['ru']),lat=m['lat'],code=m['code'],has_model=mid in MUSCLES,
                closure_status='source_geometry_missing' if mid not in MUSCLES else 'source_present_full_anatomical_review_required',
                fields={f:dict(text=m[f],sources=EVIDENCE[base]['fields'].get(f,[]),explicitly_unconfirmed=f in EVIDENCE[base].get('unconfirmed',[]),exact_locators_review_required=True) for f in ('o','i','a','n','s')},note=m.get('note','')))
            available={part for _,part in MUSCLES.get(mid,[])}
            for part,d in m.get('parts',{}).items():
                part_rows.append(dict(id=mid+':'+part,muscle=mid,muscle_ru=named(mid,m['ru']),ru=d['ru'],lat=d['lat'],code=d['code'],has_model=part in available,
                    inherited_fields=[f for f in ('o','i','a','n','s') if f not in d],own_fields={f:d[f] for f in ('o','i','a','n','s') if f in d},acceptance='M02, M03, T01, T02'))
    missing_ossicles=[
        ('A15.3.02.035','Передняя ножка стремени','crus anterius'),('A15.3.02.036','Задняя ножка стремени','crus posterius'),
        ('A15.3.02.041','Чечевицеобразный отросток наковальни','processus lenticularis'),('A15.3.02.047','Латеральный отросток молоточка','processus lateralis'),
        ('A15.3.02.048','Передний отросток молоточка','processus anterior')]
    ossicles=[dict(code=p['c'],ru=p['ru'],lat=p['lat'],current_status='surface_anchor_present_full_extent_review_required') for p in native['markers']['openear'] if p['c'].startswith('A15.3.02.')]
    ossicles += [dict(code=c,ru=r,lat=l,current_status='native_marker_missing',terminology_locator='IFAA A15.3.02; Колесников 2003, печатная с.196 / PDF с.197 (проверено в аудите).') for c,r,l in missing_ossicles]
    whole=read('research/skull-whole-scope-audit.json')
    for row in whole['rows']:
        category=row['proposed_requirement_category']
        row['owner_module']=('developmental_anatomy' if category=='developmental' or row['code']=='A02.1.00.027' else 'joints_connective_tissues' if row['code']=='A02.1.00.011' else 'skull_osteology')
        row['required_for_current_adult_skull']=row['owner_module']=='skull_osteology'
        row['scope_status']='current_module_acceptance_required' if row['required_for_current_adult_skull'] else 'explicit_future_module_not_current_skull_defect'
    modules=[
        dict(id='skull_osteology',title='Костный череп взрослого',phase='текущая приёмка',includes='22 кости, их рельеф, стенки/ходы костных каналов, костные границы полостей и глазниц, швы как границы костей, слуховые косточки и включённые варианты.'),
        dict(id='head_muscles_existing',title='Начатые мышцы головы',phase='отдельная текущая приёмка',includes='52 карточки мимических/жевательных мышц, 26 экземпляров частей, начала/прикрепления, сухожильный шлем. Остальные мышечные группы имеют собственный будущий список.'),
        dict(id='nervous_system',title='Нервная система',phase='будущий модуль',includes='Головной/спинной мозг, нервы и их ветви; связь с костными каналами.'),
        dict(id='cardiovascular_system',title='Сердечно-сосудистая система',phase='будущий модуль',includes='Сердце, артерии, вены и прочие включённые сосуды; венозная часть имеет собственные фильтры и связи.'),
        dict(id='sensory_organs',title='Органы чувств',phase='будущий модуль',includes='Зрение, слух, равновесие, обоняние, вкус, кожная чувствительность; мягкие ткани и специализированные структуры органов. Костная оболочка и её содержимое проверяются раздельно.'),
        dict(id='dentition',title='Зубы и ткани зубочелюстной системы',phase='будущий модуль',includes='Самостоятельные зубные структуры и ткани; альвеолы и костные каналы остаются в костном модуле.'),
        dict(id='joints_connective_tissues',title='Суставы, связки и соединительные ткани',phase='будущий модуль',includes='Диск, капсула, связки ВНЧС, соединения слуховых косточек, фасции и надкостница. Костные суставные поверхности и видимые линии швов входят в проверку костей сейчас.'),
        dict(id='neck_skeleton',title='Скелет шеи',phase='будущий модуль',includes='Подъязычная кость и остальные структуры собственного перечня шеи; не добавляются молча к 22 костям черепа.'),
        dict(id='developmental_anatomy',title='Возрастное развитие',phase='будущий модуль',includes='Детский череп, роднички, хрящевой/перепончатый череп и возрастные серии по собственным реальным образцам.'),
        dict(id='other_body_systems',title='Остальные системы всего тела',phase='будущие отдельные модули',includes='Внутренние органы и остальные системы получают собственные конечные перечни TA98 и критерии; текущая приёмка черепа не является заявлением об их готовности.'),
    ]
    counts=Counter(x['current_localization'] for x in bone_rows)
    assert all(r['owner_module'] in {m['id'] for m in modules} for r in whole['rows'])
    assert len(bone_rows)==521 and dict(counts)=={'surface':325,'variant':14,'projection':182}
    assert len(muscle_rows)==52 and sum(not x['has_model'] for x in muscle_rows)==9
    assert len(part_rows)==26 and sum(not x['has_model'] for x in part_rows)==10
    assert len(ossicles)==13
    report=dict(date='2026-10-13',scope_version=1,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        status='acceptance_requirements_only_not_anatomical_completion',complete_skull_claim=False,
        scope_policy='Все перечисленные пункты должны получить явное решение. Этот реестр не меняет геометрию, карточки или статус маркеров. «100%» означает принятую конечную спецификацию, а не все человеческие варианты или всю голову.',
        counting_policy='521 — экземпляры маркеров, 349 — разные термины; 182 проекции — 113 разных терминов; 14 мест вариантов — 12 разных типов. 9 и 10 учитывают стороны. Эти числа не складываются в процент завершения.',
        user_scope_clarification='Пользователь планирует весь организм со всеми органами, органами чувств, нервной и сосудистой системами. Поэтому приёмка черепа отделена от будущего содержимого головы и остальных систем.',
        module_ownership=modules,
        cross_module_contract='Для анатомической сущности сохраняются TA98, сторона и часть; для геометрии — отдельные идентификаторы источника/образца. Связи «канал — содержимое», «мышца — место прикрепления», «орган — питание/иннервация» не заменяют доказательство каждой связанной структуры. Совмещение независимых образцов требует отдельной проверки.',
        gates=[dict(id=i,title=t,current_status=s,work=w,done_when=d) for i,t,s,w,d in GATES],
        baseline_counts=dict(bones=len(BONES),markers=len(bone_rows),unique_marker_terms=len({r['code'] for r in bone_rows}),localizations=dict(counts),muscle_cards=len(muscle_rows),muscle_parts=len(part_rows)),
        bone_features=bone_rows,skull_as_whole=whole,muscles=muscle_rows,muscle_parts=part_rows,ossicle_features=ossicles,
        separate_channel_objects=status['source_channel_geometry'],source_muscle_requirements=read('research/muscle-completion-review.json')['instances'],
        external_dependencies=['Получить реальные недостающие исходники/сканы с правом коммерческого распространения или заказать сегментацию по таким сканам.',
            'Получить независимую анатомическую рецензию.', 'Провести испытания на физических мобильных устройствах.'],
        change_policy='Не менять знаменатель и не исключать неудобные термины молча. Новое требование оформляется изменением спецификации; новый дефект существующего требования — исправлением, а не новым обещанием.')
    dest=ROOT/'research/skull-closure-requirements.json'
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    def table(headers,rows):
        return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+escape(str(x))+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(str(v))+'</td>' for v in r)+'</tr>' for r in rows)+'</tbody></table></div>'
    loc={'surface':'Видимый участок','projection':'Проекция','variant':'Место варианта'}
    body='<h1>Череп: полный реестр приёмки</h1><p>13 октября 2026 · версия требований 1 · анатомическая готовность не заявляется.</p><p>'+escape(report['counting_policy'])+'</p><p>'+escape(report['scope_policy'])+'</p>'
    body+='<h2>Границы разделов с учётом будущего атласа всего тела</h2>'+table(['Раздел','Этап','Что входит'],[(m['title'],m['phase'],m['includes']) for m in modules])+'<p>'+escape(report['cross_module_contract'])+'</p>'
    body+='<h2>Условия закрытия</h2>'+table(['Код','Пункт','Сейчас','Что сделать','Критерий готовности'],[(g['id'],g['title'],g['current_status'],g['work'],g['done_when']) for g in report['gates']])
    body+='<h2>9 мышц без модели</h2>'+table(['Код','Мышца и сторона','Латынь'],[(m['code'],m['ru'],m['lat']) for m in muscle_rows if not m['has_model']])
    body+='<h2>10 частей без модели</h2>'+table(['Код','Мышца','Часть','Латынь'],[(m['code'],m['muscle_ru'],m['ru'],m['lat']) for m in part_rows if not m['has_model']])
    body+='<h2>5 ориентиров слуховых косточек</h2>'+table(['Код','Название','Латынь'],missing_ossicles)
    body+='<h2>Все 521 записи основного черепа</h2><p>Статус «видимый участок» не является заключением о полной геометрии. Поиск фильтрует таблицы по коду, названию или кости.</p><label>Поиск <input id="filter" type="search" placeholder="Например: канал, височная, A02.1.06"></label>'
    body+=table(['Кость','TA98','Русский термин','Латынь','Сейчас','Что проверить'],[(p['bone_ru'],p['code'],p['ru'],p['lat'],loc[p['current_localization']],p['acceptance']) for p in bone_rows])
    cat={'adult_anatomy':'Анатомическая область/структура','view':'Ракурс','group':'Группа/область','developmental':'Возрастное развитие','requires_scope_review':'Нужна проверка вида представления'}
    body+='<h2>Череп как целое: все 97 строк</h2><p>Предварительная классификация вида работы; это не 97 недостающих сеток. Новые русские эквиваленты ещё нужно сверить с Колесниковым. Возрастные структуры и надкостница явно отнесены к будущим разделам.</p>'
    body+=table(['TA98','Латынь источника','Русский термин','Вид работы','Объём'],[(r['code'],r['latin'],r['russian'] or 'Сверка русского термина предстоит',cat[r['proposed_requirement_category']],'Текущий костный череп' if r['required_for_current_adult_skull'] else 'Будущий отдельный раздел') for r in whole['rows']])
    body+='<h2>Все 52 карточки мышц</h2>'+table(['Код','Название','Латынь','Геометрия'],[(m['code'],m['ru'],m['lat'],'Исходная модель есть; полная анатомическая приёмка отдельно' if m['has_model'] else 'Нет принятой исходной геометрии') for m in muscle_rows])
    body+='<h2>Все 26 экземпляров частей</h2>'+table(['Код','Мышца','Часть','Геометрия','Поля всей мышцы'],[(p['code'],p['muscle_ru'],p['ru'],'Есть исходная модель' if p['has_model'] else 'Нет отдельной модели',', '.join({'o':'начало','i':'прикрепление','a':'функция','n':'иннервация','s':'кровоснабжение'}[f] for f in p['inherited_fields'])) for p in part_rows])
    body+='<h2>Что требуется извне</h2><ul>'+''.join('<li>'+escape(s)+'</li>' for s in report['external_dependencies'])+'</ul><p>'+escape(report['change_policy'])+'</p>'
    html='<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Череп — реестр приёмки</title><style>body{font:16px/1.5 system-ui,sans-serif;margin:24px auto;max-width:1440px;padding:0 18px;color:#182c35;background:#f8faf9}h1{font-size:30px}h2{margin-top:36px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #cedbd8;padding:10px;vertical-align:top;text-align:left}th{background:#dcebe6}tr:nth-child(even){background:white}.scroll{overflow:auto}input{font:inherit;padding:10px;max-width:90%;margin:0 0 18px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}tr[hidden]{display:none}@media print{body{max-width:none}input{display:none}table{font-size:10px}}</style>'+body+'<script>document.getElementById("filter").addEventListener("input",e=>{const q=e.target.value.toLocaleLowerCase();document.querySelectorAll("tbody tr").forEach(r=>r.hidden=!r.textContent.toLocaleLowerCase().includes(q))})</script></html>'
    (ROOT/'research/skull-closure-requirements.html').write_text(html,encoding='utf-8')
    print('Acceptance inventory:',len(bone_rows),'bone entries;',len(muscle_rows),'muscles;',len(part_rows),'parts;',len(ossicles),'ossicle features;',len(GATES),'gates')

if __name__=='__main__':
    export()
