"""Addressed maxillary/palatine representation review; never generate geometry.

Definitions and existing independent source pairs are retained. The choices below
describe whole anatomical entities, not the appearance of their current marker.
"""
from copy import deepcopy
from head_skull_batch2 import _ref, GRAY_URL
from head_face_evidence import PALACKY, STANDARD


def source(key, title, url, locator, group, access='text'):
    return _ref('batch6_'+key, title, url, locator, group,
                scope='representation', access=access)


GRAY_MAX = source('gray_maxilla', 'Gray / Lewis. Anatomy of the Human Body (1918)',
    GRAY_URL+'#page=118', 'PDF pp.118–125: body, surfaces, processes, alveoli and palatine process. Original figure-specific references retained.', 'gray_lewis_1918')
GRAY_PAL = source('gray_palatine', 'Gray / Lewis. Anatomy of the Human Body (1918)',
    GRAY_URL+'#page=132', 'PDF pp.132–135: horizontal/perpendicular parts, processes, borders, grooves and apertures.', 'gray_lewis_1918')
PALACKY_REF = source('palacky', 'Libor Luňáček, Univerzita Palackého — Splanchnocranium',
    PALACKY, 'Sections MAXILLA and OS PALATINUM: plates/processes, socket septa, crests, groove/canal and palatine contribution. Not used to resolve the greater canal wall conflict.', 'lunacek_palacky')
STANDARD_REF = source('standard', 'Anatomy Standard — Maxilla', STANDARD,
    'Anterior, lateral, medial and inferior labelled views. Existing source pairs retained; this atlas does not localize this GLB.', 'anatomy_standard')
HIATUS = source('hiatus', 'Iwanaga et al. Clinical anatomy of the maxillary sinus (2019)',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC6449588/',
    'Anatomy, medial wall: isolated maxillary hiatus versus assembled ostium; PMID 30984447, DOI 10.5115/acb.2019.52.1.17. Indexed text accessible; direct PMC blocked.', 'iwanaga_2019', 'indexed_text')
ANTERIOR_SPINE = source('anterior_spine', 'Muhammad A. Javaid, IMAIOS e-Anatomy — Anterior nasal spine',
    'https://www.imaios.com/en/e-anatomy/anatomical-structures/anterior-nasal-spine-1536897012',
    'Definition: projections from the two maxillae contribute to one anterior nasal spine. Open text; no closed gallery used.', 'javaid_imaios')

# Explicit interpretation of the current definitions; never a name-based rule.
MAXILLA = {
 2: ('volume', 'Тело — костная часть с пазухой и несколькими наружными гранями; не сама пазуха и не одна поверхность.', 'maxilla'),
 5: ('area', 'Открытое костное ложе на задней части глазничной поверхности переходит в канал; линия хода нерва не заменяет ширину борозды.', 'maxilla'),
 8: ('space', 'Наружное устье подглазничного канала отличается от его просвета на всём протяжении и от костного края отверстия.', 'maxilla'),
 9: ('area', 'Клыковая ямка — углубление передней костной поверхности, латеральнее клыкового возвышения; не зубная лунка.', 'maxilla'),
 10: ('line', 'Определение обозначает вогнутую границу передней поверхности; это собственный край, а не вся грушевидная апертура.', 'maxilla'),
 11: ('volume', 'Костный выступ в составе общей передней носовой ости имеет объём; цефалометрическая точка его вершины не равна всей ости.', 'anterior_spine'),
 14: ('space', 'Группа входов задних альвеолярных каналов; одно положение маркера не представляет каждое отверстие.', 'maxilla'),
 16: ('volume', 'Бугор — задний костный выступ тела позади зубного ряда; не только его суставная площадка.', 'maxilla'),
 18: ('area', 'Собственная слёзная борозда верхней челюсти — костное ложе; не вся ямка мешка или собранный носослёзный канал.', 'existing_maxilla'),
 19: ('volume', 'Раковинный гребень — выступающий костный рельеф для нижней раковины; не сама раковина и не одна линия её соединения.', 'maxilla'),
 21: ('space', 'Расщелина — крупное отверстие изолированной верхней челюсти в пазуху; не окончательное соустье с мягкими тканями собранной носовой стенки.', 'hiatus'),
 22: ('area', 'Собственная большая нёбная борозда — открытое костное ложе для составного канала; не весь канал или его выход.', 'existing_maxilla'),
 24: ('volume', 'Лобный отросток — восходящая костная пластинка с несколькими поверхностями и соединениями.', 'maxilla'),
 25: ('volume', 'Передний слёзный гребень — костный рельеф, ограничивающий борозду; край гребня не заменяет весь гребень.', 'maxilla'),
 26: ('area', 'Слёзная вырезка — собственная выемка медиального глазничного края; не готовый просвет носослёзного канала.', 'existing_maxilla'),
 27: ('volume', 'Решётчатый гребень — костный выступ медиальной поверхности лобного отростка для средней раковины; не вся решётчатая кость.', 'maxilla'),
 28: ('volume', 'Скуловой отросток — костный выступ с толщиной; его шовная поверхность является только частью.', 'maxilla'),
 29: ('volume', 'Нёбный отросток — горизонтальная костная пластинка; его носовая и ротовая поверхности не заменяют весь объём.', 'maxilla'),
 30: ('volume', 'Носовой гребень на медиальном крае отростка — костный рельеф, а не сам сошник или линия срединного шва.', 'existing_maxilla'),
 31: ('volume', 'Резцовая кость здесь обозначает переднюю резцовую часть верхней челюсти; не независимую дополнительную кость каждого взрослого.', 'existing_maxilla'),
 32: ('line', 'Резцовый шов — линия соединения резцовой части с остальной верхней челюстью; его наличие и протяжённость на образце отдельно не приняты.', 'existing_maxilla'),
 33: ('volume', 'Нёбные ости — множественные костные выступы возле борозд, не одиночная точка и не нервно-сосудистый пучок.', 'existing_maxilla'),
 34: ('area', 'Нёбные борозды — открытые ложа нижней поверхности отростка; не внутренние малые нёбные каналы.', 'existing_maxilla'),
 35: ('volume', 'Альвеолярный отросток — зубоносная часть кости с лунками, стенками и перегородками; не только свободный край дуги.', 'maxilla'),
 37: ('volume', 'Зубные альвеолы — лунки для корней с глубиной и стенками; их входы или точки на соседней кости не заменяют весь объём.', 'maxilla'),
 38: ('volume', 'Межальвеолярные перегородки — костное вещество между соседними лунками, а не линия между зубами.', 'maxilla'),
 39: ('volume', 'Межкорневые перегородки — костные разделители внутри лунки многокорневого зуба; отличны от межальвеолярных.', 'existing_maxilla'),
 40: ('volume', 'Альвеолярные возвышения — наружный костный рельеф, соответствующий корням; не сами зубы и не осевые линии корней.', 'maxilla'),
}
PALATINE = {
 2: ('volume', 'Перпендикулярная пластинка имеет толщину, носовую и верхнечелюстную поверхности; одна грань не представляет всю пластинку.', 'palatine'),
 5: ('space', 'Промежуток между глазничным и клиновидным отростками — собственная открытая вырезка; не автоматически весь контур собранного клиновидно-нёбного отверстия.', 'palatine'),
 6: ('area', 'Большая нёбная борозда — открытое ложе на верхнечелюстной стороне пластинки; не вся полость общего канала.', 'existing_palatine'),
 7: ('volume', 'Пирамидальный отросток — костная часть на соединении пластинок с поверхностями и внутренними каналами.', 'palatine'),
 9: ('volume', 'Нижний раковинный гребень — костный рельеф носовой поверхности для нижней раковины, не сама раковина.', 'palatine'),
 10: ('volume', 'Верхний решётчатый гребень — костный рельеф для средней раковины; не линия границы всего среднего носового хода.', 'palatine'),
 11: ('volume', 'Глазничный отросток имеет несколько соединительных и свободных поверхностей; только верхняя глазничная грань участвует в дне глазницы.', 'existing_palatine'),
 12: ('volume', 'Клиновидный отросток — собственная костная пластинка с несколькими гранями; не весь нёбно-влагалищный канал.', 'existing_palatine'),
 13: ('volume', 'Горизонтальная пластинка — костная часть с двумя гранями и краями; не всё твёрдое нёбо и не одна поверхность.', 'palatine'),
 16: ('space', 'Малые нёбные отверстия — группа выходов каналов на нижней стороне пирамидального отростка, не сами каналы.', 'existing_palatine'),
 17: ('volume', 'Костный вклад горизонтальной пластинки в общую заднюю носовую ость; не отдельная математическая вершина справа или слева.', 'palatine'),
 18: ('volume', 'Носовой гребень — возвышающийся костный край пластинки для соединения с сошником; не сам сошник или срединный шов.', 'existing_palatine'),
 19: ('volume', 'Нёбный гребень — поперечный костный рельеф у заднего края ротовой поверхности; не линия свободного заднего края нёба.', 'existing_palatine'),
}

DESCRIPTION_FIXES = {
 'A02.1.12.011': 'Костный выступ у нижнего конца носовой вырезки. Вместе с выступом противоположной верхней челюсти участвует в образовании общей передней носовой ости; локальная запись не означает отдельную ость каждой стороны.',
 'A02.1.12.021': 'Большое отверстие носовой поверхности изолированной верхней челюсти в пазуху. В собранной стенке носовой полости его закрывают части соседних костей и мягкие ткани; оно не тождественно окончательному соустью пазухи.',
 'A02.1.13.017': 'Медиальный выступ заднего края горизонтальной пластинки. Вместе с соответствующим выступом противоположной нёбной кости образует общую заднюю носовую ость; локальная запись обозначает вклад своей кости.',
}


def reviewed_decisions():
    rows = {}
    for side in ('right', 'left'):
        for bone, prefix, decisions in [('maxilla', 'A02.1.12.', MAXILLA), ('palatine', 'A02.1.13.', PALATINE)]:
            rows.update({(bone+'_'+side, prefix+f'{n:03}'): dict(kind=k, reason=r, group=g)
                         for n, (k, r, g) in decisions.items()})
        rows['maxilla_'+side, 'A02.1.00.062'] = dict(kind='space', group='existing_maxilla',
            reason='Устья резцовых каналов в переднем нёбе — отверстия; не вся резцовая ямка и не полный разветвлённый ход каналов. Число и объединение устьев вариабельны и на образце не приняты.')
    return rows


def decision_sources(decision):
    return {'maxilla': (GRAY_MAX, PALACKY_REF, STANDARD_REF),
            'palatine': (GRAY_PAL, PALACKY_REF),
            'existing_maxilla': (GRAY_MAX,), 'existing_palatine': (GRAY_PAL,),
            'hiatus': (GRAY_MAX, HIATUS), 'anterior_spine': (GRAY_MAX, ANTERIOR_SPINE)}[decision['group']]


def apply_record_review(record):
    decision = reviewed_decisions().get((record['b'], record['c']))
    if not decision: return
    assert record['geometryKind'] == decision['kind']
    record['geometryReview'] = dict(status='representation_reviewed', rationale=decision['reason'],
        source='research/stage5-skull-batch6-2026-10-16/geometry-kind-review.json',
        coordinateAcceptance=False, extentAcceptance=False)
    # Do not share mutable source lists with the other side.
    record['refs'] = record['refs'] + deepcopy(list(decision_sources(decision)))
    if record['c'] in DESCRIPTION_FIXES:
        record['x'] = DESCRIPTION_FIXES[record['c']]
    record['modelNote'] += ' Проверен анатомический тип; координата, полный контур, поверхность и внутренний ход на этой модели отдельно не приняты.'
