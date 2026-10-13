"""Small bone-only lumbar supplement; no invented surface coordinates.

TA98 generic/regional terms are applied editorially, not official per-bone counts.
The electronic IFAA spelling mammillaris is retained; Kolesnikov prints mamillaris.
"""
from pathlib import Path
import json
from neck_terms import T as NT, DESCRIPTIONS as ND, ref, IFAA_URL, GRAY_URL, OPENSTAX, GRAY_GENERAL

AS_URL = 'https://www.anatomystandard.com/ossa-et-juncturae/columna-vertebralis/vertebra-lumbalis-typica.html'
GRAY = ref('Gray (1918) — The Lumbar Vertebrae', GRAY_URL+'#page=35', 'PDF с.35–37, The Lumbar Vertebrae; Fig.92–94; Fifth Lumbar Vertebra.')
AS = ref('Anatomy Standard — Typical Lumbar Vertebra', AS_URL, 'L3: front, top, side and back oblique views; подписанные поверхности и отростки.')
T = {c:v for c,v in NT.items() if c.startswith('A02.2.01.')}
T.update({
 'A02.2.04.001':('vertebrae lumbales [L I - L V]','Поясничные позвонки [L I–L V]',''),
 'A02.2.04.002':('processus accessorius','Добавочный отросток',''),
 'A02.2.04.003':('processus costiformis; processus costalis','Рёберный отросток',''),
 'A02.2.04.004':('processus mammillaris','Сосцевидный отросток',''),
 'A02.2.00.007':('lordosis lumbalis','Поясничный лордоз',''),
})
for c in ('A02.2.00.001','A02.2.00.009'): T[c]=NT[c]
DESCRIPTIONS={c:dict(v) for c,v in ND.items() if c in T}
# The cervical ring-apophysis studies in neck_terms do not attest lumbar levels.
DESCRIPTIONS['A02.2.01.004']=dict(x='Кольцевая краевая область тела позвонка.',refs=[AS,ref('Gray (1918) — Ossification of the Vertebral Column',GRAY_URL+'#page=46','PDF с.46, Ossification of the Vertebral Column: secondary centers на верхней и нижней поверхностях тела; Fig.103.')],scope='anatomy',note='Возрастную стадию и границы эпифиза нельзя установить по внешней сетке взрослой кости.')
for c,x in {
 'A02.2.04.002':'Небольшой выступ сзади у основания латерального отростка поясничного позвонка.',
 'A02.2.04.003':'Латерально направленный рёберный отросток поясничного позвонка.',
 'A02.2.04.004':'Выступ на задней стороне верхнего суставного отростка.',
}.items(): DESCRIPTIONS[c]=dict(x=x,refs=[GRAY,AS],scope='anatomy')
DESCRIPTIONS['A02.2.04.004']['note']='В электронной IFAA написание mammillaris, в русском издании Колесникова — mamillaris; это орфографическое различие названия одного образования.'
DESCRIPTIONS['A02.2.04.001']=dict(x='Пять поясничных позвонков между грудным отделом и крестцом.',refs=[GRAY,OPENSTAX],scope='anatomy')
DESCRIPTIONS['A02.2.00.007']=dict(x='Поясничный изгиб позвоночного столба выпуклостью вперёд.',refs=[ref('Gray (1918) — Vertebral Column as a Whole',GRAY_URL+'#page=52','PDF с.52, Curves — lumbar curve.'),OPENSTAX],scope='anatomy')
DESCRIPTIONS['A02.2.01.013']=dict(x='Общее название бокового отростка позвонка. В поясничной области его соотношение с рёберным и добавочным отростками требует региональной терминологии.',refs=[GRAY,AS],scope='anatomy',note='Не обозначает дополнительный независимый выступ рядом с рёберным отростком. В разных учебных описаниях термин transverse process применяется к латеральному отростку в более широком смысле.')
WHOLE_TERMS=['A02.2.00.001','A02.2.00.007','A02.2.00.009','A02.2.01.008','A02.2.04.001']
APPLICABILITY_NOTE='Общие и поясничные списки TA98 применены к L1–L5 редакционно по анатомическим источникам; это не отдельные официальные количества IFAA для каждого позвонка. Каталог не подтверждает форму конкретной сетки.'
APPLICATION_NOTES={f'lumbar_{i}':'Общие образования позвонка и три поясничных отростка. Межпозвоночное отверстие и поясничный изгиб относятся к нескольким структурам; вынесены в общий список. Общий поперечный и региональный рёберный отростки не следует считать двумя отдельными одинаковыми выступами.' for i in range(1,6)}
GENERAL=[f'A02.2.01.{i:03}' for i in range(2,18) if i!=8]
BONE_CODES={f'lumbar_{i}':GENERAL+[f'A02.2.04.{j:03}' for j in (2,3,4)] for i in range(1,6)}
ORD=['Первый','Второй','Третий','Четвёртый','Пятый']
BONES={f'lumbar_{i}':dict(ru=f'{ORD[i-1]} поясничный позвонок (L{i})',lat=T['A02.2.04.001'][0],code='A02.2.04.001',level=f'L{i}',x=f'Позвонок L{i} поясничного отдела: тело, дуга и отростки. Поясничный отдел расположен между грудным отделом и крестцом.',refs=[GRAY,OPENSTAX],note=APPLICATION_NOTES[f'lumbar_{i}'],termNote='Латынь и код — групповой термин TA98; L1–L5 обозначают выбранный уровень, а не пять отдельных строк TA98.') for i in range(1,6)}
for v in BONES.values(): v.update(g='b_lumbar',sub='lumbar',sec='leg')

def description_for(bone,code):
    return dict(DESCRIPTIONS[code])

def export_evidence(path):
    data=dict(version=1,reviewed='2026-10-13',scope='Поясничные кости: карточки, номенклатура и применимость; без мышц и новых координат.',geometryVerified=False,catalogueIsOfficialPerBoneCount=False,applicabilityNote=APPLICABILITY_NOTE,applicationNotes=APPLICATION_NOTES,terms={c:dict(lat=v[0],ru=v[1],flag=v[2]) for c,v in T.items()},bones={b:{**v,'codes':BONE_CODES[b],'entries':{c:description_for(b,c) for c in BONE_CODES[b]}} for b,v in BONES.items()},wholeTerms={c:DESCRIPTIONS[c] for c in WHOLE_TERMS},nomenclature=[ref('IFAA TA98',IFAA_URL,'A02.2.01; A02.2.04.001–004; A02.2.00.007.'),dict(title='Международная анатомическая терминология, ред. Л. Л. Колесников, 2003',locator='Печатная с.20: поясничные позвонки, добавочный, рёберный и сосцевидный отростки; локальная копия не публикуется.')])
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':
    assert all(c in T and c in DESCRIPTIONS for cs in BONE_CODES.values() for c in cs)
    export_evidence(Path(__file__).resolve().parents[1]/'research/lumbar-bone-evidence.json')
    print(len(BONES),'bones;',sum(map(len,BONE_CODES.values())),'editorial catalogue entries; no coordinates')
