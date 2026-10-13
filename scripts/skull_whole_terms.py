"""Reviewed TA98 skull-as-whole text; geometry claims are generated separately.

Russian labels transcribed from Kolesnikov (2003), printed pp. 9–11.
Latin/codes deliberately come from the frozen IFAA inventory, not these strings.
Descriptions are concise original summaries, not reproduced textbook passages.
"""
from __future__ import annotations

GRAY_URL = 'https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf'
BUCHANAN_URL = "https://embryology.med.unsw.edu.au/embryology/index.php?title=Book_-_Buchanan%27s_Manual_of_Anatomy_including_Embryology_5"
KOLESNIKOV_URL = 'https://rsmu.ru/fileadmin/templates/DOC/Faculties/PF/Dept_latin_language/Kolesnikov_-_Terminologia_Anatomica_1.pdf'

# number | exact Russian terminology (е/ё normalized) | original short definition
TEXT = '''
1|Череп|Костная основа головы, объединяющая мозговой и лицевой отделы.
2|Лицевая норма; лобная норма|Вид черепа спереди.
3|Верхняя норма; вертикальная норма|Вид черепа сверху.
4|Затылочная норма|Вид черепа сзади.
5|Латеральная норма|Вид черепа сбоку.
6|Нижняя норма; базальная норма|Вид черепа снизу.
7|Мозговой череп; нейрокраниум|Отдел черепа, окружающий полость черепа.
8|Лицевой череп; висцерокраниум|Костная основа лица.
9|Хрящевой череп; хондрокраниум|Хрящевая основа развивающегося черепа.
10|Перепончатый череп; десмокраниум|Перепончатая основа развивающегося черепа.
11|Надкостница черепа; перикраниум|Надкостница на наружной поверхности костей черепа.
12|Полость черепа|Пространство, ограниченное костями мозгового черепа.
13|Лоб|Передняя область черепа в области лобной кости.
14|Затылок|Задняя область черепа в области затылочной кости.
15|Назион|Ориентир средней линии в месте соединения лобной и носовых костей.
16|Брегма|Ориентир в месте встречи венечного и сагиттального швов.
17|Ламбда|Ориентир в месте встречи сагиттального и ламбдовидного швов.
18|Инион|Ориентир наружного затылочного выступа.
19|Птерион|Область соединения лобной, теменной, височной и клиновидной костей.
20|Астерион|Область соединения теменной, затылочной и височной костей.
21|Гонион|Ориентир в области угла нижней челюсти.
22|Височная ямка|Ямка боковой поверхности черепа выше скуловой дуги.
23|Скуловая дуга|Дуга, образованная скуловым отростком височной кости и височным отростком скуловой кости.
24|Подвисочная ямка|Пространство под скуловой дугой, позади верхней челюсти.
25|Крыловидно-нёбная ямка|Пространство между верхней челюстью, крыловидным отростком клиновидной кости и нёбной костью.
26|Крыловидно-верхнечелюстная щель|Щель между верхней челюстью и крыловидным отростком, связывающая подвисочную и крыловидно-нёбную ямки.
27|Роднички|Перепончатые промежутки между костями развивающегося черепа.
28|Передний родничок|Родничок между лобной и теменными костями.
29|Задний родничок|Родничок между теменными и затылочной костями.
30|Клиновидный родничок; переднелатеральный родничок|Родничок у клиновидного угла теменной кости.
31|Сосцевидный родничок; заднелатеральный родничок|Родничок у сосцевидного угла теменной кости.
32|Свод черепа|Верхняя, сводчатая часть мозгового черепа.
33|Темя|Наиболее высокая область свода черепа в срединной плоскости при вертикально ориентированной голове.
34|Наружная пластинка|Наружный слой компактного вещества костей свода.
35|Диплоэ|Губчатое вещество между наружной и внутренней пластинками костей свода.
36|Диплоические каналы|Костные каналы в диплоэ.
37|Внутренняя пластинка|Внутренний слой компактного вещества костей свода.
38|Борозда верхнего сагиттального синуса|Срединная борозда на внутренней поверхности свода черепа.
39|Ямочки грануляций|Небольшие углубления внутренней поверхности свода, в том числе по сторонам борозды верхнего сагиттального синуса.
40|Вдавления извилин; пальцевидные вдавления; мозговые возвышения|Углубления и возвышения внутренней поверхности черепа, соответствующие рельефу поверхности мозга.
41|Венозные борозды|Борозды для венозных сосудов на внутренней поверхности черепа.
42|Артериальные борозды|Борозды для артериальных сосудов на внутренней поверхности черепа.
43|Кость шва|Дополнительная кость в шве черепа; вариант строения.
44|Основание черепа|Нижняя часть мозгового черепа.
45|Внутреннее основание черепа|Поверхность основания, обращённая в полость черепа.
46|Клиновидно-каменистая щель|Щель между клиновидной костью и каменистой частью височной кости.
47|Каменисто-затылочная щель|Щель между каменистой частью височной кости и базилярной частью затылочной кости.
48|Передняя черепная ямка|Передний отдел внутреннего основания черепа, ограниченный сзади малыми крыльями клиновидной кости.
49|Средняя черепная ямка|Отдел внутреннего основания между малыми крыльями клиновидной кости и верхними краями каменистых частей височных костей.
50|Задняя черепная ямка|Задний отдел внутреннего основания, позади спинки седла и каменистых частей височных костей, вокруг большого отверстия.
51|Скат|Наклонная поверхность внутреннего основания от спинки седла к большому отверстию.
52|Борозда нижнего каменистого синуса|Борозда вдоль границы каменистой части височной кости и базилярной части затылочной кости.
53|Наружное основание черепа|Нижняя поверхность основания черепа.
54|Яремное отверстие|Отверстие между затылочной и височной костями в области их яремных вырезок.
55|Рваное отверстие|Отверстие у вершины каменистой части височной кости, между височной, клиновидной и затылочной костями.
56|Костное нёбо|Образовано нёбными отростками верхних челюстей и горизонтальными пластинками нёбных костей.
57|Большой нёбный канал|Канал между верхней челюстью и нёбной костью, направляющийся к костному нёбу.
58|Большое нёбное отверстие|Отверстие в заднелатеральном отделе костного нёба.
59|Малые нёбные отверстия|Отверстия в области пирамидального отростка нёбной кости.
60|Резцовая ямка|Углубление по средней линии костного нёба позади верхних резцов.
61|Резцовые каналы|Каналы между передним отделом костного нёба и носовой полостью.
62|Резцовые отверстия|Отверстия резцовых каналов в переднем отделе костного нёба.
63|Нёбный валик|Вариант костного возвышения по средней линии костного нёба.
64|Нёбно-влагалищный канал|Канал между клиновидным отростком нёбной кости и влагалищным отростком клиновидной кости.
65|Сошниково-влагалищный канал|Канал между крылом сошника и влагалищным отростком клиновидной кости.
66|Сошниково-клювовидный канал|Канал между верхним краем сошника и клиновидным клювом.
67|Глазница|Костная глазница, образованная окружающими её костями черепа.
68|Полость глазницы|Пространство между костными стенками глазницы.
69|Вход в глазницу|Переднее отверстие глазницы.
70|Глазничный край|Костная граница входа в глазницу.
71|Надглазничный край|Верхний край входа в глазницу, образованный лобной костью.
72|Подглазничный край|Нижний край входа в глазницу, образованный верхней челюстью и скуловой костью.
73|Латеральный край|Наружный край входа в глазницу.
74|Медиальный край|Край входа в глазницу со стороны носа.
75|Верхняя стенка|Крыша глазницы, образованная преимущественно лобной костью и малым крылом клиновидной кости.
76|Нижняя стенка|Дно глазницы, в образовании которого участвуют верхняя челюсть, скуловая и нёбная кости.
77|Латеральная стенка|Наружная стенка глазницы, образованная скуловой костью и большим крылом клиновидной кости.
78|Медиальная стенка|Внутренняя стенка глазницы; в её образовании участвуют верхняя челюсть, слёзная, решётчатая и клиновидная кости.
79|Переднее решётчатое отверстие|Переднее отверстие в области соединения лобной и решётчатой костей в медиальной стенке глазницы.
80|Заднее решётчатое отверстие|Заднее отверстие в области соединения лобной и решётчатой костей в медиальной стенке глазницы.
81|Слёзная борозда|Борозда в переднем отделе медиальной стенки глазницы.
82|Ямка слёзного мешка|Углубление для слёзного мешка в переднем отделе медиальной стенки глазницы.
83|Верхняя глазничная щель|Щель между малым и большим крыльями клиновидной кости, соединяющая глазницу со средней черепной ямкой.
84|Нижняя глазничная щель|Щель между латеральной стенкой и дном в заднем отделе глазницы.
85|Носо-слёзный канал|Костный канал от переднемедиального отдела глазницы к нижнему носовому ходу.
86|Костная носовая полость|Полость носа, ограниченная костями черепа.
87|Костная перегородка носа|Основные компоненты костной перегородки — перпендикулярная пластинка решётчатой кости и сошник.
88|Грушевидная апертура|Переднее костное отверстие носовой полости.
89|Верхний носовой ход|Пространство между верхней и средней носовыми раковинами.
90|Средний носовой ход|Пространство между средней и нижней носовыми раковинами.
91|Нижний носовой ход|Пространство под нижней носовой раковиной, над дном носовой полости.
92|Отверстие носослёзного канала|Нижнее отверстие носослёзного канала в переднем отделе нижнего носового хода.
93|Общий носовой ход|Пространство между носовыми раковинами и перегородкой носа.
94|Клиновидно-решётчатое углубление|Углубление выше и позади верхней носовой раковины.
95|Носоглоточный ход|Задний отдел носовой полости позади задних концов носовых раковин.
96|Хоана; заднее носовое отверстие|Заднее костное отверстие носовой полости.
97|Клиновидно-нёбное отверстие|Отверстие между нёбной и клиновидной костями, соединяющее носовую полость с крыловидно-нёбной ямкой.
'''
TERMS = {int(n): {'ru': ru, 'description': description} for n, ru, description in
         (line.split('|') for line in TEXT.strip().splitlines())}
assert set(TERMS) == set(range(1, 98))


def reference(title, url, locator, author_group, kind='anatomical'):
    return dict(title=title, url=url, locator=locator, authorGroup=author_group, kind=kind)


def gray(page, locator):
    return reference('Gray’s Anatomy (1918)', GRAY_URL + '#page=' + str(page),
                     f'PDF, с. {page}: {locator}', 'gray_lewis_1918')


def buchanan(locator):
    return reference('Buchanan’s Manual of Anatomy, глава V', BUCHANAN_URL,
                     locator, 'buchanan_1949')


# Locators refer to the inspected full source, including the named figures.
REFS = {}


def pair(numbers, page, gray_loc, buchanan_loc):
    for number in numbers:
        assert number not in REFS
        REFS[number] = [gray(page, gray_loc), buchanan(buchanan_loc)]


pair([1, 7, 8], 75, '5. The Skull: division into cranium and skeleton of face', 'The Skull as a Whole; Development of Skull: cranial and facial parts')
pair([12], 163, 'The Interior of the Skull: skull-cap and floor of cranial cavity', 'The Interior of the Cranium: vault and floor of cranial cavity')
pair([2, 13, 15], 157, 'Norma Frontalis; с. 158–159: frontal view, nasion', 'The Anterior Aspect of the Skull: forehead, nasion')
pair([3, 16, 17], 149, 'Norma Verticalis; продолжение с. 150: bregma, lambda', 'The Skull viewed from Above: bregma, lambda')
pair([32], 162, 'The Interior of the Skull: skull-cap', 'The Interior of the Cranium: calvaria, vaulted roof of cranium')
pair([4, 14, 18, 20], 157, 'Norma Occipitalis: inion, asterion, occipital region', 'The Posterior Aspect of the Skull: inion, asterion')
pair([5, 19, 22, 23], 154, 'Norma Lateralis; с. 155: pterion, temporal fossa, zygomatic arch', 'The Lateral Aspect of the Skull: pterion, temporal fossa, zygomatic arch')
pair([6, 53, 56, 58, 59, 60, 61, 62], 152, 'Norma Basalis; с. 153: hard palate, palatine foramina, incisive fossa/canals', 'The Inferior Aspect of the Skull: hard palate, incisive fossa, incisive and palatine foramina')
pair([9, 10], 8, 'The Skull: membranous and cartilaginous neurocranium; с. 9–10', 'Development of Skull — A. Cranial Development: membranous and cartilaginous stages')
pair([21], 173, 'Craniometry: Gonion, paragraph 42', 'The Lateral Aspect of the Skull: outer side of mandibular angle (gonion)')
pair([24], 156, 'Infratemporal Fossa', 'The Lateral Aspect of the Skull — Infratemporal Fossa')
pair([25, 26, 57, 97], 157, 'Pterygopalatine Fossa: walls and communications', 'The Lateral Aspect of the Skull — Pterygo-palatine Fossa: boundaries and communications')
pair(range(27, 32), 170, 'Differences in the Skull Due to Age; с. 171: fontanelles', 'The Skull at Birth: anterior, posterior, sphenoidal and mastoid fontanelles')
pair([34, 35, 37], 2, 'Flat Bones: outer/inner tables and intervening diploë', 'The Interior of the Cranium: outer plate, inner vitreous plate, cancellated diploe')
pair([38, 39, 40, 42], 162, 'The Interior of the Skull — Inner Surface of Skull-cap; продолжение с. 163: sinus groove, arachnoid depressions, cerebral impressions, meningeal furrows', 'The Interior of the Cranium: vault and calvaria, meningeal grooves, impressions for cerebral gyri, arachnoid pits')
pair([41], 167, 'Posterior Fossa: grooves for transverse, sigmoid and petrosal sinuses', 'The Intracranial Surface of the Base — Posterior Fossa: grooves for venous sinuses')
pair([43], 157, 'Norma Occipitalis: sutural bones', 'Sutural Bones: accessory bones along cranial sutures')
pair([44, 45, 48], 163, 'The Interior of the Skull — base, Anterior Fossa', 'The Intracranial Surface of the Base of the Skull; Anterior Fossa')
pair([46, 49, 55], 163, 'Middle Fossa; продолжение с. 164–166, Fig. 193: sphenopetrosal junction, petrous apex, foramen lacerum, boundaries', 'Sutures: petro-sphenoidal suture between anterior border of petrous temporal and posterior border of greater sphenoidal wing; The Intracranial Surface of the Base — Middle Fossa')
pair([47, 50, 51, 52, 54], 166, 'Posterior Fossa; с. 167: clivus, petrous/occipital border, jugular foramen', 'The Intracranial Surface of the Base — Posterior Fossa: petro-basilar suture, clivus, inferior petrosal groove, jugular foramen')
pair(range(67, 86), 160, 'The Orbits; с. 161–162: walls, margins, orbital fissures, ethmoidal foramina, lacrimal fossa and canal', 'The Orbits: base and margins, roof/floor/lateral/medial walls, fissures, ethmoidal foramina and lacrimal passage')
pair([86, 87, 89, 90, 91, 92, 94, 96], 168, 'The Nasal Cavity; с. 169–170: septum, meatuses, sphenoethmoidal recess, choanae', 'The Nasal Fossae: medial and lateral walls, meatuses, spheno-ethmoidal recess, posterior nares')
pair([88], 158, 'Norma Frontalis: piriform aperture', 'The Anterior Aspect of the Skull: anterior nasal aperture')

REFS[11] = [
    reference('An algorithmic approach to scalp reconstructive surgery (2024)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11058610/', 'Anatomy and physiology — Layers: deepest scalp layer, periosteum of underlying cranial bone', 'scalp_reconstruction_2024'),
    reference('Immersive Surgical Anatomy of the Pterional Approach (2019)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6759424/', 'Scalp Layers and Figure 4: frontal periosteum (pericranium)', 'pterional_2019'),
]
REFS[36] = [
    reference('The elusive diploic veins: anthropological and anatomical perspective (1999)', 'https://pubmed.ncbi.nlm.nih.gov/10096685/', 'Abstract: diploic venous tunnels protected by two bony laminae', 'hershkovitz_et_al_1999'),
    reference('Diploic vein variation (Journal of Morphology, 2022)', 'https://onlinelibrary.wiley.com/doi/10.1002/jmor.21505', 'Abstract, first sentence: diploic veins leave channels within cranial diploe', 'jmor_21505_2022'),
]
REFS[33] = [
    buchanan('The Skull viewed from Above: highest point in course of sagittal suture, called vertex'),
    reference('Dictionnaire de l’Académie nationale de médecine', 'https://www.academie-medecine.fr/le-dictionnaire/index.php?q=vertex', 'Entry «vertex»: highest point of vault in median sagittal plane with head upright', 'academie_medecine'),
]
REFS[63] = [
    buchanan('The Maxilla — Palatine Process: torus palatinus, antero-posterior midline elevation behind incisive fossa'),
    reference('Prevalence of torus palatinus in Cappadocia region (2008)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2634781/', 'Introduction: bony protuberance along median palatal suture, anatomical variation', 'cappadocia_2008'),
]
for number in (64, 65):
    REFS[number] = [
        reference('Visualization of the vomerovaginal canal during endoscopic transnasal surgery (2019)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6637440/', 'Osteological study and endoscopic dissection: relationships of vomer, vaginal process and palatine sphenoidal process', 'vvc_2019'),
        reference('Simultaneous observation and discrimination of palatovaginal and vomerovaginal canals (2015)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4658943/', 'Discussion and Figures 2–3: separate bony boundaries of PVC and VVC', 'pvc_vvc_2015'),
    ]
REFS[66] = [
    reference('Dictionnaire de l’Académie nationale de médecine', 'https://www.academie-medecine.fr/le-dictionnaire/index.php?q=canal+vom%C3%A9ro+vaginal', 'Entry «canal voméro-rostral», 2015: sphenoidal rostrum and groove between vomer wings', 'academie_medecine'),
    reference('IFAA Terminologia Anatomica Humana: anatomical definition', 'https://ifaa.unifr.ch/Public/TNAEntryPage/auto/unit/EN/TAH370%20Unit%20EN.htm', 'Taxonomic definition (not the name field): canal located between vomer and sphenoidal rostrum', 'ifaa_definition', 'anatomical_definition'),
]
REFS[93] = [
    reference('Computational fluid dynamics study of nasal airflow (2022)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC9689633/', 'Methods, paragraph following Figure 4: common meatus between septum and turbinates', 'nasal_cfd_2022'),
    reference('Anterior meatuscopy is more reliable than a sniff test (2015)', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4683136/', 'The MNM versus the INM; Figure 3: common nasal meatus between nasal septum and inferior turbinate', 'meatuscopy_2015'),
]
REFS[95] = [
    reference('Surgical Anatomy—Nose and Paranasal Sinuses, CBS Publishers sample', 'https://cbspd.s3.ap-south-1.amazonaws.com/assets/documents/9789390709571S.pdf', 'Printed p. 7: part of nasal cavity behind posterior ends of conchae is nasopharyngeal meatus', 'cbs_nasal_anatomy'),
    reference('Dictionnaire de l’Académie nationale de médecine', 'https://www.academie-medecine.fr/le-dictionnaire/index.php?q=nerf+naso-palatin', 'Entry «méat naso-pharyngien»: posterior opening of nasal meatuses towards pharynx', 'academie_medecine'),
]
assert set(REFS) == set(TERMS)

FUTURE = {9, 10, 11, 27, 28, 29, 30, 31}
VIEWS = {2: 'ant', 3: 'sup', 4: 'post', 5: 'right', 6: 'inf'}
VARIANTS = {43, 63}
GROUPS = {1, 7, 8, 9, 10, 12, 27, 32, 44, 45, 53, 67, 68, 86}
NOTES = {
    40: 'Печатное издание Колесникова (с. 10) дополнительно приводит синоним impressiones digitatae; основной латинский список сохранён по электронной TA98 IFAA.',
    61: 'В издании Колесникова на с. 10 напечатано «Canalis incisivi / Резцовый канал», на с. 17 — «Canales incisivi / Резцовые каналы». Здесь сохранено множественное число по с. 17, электронной TA98 IFAA и уже существующим карточкам атласа.',
}
