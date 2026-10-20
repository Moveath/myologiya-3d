"""Reviewed multi-bone instances; terminology remains in the skull-wide catalogue.

Relations describe anatomy, b is only the legacy navigation owner. Coordinates
are a separate reviewed input and are never synthesized from related bones.
"""
from skull_whole_terms import TERMS
from shared_landmark_catalogue import additional_instances, CLIVUS, ZYGOMAX
from skull_shared_stage5 import additional_instances as stage5_instances
from head_skull_batch2 import additional_instances as batch2_instances
from head_skull_batch3 import additional_instances as batch3_instances

def source(id, title, url, locator, group, access='full_text'):
    return dict(id=id,title=title,url=url,locator=locator,authorGroup=group,kind='anatomical',checked='2026-10-15',access=access)


SINUS_SOURCES = [
    source('gray_sinus_tarsi','Gray / Lewis (1918)',
           'https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf#page=277',
           'PDF p. 277: Calcaneus, superior surface; p. 283: Talus, inferior surface', 'gray_lewis_1918'),
    source('stella_sinus_tarsi','Stella et al. Sonographic visibility of the sinus tarsi with a 12 MHz transducer',
           'https://pmc.ncbi.nlm.nih.gov/articles/PMC4879007/',
           'Introduction, first paragraph; Conclusions, first paragraph', 'stella_ultrasound'),
]


def patch(id, bones, refs, role='boundaryContribution', **fields):
    return dict(id=id,relations=[dict(bone=b,role=role,refs=[r['id'] for r in refs]) for b in bones],
                refs=refs,catalogueBones=[bones[0]],**fields)


def existing_patches():
    # Decorate the existing object; retain its ID, TA code, description and raw p/n.
    yield patch('cal_sinus_tarsi',['calcaneus','talus'],SINUS_SOURCES,
                concept='tarsal-sinus',side='right',anchorStatus='unverified',anchors=[],
                modelNote='Пазуха связана с таранной и пяточной костями. Старая точка лежит на латеральной поверхности пяточной кости; точное положение в пазухе не подтверждено при осмотре Blender. Координата сохранена для проверки, но маркер и наведение на неё отключены. Новая точка не создавалась.')
    yield patch('head_occipital_A02_1_04_006',['occipital','sphenoid'],CLIVUS,role='component',
                concept='skull-whole-051',educationCode='A02.1.00.051',geometryKind='area',
                modelNote='Скат включает затылочный и клиновидный вклады. Старый ID и код затылочного каталога сохранены. Существующий маркер находится на затылочном участке ската, что проверено в Blender; он не обозначает всю поверхность обеих костей.')
    for side in ['right','left']:
        yield patch(f'head_maxilla_{side}_A02_1_12_012',[f'maxilla_{side}',f'zygomatic_{side}'],ZYGOMAX,
                    concept='zygomaticomaxillary-suture',side=side,geometryKind='line',anchorStatus='unverified',anchors=[],
                    modelNote='Один шов связан с верхней челюстью и скуловой костью своей стороны. Близость старой точки к обеим сеткам измерена в Blender, но её точное положение на шве визуально не подтверждено. Координата сохранена; маркер временно скрыт. Полная линия шва не размечена.')

SOURCES = [
    dict(id='gray_1918_jugular', title='Gray / Lewis, Anatomy of the Human Body (1918)',
         url='https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf#page=153',
         locator='PDF, страница 153 (индекс 152): External Surface of the Base, абзац Behind the carotid canal…',
         authorGroup='gray_lewis_1918', kind='anatomical', checked='2026-10-15'),
    dict(id='singh_das_2023_jugular', title='Singh O, Das JM. Anatomy, Head and Neck: Jugular Foramen (обновление 03.04.2023)',
         url='https://www.ncbi.nlm.nih.gov/sites/books/NBK538507/',
         locator='Introduction; Structure and Function, первый абзац: височная кость спереди, затылочная сзади',
         authorGroup='singh_das_statpearls', kind='anatomical', checked='2026-10-15'),
]


def instances(terminology=None):
    """Right/left are distinct instances; each is shared by two bones."""
    for side, label in [('right', 'правое'), ('left', 'левое')]:
        yield dict(
            id='shared_jugular_foramen_' + side,
            concept='skull-whole-054', c='A02.1.00.054', side=side,
            b='temporal_' + side, t='ta', lat='foramen jugulare',
            ru=TERMS[54]['ru'] + ' · ' + label,
            x=TERMS[54]['description'], m=[], g='Общие образования черепа',
            relations=[dict(bone=bone, role='boundaryContribution', refs=[r['id'] for r in SOURCES])
                       for bone in ['temporal_' + side, 'occipital']],
            refs=SOURCES,
            anchors=[], geometryKind='space',
            catalogueBones=[],
            modelNote='Связь с обеими костями подтверждена источниками. Точная точка и полный контур отверстия на этой модели пока не подтверждены; координаты не созданы.',
        )
    if terminology is not None:
        yield from additional_instances(terminology)
        yield from stage5_instances(terminology)
        yield from batch2_instances(terminology)
        yield from batch3_instances(terminology)
