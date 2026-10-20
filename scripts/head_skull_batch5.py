"""Addressed petromastoid/tympanic representation choices; no new coordinates.

The decisions concern each existing definition, not string-based classification.
Source pairs already attached to records remain valid and are not replaced.
"""
from copy import deepcopy
from head_skull_batch2 import _ref, GRAY_URL, OXFORD_URL
from head_skull_batch4 import GULYA_URL

def source(key, title, url, locator, group, access='text'):
    return _ref('batch5_'+key, title, url, locator, group,
                scope='representation', access=access)

GRAY = source('gray_temporal', 'Gray / Lewis. Anatomy of the Human Body (1918)',
    GRAY_URL+'#page=94', 'PDF pp.93–99: mastoid, petrous surfaces/borders, apertures and tympanic plate. Existing figure-specific references retained.', 'gray_lewis_1918')
OXFORD = source('oxford_temporal', 'van Gijn DR, Dunne J. Oxford Handbook of Head and Neck Anatomy (2022)',
    OXFORD_URL, 'Printed pp.23–28 / PDF pp.42–47: petrous, mastoid and tympanic parts. Only the publisher preview was read.', 'van_gijn_dunne')
GULYA = source('gulya', 'Aina Julianna Gulya. Gulya and Schuknecht’s Anatomy of the Temporal Bone, 3rd ed. (2007)',
    GULYA_URL, 'Printed pp.1–4 / PDF pp.22–25, figures A–E: petrous surfaces/apex, grooves, apertures, tympanic plate and sulcus. No specimen dimensions transferred.', 'gulya_schuknecht')
ISAACSON = source('isaacson', 'Brandon Isaacson. Anatomy and Surgical Approach of the Ear and Temporal Bone (2018)',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC6081290/', 'Anatomy: osseous segments, annulus, petrous segment and apex; PMID 30069845; DOI 10.1007/s12105-018-0926-2.', 'isaacson_2018', 'full_text')
HAMULUS = source('hamulus', 'Malkidou et al. Pterygoid Hamulus: Morphological Analysis and Clinical Implications (2024)',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC10997969/', 'Introduction: tendon and bursa at hamular groove; PMID 38586645; DOI 10.7759/cureus.55694. Specimen averages do not define this GLB.', 'malkidou_2024', 'indexed_text')
PROCESS = source('process', 'Yadav et al. Pterygospinous Bar and Foramen in the Adult Human Skulls of North India (2014)',
    'https://pubmed.ncbi.nlm.nih.gov/24963408/', 'Abstract: process on posterior border of lateral pterygoid plate, distinct from ligament/bar/foramen; DOI 10.1155/2014/286794. Full PMC page blocked; no full-text claim.', 'yadav_2014', 'indexed_abstract')
PLATE = source('plate', 'Elsevier Complete Anatomy — Lateral Pterygoid Plate (Right)',
    'https://www.elsevier.com/resources/anatomy/skeletal-system/axial-skeleton/lateral-pterygoid-plate-right/19067',
    'Description: bony lateral plate and its pterygospinous process; text only, no app mesh or image reused.', 'elsevier_complete_anatomy')
SPINE = source('spine', 'Antoine Micheau, IMAIOS e-Anatomy — Greater tympanic spine',
    'https://www.imaios.com/en/e-anatomy/anatomical-structures/greater-tympanic-spine-1536895836',
    'Definition: anterior end of the bony tympanic ring. Existing Spalteholz/Fay pair retained; no closed CT gallery claimed.', 'micheau_imaios')

# Code: kind, interpretation of the actual structure, additional source group.
TEMPORAL = {
 2: ('volume', 'Каменистая часть — костная часть с внутренними полостями и наружными гранями, не одна грань.', 'petrous'),
 3: ('line', 'Собственный задний край сосцевидной области задаёт линию границы кости; это не весь затылочно-сосцевидный шов.', 'mastoid'),
 4: ('volume', 'Сосцевидный отросток — костный выступ с толщиной и внутренним строением; поверхность его вершины не заменяет весь отросток.', 'mastoid'),
 5: ('area', 'Сосцевидная вырезка здесь обозначает углублённое костное ложе на медиальной стороне отростка, не пустой канал.', 'mastoid'),
 6: ('area', 'Собственная сигмовидная борозда височной кости — костное ложе; это не просвет венозного синуса и не весь многокостный ход.', 'mastoid'),
 7: ('area', 'Борозда затылочной артерии — углублённый участок поверхности; артерия и её ось не входят в эту запись.', 'mastoid'),
 8: ('space', 'Сосцевидное отверстие — вариабельный проход; классификация не подтверждает его наличие или постоянную шовную принадлежность.', 'mastoid'),
 10: ('volume', 'Коленце обозначает изгибающийся участок внутреннего лицевого канала с просветом; точка поворота и осевая линия не заменяют этот участок.', 'existing'),
 12: ('volume', 'Верхушка пирамиды — переднемедиальная костная область, содержащая апертуру; это не математическая вершина и не единственная крайняя точка.', 'apex'),
 14: ('space', 'Наружная апертура — вход в сонный канал; отдельно от костного края и всего внутрикостного хода.', 'inferior'),
 15: ('space', 'Внутренняя апертура — выход сонного канала у верхушки; старый поверхностный якорь не является центром просвета.', 'petrous'),
 20: ('volume', 'Перегородка между полуканалами — костная пластинка с толщиной; не один её свободный край и не оба полуканала.', 'existing'),
 21: ('area', 'Рассматривается передняя грань каменистой части, а не вся пирамида или средняя черепная ямка.', 'petrous'),
 22: ('volume', 'Крыша барабанной полости — костная пластинка, разделяющая полости; её нижняя поверхность не заменяет всю пластинку.', 'petrous'),
 23: ('volume', 'Дугообразное возвышение — костный рельеф; его объём не считается реконструкцией лежащего глубже полукружного канала.', 'petrous'),
 24: ('space', 'Расщелина здесь — выход канала большого каменистого нерва; отличается от продолжающей её поверхностной борозды.', 'petrous'),
 25: ('area', 'Собственная борозда большого каменистого нерва — костное ложе, не нерв и не внутренний канал.', 'existing'),
 26: ('space', 'Расщелина малого каменистого нерва обозначает выход; не смешивается с бороздой или вариабельным выходом нерва из черепа.', 'petrous'),
 27: ('area', 'Поверхностная борозда малого каменистого нерва имеет ширину ложа; одна линия хода не представляет всю борозду.', 'existing'),
 28: ('area', 'Тройничное вдавление — вдавленная костная поверхность; объём узла и полость Меккеля в эту запись не включаются.', 'petrous'),
 29: ('line', 'Верхний край — граница передней и задней граней; расположенная вдоль него борозда имеет отдельную запись.', 'petrous'),
 30: ('area', 'Борозда верхнего каменистого синуса — костное ложе вдоль края, не сам край или просвет синуса.', 'petrous'),
 31: ('area', 'Задняя грань пирамиды — протяжённая костная поверхность; одно внутреннее слуховое отверстие её не заменяет.', 'petrous'),
 32: ('space', 'Внутреннее слуховое отверстие — вход, отдельно от всего внутреннего слухового прохода и его дна.', 'petrous'),
 34: ('area', 'Поддуговая ямка в текущем взрослом определении — поверхностное углубление; продолжающий её канал не присоединяется к этой области автоматически.', 'petrous'),
 36: ('space', 'Апертура канальца преддверия — выходное отверстие; не эндолимфатический мешок и не весь каналец.', 'petrous'),
 37: ('line', 'Задний край разграничивает заднюю и нижнюю грани; его борозды и вырезки учитываются отдельными структурами.', 'existing'),
 39: ('area', 'Собственная яремная вырезка — участок выемки височной кости у края; не всё совместное яремное отверстие. Два каталожных кода не означают две вырезки.', 'existing'),
 40: ('area', 'Нижняя грань — костная поверхность основания с собственными отверстиями и ямками, не целая пирамида.', 'inferior'),
 41: ('area', 'Яремная ямка обозначает вогнутое костное ложе луковицы; оно не равно объёму луковицы или всему яремному отверстию.', 'inferior'),
 43: ('space', 'Апертура канальца улитки — наружное сообщение; отличается от канальца преддверия и всей протяжённости канальца улитки.', 'inferior'),
 45: ('area', 'Нижний каталожный вид той же яремной вырезки: проверяется костная выемка, не новый отдельный объект и не полное отверстие.', 'existing'),
 46: ('volume', 'Внутрияремный отросток — костный выступ края, не произвольная линия разделения всего отверстия.', 'existing'),
 47: ('volume', 'Шиловидный отросток — костный объём; его вершина и возможное окостенение связки не заменяют весь отросток.', 'inferior'),
 48: ('space', 'Шилососцевидное отверстие — выход лицевого канала; не весь лицевой канал и не точка между отростками.', 'inferior'),
 50: ('area', 'Каменистая ямочка — небольшое углублённое костное ложе; начинающийся здесь каналец является отдельной записью.', 'existing'),
 52: ('volume', 'Барабанная часть — изогнутая костная пластинка с несколькими поверхностями, не весь наружный слуховой проход.', 'tympanic'),
 53: ('volume', 'Барабанное кольцо в этой карточке костное и незамкнутое; его вещество не равно фиброзному кольцу перепонки или линии борозды.', 'ring'),
 54: ('space', 'Наружное слуховое отверстие — вход в костный проход; не весь проход и не наружное ухо.', 'tympanic'),
 56: ('volume', 'Большая барабанная ость — передний костный выступ кольца; отдельный от борозды и места фиксации мягкой ткани.', 'spines'),
 57: ('volume', 'Малая барабанная ость — задний костный выступ кольца; не точка и не синоним большой ости.', 'existing'),
 58: ('area', 'Барабанная борозда — узкое костное ложе прикрепления кольца перепонки; осевая линия не передаёт ширину ложа.', 'ring'),
 59: ('space', 'Барабанная вырезка — незамкнутый верхний промежуток костного кольца; не сама ненатянутая часть перепонки.', 'ring'),
 60: ('volume', 'Влагалище шиловидного отростка — костная пластинка барабанной части; не соединительнотканная оболочка и не сам отросток.', 'tympanic'),
 63: ('area', 'Теменная вырезка — собственная углублённая область края на стыке частей височной кости; не вся межкостная линия шва.', 'existing'),
}
SPHENOID = {
 52: ('area', 'Борозда крючка — костное ложе у поворота сухожилия; не само сухожилие, бурса или весь крючок.', 'hamulus'),
 54: ('volume', 'Крыловидно-остистый отросток — выступ латеральной пластинки; не весь окостеневший мостик, связка или образуемое ими отверстие.', 'process'),
}

def reviewed_decisions():
    rows = {('sphenoid', f'A02.1.05.{n:03d}'): dict(kind=k, reason=r, group=g)
            for n, (k, r, g) in SPHENOID.items()}
    rows.update({('temporal_'+side, f'A02.1.06.{n:03d}'): dict(kind=k, reason=r, group=g)
                 for side in ('right', 'left') for n, (k, r, g) in TEMPORAL.items()})
    return rows

def decision_sources(decision):
    group = decision['group']
    return {'petrous': (GRAY,GULYA), 'apex': (OXFORD,ISAACSON),
            'mastoid': (GRAY,OXFORD), 'inferior': (GRAY,GULYA),
            'tympanic': (GRAY,ISAACSON), 'ring': (GULYA,),
            'spines': (SPINE,), 'hamulus': (HAMULUS,),
            'process': (PROCESS,PLATE), 'existing': ()}[group]

def apply_record_review(record):
    decision = reviewed_decisions().get((record['b'], record['c']))
    if not decision: return
    assert record['geometryKind'] == decision['kind']
    record['geometryReview'] = dict(status='representation_reviewed', rationale=decision['reason'],
        source='research/stage5-skull-batch5-2026-10-16/geometry-kind-review.json',
        coordinateAcceptance=False, extentAcceptance=False)
    record['refs'].extend(deepcopy(list(decision_sources(decision))))
    record['modelNote'] += ' Проверен тип представления; координата, центр просвета, полный контур и поверхность этой модели отдельно не приняты.'
    if record['b'] == 'sphenoid':
        record['modelNote'] += ' Одиночная исходная точка не подтверждает обе стороны парного образования.'
