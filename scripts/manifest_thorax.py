"""Thoracic musculoskeletal source meshes: BodyParts3D 3.0, CC BY-SA 2.1 JP.

Original sides and levels only. Aggregate source objects are not split into
invented individual muscles, ligaments or levels.
"""
from manifest_neck import NAME2ID, ids

ORDINALS=['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth','eleventh','twelfth']
BONES={f'thoracic_{i}':ids(f'{word} thoracic vertebra') for i,word in enumerate(ORDINALS,1)}
for side in ('right','left'):
    for i,word in enumerate(ORDINALS,1):
        BONES[f'rib_{i}_{side}']=ids(f'{side} {word} rib')
BONES['sternum']=ids('manubrium','body of sternum','xiphoid process')
SIMPLE_MUSCLES={
    'pectoralis_minor':'pectoralis minor','subclavius':'subclavius',
    'serratus_anterior':'serratus anterior',
    'serratus_posterior_superior':'serratus posterior superior',
    'serratus_posterior_inferior':'serratus posterior inferior',
    'transversus_thoracis':'transversus thoracis',
    'iliocostalis_thoracis':'iliocostalis thoracis',
    'longissimus_thoracis':'longissimus thoracis','spinalis_thoracis':'spinalis thoracis',
    'semispinalis_thoracis':'semispinalis thoracis', 'multifidus':'multifidus',
    'latissimus_dorsi':'latissimus dorsi','rhomboid_major':'rhomboid major','rhomboid_minor':'rhomboid minor',
}
MUSCLES={}
for side in ('right','left'):
    for key,name in SIMPLE_MUSCLES.items():
        MUSCLES[f'thorax_{key}_{side}']=[(NAME2ID[f'{side} {name}'],None)]
    MUSCLES[f'thorax_pectoralis_major_{side}']=[
        (NAME2ID[f'{part} part of {side} pectoralis major'],part)
        for part in ('clavicular','sternocostal','abdominal')]
    MUSCLES[f'thorax_trapezius_{side}']=[
        (NAME2ID[f'{part} part of {side} trapezius'],part)
        for part in ('descending','transverse','ascending')]
    MUSCLES[f'thorax_levatores_costarum_{side}']=[
        (NAME2ID[f'set of {side} levatores costarum {part}'],part) for part in ('longi','breves')]
for key,name in {
    'diaphragm':'diaphragm', 'intercostales_externi':'external intercostal muscle',
    'intercostales_interni':'internal intercostal muscle',
    'intercostales_intimi':'innermost intercostal muscle',
    'rotatores_thoracis':'thoracic rotator',
    'interspinales_thoracis':'set of interspinales thoracis',
}.items():
    MUSCLES['thorax_'+key]=[(NAME2ID[name],None)]

# The aggregate cartilage objects cover the costal cartilage source set.
# Do not duplicate them with individual FMA 1–7 cartilages.
OTHER={f'thorax_costal_cartilages_{side}':ids(f'{side} costal cartilage') for side in ('right','left')}
CONTEXT=ids('seventh cervical vertebra','first lumbar vertebra','second lumbar vertebra',
            'third lumbar vertebra','fourth lumbar vertebra','fifth lumbar vertebra',
            'right clavicle','left clavicle','right scapula','left scapula',
            'right humerus','left humerus','sacrum','right hip bone','left hip bone')
for word in ORDINALS:
    CONTEXT += ids(f'intervertebral disk of {word} thoracic vertebra')

# Large aggregate groups retain more source detail than a small single muscle.
MUSCLE_BUILD={key:(0.4,3000,80000) for key in MUSCLES
              if key in ('thorax_intercostales_externi','thorax_intercostales_interni','thorax_intercostales_intimi','thorax_diaphragm')}
def all_ids():
    return [fid for parts in MUSCLES.values() for fid,_ in parts]+[
        fid for group in (BONES,OTHER) for fids in group.values() for fid in fids]+CONTEXT

if __name__=='__main__':
    print(len(BONES),'bones;',len(MUSCLES),'muscle objects;',len(OTHER),'soft objects;',len(all_ids()),'source files')
