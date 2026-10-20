"""Reviewed relations only. Never infer bone membership from a launch/view list.

Names/codes/descriptions are reused from the existing frozen skull catalogue.
These are reference-anatomy relations, not segmentation claims for this specimen.
"""
from skull_whole_terms import TERMS, GRAY_URL

def ref(id,title,url,locator,group,access='full_text'):
    return dict(id=id,title=title,url=url,locator=locator,authorGroup=group,kind='anatomical',checked='2026-10-15',access=access)

def gray(id,page,locator):
    return ref('gray_'+id,'Gray / Lewis (1918)',GRAY_URL+'#page='+str(page),f'PDF p. {page}: '+locator,'gray_lewis_1918')

CRANIOMETRY=[gray('craniometry',173,'Craniometry: Nasion, Bregma, Lambda, Pterion, Asterion; sutures pp. 155–157'),
    ref('vigo_2020','Vigo et al. Immersive Surgical Anatomy of the Craniometric Points (2020)',
        'https://assets.cureus.com/uploads/technical_report/pdf/31561/1592247735-20200615-9766-fz9gxn.pdf',
        'Sutures and Suture junctions, PDF pp. 4–9; DOI 10.7759/cureus.8643','vigo_2020')]
ORBIT=[gray('orbit',161,'The Orbits: roof, floor, medial wall; continuation p. 162: lateral wall, ethmoidal foramina; inferior fissure also pp. 128, 132, 135'),
    ref('shumway_orbit','Shumway, Motlagh, Wade. Anatomy, Head and Neck, Orbit Bones (2023)',
        'https://www.ncbi.nlm.nih.gov/sites/books/NBK531490/',
        'Introduction; Walls of the Orbit; Lateral Orbital Wall; Orbital Foramina, Fissures, and Ducts','shumway_orbit')]
ARCH=[ref('openstax_arch','OpenStax Anatomy and Physiology 2e, 7.2',
          'https://openstax.org/books/anatomy-and-physiology-2e/pages/7-2-the-skull','Lateral View of Skull; Figure 7.5','openstax'),
      ref('yu_zygomatic','Yu, Wang. Anatomy, Head and Neck, Zygomatic',
          'https://ncbi.nlm.nih.gov/sites/books/NBK544257/?report=reader','Structure and Function, zygomatic arch','yu_wang')]
PALATE=[gray('palate',152,'Norma Basalis: hard palate; Palatine horizontal plate p. 132'),
    ref('openstax_palate','OpenStax Anatomy and Physiology 2e, 7.2',
        'https://openstax.org/books/anatomy-and-physiology-2e/pages/7-2-the-skull','Maxillary Bone; Palatine Bone; Figure 7.8(a)','openstax')]
CLIVUS=[gray('clivus',166,'Posterior Fossa, groove anterior to foramen magnum; Sphenoid p. 103'),
    ref('clivus_29955940','A comprehensive review of the clivus: anatomy, embryology, variants, pathology, and surgical approaches (2018)',
        'https://pubmed.ncbi.nlm.nih.gov/29955940/','Abstract, Introduction: basioccipital and basisphenoid','clivus_2018','abstract')]
LACERUM=[gray('lacerum',153,'Norma Basalis, triangular aperture at petrous apex'),
    ref('statpearls_lacerum','Anatomy, Head and Neck: Foramen Lacerum, StatPearls',
        'https://www.ncbi.nlm.nih.gov/sites/books/NBK541026/','Structure and Function, first paragraph','statpearls_lacerum')]
SPHENOPALATINE=[gray('sphenopalatine',134,'Palatine: superior border and sphenopalatine notch'),
    ref('souza_raggio','Souza, Raggio. Anatomy, Head and Neck, Sphenopalatine Foramen (2023)',
        'https://www.ncbi.nlm.nih.gov/sites/books/NBK549911/','Introduction; Structure and Function, Boundaries','souza_raggio')]
ZYGOMAX=[gray('zygomax',162,'The Orbits, base: maxilla and zygomatic united by zygomaticomaxillary suture'),
    ref('yu_zygomax','Yu, Wang. Anatomy, Head and Neck, Zygomatic',
        'https://ncbi.nlm.nih.gov/sites/books/NBK544257/?report=reader','Structure and Function, first two paragraphs','yu_wang')]
KOSHI=ref('koshi_skull','Koshi. Cunningham’s Manual of Practical Anatomy, 16th ed., Vol. 3',
    'https://api.pageplace.de/preview/DT0400.9780192516480_A35505968/preview-9780192516480_A35505968.pdf#page=29',
    'Printed p. 18 / PDF p. 29: Posterior cranial fossa, clivus and petro-occipital fissure','koshi_cunningham','publisher_preview')
CLIVUS.append(KOSHI)
PETRO_OCCIPITAL=[gray('petro_occipital',166,'Posterior Fossa: petro-occipital fissure beside clivus'),KOSHI]

# number, bones (a {side} placeholder creates two instances), role, evidence.
# A component is different from a boundary of an opening; context is not either.
DEFINITIONS=[
 (15,['frontal','nasal_right','nasal_left'],'boundaryContribution',CRANIOMETRY),
 (16,['frontal','parietal_right','parietal_left'],'boundaryContribution',CRANIOMETRY),
 (17,['occipital','parietal_right','parietal_left'],'boundaryContribution',CRANIOMETRY),
 (19,['frontal','parietal_{side}','temporal_{side}','sphenoid'],'boundaryContribution',CRANIOMETRY),
 (20,['occipital','parietal_{side}','temporal_{side}'],'boundaryContribution',CRANIOMETRY),
 (23,['zygomatic_{side}','temporal_{side}'],'component',ARCH),
 (47,['occipital','temporal_{side}'],'boundaryContribution',PETRO_OCCIPITAL),
 (55,['sphenoid','temporal_{side}','occipital'],'boundaryContribution',LACERUM),
 (56,['maxilla_right','maxilla_left','palatine_right','palatine_left'],'component',PALATE),
 (67,['frontal','sphenoid','ethmoid','maxilla_{side}','zygomatic_{side}','lacrimal_{side}','palatine_{side}'],'boundaryContribution',ORBIT),
 (75,['frontal','sphenoid'],'component',ORBIT),
 (76,['maxilla_{side}','zygomatic_{side}','palatine_{side}'],'component',ORBIT),
 (77,['zygomatic_{side}','sphenoid'],'component',ORBIT),
 (78,['ethmoid','lacrimal_{side}','maxilla_{side}','sphenoid'],'component',ORBIT),
 (79,['frontal','ethmoid'],'boundaryContribution',ORBIT),
 (80,['frontal','ethmoid'],'boundaryContribution',ORBIT),
 (84,['sphenoid','maxilla_{side}','palatine_{side}','zygomatic_{side}'],'boundaryContribution',ORBIT),
 (97,['palatine_{side}','sphenoid'],'boundaryContribution',SPHENOPALATINE),
]

def additional_instances(terminology):
    for number,bone_patterns,role,refs in DEFINITIONS:
        paired=any('{side}' in b for b in bone_patterns) or number in {75,79,80}
        for side in ['right','left'] if paired else [None]:
            bones=[b.format(side=side) for b in bone_patterns]
            code=f'A02.1.00.{number:03}'
            ru=TERMS[number]['ru']
            if 75<=number<=78:ru+=' глазницы'
            if side:ru+=' · '+('справа' if side=='right' else 'слева')
            note='Связи отражают типовой костный состав по источникам. Точка, полный контур и индивидуальные варианты на этой модели не подтверждены; координаты не создавались.'
            if number in {19,20,84}:note+=' Возможны варианты состава шва/края; наличие варианта на данном образце не установлено.'
            yield dict(id=f'shared_skull_{number:03}'+('_'+side if side else ''),concept=f'skull-whole-{number:03}',
                       c=code,b=bones[0],t='ta',lat=terminology[code],ru=ru,x=TERMS[number]['description'],
                       side=side,m=[],g='Общие образования черепа',catalogueBones=[],anchors=[],
                       relationScope='reference_anatomy',modelNote=note,refs=refs,
                       relations=[dict(bone=b,role=role,refs=[r['id'] for r in refs]) for b in bones])
