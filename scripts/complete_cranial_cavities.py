"""Package registered source cavity surfaces as an illustrative comparison layer.

The layer does not turn projection markers into confirmed internal landmarks.
It does not cut bone, invent channels, or imply a shared individual specimen.
"""
from pathlib import Path
import copy,hashlib,json,sys
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build_head/complete_cranial'
SOURCE=ROOT/'research/cache/z-detail'
fit=json.loads((OUT/'registration-fit.json').read_text())
matrix=np.array(fit['transform_z_to_bp'])
source_meta=json.loads((ROOT/'site/skull-z-detail.json').read_text(encoding='utf-8'))
containment=json.loads((OUT/'cavity-containment.json').read_text())
scene=trimesh.Scene()
rows=[]
for row in source_meta['cavities']:
    row=copy.deepcopy(row)
    raw=json.loads((SOURCE/f"{row['id']}.json").read_text())
    mesh=trimesh.Trimesh(raw['vertices'],raw['faces'],process=False)
    mesh.apply_transform(matrix)
    mesh.visual=trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        name='Illustrative air cavity volume',baseColorFactor=[77,176,209,255],
        metallicFactor=0,roughnessFactor=.7,doubleSided=True))
    name='o|'+row['id']
    scene.add_geometry(mesh,node_name=name,geom_name=name)
    row['bounds']=mesh.bounds.tolist()
    row['modelNote']='Учебная форма воздушной полости из Z-Anatomy приблизительно совмещена с основным черепом по общим костным поверхностям. Она не является сегментацией этого же образца BodyParts3D; мелкие сообщения, стенки и индивидуальная форма не подтверждены. Цвет обозначает воздушное пространство, не ткань.'
    row['localizationStatus']='educational_composite'
    row['containmentReview']=next(r for r in containment if r['cavity']==row['id'])
    rows.append(row)
scene.metadata.update(license='CC BY-SA 4.0',
    source=source_meta['source'],
    modifications='Author-supplied cavity surfaces; one cranial similarity transform; no cutting or deformation.',
    claim='Illustrative comparison layer; does not confirm BodyParts3D internal anatomy.')
asset=OUT/'head-cavities.glb'
asset.write_bytes(scene.export(file_type='glb'))
metadata={
    'title':'Воздушные полости · учебное совмещение',
    'file':asset.name,
    'source':source_meta['source'],
    'license':copy.deepcopy(source_meta['license']),
    'cavities':rows,
    'coordinateFrame':{'units':'metres','base':'BodyParts3D main atlas',
        'registration':'Approximate global cranial similarity, not specimen-specific registration',
        'transform':matrix.tolist()},
    'geometry':{'bytes':asset.stat().st_size,'sha256':hashlib.sha256(asset.read_bytes()).hexdigest()},
    'limitations':[
        'Совмещение проверено по основным костным поверхностям и отдельным крупным ориентирам; оно не подтверждает индивидуальные стенки пазух.',
        'Часть поверхностей полостей выходит за оболочку основной кости: до 1,62 мм для лобной пазухи, до 3,54 мм для клиновидной пазухи и до 2,80 мм для решётчатых ячеек в выполненной выборочной проверке.',
        'Не использовать как инструмент измерения или как основание для автоматического перевода маркеров projection в internal.',
        'Исходные стенки пазух имеют открытые края; отверстия и пути оттока отдельно не реконструированы.'
    ],
    'review':'research/cranial-completion-registration.json'
}
metadata['license']['changes']+=' Выполнено приблизительное единое совмещение с черепом BodyParts3D; исходные поверхности полостей не деформированы.'
metadata['license']['notice']='Исследовательский GLB содержит только восемь авторских поверхностей пазух/групп решётчатых ячеек, извлечённых из Z-Anatomy. Кости, модели внутреннего уха и почки не включены. Геометрия распространяется по CC BY-SA 4.0 с сохранением исходных атрибуций.'
metadata['publicationStatus']='Research only; rejected for integration into the main BodyParts3D model.'
(OUT/'head-cavities.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(metadata['geometry']))
