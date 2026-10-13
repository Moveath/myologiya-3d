"""Source-linked educational disposition of all 78 head attachment records.

This creates relational diagrams, not anatomical geometry. An origin/insertion
text and a representative point do not specify a measured attachment polygon.
No coordinates, mesh patches or boundaries are invented by this exporter.
The previously reviewed field texts/locators are copied without promotion of
parent-muscle evidence to a particular part. Run after the attachment exporter.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site/skull-muscle-attachments.json'

# These short labels index the existing source-supported text, not additional
# anatomical claims. Each pair is (origin reading cue, insertion reading cue).
REGIONS = {
    'occipitofrontalis': ('Кожа бровей; затылочная кость', 'Сухожильный шлем'),
    'occipitofrontalis:frontal': ('Кожа бровей и соседние мышцы', 'Сухожильный шлем'),
    'occipitofrontalis:occipital': ('Область выйных линий', 'Сухожильный шлем'),
    'temporoparietalis': ('Фасции над ушной раковиной', 'Сухожильный шлем'),
    'orbicularis_oculi': ('Медиальная область глазницы и век', 'Ткани век и кожа вокруг глазницы'),
    'orbicularis_oculi:orbital': ('Медиальный край глазницы', 'Кожа и мягкие ткани вокруг глазницы'),
    'orbicularis_oculi:palpebral': ('Медиальная связка века', 'Латеральный шов век'),
    'orbicularis_oculi:deep': ('Слёзная кость у слёзного гребня', 'Вековая часть у медиальной области век'),
    'orbicularis_oculi:ciliary': ('Общее начало круговой мышцы глаза', 'Общее прикрепление круговой мышцы глаза'),
    'corrugator_supercilii': ('Медиальный участок надбровной дуги', 'Кожа брови'),
    'procerus': ('Носовая кость и хрящ носа', 'Кожа межбровья'),
    'nasalis': ('Верхняя челюсть у основания носа', 'Апоневроз спинки носа; ткани крыла носа'),
    'nasalis:transverse': ('Верхняя челюсть сбоку от основания носа', 'Апоневроз спинки носа'),
    'nasalis:alar': ('Верхняя челюсть над латеральным резцом', 'Ткани крыла носа'),
    'depressor_septi_nasi': ('Верхняя челюсть над медиальным резцом', 'Подвижная часть перегородки носа'),
    'orbicularis_oris': ('Околоротовые мышцы, узел угла рта, челюсти', 'Кожа и слизистая губ'),
    'orbicularis_oris:marginal': ('Общее начало круговой мышцы рта', 'Общее прикрепление круговой мышцы рта'),
    'orbicularis_oris:labial': ('Общее начало круговой мышцы рта', 'Общее прикрепление круговой мышцы рта'),
    'depressor_anguli_oris': ('Нижняя челюсть у косой линии', 'Узел угла рта'),
    'depressor_labii_inferioris': ('Косая линия нижней челюсти', 'Кожа и слизистая нижней губы'),
    'mentalis': ('Нижняя челюсть ниже резцов', 'Кожа подбородка'),
    'risorius': ('Фасции околоушной и жевательной областей', 'Узел угла рта и кожа'),
    'zygomaticus_major': ('Наружная поверхность скуловой кости', 'Узел угла рта'),
    'zygomaticus_minor': ('Скуловая кость у нижнего края глазницы', 'Ткани верхней губы'),
    'levator_labii_superioris': ('Подглазничный край верхней челюсти', 'Ткани верхней губы'),
    'levator_nasolabialis': ('Лобный отросток верхней челюсти', 'Верхняя губа и крыло носа'),
    'levator_anguli_oris': ('Клыковая ямка верхней челюсти', 'Узел угла рта'),
    'buccinator': ('Альвеолярные области; крылонижнечелюстной шов', 'Узел угла рта; круговая мышца рта'),
    'masseter': ('Скуловая дуга', 'Наружная поверхность ветви и угла челюсти'),
    'masseter:superficial': ('Передний отдел скуловой дуги', 'Наружная поверхность угла и нижней части ветви'),
    'masseter:deep': ('Глубокая поверхность заднего отдела дуги', 'Наружная поверхность ветви выше поверхностной части'),
    'temporalis': ('Височная ямка и фасция', 'Венечный отросток нижней челюсти'),
    'lateral_pterygoid': ('Большое крыло; латеральная пластинка', 'Шейка челюсти; структуры сустава'),
    'lateral_pterygoid:upper': ('Подвисочная поверхность большого крыла', 'Общее прикрепление латеральной крыловидной мышцы'),
    'lateral_pterygoid:lower': ('Наружная поверхность латеральной пластинки', 'Общее прикрепление латеральной крыловидной мышцы'),
    'medial_pterygoid': ('Клиновидная, верхнечелюстная и нёбная кости', 'Медиальная поверхность ветви и угла челюсти'),
    'auricularis_anterior': ('Височная фасция; край сухожильного шлема', 'Ость завитка ушной раковины'),
    'auricularis_superior': ('Сухожильный шлем', 'Верхняя часть ушной раковины'),
    'auricularis_posterior': ('Сосцевидный отросток', 'Задняя поверхность хряща ушной раковины'),
    'depressor_supercilii': ('Лобный отросток верхней челюсти', 'Кожа медиальной части брови'),
    'transversus_menti': ('Мышца, опускающая угол рта, с одной стороны', 'Соответствующие волокна противоположной стороны'),
}

# Field-specific ways to read the existing record. No new functional claims,
# exact polygon boundaries, measurements or inferred attachment coordinates.
GUIDANCE = {
    'occipitofrontalis': (
        'Открой отдельно лобное и затылочное брюшки: в общей строке перечислены два разных участка начала.',
        'Сопоставь оба брюшка с сухожильным шлемом; схема не измеряет их переход в апоневроз.'),
    'occipitofrontalis:frontal': (
        'Читай начало как связь с кожей бровей и соседними мышцами; костной точки для этой строки нет.',
        'Сопоставь лобное брюшко и сухожильный шлем. Точное распределение переходящих волокон не размечено.'),
    'occipitofrontalis:occipital': (
        'Сравни примечание о наивысшей и верхней выйных линиях; не заучивай их как один ориентир.',
        'Сопоставь затылочное брюшко и сухожильный шлем. Их граница на схеме не является измерением.'),
    'temporoparietalis': (
        'Запоминай указанную фасциальную область над ушной раковиной; отдельная костная площадка здесь не заявлена.',
        'Сопоставь мышцу с сухожильным шлемом; контур её перехода в него не нанесён.'),
    'orbicularis_oculi': (
        'Открой отдельные части: общая строка объединяет несколько областей начала.',
        'Разделяй ткани век и кожу вокруг глазницы; общая схема не распределяет все волокна по частям.'),
    'orbicularis_oculi:orbital': (
        'Сопоставь медиальный край глазницы со слёзным гребнем и лобным отростком из полного описания.',
        'Это мягкотканная область вокруг края глазницы; окраска кости не могла бы показать её прикрепление.'),
    'orbicularis_oculi:palpebral': (
        'Запоминай медиальную связку века как названную область начала, не как всю медиальную стенку глазницы.',
        'Прочитай оговорку о названиях латерального шва и связки в источниках; это не дополнительная костная точка.'),
    'orbicularis_oculi:deep': (
        'Сопоставь слёзную кость и область гребня; одна точка на гребне не задаёт ширину начала.',
        'Открой примечание части: краткое поле описывает переход к вековой части, а не исчерпывающую карту всех волокон.'),
    'orbicularis_oculi:ciliary': (
        'Сейчас приведено общее начало круговой мышцы глаза. Его нельзя автоматически приписывать ресничному пучку.',
        'Сейчас приведено общее прикрепление круговой мышцы глаза. Отдельный путь волокон ресничного пучка не установлен этим полем.'),
    'corrugator_supercilii': (
        'Ищи медиальный участок надбровной дуги, а не всю дугу целиком.',
        'Связь относится к коже брови; она не задаёт костную площадку прикрепления.'),
    'procerus': (
        'В начале указаны и кость, и прилежащий хрящ; одна костная поверхность не представляет всю строку.',
        'Запоминай кожу межбровья как область прикрепления; её граница не измерена по костному черепу.'),
    'nasalis': (
        'Для более точного чтения открой поперечную и крыльную части отдельно.',
        'Разделяй две названные области: апоневроз спинки носа и ткани крыла носа.'),
    'nasalis:transverse': (
        'Сопоставь начало с боковой областью основания носа; не принимай всю верхнюю челюсть за площадь начала.',
        'Схема называет апоневроз спинки носа; размер и границы перехода в него не показаны.'),
    'nasalis:alar': (
        'Для ориентирования используй область верхней челюсти над латеральным резцом из полного описания.',
        'Прикрепление относится к тканям крыла носа; соответствующего костного контура нет.'),
    'depressor_septi_nasi': (
        'Различай область над медиальным резцом и область над латеральным резцом в карточке крыльной части носовой мышцы.',
        'Прикрепление относится к подвижной части перегородки, а не ко всей костной перегородке.'),
    'orbicularis_oris': (
        'Читай перечисленные околоротовые связи вместе: схема не сводит их к одной костной точке.',
        'Разделяй кожу и слизистую губ; их пространственные границы не следуют из модели челюстей.'),
    'orbicularis_oris:marginal': (
        'Здесь сохранены сведения всей круговой мышцы рта. Они не задают собственное начало краевой части.',
        'Здесь сохранены сведения всей круговой мышцы рта. Отдельная граница прикрепления краевой части не подтверждена.'),
    'orbicularis_oris:labial': (
        'Здесь сохранены сведения всей круговой мышцы рта. Они не задают собственное начало губной части.',
        'Здесь сохранены сведения всей круговой мышцы рта. Отдельная граница прикрепления губной части не подтверждена.'),
    'depressor_anguli_oris': (
        'Сопоставь наружную поверхность нижней челюсти и косую линию; не закрашивай всю линию как одну площадку.',
        'Запоминай узел угла рта как названную мягкотканную область, не как точку на челюсти.'),
    'depressor_labii_inferioris': (
        'Используй косую линию как ориентир области начала; её длина не равна измеренной длине начала мышцы.',
        'Схема различает кожу и слизистую нижней губы, но не показывает карту вплетения волокон.'),
    'mentalis': (
        'Сопоставь переднюю поверхность нижней челюсти и область ниже резцов из полного описания.',
        'Прикрепление относится к коже подбородка; это не вся поверхность подбородочного выступа.'),
    'risorius': (
        'Открой примечание об изменчивых начальных прикреплениях. Не выбирай одну обязательную точку из общего перечня.',
        'Читай вместе узел угла рта и прилежащую кожу; схема не проводит между ними точную границу.'),
    'zygomaticus_major': (
        'Ищи указанную наружную поверхность скуловой кости; весь объект кости не является площадью начала.',
        'Сопоставь мышцу с узлом угла рта из описания; точный объём вплетения не выделен.'),
    'zygomaticus_minor': (
        'Используй нижний край глазницы для ориентирования на скуловой кости.',
        'Сопоставь мышцу с тканями верхней губы; участок кожи и глубина вплетения не измерены.'),
    'levator_labii_superioris': (
        'Доступный костный маркер помогает найти подглазничную область, но не очерчивает начало мышцы.',
        'Прикрепление описывает ткани верхней губы; его нельзя восстановить по одной костной точке.'),
    'levator_nasolabialis': (
        'Доступный маркер показывает лобный отросток верхней челюсти; не весь отросток является измеренной площадкой начала.',
        'Разделяй названные области верхней губы и крыла носа; схема не задаёт количественное распределение волокон.'),
    'levator_anguli_oris': (
        'Костный ориентир позволяет найти клыковую ямку. Границы ямки не заменяют границы начала мышцы.',
        'Сопоставь мышцу с узлом угла рта; точный контур мягкотканного вплетения в модели не размечен.'),
    'buccinator': (
        'Запоминай все три составляющие описания: альвеолярные области обеих челюстей и крылонижнечелюстной шов.',
        'Читай обе связи: узел угла рта и вплетение в круговую мышцу рта. Это не одна костная площадка.'),
    'masseter': (
        'Открой обе части мышцы: общая скуловая дуга не задаёт одинаковое начало для них.',
        'Ищи наружную сторону ветви и угла челюсти. Маркер жевательной бугристости — только ориентир общей мышцы.'),
    'masseter:superficial': (
        'Прочитай полное описание: кроме переднего отдела дуги указан верхнечелюстной отросток скуловой кости.',
        'Сопоставь наружную сторону угла и нижнего участка ветви; маркер всей мышцы не считается разметкой поверхностной части.'),
    'masseter:deep': (
        'Сравни примечание о границах заднего отдела дуги в источниках; на схеме не выбирается одна точная линия.',
        'Сопоставь положение выше прикрепления поверхностной части; схема не измеряет границу между их областями.'),
    'temporalis': (
        'Читай вместе височную ямку и фасцию. Точка на височной кости не представляет всю ямку и фасцию.',
        'Костный ориентир показывает венечный отросток, но не измеренную площадку прикрепления.'),
    'lateral_pterygoid': (
        'Открой верхнюю и нижнюю головки: в общей строке объединены две разные костные области.',
        'Разделяй костную ямку и суставные структуры. Прочитай примечание: их нельзя одинаково приписать обеим головкам.'),
    'lateral_pterygoid:upper': (
        'Сопоставь подвисочную поверхность большого крыла клиновидной кости из собственного описания этой головки.',
        'Показано прикрепление всей мышцы. Карточка не подтверждает распределение между ямкой, диском и капсулой именно для верхней головки.'),
    'lateral_pterygoid:lower': (
        'Используй наружную сторону латеральной пластинки; костный маркер не задаёт всю площадь начала.',
        'Показано прикрепление всей мышцы. Карточка не подтверждает распределение между ямкой, диском и капсулой именно для нижней головки.'),
    'medial_pterygoid': (
        'Сопоставь три названные костные области. Маркер пластинки не заменяет проверку её медиальной стороны.',
        'Сравни медиальную сторону ветви и угла с наружным прикреплением жевательной мышцы.'),
    'auricularis_anterior': (
        'Разделяй височную фасцию и край сухожильного шлема; они не задают одну костную площадку.',
        'Запоминай ость завитка из описания; точный контур её связи с мышцей на исходной модели не размечен.'),
    'auricularis_superior': (
        'Сопоставь мышцу с сухожильным шлемом; костного места начала эта строка не задаёт.',
        'Читай верхнюю часть ушной раковины как область, а не точно ограниченную измеренную площадку.'),
    'auricularis_posterior': (
        'Сопоставь мышцу с сосцевидным отростком; окраска всего отростка завысила бы область начала.',
        'Прочитай указание задней поверхности хряща; эта связь не отображается площадкой на височной кости.'),
    'depressor_supercilii': (
        'Открой примечание: анатомические исследования и сводная таблица расходятся в названии кости начала.',
        'Сопоставь медиальную часть кожи брови; точная линия вплетения не нанесена.'),
    'transversus_menti': (
        'Схема описывает непостоянный поперечный пучок. Обозначение начала на одной стороне служит для чтения связи, а не для обязательной асимметрии.',
        'Сопоставь волокна противоположной стороны. Эта связь не подтверждает отдельную функцию или единственную питающую артерию.'),
}


def base_key(record):
    muscle = record['muscleId'].removesuffix('_right').removesuffix('_left')
    return muscle + (':' + record['part'] if record['part'] else '')


def make_field(rec, name, n):
    source = rec[name]
    key = base_key(rec)
    inherited = rec['kind'] == 'part' and source['scope'] == 'whole_muscle'
    label = REGIONS[key][n]
    refs = deepcopy(source['refs'])
    assert len({r['independentSource'] for r in refs}) >= 2
    assert all(r.get('locator') and r.get('url') for r in refs)
    unknown = (f'Для части «{rec["ru"]}» здесь нет собственного подтверждённого описания этой связи: '
               'поле унаследовано от всей мышцы. Её отдельная область и граница на модели не установлены.'
               if inherited else
               f'Для области «{label}» в опубликованном наборе не размечен собственный контур '
               'начала или прикрепления этой мышцы. Площадь, ширина и точная граница на 3D-сетке не измерены.')
    reason = ('Источники этого поля описывают всю мышцу; они не выделяют в нём отдельное прикрепление выбранной части.'
              if inherited else
              'Сохранённые ссылки подтверждают словесное описание. К этому полю не приложены '
              'контур сегментации или координаты границы, сопоставленные с конкретной исходной моделью.')
    if source['representativeMarkerIds']:
        reason += ' Имеющиеся маркеры выбирают отдельные ориентиры; соединение их в полигон было бы новым предположением.'
    if source['parentMuscleMarkers']:
        reason += ' Ориентиры родительской мышцы не используются как собственная разметка этой части.'
    return {
        'label': 'Начало' if name == 'origin' else 'Прикрепление',
        'text': source['text'], 'known': source['text'], 'areaLabel': label,
        'scope': source['scope'], 'status': source['status'],
        'evidenceAppliesTo': 'parent_muscle' if inherited else 'selected_record',
        'presentation': 'parent_relation_only' if inherited else 'documented_relation',
        'scopeLabel': 'Сведения всей мышцы; для этой части отдельно не подтверждены' if inherited else
                      ('Собственные сведения части' if rec['kind'] == 'part' else 'Сведения мышцы'),
        'unknown': unknown, 'whyNoBoundary': reason,
        'learningGuidance': GUIDANCE[key][n], 'refs': refs,
        'representativeMarkerIds': source['representativeMarkerIds'],
        'representativeMarkers': deepcopy(source['representativeMarkers']),
        'parentMuscleMarkers': deepcopy(source['parentMuscleMarkers']),
        'completeAttachmentArea': False, 'geometryStatus': 'no_measured_boundary',
        'fallbackImplemented': True,
        'completionRoute': 'explained_limit_with_source_linked_relation',
    }


def acceptance_findings():
    requirements = json.loads((ROOT/'research/skull-closure-requirements.json').read_text(encoding='utf8'))
    whole = json.loads((ROOT/'site/skull-whole.json').read_text(encoding='utf8'))
    return {
        'reviewType': 'internal_educational_disposition_audit_not_external_anatomical_acceptance',
        'ruleChange': 'Пользователь разрешил явно обозначенные реконструкции и объяснение того, что не удалось подтвердить. '
                      'Это позволяет завершить учебную обработку конечного перечня без объявления всей геометрии подтверждённой.',
        'preserveClaims': {
            'completeSkullGeometry': False, 'completeAttachmentAreas': False,
            'externalExpertReviewCompleted': False, 'physicalPhoneReviewCompleted': False,
        },
        'requiredDisposition': [
            {'scope':'521 запись костных образований',
             'requirement':'У каждой сохранить исходную локализацию, результат проверки полной протяжённости и конкретное ограничение. '
                           'Реконструкция или схема не переводит исходную projection в surface.',
             'currentCounts':requirements['baseline_counts']['localizations']},
            {'scope':'97 строк «череп как целое»',
             'requirement':'Сохранить 89 текущих и 8 будущих строк. У контекстного вида объяснить, какие границы он показывает '
                           'и чего не подтверждает. У микроструктур и вариантов без геометрии нужен собственный текст пробела.',
             'currentCounts':whole['counts']},
            {'scope':'13 ориентиров слуховых косточек',
             'requirement':'Разделять наличие ориентира и полную форму. У чечевицеобразного отростка наковальни '
                           '(A15.3.02.041) отдельно указать неразделённые ножку и край пластинки; у переднего отростка '
                           'молоточка (A15.3.02.048) — неподтверждённое тонкое продолжение. Правый препарат не объявлять двумя сторонами.'},
            {'scope':'156 полей начал и прикреплений',
             'requirement':'Все поля содержат известное, источник с локатором, неизвестное в данном наборе и способ чтения схемы. '
                           '12 унаследованных полей частей не повышать до собственной анатомической разметки.'},
            {'scope':'Факты и внешняя приёмка',
             'requirement':'Функция и конкретное кровоснабжение transversus menti сохраняют неопределённость. '
                           'Автотесты не являются независимой анатомической рецензией или проверкой физического телефона.'},
            {'scope':'Публикация',
             'requirement':'Различать завершённую обработку учебного перечня и полную геометрическую/экспертную приёмку. '
                           'Не оставлять обещания «все поверхности подтверждены», если применены объяснённые ограничения.'},
        ],
    }


def generate():
    data = json.loads(SOURCE.read_text(encoding='utf8'))
    items = []
    for rec in data['items']:
        key = base_key(rec)
        assert key in REGIONS and key in GUIDANCE, key
        origin, insertion = (make_field(rec, name, n) for n, name in enumerate(('origin','insertion')))
        item = {k:deepcopy(rec[k]) for k in ('id','muscleId','part','kind','ru','lat','ta98','side','note','partNote','geometry')}
        item.update({
            'status':'explained_attachment_limits', 'origin':origin, 'insertion':insertion,
            'representation':{
                'kind':'relation_diagram', 'spatialGeometry':False,
                'title':'Связи начала и прикрепления',
                'description':'Панели обозначают названные в источниках области. Их размер, расстояния и стрелки — '
                              'схема чтения, а не форма, положение, длина волокон или направление сокращения.',
                'nodes':[
                    {'role':'origin','label':origin['areaLabel'],'scope':origin['scope'],
                     'evidenceAppliesTo':origin['evidenceAppliesTo'],'text':origin['text']},
                    {'role':'muscle','label':rec['ru'],'latin':rec['lat']},
                    {'role':'insertion','label':insertion['areaLabel'],'scope':insertion['scope'],
                     'evidenceAppliesTo':insertion['evidenceAppliesTo'],'text':insertion['text']},
                ],
                'edges':[
                    {'from':'origin','to':'muscle','meaning':'beginning_relation','anatomicalPath':False},
                    {'from':'muscle','to':'insertion','meaning':'attachment_relation','anatomicalPath':False},
                ],
            },
            'completeAttachmentArea':False, 'sourceGeometryAltered':False,
            'educationalDisposition':'documented_relation_and_explicit_limit',
            'limitations':[
                'Схема не является 3D-реконструкцией поверхности прикрепления.',
                'Площадь начала или прикрепления не вычисляется из костного маркера или габаритов мышцы.',
            ],
            'links':{'atlasCard':{'section':'head','muscle':rec['muscleId'],'part':rec['part']},
                     'sourceRegistry':'skull-muscle-attachments.json'},
        })
        items.append(item)
    assert len(items)==78 and len({v['id'] for v in items})==78
    assert set(REGIONS)=={base_key(r) for r in data['items']}==set(GUIDANCE)
    fields = [v[f] for v in items for f in ('origin','insertion')]
    assert len(fields)==156 and all(v['known'] and v['unknown'] and v['whyNoBoundary'] and v['learningGuidance'] for v in fields)
    inherited=sum(v['evidenceAppliesTo']=='parent_muscle' for v in fields)
    assert inherited==12
    counts={'records':78,'wholeMuscles':52,'parts':26,'fields':156,
            'sourceLinkedFields':156,'explainedLimits':156,'relationDiagrams':78,
            'inheritedPartFields':inherited,'sourceMeasuredAttachmentAreas':0,
            'new3DAttachmentAreas':0,'changedSourcePins':0}
    output = {
        'schemaVersion':1, 'generatedBy':'scripts/skull_attachment_education.py',
        'title':'Начала и прикрепления: что известно и как читать схемы',
        'description':'Все 78 записей текущих мышц и частей. У каждого начала и прикрепления разделены '
                      'анатомическое описание, предел данных и способ ориентирования.',
        'counts':counts, 'completeAttachmentArea':False,
        'geometryFile':None,
        'geometryDecision':'Отдельная GLB не создаётся: документы не содержат проверенных пространственных '
                           'контуров прикрепления. Условные объёмы не добавили бы достоверной пространственной информации.',
        'sourceRegistry':'skull-muscle-attachments.json',
        'sourceRegistrySha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'items':items,
    }
    target=ROOT/'site/skull-attachment-education.json'
    target.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    review={
        'date':'2026-10-13','generator':'scripts/skull_attachment_education.py','counts':counts,
        'source':'site/skull-muscle-attachments.json','sourceSha256':output['sourceRegistrySha256'],
        'output':'site/skull-attachment-education.json',
        'outputSha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'sourceTextChanged':False,'geometryCreated':False,'sourcePinsChanged':False,
        'externalExpertReviewCompleted':False,
        'fieldStatusCounts':dict(Counter(v['status'] for v in fields)),
        'validation':{'allFieldsHaveTwoIndependentSourcesAndLocators':True,
                      'allFieldsHaveKnownUnknownReasonAndGuidance':True,
                      'inheritedFieldsRemainParentScoped':True,
                      'noMeshBoundariesInferredFromPointsOrBoundingBoxes':True},
        'acceptanceFindings':acceptance_findings(),
    }
    (ROOT/'research/skull-attachment-education-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(counts,ensure_ascii=False))


if __name__=='__main__':
    generate()
