"""Addressed skull catalogue decisions. No coordinates or specimen geometry."""
from copy import deepcopy
from head_skull_final import record, ref
from head_skull_batch7 import GRAY
from head_skull_batch2 import GRAY_URL
from skull_shared_stage5 import _record

REPORT = 'research/stage5-skull-targeted-2026-10-17/decisions.json'
BUCHANAN_URL = "https://embryology.med.unsw.edu.au/embryology/index.php?title=Book_-_Buchanan%27s_Manual_of_Anatomy_including_Embryology_5"

def buchanan(key, locator):
    return ref('targeted_buchanan_'+key, "Frazer JE. Buchanan's Manual of Anatomy including Embryology, 6th ed. (1937)",
               BUCHANAN_URL, locator, 'frazer_buchanan_1937', access='full_text', scopeNote='Selected osteological definitions only; not specimen localization or historical prevalence.')

SOURCES = {group: [deepcopy(GRAY[group]), buchanan(group, section)] for group, section in [
    ('nasal', 'The Nasal Bones: two surfaces, four borders; medial ledges jointly form nasal crest.'),
    ('lacrimal', 'The Lacrimal Bones: paragraph describing all four borders, not the entire orbital wall.'),
    ('inferior_concha', 'The Inferior Nasal Conchse: two surfaces, two borders, anterior/posterior extremities; Fig.144.'),
    ('vomer', 'The Vomer: two lateral surfaces and four borders. Grooves and alae are separate features.'),
]}
NOTCH_SOURCES = [
    ref('targeted_notch_terms', 'Kitagawa N et al. The notch of the mandible: what do different fields call it? (2023)',
        'https://pmc.ncbi.nlm.nih.gov/articles/PMC10520864/', 'Introduction; Table 1. Synonyms for a variable inferior-border notch; not incisura mandibulae, no vascular-causation claim.',
        'kitagawa_2023', pmid='37106571', doi='10.5115/acb.23.022', access='full_text'),
    ref('targeted_notch_dry', 'Porwolik M et al. Typology of the antegonial notch in the human mandible (2015)',
        'https://pubmed.ncbi.nlm.nih.gov/26339819/', 'Official EFetch abstract: 251 mandibles, side-specific morphology. No sample proportions or coordinates transferred.',
        'porwolik_2015', pmid='26339819', doi='10.5603/FM.2015.0055', access='efetch_abstract'),
    ref('targeted_notch_ct', 'Tunis TS et al. Association of antegonial notch size with craniofacial morphology and masticatory muscle dimensions (2025)',
        'https://pmc.ncbi.nlm.nih.gov/articles/PMC12223038/', 'Abstract, Methods/Study sample and Limitations: 311 adult CTs, variable presence; unilateral measurements on right side. No bilateral symmetry inferred.',
        'tunis_2025', pmid='40603468', doi='10.1038/s41598-025-08800-x', access='full_text'),
]

# Explicit anatomical entities, not a name-based classifier. A border is its
# course, a surface its extent, an extremity includes bone thickness.
FACIAL = {
 'nasal': [
  ('surface_external','Наружная поверхность','area','Лицевая сторона носовой кости; отличается от её носовой стороны и от сосудистого отверстия.'),
  ('surface_internal','Внутренняя поверхность','area','Носовая сторона кости; борозда на ней не равна всей поверхности.'),
  ('border_superior','Верхний край','line','Край соединения носовой кости с лобной.'),
  ('border_inferior','Нижний край','line','Нижняя граница носовой кости; не весь хрящ наружного носа.'),
  ('border_lateral','Латеральный край','line','Край, соединяющийся с лобным отростком верхней челюсти.'),
  ('border_medial','Медиальный край','line','Край соединения с противоположной носовой костью. Задние выступы обоих краёв участвуют в одном общем гребне носовых костей.'),
 ],
 'lacrimal': [
  ('border_superior','Верхний край','line','Верхняя граница слёзной кости у лобной кости.'),
  ('border_inferior','Нижний край','line','Нижняя граница слёзной кости: её части соединяются с верхней челюстью и слёзным отростком нижней носовой раковины.'),
  ('border_anterior','Передний край','line','Передняя граница у лобного отростка верхней челюсти.'),
  ('border_posterior','Задний край','line','Задняя граница у глазничной пластинки решётчатой кости.'),
 ],
 'inferior_concha': [
  ('surface_medial','Медиальная поверхность','area','Поверхность, обращённая в носовую полость; не объём всей раковины.'),
  ('surface_lateral','Латеральная поверхность','area','Вогнутая поверхность, обращённая к латеральной стенке носовой полости.'),
  ('border_superior','Верхний край','line','Прикреплённый край; его отростки имеют самостоятельные карточки.'),
  ('border_inferior','Нижний край','line','Свободный нижний край раковины; требуется линия его протяжённости.'),
  ('end_anterior','Передний конец','volume','Передний костный конец раковины; конечная часть имеет толщину и не сводится к одной точке.'),
  ('end_posterior','Задний конец','volume','Задний суженный костный конец; точка вершины не определяет всю конечную часть.'),
 ],
 'vomer': [
  ('surface_right','Правая боковая поверхность','area','Правая сторона сошника; ход борозды на ней не задаёт всей поверхности.'),
  ('surface_left','Левая боковая поверхность','area','Левая сторона сошника; отклонение перегородки не меняет анатомическую сторону.'),
  ('border_superior','Верхний край','line','Верхний край с крыльями и бороздой для клиновидного клюва; не один из отдельных крыльев.'),
  ('border_inferior','Нижний край','line','Нижняя граница сошника у носовых гребней верхних челюстей и нёбных костей.'),
  ('border_anterior','Передний край','line','Передняя граница с участками соединения с перпендикулярной пластинкой решётчатой кости и хрящом перегородки.'),
  ('border_posterior','Задний край','line','Свободный задний край между хоанами; не весь объём сошника.'),
 ],
}

def additional_records():
    for group, definitions in FACIAL.items():
        for side in ([None] if group=='vomer' else ['right','left']):
            bone=group+('_'+side if side else '')
            for key,ru,kind,description in definitions:
                suffix={'right':' справа','left':' слева',None:''}[side]
                p=record('candidate_'+bone+'_'+key,bone,key,ru+suffix,kind,description,SOURCES[group],[],side)
                p['geometryReview']['source']=REPORT
                if group=='nasal' and key=='border_medial':p['relatedLandmarks']=['shared_skull_nasal_bone_crest']
                yield p
    for side,label in [('right','справа'),('left','слева')]:
        p=record('mandible_'+side+'_facial_artery_groove','mandible','antegonial_notch_'+side,
                 'Предугловая вырезка нижней челюсти '+label,'area',
                 'Вариабельная вогнутость нижнего края кпереди от области угла. В литературе также называется преджевательной вырезкой или бороздой лицевых сосудов. Не путать с вырезкой между отростками ветви; название не доказывает образование углубления артерией.',
                 NOTCH_SOURCES,['head_mandible_A02_1_15_034'],side)
        p['geometryReview']['source']=REPORT
        p['anatomicalVariation']=True
        p['modelNote']='Наличие и форма варианта на этом образце не подтверждены. Карточка справочная, без координат и без утверждения симметрии сторон.'
        yield p

KINDS = {
 15:('point','Краниометрический назион — определённая точка срединного соединения швов, а не весь шов.'),
 16:('point','Брегма — краниометрическая точка встречи венечного и сагиттального швов.'),
 17:('point','Ламбда — краниометрическая точка встречи сагиттального и ламбдовидного швов.'),
 19:('point','Птерион представлен как краниометрический ориентир соединения; вариабельная область и рисунок швов не сводятся к принятой координате.'),
 20:('point','Астерион — краниометрическая точка соединения швов; индивидуальная точка пока не назначена.'),
 23:('volume','Дуга — составная костная перемычка с толщиной, а не линия её проекции.'),
 47:('space','Щель — промежуток между каменистой частью и затылочной костью; не борозда синуса или только линия шва.'),
 55:('space','Костный промежуток рваного отверстия в живом теле занят фиброзно-хрящевой тканью; это не открытый пустой сосудистый канал.'),
 56:('volume','Костное нёбо — составная пластинка с толщиной; его ротовая поверхность является только одной стороной.'),
 67:('space','Глазница — полость, ограниченная стенками, а не весь объём участвующих костей.'),
 75:('area','Верхняя стенка здесь обозначает протяжённую границу глазничной полости; граница не задана одной точкой.'),
 76:('area','Нижняя стенка — протяжённое дно глазничной полости, не отдельное отверстие или точка.'),
 77:('area','Латеральная стенка — протяжённая граница глазницы; для неё нужна область костной поверхности.'),
 78:('area','Медиальная стенка — составная поверхность границы глазницы; её тонкие пластинки не локализованы одним якорем.'),
 79:('space','Передняя решётчатая апертура — отверстие в области лобно-решётчатого соединения, не весь ход канала.'),
 80:('space','Задняя решётчатая апертура — отдельное отверстие, не одноимённый сосуд и не вся стенка глазницы.'),
 84:('space','Нижняя глазничная щель — промежуток сообщения полостей, не линия проекции её края.'),
 97:('space','Клиновидно-нёбная апертура образована замыканием вырезки; она отличается от самой нёбной вырезки.'),
}

def review_shared(record):
    if record.get('geometryKind')!='unknown':return record
    number=int(record['c'].split('.')[-1]);kind,reason=KINDS[number]
    record['geometryKind']=kind;record['geometryKindReason']=reason
    record['geometryReview']=dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False)
    record['modelNote']+=' Тип представления проверен; координаты, полная граница и геометрия данного образца не приняты.'
    return record

def new_shared(terminology):
    refs=SOURCES['nasal']
    crest=_record('shared_skull_nasal_bone_crest',None,'','Гребень носовых костей',
        'Задние костные выступы медиальных краёв правой и левой носовых костей вместе образуют один гребень. Это не носовой гребень твёрдого нёба.',
        ['nasal_right','nasal_left'],None,'component','volume',refs,
        'Код TA98 не присвоен. Полная форма и положение гребня на этом образце не приняты; координат нет.')
    crest.pop('c',None);crest['t']='additional';crest['educationAvailable']=False
    crest['candidateIds']=['candidate_nasal_'+s+'_septal_crest_contribution' for s in ['right','left']]
    crest['partOf']='shared_skull_087'
    yield crest
    definitions=[
      (50,'Задняя черепная ямка','space',166,'The Posterior Fossa: full list includes sphenoid and mastoid angles of parietals.',
       'Regions / Posterior Fossa: limits and explicit bone list.',
       [('occipital','основная, латеральные и чешуйчатая части'),('sphenoid','спинка седла и клиновидный участок ската'),
        ('temporal_right','каменистая и сосцевидная части справа'),('temporal_left','каменистая и сосцевидная части слева'),
        ('parietal_right','сосцевидный угол справа'),('parietal_left','сосцевидный угол слева')],
       'Пространство задней черепной ямки с костными границами; перечень включает малые вклады, а не только затылочно-височное дно.'),
      (87,'Костная перегородка носа','volume',169,'Nasal cavities / medial wall: plates and supporting crests explicitly distinguished.',
       'Regions / Nasal Fossae: inner wall, osseous septum and its ten contributing bones.',
       [('ethmoid','перпендикулярная пластинка'),('vomer','основная костная пластинка сошника'),('sphenoid','клюв'),
        ('frontal','носовая ость'),('nasal_right','вклад в гребень носовых костей'),('nasal_left','вклад в гребень носовых костей'),
        ('maxilla_right','носовой гребень'),('maxilla_left','носовой гребень'),('palatine_right','носовой гребень'),('palatine_left','носовой гребень')],
       'Костная часть перегородки включает основные пластинки и опорные гребни. Хрящ перегородки в эту костную карточку не включён.'),
    ]
    for num,ru,kind,page,locator,blocator,parts,description in definitions:
        sources=[ref('targeted_gray_'+str(num),'Gray / Lewis. Anatomy of the Human Body (1918)',GRAY_URL+'#page='+str(page),locator,'gray_lewis_1918'),buchanan(str(num),blocator)]
        code='A02.1.00.'+str(num).zfill(3)
        p=_record('shared_skull_'+str(num).zfill(3),code,terminology[code],ru,description,
                  [b for b,_ in parts],None,'boundaryContribution' if num==50 else 'component',kind,sources,
                  'Состав костных вкладов подтверждён; отдельные участки, полный контур и геометрия конкретного образца ещё не приняты. Координаты не созданы.')
        for relation,(_,detail) in zip(p['relations'],parts):relation['contribution']=detail
        p['geometryReview']=dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False)
        yield p
