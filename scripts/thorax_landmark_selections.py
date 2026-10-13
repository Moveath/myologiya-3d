"""Manual orthographic selections after viewing individual source bone meshes.

Screen coordinates are individually selected, never reflected or copied along
a vertebral/rib series. A point confirms only the indicated surface patch.
"""
SELECTIONS=[]
def add(bone,code,view,uv,meaning):
    SELECTIONS.append(dict(bone=bone,code=code,view=view,uv=uv,meaning=meaning))

G='A02.2.01.'
R='A02.3.02.'
S='A02.3.03.'

# body is anterior, superior articular patch is posterior (right side appears
# on the right of that view); inferior articular patch is inferior.
V={
 1:dict(body=[.5,.565],plate=[.50,.835],arch=[.415,.49],pedicle=[.335,.711],lamina=[.365,.55],rim=[.455,.526],spine=[.50,.22],transverse=[.115,.628],upper=[.70,.45],lower=[.68,.45]),
 2:dict(body=[.5,.58],plate=[.51,.825],arch=[.42,.49],pedicle=[.335,.697],lamina=[.385,.545],rim=[.49,.50],spine=[.5,.2],transverse=[.12,.54],upper=[.67,.37],lower=[.65,.46]),
 3:dict(body=[.5,.58],plate=[.51,.8],arch=[.42,.48],pedicle=[.335,.68],lamina=[.375,.53],rim=[.49,.48],spine=[.51,.22],transverse=[.17,.50],upper=[.665,.29],lower=[.64,.51]),
 4:dict(body=[.5,.55],plate=[.50,.78],arch=[.42,.43],pedicle=[.325,.616],lamina=[.37,.47],rim=[.49,.44],spine=[.495,.18],transverse=[.15,.437],upper=[.69,.30],lower=[.64,.585]),
 5:dict(body=[.5,.50],plate=[.495,.77],arch=[.45,.37],pedicle=[.33,.554],lamina=[.395,.39],rim=[.505,.383],spine=[.52,.2],transverse=[.14,.365],upper=[.65,.24],lower=[.66,.64]),
 6:dict(body=[.5,.44],plate=[.495,.73],arch=[.45,.30],pedicle=[.35,.48],lamina=[.395,.355],rim=[.495,.335],spine=[.52,.17],transverse=[.13,.32],upper=[.66,.185],lower=[.665,.67]),
 7:dict(body=[.51,.40],plate=[.50,.735],arch=[.465,.28],lamina=[.405,.323],rim=[.49,.31],spine=[.51,.17],transverse=[.125,.29],upper=[.655,.215],lower=[.665,.67]),
 8:dict(body=[.50,.35],plate=[.5,.70],arch=[.45,.29],lamina=[.40,.335],rim=[.51,.325],spine=[.498,.14],transverse=[.16,.30],upper=[.685,.22],lower=[.67,.65]),
 9:dict(body=[.50,.34],plate=[.5,.71],arch=[.47,.29],lamina=[.40,.33],rim=[.50,.32],spine=[.507,.14],transverse=[.15,.26],upper=[.655,.255],lower=[.67,.665]),
 10:dict(body=[.505,.33],plate=[.51,.72],arch=[.45,.31],lamina=[.395,.35],rim=[.515,.329],spine=[.508,.145],transverse=[.16,.30],upper=[.65,.24],lower=[.66,.625]),
 11:dict(body=[.50,.29],plate=[.5,.70],arch=[.45,.315],lamina=[.4,.35],rim=[.505,.327],spine=[.509,.14],transverse=[.258,.30],upper=[.71,.20],lower=[.645,.64]),
 12:dict(body=[.50,.31],plate=[.50,.72],arch=[.455,.35],lamina=[.425,.38],rim=[.495,.361],spine=[.507,.17],transverse=[.28,.285],upper=[.745,.18],lower=[.625,.665]),
}

def vertebrae():
    for number,p in V.items():
        bone=f'thoracic_{number}'
        for code,view,key,meaning in [
            ('002','ant','body','передняя поверхность тела'),
            ('003','sup','plate','верхняя межпозвоночная поверхность тела'),
            ('005','sup','arch','участок задней части дуги'),
            ('007','sup','lamina','правая пластинка дуги'),
            ('011','sup','rim','видимый костный край позвоночного отверстия'),
            ('012','sup','spine','остистый отросток'),
            ('013','sup','transverse','правый поперечный отросток'),
            ('014','post','upper','правый верхний суставной отросток, суставной участок'),
            ('015','post','upper','правая верхняя суставная поверхность'),
            ('016','inf','lower','левый нижний суставной отросток, суставной участок'),
            ('017','inf','lower','левая нижняя суставная поверхность')]:
            add(bone,G+code,view,p[key],meaning)

vertebrae()

# Ribs: head, neck, body, tubercle and angle are individually inspected. Ribs I,
# XI and XII keep their specific applicability; absent features are not invented.
RIBS={
 'rib_1_right':dict(head=[.817,.175],neck=[.735,.14],body=[.30,.66],tubercle=[.615,.08]),
 'rib_1_left':dict(head=[.171,.178],neck=[.24,.133],body=[.716,.64],tubercle=[.405,.08]),
 'rib_2_right':dict(head=[.810,.163],neck=[.751,.142],body=[.275,.591],tubercle=[.685,.091],angle=[.303,.203]),
 'rib_2_left':dict(head=[.187,.171],neck=[.255,.132],body=[.718,.573],tubercle=[.311,.09],angle=[.695,.207]),
 'rib_3_right':dict(head=[.785,.192],neck=[.741,.14],body=[.28,.6],tubercle=[.695,.097],angle=[.302,.165]),
 'rib_3_left':dict(head=[.21,.193],neck=[.25,.14],body=[.731,.575],tubercle=[.298,.093],angle=[.655,.156]),
 'rib_4_right':dict(head=[.769,.224],neck=[.719,.157],body=[.272,.67],tubercle=[.671,.10],angle=[.355,.145]),
 'rib_4_left':dict(head=[.227,.223],neck=[.285,.155],body=[.714,.646],tubercle=[.319,.101],angle=[.636,.152]),
 'rib_5_right':dict(head=[.756,.202],neck=[.72,.162],body=[.285,.718],tubercle=[.68,.126],angle=[.357,.16]),
 'rib_5_left':dict(head=[.245,.204],neck=[.281,.164],body=[.684,.71],tubercle=[.320,.125],angle=[.642,.16]),
 'rib_6_right':dict(head=[.76,.215],neck=[.72,.17],body=[.29,.74],tubercle=[.682,.137],angle=[.36,.155]),
 'rib_6_left':dict(head=[.236,.219],neck=[.276,.167],body=[.691,.734],tubercle=[.31,.137],angle=[.635,.155]),
 'rib_7_right':dict(head=[.790,.207],neck=[.751,.168],body=[.22,.691],tubercle=[.707,.137],angle=[.345,.149]),
 'rib_7_left':dict(head=[.208,.208],neck=[.254,.169],body=[.77,.688],tubercle=[.289,.135],angle=[.633,.155]),
 'rib_8_right':dict(head=[.808,.236],neck=[.765,.188],body=[.20,.707],tubercle=[.720,.147],angle=[.352,.166]),
 'rib_8_left':dict(head=[.192,.233],neck=[.234,.188],body=[.789,.701],tubercle=[.276,.153],angle=[.64,.163]),
 'rib_9_right':dict(head=[.863,.319],neck=[.818,.26],body=[.13,.711],tubercle=[.786,.216],angle=[.385,.149]),
 'rib_9_left':dict(head=[.135,.318],neck=[.178,.26],body=[.867,.71],tubercle=[.201,.223],angle=[.615,.155]),
 'rib_10_right':dict(head=[.923,.378],neck=[.885,.303],body=[.079,.72],tubercle=[.837,.239],angle=[.429,.112]),
 'rib_10_left':dict(head=[.073,.378],neck=[.119,.309],body=[.915,.717],tubercle=[.166,.253],angle=[.55,.127]),
 'rib_11_right':dict(head=[.910,.473],body=[.20,.479]),
 'rib_11_left':dict(head=[.085,.474],body=[.788,.461]),
 'rib_12_right':dict(head=[.9,.73],body=[.344,.281]),
 'rib_12_left':dict(head=[.09,.738],body=[.67,.3]),
}
for bone,p in RIBS.items():
    for key,code,meaning in [('head','002','головка ребра'),('neck','005','шейка ребра'),
                             ('body','007','участок тела ребра'),('tubercle','008','бугорок ребра'),
                             ('angle','010','участок изгиба в области угла ребра')]:
        if key in p: add(bone,R+code,'sup',p[key],meaning)

add('sternum',S+'002','ant',[.50,.19],'передняя поверхность рукоятки грудины')
add('sternum',S+'003','sup',[.28,.15],'правая ключичная вырезка')
add('sternum',S+'004','ant',[.50,.083],'костный край яремной вырезки')
add('sternum',S+'005','lat',[.55,.30],'передний костный край в области угла грудины')
add('sternum',S+'006','ant',[.50,.58],'передняя поверхность тела грудины')
add('sternum',S+'007','ant',[.50,.90],'передняя поверхность мечевидного отростка')
add('sternum',S+'008','lat',[.568,.454],'одна из правых рёберных вырезок тела грудины')
