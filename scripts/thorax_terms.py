"""TA98 catalogue of the thoracic skeleton; editorial per-bone applicability.

No coordinates or complete-mesh claims. Russian nomenclature was checked in
Kolesnikov (2003), printed pp.19–22. Source illustrations are linked, not copied.
"""
from pathlib import Path
import json
from copy import deepcopy
import neck_terms as neck

ref = neck.ref
IFAA_URL = 'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH851%20A2F%20EN.htm'
GRAY_URL = neck.GRAY_URL
AS_BASE = 'https://www.anatomystandard.com/ossa-et-juncturae/'
GRAY_T = ref('Gray (1918) — Thoracic Vertebrae',GRAY_URL+'#page=33','PDF с.33–35; общие признаки; First, Ninth, Tenth, Eleventh, Twelfth Thoracic Vertebra.')
GRAY_R = ref('Gray (1918) — The Ribs',GRAY_URL+'#page=66','PDF с.66–73; General Characteristics; Head; Neck; Body; Peculiar Ribs.')
GRAY_S = ref('Gray (1918) — The Sternum',GRAY_URL+'#page=60','PDF с.60–64; Manubrium, Borders, Body, Xiphoid process, Ossification.')
GRAY_W = ref('Gray (1918) — The Thorax',GRAY_URL+'#page=56','PDF с.56–58; Boundaries; upper and lower openings.')
GRAY_C = ref('Gray (1918) — The Costal Cartilages',GRAY_URL+'#page=73','PDF с.73–74, Costal Cartilages, Extremities.')
AS_T = ref('Anatomy Standard — Typical Thoracic Vertebra',AS_BASE+'columna-vertebralis/vertebra-thoracica-typica.html','T4 superior; T5 frontal, lateral, superior and inferior oblique views; T5–T6 foramen.')
AS_AT = ref('Anatomy Standard — Atypical Thoracic Vertebrae',AS_BASE+'columna-vertebralis/vertebrae-thoracicae-atypicae.html','T1 frontal/lateral: complete costal facet; T8–L1 lateral and oblique: complete facets T10–T12 and absence of transverse costal facets T11–T12. The illustrated T9 is one variant, not an invariant rule.')
AS_R = ref('Anatomy Standard — Ribs',AS_BASE+'thorax/costae.html','Typical seventh rib, posterior view; first and second rib superior view; XI and XII dorsal view.')
AS_S = ref('Anatomy Standard — Sternum',AS_BASE+'thorax/sternum.html','Frontal and anterior oblique aspects, labeled manubrium/body/xiphoid/notches.')
AS_W = ref('Anatomy Standard — Thoracic Cage',AS_BASE+'thorax/cavea-thoracis.html','Anterior, superior aperture and inferior aperture views; costal margin; pulmonary sulcus.')
OPEN_CAGE = ref('OpenStax — The Thoracic Cage','https://openstax.org/books/anatomy-and-physiology-2e/pages/7-4-the-thoracic-cage','Sternum; Parts of a Typical Rib; Rib Classifications; Figure 7.32.')
OPEN_SPINE = ref('OpenStax — The Vertebral Column',neck.OPENSTAX_URL,'Vertebral Structure; Thoracic Vertebrae; Vertebral Column Curvatures; Intervertebral Discs.')
BUCHANAN = ref('Buchanan — Manual of Anatomy, The Thorax','https://embryology.med.unsw.edu.au/embryology/index.php?title=Book_-_Buchanan%27s_Manual_of_Anatomy_including_Embryology_4','The Tenth Rib: alternative head facets depending on inferior facet of T9; tubercular facet may be absent. The Eleventh and Twelfth Ribs.')
RIB_VARIATION = ref('Silva et al. (2020) — Anatomical variations of the ribs','https://pmc.ncbi.nlm.nih.gov/articles/PMC7720665/','CERVICAL RIB; LUMBAR RIB; own MDCT illustrations. Classification sentence contains swapped false/floating labels and is not used.')
MUNI = ref('Masaryk University — Osteology, ribs','https://is.muni.cz/el/1411/podzim2012/VSAN0131s/35483703/list_of_terms_2.pdf','Ribs — Body of rib: crista costae is listed separately from head and neck crests. General classification/last-rib shorthand is not used.')
MUNI_PHOTOS = ref('Masaryk University — OsteoWeb, anatomical structures','https://is.muni.cz/do/rect/el/estud/prif/2025/osteoweb/web/pages/03_01_abecedni_seznam.html','Alphabetical photo index: Crista costae; Crista costae undecimae; Crista costae duodecimae.')
COSTAL_PATEL = dict(ref('Patel A et al. (2023) — Anatomy of the anterior ribs and the composition of the costal margin: A cadaver study.',
    'https://pubmed.ncbi.nlm.nih.gov/37982795/', 'Abstract Methods/Results/Conclusion: 30 cadavers, variable cartilaginous attachments; frequencies are not transferred to this model.'),
    id='costal_patel_2023', pmid='37982795', doi='10.1097/TA.0000000000004115', access='abstract', authorGroup='patel_2023')
COSTAL_RISK = dict(ref('Risk N et al. (2026) — Anatomic variability of the ribs and costal cartilage: A pilot study.',
    'https://pubmed.ncbi.nlm.nih.gov/42545742/', 'Abstract Methods/Results: CT of 278 patients; variability and side differences. Different data/method from Patel; overlapping research group, not an independent team.'),
    id='costal_risk_2026', pmid='42545742', doi='10.1097/TA.0000000000005147', access='abstract', authorGroup='risk_2026')

T = {c:row for c,row in neck.T.items() if c.startswith('A02.2.01.') or c in ('A02.2.00.001','A02.2.00.009')}
def add(prefix, rows):
    for number, lat, ru in rows:
        T[f'A{prefix}.{number:03}'] = (lat,ru,'')
add('02.2.00',[(2,'curvatura primaria','Первичный изгиб'),(3,'kyphosis thoracica','Грудной кифоз')])
add('02.2.03',[
 (1,'vertebrae thoracicae [T I - T XII]','Грудные позвонки [T I–T XII]'),
 (2,'fovea costalis superior','Верхняя реберная ямка'),(3,'fovea costalis inferior','Нижняя реберная ямка'),
 (4,'fovea costalis processus transversi','Реберная ямка поперечного отростка'),
 (5,'uncus corporis vertebrae thoracicae primae; processus uncinatus vertebrae thoracicae primae','Крючок тела первого грудного позвонка; крючковидный отросток первого грудного позвонка')])
add('02.3.00',[(1,'skeleton thoracis','Скелет грудной клетки')])
add('02.3.01',[(1,'costae [I - XII]','Ребра [I–XII]'),(2,'costae verae [I - VII]','Истинные ребра [I–VII]'),(3,'costae spuriae [VIII - XII]','Ложные ребра [VIII–XII]'),(4,'costae fluctuantes [XI - XII]','Колеблющиеся ребра [XI–XII]'),(5,'cartilago costalis','Реберный хрящ')])
add('02.3.02',[
 (1,'costa','Ребро'),(2,'caput costae','Головка ребра'),(3,'facies articularis capitis costae','Суставная поверхность головки ребра'),
 (4,'crista capitis costae','Гребень головки ребра'),(5,'collum costae','Шейка ребра'),(6,'crista colli costae','Гребень шейки ребра'),
 (7,'corpus costae','Тело ребра'),(8,'tuberculum costae','Бугорок ребра'),(9,'facies articularis tuberculi costae','Суставная поверхность бугорка ребра'),
 (10,'angulus costae','Угол ребра'),(11,'sulcus costae','Борозда ребра'),(12,'crista costae','Гребень ребра'),
 (13,'costa cervicalis; costa colli','Шейное ребро'),(14,'costa prima [I]','Первое [I] ребро'),
 (15,'tuberculum musculi scaleni anterioris','Бугорок передней лестничной мышцы'),(16,'sulcus arteriae subclaviae','Борозда подключичной артерии'),(17,'sulcus venae subclaviae','Борозда подключичной вены'),
 (18,'costa secunda [II]','Второе [II] ребро'),(19,'tuberositas musculi serrati anterioris','Бугристость передней зубчатой мышцы'),(20,'costa lumbalis','Поясничное ребро')])
add('02.3.03',[(1,'sternum','Грудина'),(2,'manubrium sterni','Рукоятка грудины'),(3,'incisura clavicularis','Ключичная вырезка'),(4,'incisura jugularis','Яремная вырезка'),(5,'angulus sterni','Угол грудины'),(6,'corpus sterni','Тело грудины'),(7,'processus xiphoideus','Мечевидный отросток'),(8,'incisurae costales','Реберные вырезки'),(9,'ossa suprasternalia','Надгрудинные кости')])
add('02.3.04',[(1,'cavea thoracis','Грудная клетка'),(2,'cavitas thoracis','Грудная полость'),(3,'apertura thoracis superior','Верхняя апертура грудной клетки'),(4,'apertura thoracis inferior','Нижняя апертура грудной клетки'),(5,'sulcus pulmonalis','Легочная борозда'),(6,'arcus costalis','Реберная дуга'),(7,'spatium intercostale','Межреберье'),(8,'angulus infrasternalis','Подгрудинный угол')])
TA_PAREN = ['A02.3.02.013','A02.3.02.020','A02.3.03.009']
for c in TA_PAREN:
    lat,ru,_ = T[c]
    T[c] = (lat,ru,'ta_parentheses')
PRINTED_RECONCILIATIONS = [
 dict(tid='852',rawCode='A02.3.02.001',code='A02.3.01.001',rawLatin='costae [I - XII]',latin='costae [I - XII]',reason='Электронная строка TAH852 дублирует код costa (TAH857). Печатный TA98 и Колесников 2003 с.21: A02.3.01.001.'),
 dict(tid='887',rawCode='A02.3.04.002',code='A02.3.04.002',rawLatin='cavitas thoracis; cavitas thoracica',latin='cavitas thoracis',reason='В печатной TA98 и Колесникове 2003 с.22 отсутствует добавленный электронный синоним cavitas thoracica.')]

GENERAL_CODES = list(neck.GENERAL_CODES)
BONE_CODES = {}
for i in range(1,13):
    BONE_CODES[f'thoracic_{i}'] = GENERAL_CODES + ['A02.2.03.002'] + (['A02.2.03.003'] if i<=9 else []) + (['A02.2.03.004'] if i<=10 else []) + (['A02.2.03.005'] if i==1 else [])
for i in range(1,13):
    numbers = list(range(2,13))
    if i==1: numbers = [2,3,5,7,8,9,15,16,17]
    if i==2: numbers += [19]
    if i==11: numbers = [2,3,7,10,11,12]
    if i==12: numbers = [2,3,7,12]
    for side in ('right','left'):
        BONE_CODES[f'rib_{i}_{side}'] = [f'A02.3.02.{n:03}' for n in numbers]
BONE_CODES['sternum'] = [f'A02.3.03.{i:03}' for i in range(2,10)]

DESCRIPTIONS = {}
def desc(code, text, refs, **extra):
    DESCRIPTIONS[code] = dict(x=text,refs=refs,scope='anatomy',**extra)
for c in T:
    if c in neck.DESCRIPTIONS:
        DESCRIPTIONS[c] = deepcopy(neck.DESCRIPTIONS[c])
        if c.startswith('A02.2.01.'):
            DESCRIPTIONS[c]['refs'] = [neck.GRAY_GENERAL,OPEN_SPINE]
desc('A02.2.01.001','Кость позвоночного столба.',[neck.GRAY_GENERAL,OPEN_SPINE])
desc('A02.2.01.004','Кольцевая краевая область тела позвонка.',[ref('Gray (1918) — Ossification of Vertebrae',GRAY_URL+'#page=46','PDF с.46, Ossification; Fig.103 на с.47: вторичные центры верхней и нижней поверхностей тела.'),AS_T],note='Граница и стадия сращения анулярного эпифиза отдельно не подтверждаются внешней сеткой взрослого позвонка.')
desc('A02.2.00.002','Первичная кривизна; к ней относится грудной изгиб.',[ref('Gray (1918) — Vertebral Curves',GRAY_URL+'#page=52','Curves: thoracic and pelvic curves termed primary.'),OPEN_SPINE])
desc('A02.2.00.003','Изгиб грудного отдела выпуклостью назад.',[ref('Gray (1918) — Vertebral Curves',GRAY_URL+'#page=52','Curves: thoracic curve concave forward.'),OPEN_SPINE])
desc('A02.2.03.002','Реберная суставная площадка у верхней части тела, рядом с ножкой дуги.',[GRAY_T,AS_T],note='Для T1 и нижних грудных позвонков нужны уровневые уточнения: ямка может быть целой, а не полуямкой.')
desc('A02.2.03.003','Реберная суставная площадка у нижнего края тела.',[GRAY_T,AS_T])
desc('A02.2.03.004','Суставная площадка поперечного отростка для бугорка ребра.',[GRAY_T,AS_T])
desc('A02.2.03.005','Возвышенный боковой край верхней поверхности тела T1.',[GRAY_T,neck.UNCUS2],note='Публикация Güvençer et al.: Introduction упоминает T1; её измерения C3–C7 не переносятся на T1.')
_ribs = {2:'Задний конец ребра, несущий суставную поверхность.',3:'Суставная поверхность головки, обращённая к позвонку.',4:'Гребень между двумя суставными участками головки.',5:'Суженная часть между головкой и областью бугорка.',6:'Выступающий верхний край шейки.',7:'Основная протяжённая часть ребра.',8:'Выступ у перехода шейки в тело.',9:'Суставная площадка бугорка для поперечного отростка позвонка.',10:'Область выраженного изгиба тела ребра.',11:'Продольное углубление у нижнего края внутренней поверхности.',15:'Выступ на верхней поверхности I ребра для передней лестничной мышцы.',16:'Борозда на верхней поверхности I ребра позади лестничного бугорка.',17:'Борозда на верхней поверхности I ребра впереди лестничного бугорка.',19:'Шероховатая область верхненаружной поверхности II ребра для передней зубчатой мышцы.'}
for i,text in _ribs.items(): desc(f'A02.3.02.{i:03}',text,[GRAY_R,AS_R])
desc('A02.3.02.012','Гребень тела ребра; отдельный термин, не равнозначный гребню головки или шейки.',[ref('IFAA TA98 — Crista costae',IFAA_URL,'A02.3.02.012; отдельная строка под corpus costae.',),MUNI],note='Номенклатура и учебный список подтверждают термин и принадлежность к телу. Два независимых описания точной топографии пока не согласованы; координата и протяжённость не заявляются.',evidenceScope='nomenclature_and_body_region_only',anatomyVerification='incomplete',additionalRefs=[MUNI_PHOTOS])
_sternum = {2:'Верхняя широкая часть грудины.',3:'Парная вырезка у верхнебокового края рукоятки.',4:'Срединная вырезка верхнего края рукоятки.',5:'Угол у соединения рукоятки и тела грудины.',6:'Средняя удлинённая часть грудины.',7:'Нижняя часть грудины.',8:'Участки боковых краёв грудины для реберных хрящей.'}
for i,text in _sternum.items(): desc(f'A02.3.03.{i:03}',text,[GRAY_S,OPEN_CAGE if i==5 else AS_S])
desc('A02.3.03.009','Непостоянные небольшие кости у верхнего края рукоятки.',[ref('Duraikannu et al. (2016) — MDCT evaluation of sternal variations','https://pmc.ncbi.nlm.nih.gov/articles/PMC4931775/','Suprasternal or episternal ossicle; Fig.4A–B.'),ref('Assessing Sternal Dimensions for Sex Classification (2025)','https://pmc.ncbi.nlm.nih.gov/articles/PMC12248529/','Results: suprasternal bones/ossicles among observed sternal variants; Discussion.')],inc=1,note='Вариант описан отдельно; его наличие в исходной грудине не заявлено.')
desc('A02.3.01.005','Хрящевая часть, продолжающая ребро вперёд.',[GRAY_C,OPEN_CAGE])
desc('A02.3.00.001','Костно-хрящевой каркас грудной клетки.',[GRAY_W,OPEN_CAGE])
desc('A02.3.01.001','Двенадцать пар ребер типичного скелета.',[GRAY_R,OPEN_CAGE])
desc('A02.3.01.002','В типовой учебной схеме рёбра I–VII соединяются с грудиной своими хрящами. Индивидуальные варианты числа прямых соединений проверяются отдельно; схема не подтверждает этот образец.',[GRAY_C,OPEN_CAGE,COSTAL_PATEL,COSTAL_RISK])
desc('A02.3.01.003','В типовой учебной схеме рёбра VIII–XII не имеют прямого соединения с грудиной. У нижних хрящей описаны варианты соединений и свободных концов; их наличие в этой модели не установлено.',[GRAY_C,OPEN_CAGE,COSTAL_PATEL,COSTAL_RISK],note='В TA98 XI–XII входят в ложные ребра и дополнительно названы колеблющимися.')
desc('A02.3.01.004','Ребра XI–XII с передними концами, не соединёнными с грудиной.',[GRAY_C,OPEN_CAGE])
_whole = {1:'Грудная клетка как целое: грудина, ребра с хрящами и грудной отдел позвоночного столба.',2:'Пространство внутри грудной клетки.',3:'Верхнее отверстие грудной клетки между T1, первыми ребрами и верхним краем рукоятки.',4:'Нижнее отверстие грудной клетки, ограниченное T12, нижними ребрами и реберными дугами спереди.',5:'Парное углубление грудной полости по бокам тел грудных позвонков.',6:'Дугообразный нижний передний край, образованный соединениями реберных хрящей.',7:'Промежуток между соседними ребрами.',8:'Угол между правой и левой реберными дугами под грудиной.'}
for i,text in _whole.items(): desc(f'A02.3.04.{i:03}',text,[GRAY_W,AS_W])
DESCRIPTIONS['A02.3.04.006']['x'] += ' Обычно описываются хрящи VII–X, но фактический состав и соединения вариабельны; типовая схема не задаёт контур данного образца.'
DESCRIPTIONS['A02.3.04.006']['refs'] += [COSTAL_PATEL,COSTAL_RISK]
desc('A02.3.02.013','Добавочное ребро шейного отдела позвоночника.',[ref('Gray (1918) — Cervical Ribs',GRAY_URL+'#page=74','Cervical ribs derived from the seventh cervical vertebra; anatomical variation.'),RIB_VARIATION],inc=1,note='Номенклатурный вариант; модель такого образца в текущий раздел не включена.')
desc('A02.3.02.020','Добавочное ребро поясничного отдела позвоночника.',[ref('Naidoo et al. (2017) — Supernumerary lumbar ribs','https://pmc.ncbi.nlm.nih.gov/articles/PMC5509900/','Case report: lumbar ribs in an adult skeleton.'),ref('Park et al. (2016) — Thoracolumbar junction','https://pmc.ncbi.nlm.nih.gov/articles/PMC5124870/','Definitions and CT examples of thoracolumbar variants; Discussion: lumbar rib vs accessory ossification centre.')],inc=1,note='Для разграничения поясничного ребра и несросшегося реберного отростка нужны критерии и целая последовательность позвонков; конкретный вариант здесь не моделируется.')

DESCRIPTION_OVERRIDES = {}
DESCRIPTION_OVERRIDES[('thoracic_1','A02.2.03.002')] = dict(x='Обычно целая суставная ямка для головки I ребра.',refs=[GRAY_T,AS_AT],note='Описана типичная конфигурация, не универсальная форма каждого человека.')
DESCRIPTION_OVERRIDES[('thoracic_9','A02.2.03.003')] = dict(x='Нижняя реберная ямка T9 может отсутствовать.',refs=[GRAY_T,BUCHANAN],inc=1,note='Её наличие связано с вариантом сочленения головки X ребра; в данном образце проверяется отдельно.')
for i in (10,11,12):
    DESCRIPTION_OVERRIDES[(f'thoracic_{i}','A02.2.03.002')] = dict(x=f'Суставная ямка T{i} для головки соответствующего ребра; региональное название не означает обязательную полуямку.',refs=[GRAY_T,AS_AT],note='У нижних грудных позвонков описывается целая реберная ямка, распространяющаяся на область ножки. У T10 возможна полуямка при сочленении X ребра также с T9; различие не восстанавливается по названию.',noteRefs=[GRAY_T,BUCHANAN])
DESCRIPTION_OVERRIDES[('thoracic_10','A02.2.03.004')] = dict(x='Суставная площадка поперечного отростка T10 для бугорка X ребра, если она выражена.',refs=[GRAY_T,BUCHANAN],note='Сочленение с бугорком на этом уровне вариабельно; наличие площадки должно быть проверено на исходной сетке.')
for side in ('right','left'):
    DESCRIPTION_OVERRIDES[(f'rib_10_{side}','A02.3.02.004')] = dict(x='Гребень головки X ребра при наличии двух суставных участков.',refs=[GRAY_R,BUCHANAN],inc=1,note='Gray описывает одну площадку; Buchanan прямо различает варианты с одной и двумя в зависимости от T9. Общий список не подтверждает гребень в данном экземпляре.')
    DESCRIPTION_OVERRIDES[(f'rib_11_{side}','A02.3.02.010')] = dict(x='Обычно слабый изгиб XI ребра.',refs=[GRAY_R,BUCHANAN])
    DESCRIPTION_OVERRIDES[(f'rib_11_{side}','A02.3.02.011')] = dict(x='Обычно неглубокая борозда XI ребра.',refs=[GRAY_R,BUCHANAN])

APPLICABILITY_NOTE = 'TA98 содержит общие и региональные списки. Применение общих терминов к отдельным ребрам и позвонкам составлено редакционно по анатомическим источникам. Эти количества не являются отдельными официальными счётчиками IFAA и не подтверждают детали моделей.'
APPLICATION_NOTES = {}
for i in range(1,13):
    APPLICATION_NOTES[f'thoracic_{i}'] = 'Общие образования позвонка и применимые реберные ямки; межпозвоночное отверстие относится к нескольким структурам и вынесено в общий каталог.'
APPLICATION_NOTES['thoracic_1'] += ' Верхняя реберная ямка целая; крючок тела имеет специальный код TA98.'
APPLICATION_NOTES['thoracic_9'] += ' Нижняя реберная ямка вариабельна.'
APPLICATION_NOTES['thoracic_10'] += ' Нижняя реберная ямка не добавлена. Ямка тела и суставная площадка поперечного отростка вариабельны.'
for i in (11,12): APPLICATION_NOTES[f'thoracic_{i}'] += ' Нижняя реберная ямка и реберная ямка поперечного отростка не добавлены; целая ямка для головки ребра подписана региональным термином с пояснением.'
for i in range(1,13):
    text='Общие образования ребра применены с учётом уровня; правая и левая стороны проверяются независимо.'
    if i==1: text+=' Для I ребра не добавлены гребни головки и шейки, отдельный угол и реберная борозда типичного ребра; включены собственные борозды и лестничный бугорок.'
    if i==2: text+=' Дополнительно включена бугристость передней зубчатой мышцы.'
    if i==10: text+=' Гребень головки зависит от варианта сочленения с T9–T10; включён с объяснением, не как гарантированная деталь.'
    if i in (11,12): text+=' Шейка, её гребень, гребень головки, бугорок и его суставная площадка не добавлены.'
    if i==11: text+=' Угол и борозда обычно слабо выражены.'
    if i==12: text+=' Отдельный угол и борозда не добавлены.'
    for side in ('right','left'): APPLICATION_NOTES[f'rib_{i}_{side}']=text
APPLICATION_NOTES['sternum']='Одна грудина, состоящая из рукоятки, тела и мечевидного отростка. Надгрудинные кости — отдельный вариант, а не обязательная часть исходной модели.'

BONES={}
for i in range(1,13):
    b=f'thoracic_{i}'
    BONES[b]=dict(ru=f'Грудной позвонок T{i}',lat=T['A02.2.03.001'][0],code='A02.2.03.001',level=f'T{i}',x=f'T{i} — один из двенадцати грудных позвонков; имеет тело, дугу и отростки.',refs=[GRAY_T,OPEN_SPINE],note=APPLICATION_NOTES[b],termNote='Код и латынь относятся к группе TA98; номер обозначает экземпляр, не отдельную строку номенклатуры.')
for i in range(1,13):
    for side,ru_side in [('right','правое'),('left','левое')]:
        b=f'rib_{i}_{side}'; c='A02.3.02.014' if i==1 else 'A02.3.02.018' if i==2 else 'A02.3.02.001'
        BONES[b]=dict(ru=f'{i}-е ребро, {ru_side}',lat=T[c][0],code=c,level=str(i),side=side,x=f'Ребро {i} на '+('правой' if side=='right' else 'левой')+' стороне грудной клетки.',refs=[GRAY_R,AS_R],note=APPLICATION_NOTES[b],termNote='Сторона и номер экземпляра отделены от термина TA98.')
BONES['sternum']=dict(ru='Грудина',lat='sternum',code='A02.3.03.001',x='Передняя срединная кость грудной клетки: рукоятка, тело и мечевидный отросток.',refs=[GRAY_S,AS_S],note=APPLICATION_NOTES['sternum'])
for b,data in BONES.items():
    DESCRIPTIONS.setdefault(data['code'],dict(x=data['x'],refs=data['refs'],scope='anatomy'))
WHOLE_TERMS = ['A02.2.00.001','A02.2.00.002','A02.2.00.003','A02.2.00.009','A02.2.01.008','A02.3.00.001']+[f'A02.3.01.{i:03}' for i in range(1,6)]+[f'A02.3.04.{i:03}' for i in range(1,9)]+['A02.3.02.013','A02.3.02.020']

THORAX_SOFT = {
 'cartilage':dict(ru='Реберные хрящи',lat='cartilago costalis',code='A02.3.01.005',**DESCRIPTIONS['A02.3.01.005'],note='В грудной сборке показаны только частичные агрегаты BP24/BP28; отдельные хрящи I–VII не включены. Семь правых производных мешей доступны в другом ресурсе проекта, но не заменяют оригинальные исходники и принятую разметку. Полные хрящевые границы, уровни и левая сторона требуют отдельной проверки.')}

def description_for(bone,code):
    return {**DESCRIPTIONS[code],**DESCRIPTION_OVERRIDES.get((bone,code),{})}

def export_evidence(path):
    result=dict(version=1,reviewed='2026-10-13',scope='Костный каталог груди: 12 грудных позвонков, 24 ребра, грудина; общие образования и варианты. Без координат и утверждений о полной геометрии.',catalogueIsOfficialPerBoneCount=False,geometryVerified=False,applicabilityNote=APPLICABILITY_NOTE,applicationNotes=APPLICATION_NOTES,
      nomenclature=[ref('IFAA TA98 — Skeleton thoracis',IFAA_URL,'A02.3; электронная таблица сохранена без исправления ошибок.'),ref('IFAA TA98 — Columna vertebralis',neck.IFAA_URL,'A02.2.00–01, A02.2.03.'),dict(title='Международная анатомическая терминология, ред. Л. Л. Колесников, 2003',locator='Печатные с.19–22; исследовательская копия, не публикуется.')],printedReconciliations=PRINTED_RECONCILIATIONS,
      terms={c:dict(lat=v[0],ru=v[1],flag=v[2],taParen=c in TA_PAREN) for c,v in T.items()},bones={b:{**v,'codes':BONE_CODES[b],'entries':{c:description_for(b,c) for c in BONE_CODES[b]}} for b,v in BONES.items()},wholeTerms={c:DESCRIPTIONS[c] for c in WHOLE_TERMS},contextTypes=THORAX_SOFT,
      limits=['Списки являются редакционным применением TA98 к отдельным костям.','Нет проверки координат, формы, протяжённости или обеих сторон парного образования.','Crista costae: подтверждены термин и принадлежность телу, но точные границы на сетке не установлены.','Варианты не объявляются присутствующими в исходных сетках.','Грудная полость и апертуры — составные образования, не принадлежащие одной кости.','Сосуды, нервы, органы, суставы и связки не входят в эту приёмку.'])
    Path(path).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':
    export_evidence(Path(__file__).resolve().parents[1]/'research/thorax-bone-evidence.json')
    print('Thorax terms:',len(T),'bones:',len(BONES),'catalogue entries:',sum(map(len,BONE_CODES.values())),'whole terms:',len(WHOLE_TERMS))
