"""Seven addressed catalogue decisions; never infer individual morphology from a source."""
from copy import deepcopy

REPORT='research/stage5-lumbopelvic-targeted-report-2026-10-18.md'
GRAY='https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf'
SOBOTTA='https://archive.org/download/atlastextbookofh01sobouoft/atlastextbookofh01sobouoft_djvu.txt'
OPEN='https://openstax.org/books/anatomy-and-physiology-2e/pages/8-3-the-pelvic-girdle-and-pelvis'

def ref(key,title,url,locator,group,**kw):
    return dict(id='lp_target_'+key,title=title,url=url,locator=locator,authorGroup=group,checked='2026-10-18',**kw)

PREAURICULAR=[
 ref('preauricular','Waltenberger L, Pany-Kucera D, Rebay-Salisbury K, Mitteroecker P (2021; online 2020). The association of parturition scars and pelvic shape: A geometric morphometric study.',
     'https://pmc.ncbi.nlm.nih.gov/articles/PMC7898533/','Introduction: preauricular/paraglenoid sulcus; Materials and Methods: variable expression, not an individual diagnostic rule.','waltenberger_2021',pmid='33295660',doi='10.1002/ajpa.24196',access='full_text'),
 ref('gray_preauricular','Gray / Lewis (1918)',GRAY,'PDF p.231: preauricular sulcus near auricular surface.','gray_1918',access='previously_reviewed_text'),
 ref('sobotta_preauricular','Sobotta; ed. McMurrich (1914), Atlas and Text-book of Human Anatomy, vol. I',SOBOTTA,'Printed p.95, paragraph on inner ala: paraglenoidal groove; Fig.133 mentioned in text, not newly inspected.','sobotta_1914',access='digitized_text')]
OBTURATOR=[
 ref('sobotta_obturator','Sobotta; ed. McMurrich (1914), vol. I',SOBOTTA,'Printed pp.95–96, paragraph beginning The obturator groove: posterior tubercle arises from ischium.','sobotta_1914',access='digitized_text'),
 ref('gray_obturator','Gray / Lewis (1918)',GRAY,'PDF p.234: posterior obturator tubercle on ischial border.','gray_1918',access='previously_reviewed_text')]
COCCYX=[
 ref('sobotta_coccyx','Sobotta; ed. McMurrich (1914), vol. I',SOBOTTA,'Printed p.29: apex notch completed by Co1 transverse process and ligaments; The Coccyx: transverse processes distinct from cornua.','sobotta_1914',access='digitized_text'),
 ref('gray_coccyx','Gray / Lewis (1918)',GRAY,'PDF pp.44–45: Co1 transverse processes and sacrococcygeal passages, separate from cornua.','gray_1918',access='previously_reviewed_text'),
 ref('bookshelf_coccyx','Mostafa E, Varacallo MA. Anatomy, Back, Coccygeal Vertebrae. StatPearls; updated 2023-06-05.',
     'https://www.ncbi.nlm.nih.gov/sites/books/NBK549870/','Structure and Function: transverse elements. Not used to infer that all segments are fused or equally developed.','mostafa_varacallo',access='full_text',nbk='NBK549870')]
SCIATIC=[
 ref('open_sciatic','OpenStax Anatomy & Physiology 2e',OPEN,'Pelvis, paragraph after Fig.8.14: greater notch, sacrum, sacrospinous ligament; distinction from lesser opening.','openstax',access='full_text'),
 ref('carro_sciatic','Perez Carro L et al. (2016). Deep gluteal space problems: piriformis syndrome, ischiofemoral impingement and sciatic nerve release.',
     'https://pmc.ncbi.nlm.nih.gov/articles/PMC5193530/','Indexed anatomical paragraph: outer edge of sacrum, greater sciatic notch, sacrospinous ligament. Full page returned reCAPTCHA; only this explicit passage used.','carro_2016',pmid='28066745',doi='10.11138/mltj/2016.6.3.384',access='indexed_text')]
NUTRIENT=[
 ref('bv_tzika','Tzika M, Paraskevas GK, Piagkou M, Papatolios AK, Natsis K (2021). Basivertebral foramina of true vertebrae: morphometry, topography and clinical considerations.',
     'https://pubmed.ncbi.nlm.nih.gov/33598754/','Abstract, Purpose and Results: posterior body wall, variable number and form; no study dimensions transferred.','tzika_2021',pmid='33598754',doi='10.1007/s00276-021-02690-0',access='abstract'),
 ref('bv_standard','Anatomy Standard — Typical Lumbar Vertebra (updated 2020-11-24)',
     'https://www.anatomystandard.com/ossa-et-juncturae/columna-vertebralis/vertebra-lumbalis-typica.html','Back oblique view of L3: venous opening on posterior body. Does not define counts for all levels.','anatomy_standard',access='text'),
 ref('vascular_dartmouth','Dartmouth — Basic Human Anatomy, Chapter 39',
     'https://humananatomy.host.dartmouth.edu/BHA/public_html/part_7/chapter_39.html','Parts of a Vertebra: vascular foramina on body sides.','dartmouth_bha',access='text')]
MAMILLO=[
 ref('maigne','Maigne JY, Maigne R, Guerin-Surville H (1991). The lumbar mamillo-accessory foramen: a study of 203 lumbosacral spines.',
     'https://pubmed.ncbi.nlm.nih.gov/1905063/','Abstract: ossification of mamillo-accessory ligament; individual variability.','maigne_1991',pmid='1905063',doi='10.1007/BF01623137',access='indexed_abstract'),
 ref('mahato','Mahato NK (2014). Mamillo-accessory notch and foramen: distribution patterns and correlation with superior lumbar facet structure.',
     'https://pubmed.ncbi.nlm.nih.gov/24889272/','Abstract and indexed publisher results: notch categories and foramen, independent specimen series.','mahato_2014',pmid='24889272',doi='10.1016/j.morpho.2014.03.002',access='indexed_abstract')]
TRANSITION=[
 ref('konin','Konin GP, Walz DM (2010). Lumbosacral transitional vertebrae: classification, imaging findings, and clinical relevance.',
     'https://pubmed.ncbi.nlm.nih.gov/20203111/','Previously checked indexed abstract: lumbarization/sacralization and numbering.','konin_walz_2010',pmid='20203111',doi='10.3174/ajnr.A2036',access='previously_reviewed_indexed_abstract'),
 ref('nagata','Nagata S et al. (2025). Lumbosacral transitional vertebra on whole-spine CT: prevalence and association with rib abnormalities.',
     'https://pubmed.ncbi.nlm.nih.gov/40381031/','Abstract: whole-spine CT, separate transitional and rib configurations; not evidence of a variant in BodyParts3D.','nagata_2025',pmid='40381031',doi='10.1007/s00256-025-04952-z',access='indexed_abstract')]

def review(p):
    bone=p['b'];code=p.get('c');changed=False
    def append(text,refs):
        nonlocal changed
        p['x']=p.get('x','')+' '+text;p['refs']=p.get('refs',[])+deepcopy(refs);changed=True
    if bone.startswith('lumbar_'):
        if code=='A02.2.01.002':
            append('Сосудистые отверстия тела не тождественны позвоночному или межпозвоночному отверстию. Базивертебральные отверстия задней стенки выделены отдельно; число, просветы и боковые сосудистые отверстия данного образца не размечены.',NUTRIENT)
            p['relatedLandmarks']=p.get('relatedLandmarks',[])+[f'extra_{bone}_basivertebral_foramina']
        if code in ('A02.2.04.002','A02.2.04.004'):
            append('Вариант: при окостенении связки между сосцевидным и добавочным отростками может возникать костное сосцевидно-добавочное отверстие (mamillo-accessory foramen). Это не обязательное отверстие каждого позвонка. Наличие справа/слева на этой модели не установлено; самостоятельные экземпляры варианта не созданы.',MAMILLO)
            p['relatedLandmarks']=list(dict.fromkeys(p.get('relatedLandmarks',[])+[f'context_{bone}_'+c.replace('.','_') for c in ('A02.2.04.002','A02.2.04.004') if c!=code]))
        if bone in ('lumbar_1','lumbar_5') and code=='A02.2.04.003':
            append('Отдельное поясничное ребро, удлинённый рёберный отросток и переходный позвонок не являются одним объектом. Варианты сакрализации/люмбализации рассматриваются отдельно. Нумерация этой модели сохранена по исходному каталогу; для её пересмотра нужны полный позвоночник и согласованные изображения того же образца.',TRANSITION)
    if code=='A02.5.01.312' and bone in ('hip_bone','hip_bone_left'):
        p['partOf']=f'extra_{bone}_ischium';p['nomenclatureGroup']='A02.5.01.301'
        p['x']='Непостоянный задний запирательный бугорок на седалищном крае запирательного отверстия. Он уже представлен этим ID; отдельный синоним не создаётся. Группа TA98 «лобковая кость» сохранена как номенклатурная, а анатомическая связь с седалищной частью основана на Gray и Sobotta.'
        p['anatomicalDefinition']=p['x'];p['geometryKindReason']=p['x']
        p['modelNote']='Каталожная группа TA98 не является маской части; наличие бугорка и границы седалищной части на конкретной стороне не приняты.'
        p['refs']+=deepcopy(OBTURATOR);changed=True
    if p['id'].endswith('_greater_sciatic_foramen') and bone in ('hip_bone','hip_bone_left'):
        append('В костных границах участвует также край крестца; связки остаются отдельными мягкотканными участниками. Общая запись доступна из обеих костей, без нового экземпляра.',SCIATIC)
        p.update(relations=[dict(bone=b,role='boundaryContribution',refs=[r['id'] for r in SCIATIC]) for b in (bone,'sacrum')],catalogueBones=[],anchors=[])
    if p['id']=='coc_os_coccygis':
        append('Поперечные отростки первого копчикового позвонка отличаются от его верхних рогов. Они представлены отдельной групповой карточкой; граница Co1 на объединённой модели пока не принята.',COCCYX)
        p['relatedLandmarks']=p.get('relatedLandmarks',[])+['extra_sacrum_coccyx_transverse_processes']
    if p['id']=='extra_sacrum_sacrococcygeal_joint':
        append('У боков верхушки крестца выемки дополняются поперечными отростками Co1 и связками до проходов. Это не добавленная пятая пара внутрикрестцовых отверстий. Терминальные проходы S5 пока описаны здесь без отдельных точек и без утверждения замкнутого костного контура.',COCCYX)
        p['relatedLandmarks']+=['extra_sacrum_coccyx_transverse_processes']
    if changed:p['targetedReview']=dict(source=REPORT,anatomyScope='catalogue_definition',specimenPresenceAccepted=False)
    return p

def extra_records(bones):
    def make(b,key,ru,kind,text,refs,**kw):
        return dict(id=f'extra_{b}_{key}',b=b,t='additional',ru=ru,lat='',x=text,g='Дополнительные образования',m=[],p=None,n=None,
            geometryKind=kind,geometryKindReason=text,refs=deepcopy(refs),educationAvailable=False,
            nomenclatureStatus='descriptive_term_without_assigned_TA98_code',targetedReview=dict(source=REPORT,specimenPresenceAccepted=False),**kw)
    for bone in ('hip_bone','hip_bone_left'):
        if bone not in bones:continue
        side='left' if bone.endswith('_left') else 'right';label='слева' if side=='left' else 'справа'
        yield make(bone,'preauricular_sulcus','Предушковидная борозда '+label+' (вариант)','area',
            'Вариабельное углубление у нижнего края ушковидной поверхности подвздошной части; английские названия preauricular sulcus / paraglenoid sulcus обозначают одну структуру. Полная борозда требует разметки поверхности, не случайной точки. Наличие в этом образце не установлено; по карточке нельзя определять пол или историю родов.',PREAURICULAR,
            side=side,inc=1,applicability='variant_presence_unverified',partOf=f'extra_{bone}_ilium',relatedLandmarks=['cox_facies_auricularis' if side=='right' else 'context_hip_bone_left_A02_5_01_121'])
    if 'sacrum' in bones:
        yield make('sacrum','coccyx_transverse_processes','Поперечные отростки первого копчикового позвонка','volume',
            'Парные латеральные костные выступы Co1; отличаются от направленных вверх копчиковых рогов. Групповая карточка не означает принятия обеих сторон или выделения Co1 в исходной модели.',COCCYX,
            partOf='coc_os_coccygis',anatomicalOwner='coccyx',anatomicalMultiplicity='paired',relatedLandmarks=['coc_cornu_coccygeum','extra_sacrum_sacrococcygeal_joint'])
    for i in range(1,6):
        bone=f'lumbar_{i}'
        if bone not in bones:continue
        yield make(bone,'basivertebral_foramina',f'Базивертебральные отверстия тела L{i}','space',
            'Сосудистые отверстия задней стенки тела (basivertebral foramina), ведущие во внутрикостные каналы. Не позвоночное отверстие и не все сосудистые отверстия боковых стенок. Число и форма вариабельны; это групповая карточка без заданных центров, количества просветов или внутренних контуров.',NUTRIENT,
            anatomicalMultiplicity='multiple',partOf=f'context_{bone}_A02_2_01_002',relatedLandmarks=[f'context_{bone}_A02_2_01_002'])
