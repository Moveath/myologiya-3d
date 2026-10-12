"""Export the manual face review; never infer positions for unresolved terms.

The only proposed main-atlas positions are six individually inspected ray picks.
Detailed-model positions retain the independent Z-Anatomy coordinate frame.
Run after the jobs documented in build_head/complete_face/review-picks.js.
"""
from pathlib import Path
import json
import shutil
from collections import Counter
from PIL import Image
from head_face_evidence import DESCRIPTIONS
from ta98 import T

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/'qface_complete'
OUT=ROOT/'build_head/complete_face'
OUT.mkdir(parents=True,exist_ok=True)
GRAY='https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf'

NOTES={
 'A02.1.08.003':'Маркер выбран на видимой отогнутой пластинке верхнего края нижней носовой раковины. Её положение проверено отдельно справа и слева; точка обозначает участок поверхности отростка, а не всю его границу.',
 'A02.1.09.003':'Маркер выбран на продольном углублении впереди заднего слёзного гребня. Это поверхность открытой борозды; она не означает реконструкцию всего носослёзного канала.',
 'A02.1.13.009':'Маркер выбран на нижнем поперечном возвышении носовой поверхности перпендикулярной пластинки. Обе стороны осмотрены отдельно; точка обозначает участок гребня.'}
PICKS=[('inferior_concha_right','A02.1.08.003'),('inferior_concha_left','A02.1.08.003'),
       ('lacrimal_right','A02.1.09.003'),('lacrimal_left','A02.1.09.003'),
       ('palatine_right','A02.1.13.009'),('palatine_left','A02.1.13.009')]

def refs(code):
 r=[dict(x) for x in DESCRIPTIONS[code]['refs']]
 page={'A02.1.08.003':136,'A02.1.13.009':134,'A02.1.15.031':142}.get(code)
 if page:
  r[0].update(url=GRAY+'#page='+str(page),locator={
   'A02.1.08.003':'PDF pp.135–137, inferior nasal concha: maxillary process; Fig.172 lateral surface.',
   'A02.1.13.009':'PDF p.134, vertical part: nasal surface; lower conchal crest below middle meatus.',
   'A02.1.15.031':'PDF p.142, ramus: mylohyoid groove from lower back margin of mandibular foramen, downward and forward.'}[code])
 if code=='A02.1.09.003':
  r[1]={'title':'Anatomy Standard — Os lacrimale','url':'https://www.anatomystandard.com/ossa-et-juncturae/cranium/os-lacrimale.html','locator':'Lateral aspect of right lacrimal bone: posterior lacrimal crest and lacrimal sulcus.'}
 return r

proposals=[]
for bone,code in PICKS:
 p=json.loads((QUEUE/f'candidate_{bone}.out').read_text())
 assert p['bone']==bone and p['code']==code and len(p['p'])==len(p['n'])==3
 img=f'candidate_{bone}.png';shutil.copyfile(QUEUE/img,OUT/img)
 proposals.append({'bone':bone,'code':code,'p':p['p'],'n':p['n'],'localization':'surface',
  'modelNote':NOTES[code],'refs':refs(code),'evidence':{
   'method':'manual-visible-relief-review-and-orthographic-raycast','view':p['view'],'uv':p['uv'],
   'source':'build_head/complete_face/review-picks.js','review':'Отдельный осмотр BodyParts3D обеих сторон в шести ракурсах; сопоставление видимого образования с указанными источниками. Попадание луча использовано только для записи уже выбранного участка.',
   'screenshot':'build_head/complete_face/'+img,'coordinateFrame':'BodyParts3D atlas metres'}})
(ROOT/'pins_head/face-completion.json').write_text(json.dumps(proposals,ensure_ascii=False,indent=2),encoding='utf-8')

zmarkers=[]
for side in ['right','left']:
 p=json.loads((QUEUE/f'zzz_z_groove_{side}.out').read_text())
 img=f'z_groove_{side}.png';shutil.copyfile(QUEUE/f'zzz_z_groove_{side}.png',OUT/img)
 code='A02.1.15.031'
 zmarkers.append({'id':'mandible_mylohyoid_groove_'+side,'b':'mandible','c':code,
  'ru':T[code][1]+(' · справа' if side=='right' else ' · слева'),'lat':T[code][0],
  'p':p['p'],'n':p['n'],'x':DESCRIPTIONS[code]['x'],'refs':refs(code),
  'modelNote':'Отмечен видимый участок линии борозды на авторской сетке Z-Anatomy. Это отдельная учебная модель; координаты и подтверждение рельефа не перенесены на BodyParts3D. Полный внутрикостный нижнечелюстной канал этим маркером не подтверждается.',
  'loc':'surface','source':'Z-Anatomy','side':side,'view':'left' if side=='right' else 'right',
  'cut':{'plane':'sagittal','value':.5,'reverse':side=='right'},
  'evidence':{'method':'manual-medial-surface-review-and-raycast','view':p['view'],'uv':p['uv'],
   'coordinateFrame':'Z-Anatomy [x,z,-y], metres; not registered to BodyParts3D',
   'opposite_half_hidden':True,'source':'build_head/complete_face/review-picks.js',
   'screenshot':'build_head/complete_face/'+img,
   'review':'Обе половины исходной нижней челюсти осмотрены отдельно, без противоположной ветви в луче. Видимая линия прослежена от области нижнечелюстного отверстия вниз и вперёд. Мелкие изолированные артефакты исходной сетки не использованы как ориентиры.'}})
(ROOT/'research/face-completion-z-markers.json').write_text(json.dumps(zmarkers,ensure_ascii=False,indent=2),encoding='utf-8')

# Each unresolved term gets its own documented requirement. These observations
# are limits of inspected models, not claims of absence in normal anatomy.
GAPS={
'A02.1.08.003':'Верхнечелюстной отросток: видна отогнутая пластинка, предложена повторная локализация поверхности.',
'A02.1.09.003':'Слёзная борозда: различимо углубление впереди заднего слёзного гребня, предложена поверхность.',
'A02.1.09.004':'Слёзный крючок: закруглённый нижний конец гребня есть, но отдельный направленный вперёд крючок не выделен достоверно.',
'A02.1.15.010':'Верхняя подбородочная ость: на срединной внутренней поверхности нет уверенно отделимой верхней ости.',
'A02.1.15.011':'Нижняя подбородочная ость: невозможно отделить нижний элемент от общего сглаженного срединного рельефа.',
'A02.1.15.013':'Нижнечелюстной валик: индивидуальный вариант не подтверждён; нельзя дорисовать как обязательное образование.',
'A02.1.15.030':'Нижнечелюстной канал: наличие входной области и подбородочного отверстия не подтверждает непрерывные внутрикостные стенки и ход.',
'A02.1.15.031':'Челюстно-подъязычная борозда: BP сглажен; в Z подтверждён отдельный видимый участок с обеих сторон, записаны собственные координаты.',
'A02.1.00.061':'Резцовые каналы: не прослежен непрерывный внутрикостный просвет от нёба к носовой поверхности.',
'A02.1.00.062':'Резцовые отверстия: срединный край доступен, но отдельные замкнутые края просветов достоверно не отделены.',
'A02.1.12.004':'Подглазничный канал: наружное подглазничное отверстие не доказывает внутреннюю траекторию и стенки канала.',
'A02.1.12.005':'Подглазничная борозда: глазничная поверхность в моделях сглажена, отчётливое дно и края борозды не подтверждены.',
'A02.1.12.014':'Альвеолярные отверстия: на бугре не различимы отдельные входы задних альвеолярных каналов.',
'A02.1.12.015':'Альвеолярные каналы: исходные сетки не дают проверенной системы внутренних ветвящихся просветов.',
'A02.1.12.019':'Раковинный гребень верхней челюсти: переходы носовой поверхности видны, но конкретный гребень не отделён уверенно.',
'A02.1.12.022':'Большая нёбная борозда верхней челюсти: на заднемедиальной поверхности нет уверенно прослеживаемого отдельного дна.',
'A02.1.12.026':'Слёзная вырезка: медиальный край глазничной поверхности доступен, но границы именно этой вырезки ещё не подтверждены.',
'A02.1.12.027':'Решётчатый гребень верхней челюсти: малый поперечный гребень носовой поверхности лобного отростка не отделяется достоверно.',
'A02.1.12.031':'Резцовая часть: область передних альвеол видна; самостоятельная резцовая кость и её границы у этого взрослого образца не установлены.',
'A02.1.12.032':'Резцовый шов: отдельная линия варианта в данном образце не подтверждена; нельзя вводить как обязательный шов.',
'A02.1.12.033':'Нёбные ости: нижняя поверхность нёбного отростка сглажена, отдельные выступы не различимы.',
'A02.1.12.034':'Нёбные борозды: мелкие ветвящиеся борозды на нёбной поверхности не прослежены.',
'A02.1.10.002':'Решётчатая борозда носовой кости: внутренняя поверхность есть, но отдельная продольная сосудисто-нервная борозда не подтверждена.',
'A02.1.10.003':'Носовые отверстия: пластинка не показывает достоверно отдельные сквозные просветы.',
'A02.1.13.008':'Малые нёбные каналы: непрерывные внутрикостные просветы в пирамидальном отростке не прослежены.',
'A02.1.13.009':'Раковинный гребень нёбной кости: нижнее поперечное возвышение различимо с обеих сторон, предложена поверхность.',
'A02.1.13.010':'Решётчатый гребень нёбной кости: верхний переход поверхности у корней отростков не имеет уверенно отдельной линии гребня.',
'A02.1.13.016':'Малые нёбные отверстия: мелкие выходные просветы пирамидального отростка не подтверждены.',
'A02.1.13.019':'Нёбный гребень: задняя поверхность горизонтальной пластинки доступна, но отдельный поперечный гребень не различим уверенно.',
'A02.1.11.003':'Борозда сошника: боковые пластинки сглажены, отдельный косой ход борозды не подтверждён.',
'A02.1.11.004':'Хоанный гребень сошника: видимая граница не подтверждена; дополнительно сохранено расхождение определения в источниках.',
'A02.1.11.005':'Клиновидная часть сошника: ожидаемая область доступна, но граница части в геометрии не отделяется.',
'A02.1.14.007':'Глазничный бугорок: отдельный небольшой выступ на глазничной поверхности не определён достоверно.',
'A02.1.14.008':'Краевой бугорок: общий край лобного отростка есть, отдельный краевой выступ не подтверждён.',
'A02.1.14.009':'Скулоглазничное отверстие: на глазничной поверхности не подтверждён отдельный входной просвет.',
'A02.1.14.010':'Скулолицевое отверстие: наружная поверхность гладкая, отдельный выходной просвет не различим.',
'A02.1.14.011':'Скуловисочное отверстие: внутренняя височная поверхность не даёт уверенного отдельного просвета.'}
rows=[]
baseline=json.loads((ROOT/'pins_head/face-extra.json').read_text(encoding='utf-8'))
for r in sorted(baseline,key=lambda r:(r['bone'],r['code'])):
 bone,code=r['bone'],r['code']
 if code not in DESCRIPTIONS or r['localization']=='surface':continue
 assert code in GAPS,code
 proposed=(bone,code) in PICKS
 rows.append({'bone':bone,'code':code,'ru':T[code][1],'lat':T[code][0],
  'current_localization':r['localization'],'review_result':'surface-proposal' if proposed else 'separate-Z-counterpart' if code=='A02.1.15.031' else 'unresolved',
  'model_observation':GAPS[code],'refs':refs(code),'review_image':'build_head/complete_face/'+bone+'_comparison.png',
  'next_requirement':None if proposed else 'Проверенная геометрия с различимыми границами конкретного образования; отдельная локализация на выбранной модели.'})
bones=sorted(set(r['bone'] for r in rows))
for bone in bones:
 fs=[QUEUE/(s+'_'+bone+'_'+v+'.png') for s in ['bp','z'] for v in ['ant','post','lat','med','sup','inf']]
 if all(f.exists() for f in fs):
  out=Image.new('RGB',(2400,800))
  for i,f in enumerate(fs):out.paste(Image.open(f).resize((400,400)),((i%6)*400,(i//6)*400))
  out.save(OUT/(bone+'_comparison.png'))
report={'date':'2026-10-12','scope':'14 лицевых костей; 66 ранее неподтверждённых записей из основной разметки, включая 3 варианта.',
 'method':'Шесть ортографических ракурсов каждой исходной стороны BP и Z; для нижней челюсти дополнительно медиальные поверхности со скрытой противоположной ветвью. Верхний ряд сравнительных снимков BP, нижний Z. lat/med в техническом инструменте задают -X/+X, поэтому их анатомический смысл для левой стороны меняется.',
 'counts':dict(Counter(r['review_result'] for r in rows)),'records':rows,
 'missing_muscles':{'count':9,'source_inventory':'research/face-completion-source-inventory.json',
 'result':'В Z-Anatomy нет отдельных поверхностных сеток anterior/superior/posterior auricular muscles, depressor supercilii или transversus menti. Есть групповые подписи ушных мышц в виде FONT и двухвершинных линий; они не являются мышечными моделями.',
 'excluded_shortcuts':['Не использовать групповые подписи как геометрию мышцы.','Не вырезать depressor supercilii произвольно из orbicularis oculi.','Не публиковать материалы платных атласов.']},
 'limitations':'Обзор моделей и шесть предложенных поверхностных уточнений не завершают геометрию оставшихся каналов. Z-Anatomy повторяет и упрощает большую часть лицевых костей BP; новая независимая точная сегментация здесь не получена.'}
(ROOT/'research/face-completion-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report['counts']))
