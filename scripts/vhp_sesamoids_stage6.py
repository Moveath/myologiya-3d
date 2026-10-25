"""Educational admission of the four MCP-I sesamoids from the Visible Human Male CT (method F).

Never full acceptance: a different body, 1 mm CT, visual identification, placement by registering
the CT I metacarpal to the BodyParts3D I metacarpal. Applied by make_context_bone_data.py.
"""
REPORT = 'research/stage6-vhp-thumb-sesamoids-2026-10-25.md'
BASE = 'models/vhp-male/thumb-sesamoids'
BONES = ('sesamoid_mcp1_radial_right', 'sesamoid_mcp1_ulnar_right', 'sesamoid_mcp1_radial_left', 'sesamoid_mcp1_ulnar_left')
NOTICE = ('Учебная реконструкция по КТ другого тела (Visible Human Male, NLM): форма сглажена разрешением '
          'КТ 0,94×0,94×1 мм, положение получено совмещением I пястной кости КТ с моделью атласа. '
          'Суставные фасетки, ладонная пластинка и точная форма не подтверждены.')
NOTE = ('Источник модели: КТ замороженного тела Visible Human Male (NLM), срезы 1700–1849. '
        'Пара узелков у ладонной поверхности головки I пястной кости опознана визуально на срезах; '
        'сегментация и поверхность построены автоматически; КТ-кость I пястной совмещена с I пястной '
        'BodyParts3D той же стороны (подобие, масштаб 1,003–1,007; медианная ошибка 0,75–0,80 мм). '
        'Лучевая/локтевая определены по положению: локтевая ближе ко II пястной кости и к приводящей '
        'мышце (её сухожилие прикрепляется к локтевому сесамоиду), лучевая прилежит к короткому сгибателю (прикрепляется к лучевому); в модели сухожилие длинного сгибателя проходит рядом с обеими. '
        'Размеры около 4–5 мм. Это не модель образца BodyParts3D и не независимая анатомическая приёмка.')


# Muscle relations used to check radial/ulnar identity after placement (two sources each).
RELATION_REFS = [
    ('IMAIOS e-Anatomy — Adductor pollicis', 'https://www.imaios.com/en/e-anatomy/anatomical-structures/adductor-pollicis-14218352',
     'Insertion: "primary insertion is onto the ulnar sesamoid bone and the ulnar side of the base of the proximal phalanx".'),
    ('Ebraheim N. — Anatomy of adductor pollicis (Orthopaedic Principles)', 'https://orthopaedicprinciples.com/anatomy-of-adductor-pollicis/',
     'Insertion: "The tendon inserts into the ulnar sesamoid bone of the thumb."'),
    ('Wheeless — Flexor pollicis brevis', 'https://www.wheelessonline.com/bones/hand/flexor-pollicis-brevis/',
     'Discussion: tendon "inserts into radial sesamoid & radial tubercle of proximal phalanx".'),
    ('IMAIOS e-Anatomy — Flexor pollicis brevis', 'https://www.imaios.com/en/e-anatomy/anatomical-structures/flexor-pollicis-brevis-14218224',
     'Superficial head: sesamoid "embedded within its insertion tendon"; insertion on the radial side of the proximal phalanx base.'),
]


def admit(cards):
    for bone in BONES:
        card = cards[bone]
        assert card.get('noModel') is True, 'Do not replace a functioning model'
        card.update(noModel=False, modelStatus='educational_limited', modelNotice=NOTICE,
                    modelRegionLabel='Сесамовидные кости I пальца (КТ Visible Human)',
                    modelFile=f'{BASE}/{bone}.glb', modelLicense=f'{BASE}/LICENSE-MODELS.txt',
                    modelAttribution='Courtesy of the U.S. National Library of Medicine · условия и изменения',
                    modelOrigin=dict(dataset='NLM Visible Human Project, Male, frozen CT', slices=[1700, 1849],
                                     registration='CT I metacarpal -> BodyParts3D I metacarpal, rigid + uniform scale'),
                    modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT,
                                     admissionRule='external_ct_registered_to_atlas_bone'),
                    note=NOTE)
        for title, url, locator in RELATION_REFS:
            card['refs'].append(dict(title=title, url=url, locator=locator, scope='sesamoid_muscle_relation', checked='2026-10-25'))
        card['refs'].append(dict(title='Courtesy of the U.S. National Library of Medicine — Visible Human Project (Male CT)',
                                 url='https://www.nlm.nih.gov/research/visible/getting_data.html',
                                 locator='radiological/frozenCT, slices 1700–1849; NLM Terms and Conditions',
                                 scope='geometry_provenance', checked='2026-10-25'))
