"""Screen selections made after inspecting every named BodyParts3D bone.

Coordinates are orthographic image fractions, NOT bounding-box guesses.
The corresponding images are recorded by export_neck_landmarks.py.
One TA98 row may describe paired features: supplementary picks retain the other
side without duplicating the official term. No coordinates are mirrored.
"""

SELECTIONS = []
def add(bone, code, view, uv, meaning, other=None):
    SELECTIONS.append(dict(bone=bone, code=code, view=view, uv=uv,
                           meaning=meaning, other=other or []))

H='A02.1.16.'
add('hyoid',H+'002','ant',[.5,.61],'передняя поверхность тела')
add('hyoid',H+'003','ant',[.216,.465],'правый малый рог',[[.784,.466]])
add('hyoid',H+'004','sup',[.13,.36],'правый большой рог',[[.875,.36]])

A='A02.2.02.'
add('atlas',A+'102','ant',[.3,.5],'передний участок правой латеральной массы',[[.69,.51]])
add('atlas',A+'103','sup',[.31,.565],'правая верхняя суставная поверхность',[[.66,.57]])
add('atlas',A+'104','inf',[.30,.40],'правая нижняя суставная поверхность',[[.67,.42]])
add('atlas',A+'105','ant',[.43,.50],'передняя дуга, участок рядом со срединным бугорком')
add('atlas',A+'107','ant',[.5,.515],'передний бугорок')
add('atlas',A+'108','sup',[.4,.305],'задняя дуга справа от средней линии')
add('atlas',A+'111','post',[.5,.53],'задний бугорок')
add('atlas',A+'003','sup',[.185,.633],'видимый край правого поперечного отверстия',[[.80,.64]])
add('atlas','A02.2.01.011','sup',[.45,.710],'край позвоночного отверстия у передней дуги')
add('atlas','A02.2.01.013','sup',[.105,.55],'правый поперечный отросток',[[.89,.565]])

add('axis',A+'202','ant',[.49,.34],'зуб, участок ниже передней суставной поверхности')
add('axis',A+'203','ant',[.49,.152],'верхушка зуба')
add('axis',A+'204','ant',[.495,.27],'передняя суставная поверхность зуба')
add('axis',A+'205','post',[.5,.26],'задняя суставная поверхность зуба')

# Every row below was selected independently in that vertebra's own image.
# Coordinates are deliberately not propagated along the cervical series.
# body: anterior; endplate/arch/pedicle/lamina/spine/transverse/superior: superior;
# inferior facet/process: inferior view. The vertebral foramen marker is on its
# visible rim; it is not a fabricated point floating in the void.
COMMON = {
 'axis': dict(body=[.50,.58], endplate=[.49,.19], arch=[.43,.34],
   pedicle=[.3,.60], lamina=[.34,.4], spine=[.5,.16], transverse=[.095,.718],
   superior=[.23,.75], inferior=[.2,.46], rim=[.5,.365], transverse_rim=[.21,.245]),
 'cervical_3': dict(body=[.5,.49],endplate=[.5,.83],arch=[.41,.43],
   pedicle=[.305,.65],lamina=[.35,.485],spine=[.495,.19],transverse=[.085,.765],
   superior=[.17,.56],inferior=[.17,.42],rim=[.40,.47],transverse_rim=[.205,.793]),
 'cervical_4': dict(body=[.5,.51],endplate=[.5,.81],arch=[.4,.4],
   pedicle=[.305,.675],lamina=[.40,.42],spine=[.49,.16],transverse=[.095,.74],
   superior=[.18,.58],inferior=[.17,.42],rim=[.45,.397],transverse_rim=[.245,.798]),
 'cervical_5': dict(body=[.5,.53],endplate=[.5,.85],arch=[.41,.505],
   pedicle=[.31,.705],lamina=[.37,.53],spine=[.505,.23],transverse=[.17,.82],
   superior=[.205,.615],inferior=[.18,.43],rim=[.465,.505],transverse_rim=[.22,.793]),
 'cervical_6': dict(body=[.5,.55],endplate=[.49,.85],arch=[.415,.56],
   pedicle=[.3,.72],lamina=[.36,.60],spine=[.495,.22],transverse=[.15,.83],
   superior=[.185,.665],inferior=[.21,.425],rim=[.45,.538],transverse_rim=[.23,.838]),
 'cervical_7': dict(body=[.5,.56],endplate=[.49,.85],arch=[.415,.56],
   pedicle=[.315,.714],lamina=[.355,.625],spine=[.51,.22],transverse=[.10,.70],
   superior=[.225,.69],inferior=[.25,.46],rim=[.455,.563],transverse_rim=[.24,.79]),
}

G='A02.2.01.'
for bone, p in COMMON.items():
    add(bone,G+'002','ant',p['body'],'передняя поверхность тела')
    add(bone,G+'003','inf' if bone=='axis' else 'sup',p['endplate'],
        'нижняя межпозвоночная поверхность тела' if bone=='axis' else 'верхняя межпозвоночная поверхность тела')
    add(bone,G+'005','sup',p['arch'],'участок задней части дуги')
    add(bone,G+'006','sup',p['pedicle'],'правая ножка дуги')
    add(bone,G+'007','sup',p['lamina'],'правая пластинка дуги')
    add(bone,G+'011','sup',p['rim'],'видимый край позвоночного отверстия')
    add(bone,G+'012','sup',p['spine'],'остистый отросток')
    add(bone,G+'013','sup',p['transverse'],'правый поперечный отросток')
    add(bone,G+'014','sup',p['superior'],'правый верхний суставной отросток, суставной участок')
    add(bone,G+'015','sup',p['superior'],'правая верхняя суставная поверхность')
    add(bone,G+'016','inf',p['inferior'],'правый нижний суставной отросток, суставной участок')
    add(bone,G+'017','inf',p['inferior'],'правая нижняя суставная поверхность')
    add(bone,A+'003','inf' if bone=='axis' else 'sup',p['transverse_rim'],
        'видимый край правого поперечного отверстия')

# Clearly raised lateral margins of the superior bodies. Their complete limits
# are not inferred from a single marker.
for bone, uv in {'cervical_3':[.333,.341], 'cervical_4':[.334,.356],
                 'cervical_5':[.309,.402], 'cervical_6':[.283,.44],
                 'cervical_7':[.327,.467]}.items():
    add(bone,A+'002','ant',uv,'правый крючок тела')
