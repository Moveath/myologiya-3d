"""Reviewed lumbar entities; no inferred points, mirrored sides or surface masks."""
from copy import deepcopy
from lumbar_terms import T, OPENSTAX, GRAY_GENERAL
from lumbopelvic_targeted_review import review as targeted_review, extra_records as targeted_records

REPORT='research/stage5-lumbar-report-2026-10-18.md'
DAR='https://humananatomy.host.dartmouth.edu/BHA/public_html/part_7/chapter_39.html'

def source(key,title,url,locator,group,**extra):
    return dict(id=key,title=title,url=url,locator=locator,authorGroup=group,
                checked='2026-10-18',kind='anatomical',**extra)

FORAMEN_REFS=[
 source('lumbar_gray_foramen','Gray / Lewis (1918)',GRAY_GENERAL['url'],
        'PDF p.25, vertebral notches; p.53, Lateral Surfaces.','gray_lewis_1918'),
 source('lumbar_openstax_foramen','OpenStax Anatomy & Physiology 2e',OPENSTAX['url'],
        'General Structure of a Vertebra, Fig.7.24: adjacent pedicles and disc; Lumbar Vertebrae.','openstax'),
 source('lumbar_amonoo_1988','Amonoo-Kuofi HS, el-Badawi MG, Fatani JA, Butt MM (1988). Ligaments associated with lumbar intervertebral foramina. 2. The fifth lumbar level.',
        'https://pubmed.ncbi.nlm.nih.gov/3248957/','Abstract: L5 and S1 bodies, disc and foraminal ligaments. No dimensions transferred.',
        'amonoo_1988',pmid='3248957',access='abstract',doiStatus='not_returned_by_NCBI')]
PARS_REFS=[
 source('lumbar_dartmouth_pars','Dartmouth — Basic Human Anatomy, Chapter 39',DAR,
        'Lumbar Vertebrae: pars between superior and inferior articular processes.','dartmouth_bha'),
 source('lumbar_clifton_2019','Clifton W, Williams D, Damon A, Dove C, Pichelmann M (2019). The Importance of the Pars Interarticularis as a Landmark for Safe Lumbar Pedicle Screw Placement: Technical Note.',
        'https://pmc.ncbi.nlm.nih.gov/articles/PMC6559435/','Technical report, first paragraph: lumbar pars connects facets and is continuous with posterior elements.',
        'clifton_2019',pmid='31245201',doi='10.7759/cureus.4413',access='full_text')]

# Each entry describes the entity, rather than inferring a type from its name.
GENERAL={
 2:('volume','Тело — опорная костная часть с толщиной, не одна площадка.'),
 3:('area','Две площадки тела, верхняя и нижняя, обращены к дискам.'),
 4:('volume','Периферическая зона окостенения тела; возрастная граница не равна нарисованному ободку.'),
 5:('volume','Дуга состоит из костных ножек и пластинок, окружает просвет сзади.'),
 6:('volume','Парные ножки соединяют тело с задними элементами.'),
 7:('volume','Парные пластинки имеют толщину и формируют заднюю часть дуги.'),
 9:('space','Открытая выемка верхнего края ножки; лишь вклад в межпозвоночное отверстие.'),
 10:('space','Открытая выемка нижнего края ножки; не отдельный замкнутый канал.'),
 11:('space','Просвет между телом и дугой, а не точка на стенке.'),
 12:('volume','Срединный костный отросток от основания до конца.'),
 13:('volume','Общий термин латерального отростка; в пояснице соотносится с региональными рёберным и добавочным элементами.'),
 14:('volume','Парные костные отростки, несущие верхние суставные площадки.'),
 15:('area','Собственная контактная площадка верхнего отростка, не весь сустав.'),
 16:('volume','Парные костные отростки, несущие нижние суставные площадки.'),
 17:('area','Собственная контактная площадка нижнего отростка, не соседняя кость.'),
}
REGIONAL={
 2:('volume','Костный выступ позади основания латерального отростка; выраженность индивидуальна.'),
 3:('volume','Протяжённый латеральный костный элемент, не отдельное свободное ребро.'),
 4:('volume','Костное возвышение сзади верхнего суставного отростка.'),
}
KINDS={**{f'A02.2.01.{n:03}':v for n,v in GENERAL.items()},
       **{f'A02.2.04.{n:03}':v for n,v in REGIONAL.items()}}
PAIRED={f'A02.2.01.{n:03}' for n in (6,7,9,10,13,14,15,16,17)}|{f'A02.2.04.{n:03}' for n in (2,3,4)}

def requirement(p):
    if p.get('concept')=='intervertebral-foramen':
        needed='Совмещённые соседние кости, диск и мягкотканные границы того же образца; отдельная приёмка просвета справа и слева. Вырезки не являются центрами отверстия.'
    elif p.get('c')=='A02.2.01.004':
        needed='Возраст/стадия сращения и изображения зон окостенения данного образца; наружная взрослая сетка не определяет эпифиз.'
    else:
        needed={'volume':'Принятая сегментация костной части и её границ.',
                'area':'Принятая маска всей поверхности.',
                'space':'Принятые границы выемки или просвета.'}[p['geometryKind']]
        if p.get('anatomicalMultiplicity') in ('paired','superior_inferior'):
            needed+=' Обе стороны/площадки проверять отдельно.'
    p['geometryRequirements']=dict(status='unverified_extent',coordinateReuse=False,neededEvidence=needed,source=REPORT)
    p['geometryReview']=dict(status='representation_reviewed',source=REPORT,coordinateAcceptance=False,extentAcceptance=False)
    p['modelNote']=p.get('modelNote','')+' '+needed
    return p

def review(p):
    if not p['b'].startswith('lumbar_'):return p
    code=p['c'];kind,reason=KINDS[code]
    p.update(geometryKind=kind,geometryKindReason=reason,
        anatomicalMultiplicity='paired' if code in PAIRED else ('superior_inferior' if code in ('A02.2.01.003','A02.2.01.004') else 'single'))
    if code in ('A02.2.01.013','A02.2.04.002','A02.2.04.003'):
        codes=('A02.2.01.013','A02.2.04.002','A02.2.04.003')
        p['relatedLandmarks']=['context_'+p['b']+'_'+c.replace('.','_') for c in codes if c!=code]
        p['x']+=' Общий поперечный термин и региональные элементы не означают три независимых одинаковых выступа; исходные коды сохранены.'
    if code=='A02.2.01.007':
        p['relatedLandmarks']=[f'extra_{p["b"]}_pars_interarticularis_{s}' for s in ('right','left')]
    return requirement(targeted_review(p))

def additional_records():
    for p in targeted_records({f'lumbar_{i}' for i in range(1,6)}):yield requirement(p)
    for i in range(1,6):
        bone=f'lumbar_{i}';parent=f'context_{bone}_A02_2_01_007'
        for side,label in [('right','справа'),('left','слева')]:
            yield requirement(dict(id=f'extra_{bone}_pars_interarticularis_{side}',b=bone,t='additional',
                ru=f'Межсуставная часть дуги L{i} {label}',lat='pars interarticularis',side=side,
                g='Дополнительные образования',m=[],p=None,n=None,geometryKind='volume',
                geometryKindReason='Костный перешеек между суставными отростками; имеет объём, не только контур.',
                x='Часть задних костных элементов между верхним и нижним суставными отростками одной стороны. Не сустав между двумя позвонками и не новая самостоятельная кость.',
                refs=deepcopy(PARS_REFS),partOf=parent,relatedLandmarks=[parent],educationAvailable=False,
                nomenclatureStatus='descriptive_term_without_TA98_code',
                modelNote='Подтверждено понятие, а не сегментация данного образца. Отдельный код TA98 не назначен; координаты не созданы.'))

def shared_records():
    levels=[('thoracic_12','lumbar_1','T12–L1','t12_l1')]+[(f'lumbar_{i}',f'lumbar_{i+1}',f'L{i}–L{i+1}',f'l{i}_l{i+1}') for i in range(1,5)]+[('lumbar_5','sacrum','L5–S1','l5_s1')]
    for upper,lower,level,key in levels:
        for side,label in [('right','справа'),('left','слева')]:
            refs=deepcopy(FORAMEN_REFS if lower=='sacrum' else FORAMEN_REFS[:2])
            related=[('thorax_' if upper=='thoracic_12' else 'context_')+upper+'_A02_2_01_010']
            if lower!='sacrum':related.append('context_'+lower+'_A02_2_01_009')
            # Sacral intrabony foramina are not the L5-S1 interval.
            yield requirement(dict(id=f'shared_lumbar_intervertebral_{key}_{side}',b=lower if upper=='thoracic_12' else upper,
                t='ta',c='A02.2.01.008',lat=T['A02.2.01.008'][0],ru=f'Межпозвоночное отверстие {level} {label}',
                level=level,side=side,concept='intervertebral-foramen',g='Общие образования поясничного отдела',m=[],
                x='Проход между соседними позвонками. Кости участвуют в границах; диск и мягкие ткани также необходимы для полного описания. Это пространство, не сустав и не отверстие одной кости.',
                relations=[dict(bone=b,role='boundaryContribution',refs=[r['id'] for r in refs]) for b in (upper,lower)],
                relatedLandmarks=related,refs=refs,catalogueBones=[],anchors=[],p=None,n=None,geometryKind='space',educationAvailable=False,
                modelNote='Уровень и стороны задают разные экземпляры. Подтверждены участники; точка, контур и размеры не назначены.'))
