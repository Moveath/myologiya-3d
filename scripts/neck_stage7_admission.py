"""Partial educational coverage of an additional cervical muscle group."""
REFS = [
    dict(url='https://ifaa.unifr.ch/Public/EntryPage/TAH1770%20Part98A3%20EN.htm', title='FIPAT / TA98: musculi interspinales cervicis', locator='A04.3.02.304; номенклатура, не доказательство границ меша'),
    dict(url='https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/muscle-tables/muscles-of-the-back-region/', title='UAMS: Muscles of the Back Region', locator='Строка interspinales: Origin, Insertion, Action, Innervation'),
    dict(url='https://www.imaios.com/en/e-anatomy/anatomical-structures/interspinales-muscles-1541082740', title='Gray 1918 / IMAIOS: Interspinales', locator='Definition / Description: парные пучки между соседними остистыми отростками; шесть пар C2–C3…C7–T1'),
]
NOTICE = ('Учебная 3D-модель с неполным покрытием: показаны пять правых пучков C2–C7. '
          'Пучок C7–T1 отсутствует. Точные границы и площади прикреплений не подтверждены.')


def cards():
    result = {}
    for side, label in [('right','справа'),('left','слева')]:
        id = 'interspinales_cervicis_' + side
        card = dict(ru='Межостистые мышцы шеи · '+label, lat='mm. interspinales cervicis',
                    code='A04.3.02.304', side=side, g='neck_posterior', d=3, v='post', L='Глубокий слой',
                    o='Остистые отростки шейных позвонков: верхний край нижележащего отростка.',
                    i='Нижний край остистого отростка соседнего вышележащего позвонка.',
                    a='Участвуют в разгибании шеи.', n='Задние ветви спинномозговых нервов. Точные сегментарные зоны в этой модели не размечены.',
                    s='Кровоснабжение отдельных пучков в этой партии отдельно не принято.',
                    note='Шейная группа обычно включает шесть пар между C2–C3 и C7–T1. Это отдельная группа, не межостистые мышцы грудного отдела. Источник FMA71309 содержит спорные верхние фрагменты у C1–C2: они исключены из учебной производной, не перемещены и не переименованы. Пучки C7–T1 не достраивались.',
                    refs=REFS, fieldRefs={k:REFS[1:] for k in ['o','i','a','n']},
                    relatedMuscles=['interspinales_cervicis_'+('left' if side=='right' else 'right')],
                    noModel=side=='left')
        if side=='right':
            card.update(modelStatus='educational_limited', modelNotice=NOTICE,
                        modelRegionLabel='Межостистые мышцы шеи справа: C2–C7',
                        modelLicense='models/bodyparts3d-3.0/neck-stage7/ATTRIBUTION.html',
                        modelSource='FMA71309; 5 independently reviewed connected components',
                        modelFile='models/bodyparts3d-3.0/neck-stage7/interspinales_cervicis_right.glb')
        else:
            card['note'] += ' Левая производная остаётся тестовой: выявлены локальные проникновения в костные поверхности, до 1,45 мм в выборке. Основной атлас её не загружает; зеркальная замена не выполнялась.'
        result[id] = card
    return result
