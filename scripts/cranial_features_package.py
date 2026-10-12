"""Package independently reviewed Z-Anatomy landmarks, preserving limited scope.
Markers on airspace models or aperture rims do not confirm a full bony canal.
No BodyParts3D coordinates or localization flags are changed.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
from head_cranial_evidence import DESCRIPTIONS,GRAY,AS,TMA_F
from head_localization import positions
from head_terms import T
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build_head/cranial_features';Q=OUT/'jobs'
META=json.loads((ROOT/'site/skull-z-detail.json').read_text(encoding='utf-8'))
VIEWS={'ant':{'d':[0,0,1],'up':[0,1,0]},'sup':{'d':[0,1,0],'up':[0,0,-1]}}
markers=[]
def make(row,code,scope,screenshot,detail):
    lat,ru,_=T[code];side=row.get('side')
    source_fact=DESCRIPTIONS[code]
    refs=[dict(ref) for ref in source_fact['refs']]
    bone={'A02.1.03':'frontal','A02.1.05':'sphenoid','A02.1.07':'ethmoid'}[code[:8]]
    # Existing short topography may cite a definition rather than two diagrams.
    # Both sources below were re-read for the exact structure and its topology.
    refs=[dict(GRAY[bone]),dict(AS[bone])]
    refs[1]['locator']={'frontal':'Bottom view and anterior view: frontal sinus/opening; corresponding volume above the orbital part.', 'sphenoid':'Inferior and posterior labelled views: foramen spinosum; canalis pterygoideus; oblique anterior view: sinus sphenoidalis.', 'ethmoid':'Inferior ventral labelled view: cellulae ethmoidales anteriores, mediae, posteriores; top view of the labyrinth.'}[bone]
    precise={
      'A02.1.05.038':('Greater Wings, printed pp.149–150; PDF p.106: foramen spinosum in the posterior angle, near the spine, and the infratemporal surface.','Inferior aspect, labelled foramen spinosum; compare the position posterior-lateral to foramen ovale.'),
      'A02.1.05.053':('Pterygoid Processes, printed pp.150–151; PDF p.107: anterior surface of the process near its root presents the anterior orifice of the pterygoid canal.','Dorsal aspect: labelled canalis pterygoideus; the accompanying text identifies its pathway to the pterygopalatine fossa. This labelled figure is a posterior view, not an anterior-opening diagram.'),
      'A02.1.03.029':('Orbital or Horizontal Part and structure; printed pp.136–137, PDF pp.87–89: frontal air sinuses within the frontal bone.','Bottom aspect, labelled apertura sinus frontalis; anterior view locates the surrounding frontal bone.'),
      'A02.1.05.016':('Body, printed pp.147–149, PDF pp.103–105: sphenoidal air sinuses in the body.','Oblique frontal view: labels sinus sphenoidalis and apertura sinus sphenoidalis.'),
    }
    if code in precise:
        refs[0]['locator'],refs[1]['locator']=precise[code]
    elif scope=='airspace':
        refs[0]['locator']='Labyrinth or Lateral Mass, printed pp.154–155; PDF p.112: anterior, middle and posterior groups of ethmoidal cells.'
    if code=='A02.1.03.029':
        refs.append(dict(TMA_F,locator='Squamous Part: frontal sinuses within the squamous part, above the orbits on either side of the midline.'))
    view=dict(VIEWS[row['v']]);view['distance']=.16 if row['b']=='frontal_sinus' else .075 if row['b']=='sphenoidal_sinus' else .04 if scope=='airspace' else .04
    n=np.array(row['n']);raw=n.copy()
    if np.dot(n,view['d'])<0:n=-n
    marker={'id':row['id'],'b':row['b'],'c':code,'ru':ru+({'right':' · справа','left':' · слева'}.get(side,'')), 'lat':lat,'p':row['p'],'n':n.tolist(),'loc':'surface','scope':scope,'mode':'z','source':'Z-Anatomy','view':view,'refs':refs,'x':source_fact['x'],'modelNote':detail,'geometryRefs':[{'title':'Z-Anatomy — Models of human anatomy','url':META['source'],'locator':('o|' if scope=='airspace' else 'b|')+row['b'],'scope':'geometry'}], 'evidence':{'method':'manual-multiview-structure-review-and-surface-raycast','coordinateFrame':'Published skull-z-detail.glb, metres; independent Z-Anatomy frame; no registration to BodyParts3D.', 'view':VIEWS[row['v']],'uv':row['uv'],'zoomBox':row.get('zoomBox'),'faceIndex':row['faceIndex'],'rawTriangleNormal':raw.tolist(),'normalOrientation':'Face normal oriented toward the inspection camera for marker rendering.','screenshot':'build_head/cranial_features/jobs/'+screenshot,'sourceGeometrySHA256':hashlib.sha256((ROOT/'site/skull-z-detail.glb').read_bytes()).hexdigest(),'review':'Форма и расположение осмотрены с нескольких сторон; отдельные координаты выбраны на уже распознанной поверхности. Луч фиксирует координату и не является доказательством анатомического названия.'}}
    if side:marker['side']=side
    markers.append(marker)
for cavity in META['cavities']:
    key=cavity['id'];row=json.loads((Q/(key+'-pick.out')).read_text(encoding='utf-8-sig'))
    if cavity['side'] in ('right','left'):row['side']=cavity['side']
    make(row,cavity['c'],'airspace',key+'-pick.png','Отмечена поверхность отдельного авторского объёма воздухоносной полости Z-Anatomy. Это учебная форма пространства, не костная ткань и не подтверждение всех её костных стенок, сообщений или вариантов. Маркер не изменяет статус проекции на основном черепе.')
for side in ['right','left']:
    file='sphenoid-spinosum-pick.out' if side=='right' else 'spinosum-left-pick.out'
    row=json.loads((Q/file).read_text(encoding='utf-8-sig'))
    row.update(id='z_spinosum_'+side,b='sphenoid',side=side,v='sup')
    if side=='right':row.update(uv=[.55,.1],zoomBox=[[-.04,1.57,.007],[-.022,1.595,.027]])
    make(row,'A02.1.05.038','aperture',file.replace('.out','.png'),'Отмечен видимый край внутричерепной апертуры остистого отверстия на исходной сетке Z-Anatomy. Просмотр края не доказывает полную проходимость или точность всего хода через кость; весь ход отдельно не подтверждён. Основной череп BodyParts3D сохраняет статус проекции.')
for row in json.loads((Q/'sphenoid-anterior-openings.out').read_text(encoding='utf-8-sig')):
    row['side']=row['id'].split('_')[-1]
    make(row,'A02.1.05.053','aperture','sphenoid-anterior-openings.png','Отмечен край переднего отверстия крыловидного канала у основания крыловидного отростка на исходной сетке Z-Anatomy. Полная внутренняя стенка, задний выход и непрерывность всего канала здесь не подтверждены. Это самостоятельный ориентир апертуры, не полная реконструкция канала.')
# Metric validation is separate from visual/anatomical identification.
checks=[]
for m in markers:
    data=json.loads((ROOT/'research/cache/z-detail'/(m['b']+'.json')).read_text(encoding='utf-8'))
    mesh=trimesh.Trimesh(vertices=(np.array(data['vertices'])-np.array(m['p']))*1000,faces=data['faces'],process=False)
    _,dist,_=trimesh.proximity.closest_point_naive(mesh,np.zeros((1,3)))
    checks.append({'id':m['id'],'distance_mm':float(dist[0])})
    assert dist[0]<.03,(m['id'],dist)
result={'date':'2026-10-13','source':'Z-Anatomy','registeredToBodyParts3D':False,'completeGeometryClaim':False,'markers':markers,'scope':'8 independently marked source airspace objects (5 TA98 terms), plus 4 aperture-rim landmarks (2 TA98 terms). Airspaces and aperture rims are not treated as full bony channel geometry.'}
(ROOT/'pins_head/cranial-native-features.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'geometry-check.json').write_text(json.dumps({'checks':checks,'max_distance_mm':max(c['distance_mm'] for c in checks)},indent=2)+'\n',encoding='utf-8')
print('Published source markers:',len(markers),'TA98 terms:',len({m['c'] for m in markers}))
