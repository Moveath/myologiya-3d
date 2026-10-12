"""Russian, TA98-named metadata for the actual OpenEar ZETA segments.

Composite author meshes are explicitly composite. A nerve or vessel is never
presented as a segmented bony canal, and the main atlas pin states are unchanged.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build_head/complete_temporal'
REPORT = json.loads((OUT / 'geometry-report.json').read_text(encoding='utf-8'))
GEOMETRY = {r['id']: r for r in REPORT['structures']}


def gray(n, locator):
    return {'title': 'Gray, Anatomy of the Human Body (1918)',
            'url': f'https://commons.wikimedia.org/wiki/File:Gray{n}.png',
            'locator': f'Рис. {n}: {locator}', 'scope': 'anatomy'}


def sobotta(n, locator, year=1909):
    return {'title': f'Sobotta, Atlas and Text-book of Human Anatomy ({year})',
            'url': f'https://commons.wikimedia.org/wiki/File:Sobo_{year}_{n}.png',
            'locator': f'Рис. {n}: {locator}', 'scope': 'anatomy'}


def ta(section):
    return {'title': 'Terminologia Anatomica (TA98), IFAA',
            'url': f'https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/TA98%20EN/{section}%20TA98%20EN.htm',
            'locator': f'Раздел {section}, коды перечислены в карточке', 'scope': 'nomenclature'}


PAPER = {'title': 'Sieber et al. (2019), The OpenEar library',
         'url': 'https://doi.org/10.1038/sdata.2018.297',
         'locator': 'Data Records; Table 1 (методы сегментации); Table 2 (состав исходных файлов)',
         'scope': 'geometry'}
EAR_TABLES = {'title': 'Gest & Schlesinger, Anatomy Tables — Ear, TTUHSC El Paso',
              'url': 'https://anatomy.ttuhscep.edu/schemes/ear_tables.html',
              'locator': 'Osteology: malleus (рукоятка и внутренняя поверхность перепонки)', 'scope': 'anatomy'}
FACIAL = {**EAR_TABLES,
          'locator': 'Osteology: facial canal; Nerves: facial (ход нерва через лицевой канал)'}
CHORDA = {'title': 'McManus et al. (2012), Surgical anatomy of the chorda tympani: a micro-CT study',
          'url': 'https://ourarchive.otago.ac.nz/esploro/outputs/journalArticle/Surgical-anatomy-of-the-chorda-tympani/9926558676201891',
          'locator': 'Ход барабанной струны в височной кости и барабанной полости', 'scope': 'anatomy'}
SEMMELWEIS = {'title': 'Altdorfer & Somogyi, Connections of the skull, Semmelweis University',
              'url': 'https://semmelweis.hu/anatomia/files/2014/04/Connections-of-the-Skull.pdf#page=4',
              'locator': 'С. 4 и 6: сонный канал и внутренняя сонная артерия', 'scope': 'anatomy'}
SEMMELWEIS_VIII = {**SEMMELWEIS,
                  'url': 'https://semmelweis.hu/anatomia/files/2014/04/Connections-of-the-Skull.pdf#page=5',
                  'locator': 'С. 5: Internal acoustic meatus, содержимое — Vestibulocochlear n. (VIII)'}


def part(id, ru, lat, codes, kind, text, note, refs, section, related=(), context=False):
    g = GEOMETRY[id]
    return {'id': id, 'node': g['node'], 'kind': kind, 'ru': ru, 'title': ru,
            'lat': lat, 'c': '; '.join(codes), 'ta': codes,
            'x': text, 'modelNote': note, 'color': g['color'],
            'context': context, 'refs': refs, 'nomenclature': [ta(section)],
            'geometryRefs': [PAPER], 'sourceFile': g['source'],
            'relatedTA': list(related), 'bounds_m': g['bounds_m'],
            'vertices': g['vertices'], 'triangles': g['triangles']}


STRUCTURES = [
    part('temporal_bone', 'Височная кость — костный блок', 'os temporale', ['A02.1.06.001'], 'bone',
         'Височная кость содержит полости среднего и внутреннего уха.',
         'Поверхность построена из авторской бинарной маски OpenEar ZETA на сетке 0,125 мм. Согласно статье, кость сегментирована по КТ полного препарата, исходно полученной с шагом 0,25 мм; более мелкая сетка маски не добавляет новых измеренных деталей. Это выпиленный препарат, а не целая кость; подготовительные срезы не являются анатомическими границами. Мелкие канальцы не объявляются подтверждёнными только по числу треугольников.',
         [gray(913, 'полости и костные стенки среднего уха'), sobotta(781, 'положение лабиринтов в височных костях')], '02.1.06', context=True),
    part('malleus', 'Молоточек', 'malleus', ['A15.3.02.043'], 'bone',
         'Слуховая косточка с головкой, шейкой и рукояткой.',
         'Самостоятельная исходная сегментация одной слуховой косточки. Видна её реальная поверхность; отдельные микроструктуры и все прикрепляющиеся связки этой сеткой не реконструированы.',
         [gray(916, 'головка, шейка, рукоятка и отростки молоточка'), sobotta(793, 'молоточек и его части')], '15.3.02', ['A02.1.06.051']),
    part('incus', 'Наковальня', 'incus', ['A15.3.02.038'], 'bone',
         'Слуховая косточка с телом, длинной и короткой ножками.',
         'Самостоятельная исходная сегментация наковальни. Контакт с соседней косточкой в сетке не заменяет отдельной модели суставной щели, капсулы или связок.',
         [gray(917, 'тело, длинная и короткая ножки наковальни'), sobotta(796, 'наковальня и её суставные области')], '15.3.02', ['A02.1.06.051']),
    part('stapes', 'Стремя', 'stapes', ['A15.3.02.033'], 'bone',
         'Слуховая косточка с головкой, двумя ножками и основанием.',
         'В исходной сетке непосредственно виден просвет между ножками. Кольцевая связка и стременная мышца в этом наборе отдельно не сегментированы.',
         [gray(918, 'головка, ножки и основание стремени'), sobotta(798, 'стремя с двумя ножками и основанием')], '15.3.02', ['A02.1.06.051']),
    part('scala_tympani', 'Барабанная лестница', 'scala tympani', ['A15.3.03.045'], 'cavity',
         'Одно из спиральных пространств улитки.',
         'Цветная форма обозначает сегментированный объём пространства, а не костную стенку и не отдельный сосуд. Микроскопические мембраны и рецепторы здесь не представлены.',
         [gray(923, 'костный лабиринт и улитка'), sobotta(775, 'срез улитки и барабанная лестница', 1911)], '15.3.03'),
    part('vestibular_space', 'Лестница преддверия, преддверие и полукружные каналы',
         'scala vestibuli; vestibulum; canales semicirculares',
         ['A15.3.03.043', 'A15.3.03.004', 'A15.3.03.015'], 'cavity',
         'Пространства костного лабиринта включают преддверие, полукружные каналы и улитковую часть.',
         'Автор назвал единый файл «Scala Vestibuli», но меш содержит также преддверие и петли полукружных каналов. Они не выделены в отдельные сегменты. Цвет показывает объём пространства, а не мембранозные протоки или костную ткань.',
         [gray(923, 'полукружные каналы, преддверие и улитка'), sobotta(781, 'костные лабиринты и три полукружных канала')], '15.3.03'),
    part('facial_nerve', 'Лицевой нерв — участок в височной кости', 'nervus facialis [VII]', ['A14.2.01.099'], 'nerve',
         'Лицевой нерв проходит в височной кости по лицевому каналу.',
         'Показана авторская сегментация нерва, а не стенок канала. По описанию OpenEar мягкие ткани могли измениться при подготовке препарата; нерв может не заполнять просвет канала.',
         [gray(789, 'лицевой нерв в височной кости'), FACIAL], '14.2.01', ['A02.1.06.009', 'A02.1.06.010']),
    part('chorda_tympani', 'Барабанная струна', 'chorda tympani', ['A14.2.01.118'], 'nerve',
         'Ветвь лицевого нерва, проходящая через барабанную полость.',
         'Показан сегментированный нерв. Его узкая поверхность не является моделью стенок канальца барабанной струны.',
         [gray(788, 'барабанная струна как ветвь лицевого нерва'), CHORDA], '14.2.01', ['A02.1.06.011']),
    part('vestibulocochlear_nerve', 'Преддверно-улитковый нерв — участок у внутреннего уха',
         'nervus vestibulocochlearis [VIII]', ['A14.2.01.121'], 'nerve',
         'Нерв подходит к внутреннему уху через внутренний слуховой проход.',
         'В исходном файле Cochleovestibular Nerve объединён сегмент нерва; отдельные волокна и полный просвет внутреннего слухового прохода не выделены.',
         [SEMMELWEIS_VIII, sobotta(781, 'слуховой проход, улитковый и преддверный нервы')], '14.2.01', ['A02.1.06.033']),
    part('tympanic_membrane', 'Барабанная перепонка', 'membrana tympanica', ['A15.3.01.052'], 'membrane',
         'На внутренней поверхности барабанной перепонки закрепляется рукоятка молоточка.',
         'Это сегментированная поверхность перепонки с условным учебным цветом. Слои перепонки, натянутая и ненатянутая части отдельно не размечены.',
         [gray(919, 'барабанная перепонка и рукоятка молоточка'), EAR_TABLES], '15.3.01', ['A02.1.06.051', 'A02.1.06.053', 'A02.1.06.058']),
    part('external_acoustic_meatus', 'Наружный слуховой проход — объём', 'meatus acusticus externus', ['A15.3.01.045'], 'cavity',
         'Проход, который ведёт снаружи к барабанной перепонке.',
         'Показан объём сегментированного прохода; цветная поверхность не является костной тканью. Костная и хрящевая части не разделены на самостоятельные объекты.',
         [gray(139, 'наружный слуховой проход в разрезе'), sobotta(59, 'барабанная часть и наружный слуховой проход')], '15.3.01', ['A02.1.06.054', 'A02.1.06.055']),
    part('internal_carotid_artery', 'Внутренняя сонная артерия — участок у височной кости',
         'arteria carotis interna', ['A12.2.06.001'], 'artery',
         'Внутренняя сонная артерия проходит через сонный канал височной кости.',
         'Авторская сегментация участка артерии. Она показывает содержимое канала; это не отдельная реконструкция его костных стенок и обеих апертур.',
         [gray(513, 'внутренняя сонная артерия и её ход у основания черепа'), SEMMELWEIS], '12.2.06', ['A02.1.06.013', 'A02.1.06.014', 'A02.1.06.015']),
    part('sinus_dura', 'Сигмовидный синус и твёрдая оболочка — общий сегмент',
         'sinus sigmoideus; dura mater cranialis', ['A12.3.05.108', 'A14.1.01.102'], 'context',
         'Сигмовидный синус проходит у внутренней стороны сосцевидной области височной кости.',
         'Автор объединил синус и прилежащую твёрдую оболочку в файле Sinus Dura. Общая поверхность не позволяет выбрать их по отдельности и не является отдельной сеткой костной борозды.',
         [gray(138, 'борозда сигмовидного синуса'), sobotta(56, 'сигмовидная борозда внутренней стороны височной кости')], '12.3.05', ['A02.1.06.006'], context=True),
]


def main():
    assert len(STRUCTURES) == len(GEOMETRY) == 13
    assert all(len(s['refs']) >= 2 and all(r['locator'] for r in s['refs']) for s in STRUCTURES)
    manifest = REPORT['source']
    STRUCTURES[-1]['nomenclature'].append(ta('14.1.01'))
    result = {
        'id': 'openear', 'title': 'Внутри височной кости', 'file': 'skull-openear.glb',
        'description': 'Три слуховые косточки, пространства лабиринта, нервы, перепонка и сосудистые структуры внутри одного препарата OpenEar ZETA.',
        'modelNote': 'Опубликованные сегментации OpenEar: 12 исходных поверхностей PLY и костный блок из маски на сетке 0,125 мм. Для кости использована КТ полного препарата, исходно с шагом 0,25 мм. Сетки не упрощены; при упаковке координаты квантованы до 16 бит. Это отдельный препарат в общей системе координат, не зарегистрированный к основному черепу BodyParts3D.',
        'specimen': {'id': 'ZETA', 'title': 'Препарат OpenEar ZETA',
                     'side': 'right', 'sideEvidence': 'Имена исходных DICOM-каталогов 01_CBCT_Unembedded/DICOM_rechts_20150826_* в оригинальном архиве; геометрия не отражалась.',
                     'frameNote': 'Оси исходного файла RAS повёрнуты для просмотра. Положение структур друг относительно друга сохранено; наклон выпиленного препарата не задаёт анатомические направления всего черепа. Осевые виды и плоскости среза обозначены номерами.'},
        'source': {'title': 'OpenEar — Sieber et al. (2019), ZETA',
                   'url': 'https://zenodo.org/records/1473724', 'paper': PAPER['url']},
        'license': {'name': 'CC BY 4.0', 'url': 'https://creativecommons.org/licenses/by/4.0/',
                    'attributions': [{'title': '; '.join(manifest['authors']), 'url': PAPER['url']}]},
        'geometry': {'bytes': REPORT['bytes'], 'sha256': REPORT['sha256'],
                     'changes': REPORT['changes'], 'sampling_mm': .125,
                     'bone_source_cbct_sampling_mm': .250, 'bone_mask_grid_sampling_mm': .125,
                     'frame': REPORT['coordinate_frame'], 'registrationToBodyParts3D': False},
        'defaults': {'hidden': [], 'translucentContext': True, 'view': 'antlat'},
        'limitations': [
            'Один правый препарат, а не обе височные кости основного черепа; целая кость обрезана при получении препарата.',
            'Модель не зарегистрирована к BodyParts3D. Маркеры основного черепа на неё автоматически не переносятся.',
            'Кость сегментирована по КТ полного препарата с исходным шагом 0,25 мм и записана на сетке 0,125 мм. Шаг маски и сжатие поверхности не являются гарантией точности любого малого образования.',
            'Два исходных объекта объединяют несколько структур: Scala Vestibuli и Sinus Dura. Границы отдельных компонентов не сегментированы.',
            'Нервы и сосуды показывают сегментированные ткани, а не доказывают форму стенок соответствующих костных каналов.',
            'Индивидуальные особенности препарата и возможные ошибки исходной сегментации сохранены. Все 77 терминов височной кости не объявляются доказанными этой моделью.'
        ],
        'structures': STRUCTURES,
    }
    (OUT / 'skull-openear.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Wrote 13 reviewed structure records')


if __name__ == '__main__':
    main()
