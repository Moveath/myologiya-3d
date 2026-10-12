"""Package locally confirmed temporal-bone surface features in OpenEar's frame.

A visible wall is not a reconstruction of a complete channel. Source scan and
author segmentation are reviewed independently of the nomenclature catalogue.
"""
from pathlib import Path
import hashlib
import json
import ta98
import head_terms  # extends the TA98 table

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build_head/temporal_features'


def ref(author, fig, locator):
    filename = f'Gray{fig}' if author == 'Gray' else f'Sobo_1909_{fig}'
    return {'title': 'Gray, Anatomy of the Human Body (1918)' if author == 'Gray' else
            'Sobotta, Atlas and Text-book of Human Anatomy (1909)',
            'url': f'https://commons.wikimedia.org/wiki/File:{filename}.png',
            'locator': f'Рис. {fig}: {locator}', 'scope': 'anatomy'}


CONFIG = {
    'carotid_external_aperture': {
        'scope':'aperture_rim',
        'x':'Наружная апертура сонного канала находится на нижней поверхности каменистой части, впереди яремной ямки. Отмечен участок её костного края.',
        'refs':[ref('Gray',141,'наружный вход сонного канала перед яремной ямкой'),
                ref('Sobotta',58,'наружная апертура сонного канала на нижней поверхности')],
        'modelNote':'Костный край проверен на исходной маске и зарегистрированной КТ полного препарата ZETA. В подготовленном embedded-скане часть этой области уже обрезана, поэтому для подтверждения использован full-specimen CBCT. Маркер края не подтверждает весь внутрикостный ход сонного канала; модель артерии не заменяет его стенки.',
        'scan':'full',
    },
    'stylomastoid_foramen': {
        'scope':'aperture_rim',
        'x':'Шилососцевидное отверстие расположено между шиловидным и сосцевидным отростками. Здесь отмечен видимый костный край наружного окончания лицевого канала.',
        'refs':[ref('Gray',141,'шилососцевидное отверстие между двумя отростками'),
                ref('Sobotta',58,'шилососцевидное отверстие возле основания шиловидного отростка')],
        'modelNote':'Край отверстия сопоставлен с костной маской и исходной КТ полного препарата ZETA. Для этой области подготовленный embedded-скан обрезан и не использовался как подтверждение сохранности края. Выход авторского сегмента лицевого нерва служит топографическим контекстом, а подтверждение кости получено отдельно. Полный лицевой канал этим маркером не объявляется проверенным.',
        'scan':'full',
    },
    'internal_acoustic_meatus': {
        'scope': 'channel_wall_segment',
        'x': 'Внутренний слуховой проход направляется от внутреннего слухового отверстия в толщу каменистой части. Здесь отмечен видимый участок его костной стенки.',
        'refs': [ref('Gray',140,'внутренний слуховой проход в рассечённой пирамиде'),
                 ref('Sobotta',781,'внутренний слуховой проход рядом с лабиринтом')],
        'modelNote': 'Подтверждён отдельный участок стенки прохода на исходной маске и зарегистрированной КТ OpenEar ZETA. Разметка не утверждает, что отдельно проверены все поля дна, отверстия и мелкие ответвления. Сегмент нерва VIII использован только для топографического сопоставления; он не заменяет костную стенку.',
    },
    'external_acoustic_meatus': {
        'scope': 'channel_wall_segment',
        'x': 'Наружный слуховой проход ведёт от наружного слухового отверстия к барабанной перепонке. Маркер расположен на видимом участке его костной стенки.',
        'refs': [ref('Gray',137,'наружное слуховое отверстие и костная часть прохода'),
                 ref('Sobotta',55,'наружный слуховой проход и барабанная часть')],
        'modelNote': 'Выбран участок костной стенки, совпадающий с границей кости на зарегистрированной КТ ZETA. Это не маркер барабанной перепонки и не маркер полного кожного канала. Полная протяжённость прохода и все детали барабанного кольца отдельно не заявлены.',
    },
    'tympanic_cavity': {
        'scope': 'cavity_wall_segment',
        'x': 'Барабанная полость находится в височной кости медиальнее барабанной перепонки. Здесь показан участок её костной стенки в области, доступной после экранного среза.',
        'refs': [ref('Gray',913,'вскрытая барабанная полость и её медиальная костная стенка'),
                 ref('Sobotta',59,'вскрытая височная кость: полость и окно преддверия')],
        'modelNote': 'Участок стенки подтверждён на костной маске и исходной КТ OpenEar ZETA. Срез только убирает закрывающую его часть существующей сетки; новых стенок не создаёт. Одна точка не означает отдельную сегментацию всей полости и не завершает список всех её образований.',
        'cut': {'plane':'sagittal','value':(-.026-(-.0627555996))/(.017369403711299997-(-.0627555996)), 'reverse':False},
    },
}

CROSS_VIEWS={
    'internal_acoustic_meatus':[1,1,.25],
    'external_acoustic_meatus':[-.8,-1,.3],
    'carotid_external_aperture':[.3,0,1],
    'stylomastoid_foramen':[.3,.15,1],
    'tympanic_cavity':[-1,.2,.1],
}


def main():
    picks = json.loads((OUT / 'verified-picks.json').read_text(encoding='utf-8'))
    sha = hashlib.sha256((ROOT / 'site/skull-openear.glb').read_bytes()).hexdigest()
    markers = []
    for row in picks:
        if row['id'] not in CONFIG:
            continue
        cfg = CONFIG[row['id']]
        lat, ru, _ = ta98.T[row['c']]
        marker = {'id':'openear_temporal_'+row['id'], 'b':'temporal_bone', 'mode':'openear',
                  'c':row['c'], 'ru':ru, 'lat':lat, 'p':row['p'], 'n':row['n'],
                  'loc':'surface','source':'OpenEar','specimen':'ZETA','side':'right',
                  'view':dict(row['v'],distance=.045),
                  'x':cfg['x'], 'modelNote':cfg['modelNote'], 'refs':cfg['refs'],
                  'geometryScope':cfg['scope'], 'scope':cfg['scope'],
                  'completeFeatureGeometry':False,
                  'geometryRefs':[{'title':'Sieber et al., OpenEar ZETA',
                                   'url':'https://zenodo.org/records/1473724',
                                   'locator':'ZETA.zip: 07_3D_Models/Bone.nrrd; 05_Registred_Slicer_Volumes/'+('CBCT_Unembedded.nrrd' if cfg.get('scan')=='full' else 'CBCT_Embedded.nrrd'),
                                   'scope':'geometry'}],
                  'nomenclature':[{'title':'Terminologia Anatomica (TA98), IFAA',
                                   'url':'https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/TA98%20EN/02.1.06%20TA98%20EN.htm',
                                   'locator':row['c'],'scope':'nomenclature'}],
                  'evidence': {'method':'native-multiview-surface-inspection-plus-source-cbct',
                               'geometry_sha256':sha,'faceIndex':row['faceIndex'],
                               'view':row['v'],'uv':row['uv'],'zoomBox':row['box'],
                               'coordinateFrame':'OpenEar ZETA author RAS → [-RASx,RASz,RASy], metres; no registration to BodyParts3D.',
                               'screenshot':f'build_head/temporal_features/{row["id"]}-review.png',
                               'crossView':{'d':CROSS_VIEWS[row['id']],'up':row['v']['up']},
                               'crossScreenshot':f'build_head/temporal_features/{row["id"]}-cross-review.png',
                               'scanScreenshot':f'build_head/temporal_features/{row["id"]}-cbct'+('-full' if cfg.get('scan')=='full' else '')+'.png',
                               'scanProof':'Исходный зарегистрированный CBCT, три координатных сечения через выбранный участок; сопоставлена костная граница и авторская маска, проверены соседние структуры.',
                               'review':'Выбор координаты выполнен после визуального сопоставления с двумя независимыми атласами. Это не внешняя экспертная рецензия.'}}
        if 'cut' in cfg:
            marker['cut']=cfg['cut']
        markers.append(marker)
    data={'source':'OpenEar','specimen':'ZETA','mode':'openear','side':'right',
          'geometry_sha256':sha,'complete':False,
          'scope':'Подтверждённые локальные участки геометрии; полнота каналов и всей височной кости не заявляется.',
          'markers':markers}
    (ROOT / 'pins_head/temporal-native-features.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {len(markers)} native OpenEar temporal features')


if __name__ == '__main__':
    main()
