"""Entity-specific mandibular/occipital/ethmoidal review; no new coordinates."""
from copy import deepcopy
from head_skull_batch2 import _ref, GRAY_URL
from head_face_evidence import PALACKY

REPORT = 'research/stage5-skull-batch8-2026-10-16/geometry-kind-review.json'
BONES = ('mandible', 'occipital', 'ethmoid')

def ref(key, title, url, locator, group, access='full_text', **metadata):
    return _ref('batch8_'+key, title, url, locator, group,
                scope='anatomical_entity_and_representation', access=access, **metadata)

GRAY = ref('gray', 'Gray / Lewis. Anatomy of the Human Body (1918)', GRAY_URL+'#page=140',
    'PDF pp.140–143, The Mandible: body, internal/external surfaces, rami, processes; Figs.176–177. No specimen coordinates inferred.', 'gray_lewis_1918')
PAL = ref('palacky', 'Libor Luňáček, Univerzita Palackého — Splanchnocranium', PALACKY,
    'MANDIBULA: corpus, paired rami, muscular impressions, foramina, head and neck. Used only for the named entities in this section.', 'lunacek_palacky')

def paper(pmid, title, year, doi, group, locator, access='abstract'):
    meta=dict(pmid=pmid, year=year)
    if doi: meta['doi']=doi
    return ref(pmid, title, 'https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/', locator, group, access, **meta)

MARDINGER = paper('11143307', 'Mardinger O et al. Anatomic and radiologic course of the mandibular incisive canal', 2000,
    '10.1007/s00276-000-0157-5', 'mardinger_2000', 'Abstract read through official EFetch: 46 hemimandibles; intraosseous course and variable cortical walls. No universal complete tube or dimensions inferred.', 'efetch_abstract')
ZHANG = paper('31859284', 'Zhang YQ et al. Prevalence and Morphology of Mandibular Incisive Canal', 2019,
    '10.3290/j.cjdr.a43735', 'zhang_2019', 'Abstract: independent CBCT sample, 1070 hemimandibles; incisive canal and variation with dental status. No population measurements transferred.')
PARK = paper('30895000', 'Park MK et al. Anatomical and radiographic study of the mandibular retromolar canal', 2016,
    '10.1016/j.jds.2016.04.002', 'park_2016', 'Abstract: dry mandibles, cadavers, CBCT and micro-CT; retromolar canal and aperture distinct from retromolar triangle. Print year 2016, not PubMed indexing year 2019.')
SHEN = paper('34072906', 'Shen YW et al. Assessment of the Retromolar Canal in Taiwan Subpopulation', 2021,
    '10.3390/tomography7020020', 'shen_2021', 'Abstract: independent CBCT study; variant branch of mandibular canal opening through retromolar foramen. Presence on this GLB is unknown.')
ORHAN = paper('20012078', 'Orhan M, Govsa F, Saylam C. A surgical view of the superior nasal turbinate: anatomical study', 2010,
    '10.1007/s00405-009-1169-3', 'orhan_2010', 'Abstract: cadaveric study of superior and variably present supreme turbinates; not a specimen-specific segmentation.')
GOTLIB = paper('28703849', 'Gotlib T et al. The supreme turbinate and the drainage of the posterior ethmoids: a computed tomographic study', 2018,
    '10.5603/FM.a2017.0067', 'gotlib_2018', 'Abstract: 100 CT examinations; supreme turbinate presence and posterior ethmoidal anatomy. Electronic 2017; print 2018.')
PISOVA = ref('pisova', 'Píšová H et al. Craniovascular traits in anthropology and evolution: from bones to vessels (2017)',
    'https://www.isita-org.com/Jass/Contents/2017vol95/Pisova/28190005.pdf',
    'PDF pp.8–9, Dural venous drainage system and Fig.6: endocranial imprints and occipital/marginal sinus variation. Bony bed is not the venous lumen.', 'pisova_2017', pmid='28190005', doi='10.4436/JASS.95003')
DAS = paper('19205565', 'Das S et al. An anatomico-radiological study of the grooves for occipital sinus in the posterior cranial fossa', 2008,
    None, 'das_2008', 'Abstract: grooves on dry skulls, including variant patterns; no exact course on project mesh. No DOI supplied by EFetch.')
TUBBS = paper('16572657', 'Tubbs RS et al. The marginal sinus', 2006,
    '10.3171/jns.2006.104.3.429', 'tubbs_2006', 'Abstract: marginal venous sinus anatomy. Supports anatomical relationship only; does not prove a complete bony groove.')
SPINES = ref('spines', 'Champagne R et al. A comprehensive review of the mental spine (2024)',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC10968188/', 'Terminology, Anatomy, Anatomical variation; fused or separate spines. Electronic 2023-12-15; issue 2024-03-31.',
    'champagne_2024', pmid='38098242', doi='10.5115/acb.23.220')

# Frozen decisions based on each entity's anatomy, not suffix/name heuristics.
MANDIBLE = {
 2: ('volume', 'Тело — изогнутая костная часть с наружной и внутренней поверхностями и толщиной.'),
 4: ('area', 'У взрослого это срединная область сращения половин тела; не сохраняющийся сустав и не самостоятельная кость. Тип области не задаёт её границу.'),
 5: ('volume', 'Подбородочный выступ — костное возвышение переднего отдела тела.'),
 6: ('volume', 'Боковые подбородочные бугорки — выступы рельефа, не точечные координаты.'),
 7: ('space', 'Подбородочное отверстие — выходная апертура; внутрикостный ход рассматривается отдельно.'),
 8: ('volume', 'Косая линия — костный валик наружной поверхности, продолжающий передний край ветви; линия имени не означает одномерный шов.'),
 9: ('area', 'Двубрюшная ямка — открытое поверхностное углубление; не закрытая полость.'),
10: ('volume', 'Верхние подбородочные ости — костные выступы; число и слияние вариабельны.'),
11: ('volume', 'Нижние подбородочные ости могут сливаться в гребень; маркер не подтверждает отдельные парные выступы.'),
12: ('volume', 'Челюстно-подъязычная линия — костный гребень внутренней поверхности, не шов и не граница без толщины.'),
13: ('volume', 'Torus mandibularis — вариант костного выступа; наличие на данном образце отдельно не подтверждено.'),
14: ('area', 'Подъязычная ямка — поверхностное ложе над передней частью челюстно-подъязычного гребня.'),
15: ('area', 'Поднижнечелюстная ямка — открытое ложе ниже задней части гребня.'),
16: ('volume', 'Альвеолярная часть содержит костные стенки и лунки; не равна только верхнему краю.'),
18: ('volume', 'Зубные альвеолы имеют глубину и стенки, а не только входные апертуры.'),
19: ('volume', 'Межальвеолярные перегородки — костные стенки между соседними лунками.'),
20: ('volume', 'Межкорневые перегородки — костные стенки внутри многокорневой лунки, не межзубные границы.'),
21: ('volume', 'Альвеолярные возвышения — выпуклый наружный рельеф над лунками; не сами зубы.'),
22: ('area', 'Позадимолярный треугольник — площадка позади последнего моляра, не ретромолярное отверстие.'),
23: ('area', 'Позадимолярная ямка — открытое углубление между передним краем ветви и височным гребнем; не канал.'),
24: ('volume', 'Ветвь — парная костная пластинка с толщиной, поверхностями и отростками.'),
25: ('area', 'Угол — область перехода тела в ветвь у нижнего и заднего краёв; не одна краниометрическая точка gonion.'),
26: ('area', 'Жевательная бугристость — шероховатая наружная поверхность угла; одиночная точка не задаёт её площадь.'),
27: ('area', 'Крыловидная бугристость — шероховатая медиальная поверхность угла.'),
28: ('space', 'Отверстие на медиальной стороне ветви — входная апертура канала, не весь канал.'),
29: ('volume', 'Язычок — костная пластинка у переднего края отверстия; не отверстие и не связка.'),
31: ('area', 'Челюстно-подъязычная борозда — открытое поверхностное ложе, выходящее из области отверстия; не внутрикостный канал.'),
32: ('volume', 'Венечный отросток — костная пластинка, имеющая медиальную и латеральную поверхности.'),
33: ('volume', 'Височный гребень — костный рельеф медиальной стороны венечного отростка, не шов между костями.'),
34: ('space', 'Вырезка — открытый промежуток между венечным и мыщелковым отростками; её край не равен всей вырезке.'),
35: ('volume', 'Мыщелковый отросток включает головку и шейку; не одна суставная поверхность.'),
36: ('volume', 'Головка — костный объём верхнего конца отростка; суставная поверхность покрывает лишь часть этого объёма.'),
37: ('volume', 'Шейка — суженная костная часть под головкой; не линия условного отсечения.'),
38: ('area', 'Крыловидная ямка — поверхностное углубление передней стороны шейки.'),
}
PAIRED = {6,7,8,9,12,14,15,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38}
TEXT_FIXES = {
 8: 'Костный валик наружной поверхности тела, восходящий назад к переднему краю ветви.',
12: 'Костный гребень внутренней поверхности тела, поднимающийся назад к молярам.',
25: 'Область перехода тела в ветвь у соединения нижнего и заднего краёв нижней челюсти.',
36: 'Костная головка мыщелкового отростка; её суставная поверхность и весь объём головки не тождественны.',
}

def reviewed_decisions():
    out={('mandible',f'A02.1.15.{n:03}'):dict(kind=k,reason=r,number=n) for n,(k,r) in MANDIBLE.items()}
    for n in (33,34):
        out['occipital',f'A02.1.04.{n:03}']=dict(kind='area',number=n,
            reason='Рассматривается костное ложе синуса на эндокраниальной поверхности, а не объём венозного просвета. Контур и выраженность борозды на данном образце не подтверждены.')
    out['ethmoid','A02.1.07.012']=dict(kind='volume',number=12,
        reason='Наивысшая носовая раковина — вариабельная костная пластинка решётчатой кости; не пространство носового хода. Наличие на данном образце не принято.')
    return out

def decision_sources(record):
    b,n=record['b'],int(record['c'][-3:])
    if b=='ethmoid': return [ORHAN,GOTLIB]
    if b=='occipital': return [PISOVA,DAS] if n==33 else [PISOVA,TUBBS]
    if n in (10,11): return [GRAY,SPINES]
    if n in (22,23): return [GRAY,PARK]  # ridge/triangle and original retromolar specimen study
    # Retain and explicitly reuse address-specific evidence from previous source audit.
    # These are not claimed as freshly retrieved full text (Buchanan returned 403).
    old=record['refs'][:2]
    refs=[]
    for i,r in enumerate(old):
        url=r['url']
        group=('gray_lewis_1918' if 'bartleby' in url else 'buchanan_manual' if 'Buchanan' in url else
               'source_'+url.split('/')[2])
        refs.append(ref(f'prior_{n}_{i}',r['title'],url,r['locator'],group,'previous_addressed_review'))
    if not any(r['authorGroup']=='gray_lewis_1918' for r in refs) and n not in (13,19,20,21): refs.append(GRAY)
    elif n not in (13,19,20,21): refs=[GRAY]+[r for r in refs if r['authorGroup']!='gray_lewis_1918']
    return refs

def apply_record_review(record):
    key=record['b'],record['c']; decision=reviewed_decisions().get(key)
    if decision:
        assert record['geometryKind']==decision['kind']
        record['geometryReview']=dict(status='representation_reviewed',rationale=decision['reason'],source=REPORT,
            coordinateAcceptance=False,extentAcceptance=False)
        record['refs']+=deepcopy(decision_sources(record))
        record['modelNote']+=' Проверен тип образования; точная локализация, полный контур и объём на этом образце не приняты.'
    if record['b']!='mandible': return
    n=int(record['c'][-3:])
    if n in TEXT_FIXES: record['x']=TEXT_FIXES[n]
    if n in PAIRED:
        record['lateralityReview']=dict(pattern='bilateral_on_unpaired_bone',status='coverage_unconfirmed',
            note='Образование имеется справа и слева на непарной нижней челюсти. Сохранён один прежний представительский маркер; он не подтверждает обе стороны. Координаты не зеркалировались.')
    if n in (10,11):
        record['lateralityReview']=dict(pattern='variable_midline_spines',status='coverage_unconfirmed',
            note='Подбородочные ости могут быть парными, слившимися или слабо выраженными. Один маркер не подтверждает число и раздельность остей этого образца.')

def additional_records():
    for side,label in (('right','справа'),('left','слева')):
        for key,ru,kind,desc,refs,related in (
            ('incisive_canal','Резцовый канал нижней челюсти','volume',
             'Внутрикостный ход переднего отдела нижней челюсти. Выраженность костных стенок и протяжённость вариабельны. Не путать с резцовым каналом твёрдого нёба.',[MARDINGER,ZHANG],['head_mandible_A02_1_15_030','head_mandible_A02_1_15_007']),
            ('retromolar_canal','Ретромолярный канал нижней челюсти','volume',
             'Анатомический вариант: добавочная ветвь канала нижней челюсти, выходящая в позадимолярной области. Наличие и ход на этом образце не подтверждены.',[PARK,SHEN],['head_mandible_A02_1_15_030','extra_mandible_'+side+'_retromolar_foramen']),
            ('retromolar_foramen','Ретромолярное отверстие нижней челюсти','space',
             'Анатомический вариант: апертура ретромолярного канала в позадимолярной области. Не тождественна всей позадимолярной ямке или треугольнику.',[PARK,SHEN],['extra_mandible_'+side+'_retromolar_canal','head_mandible_A02_1_15_022','head_mandible_A02_1_15_023']),
        ):
            yield dict(id='extra_mandible_'+side+'_'+key,b='mandible',t='additional',ru=ru+' '+label,lat='',x=desc,
                m=[],g='Дополнительные образования',side=side,geometryKind=kind,refs=deepcopy(refs),relatedLandmarks=related,
                educationAvailable=False,nomenclatureStatus='outside_own_TA98_list',
                geometryReview=dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False),
                modelNote='Существование образования подтверждено источниками. Его положение, границы и геометрия на этой модели не подтверждены; 3D-маркер не создан. Отдельный код TA98 не присвоен.')
