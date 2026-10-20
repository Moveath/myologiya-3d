"""TA98 neck bone vocabulary and explicit, editorial per-bone applicability.

TA98 gives general vertebral and regional lists, not a separate mandatory count
for each cervical vertebra. BONE_CODES is the project's applicability catalogue,
not a claim that IFAA published those per-bone counts. No coordinates are inferred.
Russian terms: Kolesnikov 2003, printed pp.19–20 (local source read).
"""
from pathlib import Path
import json

IFAA_URL = 'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/TA98/LAEN/TAH769%20A2F%20EN.htm'
HYOID_URL = 'https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/TA98%20EN/02.1.16%20TA98%20EN.htm'
GRAY_URL = 'https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf'
OPENSTAX_URL = 'https://openstax.org/books/anatomy-and-physiology-2e/pages/7-3-the-vertebral-column'
AS_BASE = 'https://www.anatomystandard.com/ossa-et-juncturae/columna-vertebralis/'

def ref(title, url, locator):
    return dict(title=title, url=url, locator=locator)

GRAY_GENERAL = ref('Gray (1918) — General Characteristics of a Vertebra', GRAY_URL+'#page=25', 'PDF с.25–26, Body; Pedicles; Laminae; Processes.')
GRAY_CERVICAL = ref('Gray (1918) — The Cervical Vertebrae', GRAY_URL+'#page=27', 'PDF с.27–32: типичные позвонки; First Cervical Vertebra; Second Cervical Vertebra; Seventh Cervical Vertebra.')
GRAY_HYOID = ref('Gray (1918) — The Hyoid Bone', GRAY_URL+'#page=148', 'PDF с.148–149: Body; Greater Cornua; Lesser Cornua.')
OPENSTAX = ref('OpenStax — The Vertebral Column', OPENSTAX_URL, 'Vertebral Structure; Regional Modifications of Vertebrae — Cervical Vertebrae; Fig.7.24–7.25.')
AS_ATLAS = ref('Anatomy Standard — Atlas', AS_BASE+'atlas.html', 'Anterior, top, inferior, superolateral aspects: подписанные виды атланта.')
AS_AXIS = ref('Anatomy Standard — Axis', AS_BASE+'axis.html', 'Anterior, superior, lateral, isometric aspects: зуб и суставные поверхности.')
AS_TYPICAL = ref('Anatomy Standard — Typical Cervical Vertebra', AS_BASE+'vertebra-cervicalis-typica.html', 'C3 anterior/isometric; C4 top; C6 frontal aspect, tuberculum caroticum.')
AS_C7 = ref('Anatomy Standard — C7', AS_BASE+'c7.html', 'Lateral and superior aspects: processus spinosus, sulcus nervi spinalis, foramen transversarium.')
AS_HYOID = ref('Anatomy Standard — Os hyoideum', 'https://www.anatomystandard.com/ossa-et-juncturae/cranium/os-hyoideum.html', 'Anterior and posterior aspects: corpus, cornua majora et minora.')
UNCUS1 = ref('Raveendranath et al. (2019) — Morphometry of C3–7', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6944996/', 'Methods, Uncinate Process; Fig.1–2; Table 1, C3–C7.')
UNCUS2 = ref('Güvençer et al. (2016) — Morphometric evaluation of the uncinate process', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5075958/', 'Introduction; Methods; direct cadaveric and CT measurements at C3–C7.')
RING1 = ref('Radiographic morphology of normal ring apophyses in the immature cervical spine (2018)', 'https://pubmed.ncbi.nlm.nih.gov/29497774/', 'Abstract: Background, Results and Conclusions; возрастная изменчивость и сращение.')
RING2 = ref('Uys et al. (2019) — Cervical vertebral ring apophysis ossification', 'https://pubmed.ncbi.nlm.nih.gov/31402420/', 'Abstract: anterior inferior ring apophysis development, C2–C4; исследование окостенения.')
PONTICLE = ref('Ponticulus posticus of atlas vertebrae (2017)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5623291/', 'Description: complete and partial bony bridges over the vertebral artery groove.')

T = {}
def add(prefix, rows):
    for number, lat, ru in rows:
        T[f'A{prefix}.{number:03}'] = (lat, ru, '')

add('02.1.16', [(1,'os hyoideum','Подъязычная кость'),(2,'corpus ossis hyoidei','Тело подъязычной кости'),(3,'cornu minus','Малый рог'),(4,'cornu majus','Большой рог')])
add('02.2.01', [
 (1,'vertebra','Позвонок'), (2,'corpus vertebrae','Тело позвонка'),
 (3,'facies intervertebralis','Межпозвоночная поверхность'),(4,'epiphysis anularis','Анулярный эпифиз'),
 (5,'arcus vertebrae','Дуга позвонка'),(6,'pediculus arcus vertebrae','Ножка дуги позвонка'),
 (7,'lamina arcus vertebrae','Пластинка дуги позвонка'),(8,'foramen intervertebrale','Межпозвоночное отверстие'),
 (9,'incisura vertebralis superior','Верхняя позвоночная вырезка'),(10,'incisura vertebralis inferior','Нижняя позвоночная вырезка'),
 (11,'foramen vertebrale','Позвоночное отверстие'),(12,'processus spinosus','Остистый отросток'),
 (13,'processus transversus','Поперечный отросток'),
 (14,'processus articularis superior; zygapophysis superior','Верхний суставной отросток'),
 (15,'facies articularis superior','Верхняя суставная поверхность'),
 (16,'processus articularis inferior; zygapophysis inferior','Нижний суставной отросток'),
 (17,'facies articularis inferior','Нижняя суставная поверхность')])
add('02.2.02', [
 (1,'vertebrae cervicales [C I - C VII]','Шейные позвонки [C I–C VII]'),
 (2,'uncus corporis; processus uncinatus','Крючок тела; крючковидный отросток'),
 (3,'foramen transversarium','Поперечное отверстие'),(4,'tuberculum anterius','Передний бугорок'),
 (5,'tuberculum caroticum','Сонный бугорок'),(6,'tuberculum posterius','Задний бугорок'),
 (7,'sulcus nervi spinalis','Борозда спинномозгового нерва'),
 (101,'atlas [C I]','Атлант [C I]'),(102,'massa lateralis atlantis','Латеральная масса'),
 (103,'facies articularis superior','Верхняя суставная поверхность'),
 (104,'facies articularis inferior','Нижняя суставная поверхность'),
 (105,'arcus anterior atlantis','Передняя дуга атланта'),(106,'fovea dentis','Ямка зуба'),
 (107,'tuberculum anterius','Передний бугорок'),(108,'arcus posterior atlantis','Задняя дуга атланта'),
 (109,'sulcus arteriae vertebralis','Борозда позвоночной артерии'),
 (110,'canalis arteriae vertebralis','Канал позвоночной артерии'),(111,'tuberculum posterius','Задний бугорок'),
 (201,'axis [C II]','Осевой позвонок [C II]'),(202,'dens axis','Зуб'),(203,'apex dentis','Верхушка зуба'),
 (204,'facies articularis anterior','Передняя суставная поверхность'),
 (205,'facies articularis posterior','Задняя суставная поверхность'),
 (301,'vertebra prominens [C VII]','Выступающий позвонок [C VII]')])
add('02.2.00', [(1,'columna vertebralis','Позвоночный столб'),(6,'lordosis cervicis; lordosis colli','Шейный лордоз'),(9,'canalis vertebralis','Позвоночный канал')])

ROOT_CODES = {'hyoid':'A02.1.16.001','atlas':'A02.2.02.101','axis':'A02.2.02.201',
              **{f'cervical_{i}':'A02.2.02.001' for i in range(3,7)},'cervical_7':'A02.2.02.301'}
GENERAL_CODES = [f'A02.2.01.{i:03}' for i in range(2,18) if i != 8]
REGIONAL_CODES = [f'A02.2.02.{i:03}' for i in (2,3,4,6,7)]
BONE_CODES = {
 'hyoid':[f'A02.1.16.{i:03}' for i in range(2,5)],
 'atlas':[f'A02.2.02.{i}' for i in range(102,112)] + ['A02.2.01.010','A02.2.01.011','A02.2.01.013','A02.2.02.003'],
 'axis':GENERAL_CODES + ['A02.2.02.003'] + [f'A02.2.02.{i}' for i in range(202,206)],
 **{f'cervical_{i}':GENERAL_CODES + REGIONAL_CODES + (['A02.2.02.005'] if i==6 else []) for i in range(3,8)}
}

DESCRIPTIONS = {}
def desc(code, text, refs, **extra):
    DESCRIPTIONS[code] = dict(x=text, refs=refs, scope='anatomy', **extra)

_general = {
 2:'Передняя опорная часть позвонка.',3:'Поверхность тела, обращённая к межпозвоночному диску.',
 5:'Задняя костная часть, ограничивающая позвоночное отверстие.',6:'Парная короткая часть дуги, соединённая с телом.',
 7:'Пластинчатая задняя часть дуги.',8:'Отверстие между соседними позвонками; его границы принадлежат нескольким структурам.',
 9:'Вырезка у верхнего края ножки дуги.',10:'Вырезка у нижнего края ножки дуги.',
 11:'Пространство, ограниченное костными частями позвонка.',12:'Задний срединный отросток дуги.',
 13:'Парный отросток, направленный вбок.',14:'Верхний суставной отросток позвонка.',
 15:'Суставная поверхность, обращённая к вышележащему позвонку.',16:'Нижний суставной отросток позвонка.',
 17:'Суставная поверхность, обращённая к нижележащему позвонку.'}
for i, text in _general.items(): desc(f'A02.2.01.{i:03}',text,[GRAY_GENERAL,OPENSTAX])
desc('A02.2.01.004','Кольцевая область окостенения по краю тела позвонка, срастающаяся с ним при созревании скелета.',[RING1,RING2],note='Возрастную стадию и границы эпифиза нельзя установить по одной внешней сетке взрослой кости.')
for i,text in {2:'Средняя часть кости между рогами.',3:'Небольшой выступ у соединения тела с большим рогом.',4:'Парный длинный рог, отходящий назад от тела.'}.items():
    desc(f'A02.1.16.{i:03}',text,[GRAY_HYOID,AS_HYOID])
desc('A02.2.02.002','Возвышение бокового края верхней поверхности тела C3–C7.',[UNCUS1,UNCUS2])
desc('A02.2.02.003','Отверстие в поперечном отростке.',[GRAY_CERVICAL,AS_TYPICAL],note='Форма отверстия не подтверждает его сосудистое содержимое в данной модели.')
desc('A02.2.02.004','Передний бугорок поперечного отростка типичного шейного позвонка.',[GRAY_CERVICAL,AS_TYPICAL])
desc('A02.2.02.005','Выраженный передний бугорок поперечного отростка C6.',[AS_TYPICAL,ref('Lee et al. (2013) — The Efficacy of Carotid Tubercle as an Anatomical Landmark','https://pmc.ncbi.nlm.nih.gov/articles/PMC3664672/','Introduction: carotid tubercle at the transverse process of the sixth cervical vertebra.')])
desc('A02.2.02.006','Задний бугорок поперечного отростка типичного шейного позвонка.',[GRAY_CERVICAL,AS_TYPICAL])
desc('A02.2.02.007','Борозда на верхней стороне поперечного отростка между его бугорками.',[GRAY_CERVICAL,AS_TYPICAL])
_atlas = {102:'Парная массивная часть между передней и задней дугами.',103:'Вогнутая поверхность для затылочного мыщелка.',104:'Нижняя суставная поверхность латеральной массы для C2.',105:'Передняя часть костного кольца атланта.',106:'Суставная ямка на задней стороне передней дуги для зуба C2.',107:'Срединное возвышение на передней стороне передней дуги.',108:'Задняя часть костного кольца атланта.',109:'Борозда сверху задней дуги позади латеральной массы.',111:'Срединное возвышение на задней дуге.'}
for i,text in _atlas.items(): desc(f'A02.2.02.{i}',text,[GRAY_CERVICAL,AS_ATLAS])
desc('A02.2.02.110','Непостоянный костный канал над бороздой позвоночной артерии при наличии костного мостика.',[GRAY_CERVICAL,PONTICLE],inc=1,note='Наличие канала в конкретной сетке проверяется отдельно. Скобки номенклатуры сами по себе не являются доказательством варианта.')
for i,text in {202:'Отросток, выступающий вверх из тела осевого позвонка.',203:'Верхний конец зуба.',204:'Передняя суставная поверхность зуба для ямки зуба атланта.',205:'Задняя суставная поверхность зуба, обращённая к поперечной связке атланта.'}.items():
    desc(f'A02.2.02.{i}',text,[GRAY_CERVICAL,AS_AXIS])
desc('A02.2.00.001','Последовательность позвонков, образующая позвоночный столб.',[GRAY_GENERAL,OPENSTAX])
desc('A02.2.00.006','Изгиб шейного отдела выпуклостью вперёд.',[ref('Gray (1918) — The Vertebral Column as a Whole',GRAY_URL+'#page=52','PDF с.52, Curves: cervical curve convex forward.'),OPENSTAX])
desc('A02.2.00.009','Канал, образуемый последовательностью позвоночных отверстий.',[GRAY_GENERAL,OPENSTAX])

DESCRIPTION_OVERRIDES = {
 ('atlas','A02.2.01.010'):dict(x='Нижняя позвоночная вырезка в области задней дуги атланта.',refs=[GRAY_CERVICAL,ref('Frontiers in Neuroanatomy (2025) — Sœmmerring’s error: anatomical perspectives','https://doi.org/10.3389/fnana.2025.1568824','Where is Sœmmerring’s error?: inferior notch of atlas and pedicle of axis; анатомическое описание, без принятия предложенной авторами перенумерации нервов.')],note='Термин общего списка. Особенности верхнего шейного перехода не следует переносить с типичного позвонка автоматически.'),
 ('atlas','A02.2.02.003'):dict(x='Отверстие в поперечном отростке атланта.',refs=[GRAY_CERVICAL,AS_ATLAS]),
 ('axis','A02.2.02.003'):dict(x='Отверстие в поперечном отростке осевого позвонка.',refs=[GRAY_CERVICAL,AS_AXIS]),
 ('axis','A02.2.01.003'):dict(x='Нижняя поверхность тела C2, обращённая к диску C2–C3.',refs=[GRAY_CERVICAL,OPENSTAX],note='Верхняя часть C2 несёт зуб; здесь нельзя подразумевать диск между телами C1 и C2.'),
 ('cervical_7','A02.2.02.004'):dict(x='Передний бугорок поперечного отростка: на C7 может быть слабо выражен или не обособляться.',refs=[GRAY_CERVICAL,ref('Ultrasound-Guided Cervical Selective Nerve Root Block (2024)','https://pmc.ncbi.nlm.nih.gov/articles/PMC11278421/','§2.4.2 CSNRB Group; Fig.1C: prominent posterior and rudimentary anterior tubercle of C7.')],note='Региональный термин включён для объяснения изменчивости; наличие отдельного бугорка в модели не заявлено.'),
 ('cervical_7','A02.2.02.007'):dict(x='Обычно неглубокая борозда сверху поперечного отростка C7.',refs=[GRAY_CERVICAL,AS_C7])
}

WHOLE_TERMS = ['A02.2.00.001','A02.2.00.006','A02.2.00.009','A02.2.01.008']
APPLICABILITY_NOTE = 'TA98 содержит общие и региональные списки. Применение общих терминов к каждой кости здесь составлено редакционно по анатомическим источникам; число записей не является отдельным официальным счётчиком IFAA. Перечень терминов не подтверждает детали конкретной модели.'
APPLICATION_NOTES = {
 'hyoid':'Три образования из самостоятельного раздела TA98; парные рога имеют один код на тип образования.',
 'atlas':'Специальный список атланта дополнен поперечным отростком, поперечным и позвоночным отверстиями и нижней вырезкой. Общая верхняя вырезка здесь соответствует борозде позвоночной артерии и не дублируется. Тело и остистый отросток не добавляются.',
 'axis':'Общие образования применяются с учётом зуба и отсутствия обычной верхней межпозвоночной поверхности. Региональные бугорки типичного поперечного отростка не переносятся автоматически.',
 **{f'cervical_{i}':'Общие образования позвонка и применимые региональные признаки C3–C7.' for i in range(3,8)}
}
APPLICATION_NOTES['cervical_6'] += ' Сонный бугорок — отдельное название переднего бугорка C6, а не дополнительная кость.'
APPLICATION_NOTES['cervical_7'] += ' Передний бугорок может не обособляться; это объяснение регионального термина, а не утверждение о видимой детали модели.'

_texts = {
 'hyoid':('Подъязычная кость состоит из тела и пар больших и малых рогов.',[GRAY_HYOID,AS_HYOID]),
 'atlas':('Первый шейный позвонок: кольцо из двух дуг и латеральных масс, без тела и остистого отростка.',[GRAY_CERVICAL,AS_ATLAS]),
 'axis':('Второй шейный позвонок. Зуб выступает вверх из его тела и сочленяется с атлантом.',[GRAY_CERVICAL,AS_AXIS]),
 **{f'cervical_{i}':(f'Шейный позвонок C{i}: тело, дуга и отростки. Относится к типичным шейным позвонкам.',[GRAY_CERVICAL,AS_TYPICAL]) for i in range(3,7)},
 'cervical_7':('Седьмой шейный позвонок, обычно с длинным нераздвоенным остистым отростком.',[GRAY_CERVICAL,AS_C7])
}
BONES = {b:dict(ru=T[ROOT_CODES[b]][1],lat=T[ROOT_CODES[b]][0],code=ROOT_CODES[b],x=x,refs=refs,note=APPLICATION_NOTES[b]) for b,(x,refs) in _texts.items()}
for i,ru in [(3,'Третий'),(4,'Четвёртый'),(5,'Пятый'),(6,'Шестой')]:
    BONES[f'cervical_{i}'].update(ru=f'{ru} шейный позвонок (C{i})',level=f'C{i}',termNote='Латынь и код относятся к групповому термину TA98; номер обозначает выбранный позвонок, не отдельную строку TA98.')

def description_for(bone, code):
    return {**DESCRIPTIONS[code], **DESCRIPTION_OVERRIDES.get((bone,code),{})}

def export_evidence(path):
    result=dict(version=1,scope='Кости шеи: подъязычная кость, C1–C7; термины, топография и применимость, без проверки геометрии.',
        reviewed='2026-10-13',catalogueIsOfficialPerBoneCount=False,geometryVerified=False,
        applicabilityNote=APPLICABILITY_NOTE,applicationNotes=APPLICATION_NOTES,
        nomenclature=[ref('IFAA TA98 — Columna vertebralis',IFAA_URL,'A02.2.00.001,006,009; A02.2.01; A02.2.02.'),ref('IFAA TA98 — Os hyoideum',HYOID_URL,'A02.1.16.001–004.'),dict(title='Международная анатомическая терминология, ред. Л. Л. Колесников, 2003',locator='Печатные с.19–20; локальная исследовательская копия просмотрена, не публикуется.')],
        terms={code:dict(lat=row[0],ru=row[1],flag=row[2]) for code,row in T.items()},
        bones={b:{**data,'codes':BONE_CODES[b],'entries':{c:description_for(b,c) for c in BONE_CODES[b]}} for b,data in BONES.items()},
        wholeTerms={c:DESCRIPTIONS[c] for c in WHOLE_TERMS},
        limits=['Нет координат или подтверждения деталей сетки.','Один термин парного образования не означает проверку обеих сторон.','Межпозвоночное отверстие — составное образование; не приписывается одной кости.','Анулярный эпифиз: стадия сращения отдельно не проверена.'])
    Path(path).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if __name__ == '__main__':
    export_evidence(Path(__file__).resolve().parents[1]/'research/neck-bone-evidence.json')
    print('Neck bone terms:',len(T),'bone catalogue entries:',sum(map(len,BONE_CODES.values())))
