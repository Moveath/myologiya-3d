"""Individual educational admission; never inferred from availability of an OBJ."""
NOTICE='Учебная 3D-модель. Точные границы, площади прикреплений и контакты с соседними структурами не подтверждены.'
ROOT_URL='https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip'
SOURCES={
 'puborectalis_right':dict(fma='FMA45856',side='right',sha256='676488c532a2788e9b4f7fa214157b95ae5c89925463c77c00f540d6d90bf7f4'),
 'puborectalis_left':dict(fma='FMA45857',side='left',sha256='e11fedb7d4590844ba4e9750d886938b1183fff16a92629925f294aa8240208b'),
}
REFS=[
 dict(url='https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/TA98%20EN/04.5.04%20TA98%20EN.htm',title='FIPAT / TA98: диафрагма таза',locator='A04.5.04.002–.008; puborectalis A04.5.04.007'),
 dict(url='https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/muscle-tables/muscles-of-the-pelvis-and-perineum/',title='UAMS: мышцы таза и промежности',locator='Строка puborectalis: Origin, Insertion, Action; отдельные строки pubococcygeus и iliococcygeus'),
 dict(url='https://www.ncbi.nlm.nih.gov/sites/books/NBK556078/',title='NCBI Bookshelf: Levator Ani Muscle',locator='Gowda, Bordoni; 26.10.2022; Structure and Function / Origin, Course, and Insertion; Muscles; Physiologic Variants'),
 dict(url='https://pubmed.ncbi.nlm.nih.gov/15229017/',title='Kearney et al., 2004: состав levator ani',locator='PMID 15229017; DOI 10.1097/01.AOG.0000128906.61529.6b; Table 3 в PMC1415268. Обзор женских препаратов; не измерение этой 3D-модели'),
]
def cards():
 out={}
 for id,source in SOURCES.items():
  out[id]=dict(ru='Лобково-прямокишечная мышца · '+('правая'if source['side']=='right'else'левая'),
   lat='m. puborectalis',code='A04.5.04.007',g='pelvic_floor',d=3,v='pelvsup',side=source['side'],
   L='компонент мышцы, поднимающей задний проход',
   o='Задняя поверхность лобковой кости.',
   i='Волокна соединяются с противоположной стороной позади прямой кишки, образуя мышечную петлю.',
   a='Участвует в поддержании аноректального угла и удержании кала.',
   n='Точная схема иннервации этой части требует отдельной сверки; данные всей levator ani не приписываются ей автоматически.',
   s='Кровоснабжение этой части отдельно не принято; схема сосудов в модели не представлена.',
   note='Это самостоятельный компонент levator ani, а не синоним pubococcygeus. Общая форма BodyParts3D показана без реконструкции внутренних органов. Пол и индивидуальные параметры конкретного образца не установлены; модель не описывает варианты женского тазового дна. Сохраняются небольшие самопересечения и перекрытия с соседними сетками; точная граница раздела не принята.',
   refs=REFS,fieldRefs={key:REFS[1:3]for key in ['o','i','a']},
   noModel=False,modelStatus='educational_limited',modelNotice=NOTICE,
   modelRegionLabel='Лобково-прямокишечные мышцы',modelLicense='models/bodyparts3d-3.0/muscles-stage7/ATTRIBUTION.html',
   modelFile=f'models/bodyparts3d-3.0/muscles-stage7/{id}.glb',modelSource=source['fma'],
   relatedMuscles=['levator_ani','puborectalis_left'if source['side']=='right'else'puborectalis_right'])
 return out
