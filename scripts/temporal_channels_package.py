"""Describe the checked channel-wall subset, preserving its limited scope."""
import json,hashlib
import ta98,head_terms
from temporal_channels_probe import ROOT,OUT

def source(title,url,locator,scope='anatomy'):
    return {'title':title,'url':url,'locator':locator,'scope':scope}

GEOMETRY=source('Sieber et al. (2019), OpenEar ZETA','https://zenodo.org/records/1473724',
                'ZETA.zip: 07_3D_Models/Bone.nrrd; 05_Registred_Slicer_Volumes/CBCT_Unembedded.nrrd и CBCT_Embedded.nrrd. Маска и две зарегистрированные КТ одного препарата.','geometry')
CONFIG={
 'facial_canal_wall':{'code':'A02.1.06.009','ru':'Лицевой канал — выбранные стенки',
   'description':'Лицевой канал проходит в височной кости от дна внутреннего слухового прохода к шилососцевидному отверстию. Здесь отдельно показан протяжённый участок его костной стенки, выделенный на исходной маске OpenEar ZETA.',
   'modelNote':'Стенки выделены из исходной костной маски; модель нерва использована только для выбора области проверки. Проверены 224 последовательных положения косой плоскости вдоль направляющей длиной около 27,9 мм. Продолжение к внутреннему слуховому проходу проверено по КТ подготовленного препарата; неидентифицированная конечная ветвь исключена. Это не измерение полного канала: стенка местами неполна, открытые края и сообщения сохранены. Мелкие ответвления, обе апертуры и точная форма неразличимых тонких стенок не объявлены завершёнными.',
   'refs':[source('Gray, Anatomy of the Human Body (1918), рис. 140 и 913','https://commons.wikimedia.org/wiki/File:Gray913.png','Рис. 913: ход лицевого канала относительно барабанной полости и шилососцевидного отверстия; рис. 140: внутренний слуховой проход.'),
           source('Kozerska et al. (2017), Micro-CT study of the dehiscences of the tympanic segment of the facial canal','https://doi.org/10.1007/s00276-016-1744-4','Введение и рис. 1: начало, окончание, три сегмента канала и его положение относительно барабанной полости; рис. 2–4: костная стенка и её разрывы.')]},
 'carotid_canal_wall':{'code':'A02.1.06.013','ru':'Сонный канал — фрагмент стенки',
   'description':'Сонный канал расположен в каменистой части височной кости между наружной апертурой на нижней поверхности и внутренней апертурой у верхушки. Отдельно выделены сохранившиеся участки костной стенки вдоль просвета.',
   'modelNote':'Показаны существующие стенки исходной Bone.nrrd вдоль направляющей длиной около 12,7 мм, проверенные по 103 косым сечениям КТ полного препарата. В большинстве положений маска не замыкает контур; существующие стенки выделены и там, а разрывы сохранены. Это не полный закрытый канал. Модель артерии использована только как ориентир области проверки. Подготовленный препарат местами обрезан; полную КТ и отсутствие стенки в маске нельзя подменять дорисованной трубкой.',
   'refs':[source('Gray, Anatomy of the Human Body (1918), рис. 138, 141 и 913','https://commons.wikimedia.org/wiki/File:Gray141.png','Рис. 141: наружная апертура; рис. 138: внутренняя апертура у верхушки; рис. 913: сонный канал во вскрытой височной кости.'),
           source('Sobotta, Atlas and Text-book of Human Anatomy (1909), рис. 57–58','https://commons.wikimedia.org/wiki/File:Sobo_1909_58.png','Рис. 58: наружная апертура сонного канала; рис. 57: внутренняя апертура у верхушки каменистой части.')]},
}

def main():
    report=json.loads((OUT/'geometry-report.json').read_text());views=json.loads((OUT/'reviewed-views.json').read_text());objects=[]
    for row in report['structures']:
        cfg=CONFIG[row['id']];lat,ru,_=ta98.T[cfg['code']];v=next(x for x in views if x['id']==row['id'] and x['suffix']=='view1');v={k:v[k] for k in ['d','up','distance','target']}
        objects.append({'id':row['id'],'ru':cfg['ru'],'lat':lat,'ta98':cfg['code'],'description':cfg['description'],'modelNote':cfg['modelNote'],'refs':cfg['refs'],'geometryRefs':[GEOMETRY],
                        'view':v,'color':'#d7ab5c' if row['id'].startswith('facial') else '#cf8580','scope':'channel_wall_segment','completeFeatureGeometry':False,
                        'source':'OpenEar','specimen':'ZETA','side':'right','evidence':row,'slices':row['id']})
    payload={'title':'Костные стенки каналов: OpenEar ZETA','mode':'channels','file':report['geometry_file'],'sha256':report['geometry_sha256'],
             'contextFile':report['context_file'],'contextSha256':report['context_sha256'],'slicesFile':'skull-temporal-channel-slices.json','source':'OpenEar ZETA','sourceUrl':'https://zenodo.org/records/1473724','license':'CC BY 4.0',
             'attribution':'Daniel Manuel Sieber, Peter Erfurt, Samuel John, Gabriel Ribeiro dos Santos, Daniel Schurzig, Mads Sølvsten Sørensen, Thomas Lenarz — OpenEar (2019).',
             'coordinateFrame':report['coordinate_frame'],'structures':objects,'complete_channel_geometry_claim':False,
             'context':{'id':'temporal_context','ru':'Кость вокруг каналов — вырезка исходной маски','lat':'Os temporale','context':True,
                        'modelNote':'Контекст ограничен прямоугольной областью исходных данных. Открытые края этой выборки не являются анатомическими отверстиями. Плоские крышки и отсутствующие стенки не добавлялись.'},
             'changes':['Из исходной Bone.nrrd извлечена поверхность без разрежения маски и без децимации.','Отобраны проверенные участки существующих треугольников; отверстия не заделывались, крышки не добавлялись.','Применено то же преобразование осей и мм → м, что у OpenEar; регистрация к BodyParts3D не выполнялась.','Для браузера использованы meshopt и 16-битное квантование координат.'],
             'limitations':['Это два набора выделенных костных стенок, а не завершённые каналы.','КТ полного препарата получена с шагом 0,25 мм, КТ подготовленного препарата — 0,125 мм. Зарегистрированные сетки и костная маска имеют шаг 0,125 мм. Источник указан у каждого кадра. Шаг сетки не равен анатомической точности.','Открытый контур маски сам по себе не доказывает анатомическую дегисценцию: тонкая стенка может не разрешаться на КТ или не войти в сегментацию.'],
             'limitationRefs':[source('Comparison of cone beam-computed and micro-computed tomography data for measuring facial canal dehiscence (2025)','https://pubmed.ncbi.nlm.nih.gov/40296137/','Результаты и выводы: CBCT и микро-КТ по-разному выявляют тонкую костную стенку.','imaging_limits')]}
    for target in [OUT/'skull-temporal-channels.json',ROOT/'pins_head/temporal-channels.json']:
        target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    audit={'source':'OpenEar ZETA','question':'Можно ли получить полные костные каналы, а не поверхность нерва/артерии?','outcome':'Два проверенных фрагмента стенок; полные каналы не подтверждены.','geometry':report,
           'reviewed_source_sections':{'facial':224,'carotid':103},'anatomical_sources':{k:v['refs'] for k,v in CONFIG.items()},
           'facial_entire_guide_review':{'planes':226,'closed_bone_mask_contours':216,'not_closed':10,'exported_planes':224,'limits':'Число замкнутых контуров не подтверждает стенку по всей окружности с анатомической точностью. После сравнения CBCT полного и подготовленного препарата выборка расширена по сохранившимся костным стенкам; открытый контур сам по себе не исключает стенку из выборки. Неразличимые тонкие стенки не дорисованы.'},
           'facial_terminal_review':{'original_longest_author_nerve_branch_rejected_as_endpoint':True,'unclassified_long_branch_excluded':True,'short_branch_connection_to_IAC_seen_in_source_CBCT':True,'independent_reviewer':'skull_cranial_features','reviewer_conclusion':'Узкий кортикально ограниченный ход рядом с улиткой непрерывно расширяется до IAC. Согласуется с лабиринтным продолжением. Место коленчатого узла и длинная развилка отдельно не подтверждены.','source_images':['facial-endpoint-axis1-embedded.png','facial-endpoint-axis2-embedded.png','facial-proximal-candidate.png'],'navigation_parameters':json.loads((OUT/'facial-oblique.json').read_text())['terminal_navigation_review'],'export_limit':'Выборка останавливается внутри узкого продолжения перед расширением в IAC. Полнота апертуры не объявлена.'},
           'carotid_entire_guide_review':{'planes':103,'closed_bone_mask_contours':15,'not_closed':88,'limits':'В большинстве проверенных положений костная маска не замыкает контур; по выбранному набору полный просвет без догадки не сегментирован.'},
           'raw_roi_files':'build_head/temporal_channels/*-voxel-roi.npz и *-source-selection.npz; только исследовательский кэш, не сайт.',
           'reviewed_images':[str(p.relative_to(ROOT)).replace('\\','/') for p in sorted(OUT.glob('skull-channel-*-slices-*.png'))],
           'source_geometry_verification':json.loads((OUT/'source-geometry-verification.json').read_text()),
           'next_needed':'Для полного канала необходима отдельная проверка конечных отверстий и тонких стенок на более детальных исходных срезах или другом открытом препарате; разрывы текущей маски не замыкать.'}
    (ROOT/'research/temporal-channel-review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Prepared metadata for',len(objects),'actual wall patches')

if __name__=='__main__':main()
