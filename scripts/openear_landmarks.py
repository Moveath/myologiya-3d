"""Package eight directly reviewed OpenEar ossicle landmarks, without mesh changes.

These are a supplemental, explicitly partial set. They do not replace the full
TA98 lists or the localization states on the BodyParts3D temporal bones.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'build_head/openear_landmarks'

TERMS = {
    'malleus_head': ('Головка молоточка', 'caput mallei', 'Расширенная часть молоточка над его шейкой.'),
    'malleus_neck': ('Шейка молоточка', 'collum mallei', 'Суженный участок между головкой и основанием рукоятки молоточка.'),
    'malleus_handle': ('Рукоятка молоточка', 'manubrium mallei', 'Удлинённая часть молоточка ниже его шейки.'),
    'incus_body': ('Тело наковальни', 'corpus incudis', 'Основная расширенная часть наковальни, от которой отходят её ножки.'),
    'incus_long_limb': ('Длинная ножка наковальни', 'crus longum', 'Длинный отросток, отходящий от тела наковальни.'),
    'incus_short_limb': ('Короткая ножка наковальни', 'crus breve', 'Короткий отросток, отходящий от тела наковальни.'),
    'stapes_head': ('Головка стремени', 'caput stapedis', 'Расширенная часть стремени со стороны схождения двух ножек.'),
    'stapes_base': ('Основание стремени', 'basis stapedis', 'Пластинка, соединяющая концы двух ножек стремени.'),
}


def references(bone):
    gray, sobotta, locator = {
        'malleus': (916, 793, 'головка, шейка и рукоятка молоточка'),
        'incus': (917, 796, 'тело, длинная и короткая ножки наковальни'),
        'stapes': (918, 798, 'головка, ножки и основание стремени'),
    }[bone]
    return [
        {'title': 'Gray, Anatomy of the Human Body (1918)',
         'url': f'https://commons.wikimedia.org/wiki/File:Gray{gray}.png',
         'locator': f'Рис. {gray}: {locator}', 'scope': 'anatomy'},
        {'title': 'Sobotta, Atlas and Text-book of Human Anatomy (1909)',
         'url': f'https://commons.wikimedia.org/wiki/File:Sobo_1909_{sobotta}.png',
         'locator': f'Рис. {sobotta}: {locator}', 'scope': 'anatomy'},
    ]


def main():
    picks = json.loads((REVIEW / 'picks.json').read_text(encoding='utf-8'))
    assert len(picks) == len(TERMS) == 8
    markers = []
    for row in picks:
        ru, lat, text = TERMS[row['id']]
        assert len(row['p']) == len(row['n']) == 3
        view = dict(row['v'], distance=.020 if row['b'] != 'stapes' else .012)
        if row['id'] == 'stapes_base':
            view = {'d': [0, 1, 0], 'up': [0, 0, 1], 'distance': .012}
        elif row['b'] == 'stapes':
            view = {'d': [0, 0, 1], 'up': [-1, -2, 0], 'distance': .012}
        marker = {
            'id': 'openear_' + row['id'], 'b': row['b'], 'c': row['c'],
            'ru': ru, 'lat': lat, 'p': row['p'], 'n': row['n'], 'x': text,
            'refs': references(row['b']), 'loc': 'surface',
            'source': 'OpenEar', 'specimen': 'ZETA', 'side': 'right',
            'view': view,
            'modelNote': 'Отмечен видимый участок исходной поверхности слуховой косточки OpenEar ZETA. Это отдельный правый препарат; точка не перенесена на BodyParts3D и не означает отдельную сегментацию всей части косточки.',
            'nomenclature': [
                {'title': 'Terminologia Anatomica (TA98), IFAA',
                 'url': 'https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/TA98%20EN/15.3.02%20TA98%20EN.htm',
                 'locator': row['c'], 'scope': 'nomenclature'},
                {'title': 'Международная анатомическая терминология, под ред. Л. Л. Колесникова (2003)',
                 'url': 'https://rsmu.ru/fileadmin/templates/DOC/Faculties/PF/Dept_latin_language/Kolesnikov_-_Terminologia_Anatomica_1.pdf',
                 'locator': f'Печатная с. 196, {row["c"]}; для ножек добавлено название кости для однозначности карточки.',
                 'scope': 'nomenclature'},
            ],
            'geometryRefs': [{'title': 'Sieber et al. (2019), The OpenEar library — ZETA',
                              'url': 'https://zenodo.org/records/1473724',
                              'locator': {'malleus': '03_Malleus.ply', 'incus': '04_Incus.ply', 'stapes': '05_Stapes.ply'}[row['b']],
                              'scope': 'geometry'}],
            'evidence': {
                'method': 'manual-multiview-surface-review-and-raycast',
                'view': row['v'], 'uv': row['uv'], 'faceIndex': row['faceIndex'],
                'coordinateFrame': 'OpenEar ZETA native specimen; author RAS transformed by [-RASx,RASz,RASy], metres. No registration to BodyParts3D.',
                'source': 'build_head/openear_landmarks/picks.json',
                'screenshot': f'build_head/openear_landmarks/{row["b"]}-markers.png',
                'review': 'Поверхность осмотрена из нескольких направлений, форма сопоставлена с независимыми рисунками Gray и Sobotta. Номера граней относятся к опубликованному GLB, а не исходным PLY. Луч выбирает координату на уже распознанном образовании; само попадание луча не считается анатомической проверкой.'
            }
        }
        markers.append(marker)
    result = {
        'source': 'OpenEar', 'specimen': 'ZETA', 'side': 'right',
        'geometry_sha256': hashlib.sha256((ROOT / 'site/skull-openear.glb').read_bytes()).hexdigest(),
        'complete': False,
        'scope': 'Восемь отдельно проверенных поверхностных ориентиров слуховых косточек. Это не полный список образований среднего уха и не замена 521 маркеру основного черепа.',
        'markers': markers,
        'groups': [
            {'id': 'ossicles', 'ru': 'Слуховые косточки', 'parts': ['malleus', 'incus', 'stapes'],
             'view': {'d': [1, 0, 0], 'up': [0, 0, -1], 'distance': .029},
             'screenshot': 'build_head/openear_landmarks/ossicles-group.png'},
            {'id': 'labyrinth', 'ru': 'Пространства лабиринта', 'parts': ['scala_tympani', 'vestibular_space'],
             'view': {'d': [1, .4, .5], 'up': [0, 0, -1], 'distance': .045},
             'screenshot': 'build_head/openear_landmarks/labyrinth-group.png'},
            {'id': 'nerves', 'ru': 'Нервы', 'parts': ['facial_nerve', 'chorda_tympani', 'vestibulocochlear_nerve'],
             'view': {'d': [1, 0, 0], 'up': [0, 0, -1], 'distance': .075},
             'screenshot': 'build_head/openear_landmarks/nerves-group.png'},
        ],
    }
    (ROOT / 'pins_head/openear-native.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report = {
        'source': 'OpenEar ZETA', 'geometry_sha256': result['geometry_sha256'],
        'new_surface_landmarks': len(markers), 'temporal_bone_projection_promotions': 0,
        'completion_claim': False,
        'anatomical_review': 'Машинная геометрическая проверка и визуальное сопоставление с двумя атласами; не выдаётся за внешнюю экспертную рецензию анатома.',
        'bone_mask_review': 'Осмотрены шесть координатных направлений, область внутреннего слухового прохода с нервом VIII и срез на y=0.044 м. Шумная поверхность и подготовительные границы блока не позволяют уверенно отделить все костные апертуры и стенки мелких каналов. Новые костные каналы и их точки не заявлены.',
        'orientation': 'Сохранены векторы камеры в координатах образца; направления сетки не названы анатомическими видами тела. Препарат ориентирован произвольно относительно осей сканера.',
        'not_marked': [
            'Передний и латеральный отростки молоточка: отдельный уверенный выбор этих малых отростков не завершён.',
            'Чечевицеобразный отросток наковальни: не выдан за независимый подтверждённый участок лишь по близости к стремени.',
            'Передняя и задняя ножки стремени: просвет и обе ножки видны, но отдельное анатомическое различение сторон не подтверждено одним заголовком RAS.',
            'Отдельные компоненты общего сегмента Scala Vestibuli не разделены; цветной объём не является костной стенкой.'
        ],
        'markers': [{'id': m['id'], 'code': m['c'], 'bone': m['b']} for m in markers],
    }
    (ROOT / 'research/openear-landmark-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Wrote 8 OpenEar native landmarks; no BodyParts3D state changes')


if __name__ == '__main__':
    main()
