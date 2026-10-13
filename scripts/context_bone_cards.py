"""Bone-only cards for former context. Never mirror right-hand coordinates.

Codes are the established unsided TA98 catalogues. Import ta98 only inside the
catalogue function so callers may integrate this module without import cycles.
"""
from neck_terms import ref, GRAY_URL

NOTE='Левая сторона, собственная исходная сетка BodyParts3D. Добавлена выбираемая кость; набор мышц левой конечности этим дополнением не заявляется. Новых проверенных координат образований нет; точки правой стороны не отражаются.'
OPENSTAX_BASE='https://openstax.org/books/anatomy-and-physiology-2e/pages/'
CONTEXT_BONE_CARDS={
 'hip_bone_left':dict(ru='Левая тазовая кость',lat='os coxae',code='A02.5.01.001',g='b_pelvis',sub='pelvis',sec='leg',sourceId='FMA16587',catalogueSourceBone='hip_bone',x='Тазовая кость взрослого образована подвздошной, седалищной и лобковой частями, соединёнными в области вертлужной впадины.',refs=[ref('Gray (1918) — The Hip Bone',GRAY_URL+'#page=226','PDF с.226–227: The Hip Bone, начальный абзац и состав кости.'),ref('OpenStax — The Pelvic Girdle and Pelvis',OPENSTAX_BASE+'8-3-the-pelvic-girdle-and-pelvis','Hip Bone; Fig.8.13; Pelvis — acetabulum.')]),
 'clavicle_left':dict(ru='Левая ключица',lat='clavicula',code='A02.4.02.001',g='b_girdle',sub='shoulder',sec='arm',sourceId='FMA13323',catalogueSourceBone='clavicle',x='Кость плечевого пояса между рукояткой грудины и акромионом лопатки.',refs=[ref('Gray (1918) — The Clavicle',GRAY_URL+'#page=177','PDF с.177, начальный абзац: медиальное и латеральное сочленения.'),ref('OpenStax — The Pectoral Girdle',OPENSTAX_BASE+'8-1-the-pectoral-girdle','Clavicle — sternal and acromial ends.')]),
 'scapula_left':dict(ru='Левая лопатка',lat='scapula',code='A02.4.01.001',g='b_girdle',sub='shoulder',sec='arm',sourceId='FMA13396',catalogueSourceBone='scapula',x='Плоская треугольная кость задней части плечевого пояса.',refs=[ref('Gray (1918) — The Scapula',GRAY_URL+'#page=179','PDF с.179, The Scapula, начальный абзац.'),ref('OpenStax — The Pectoral Girdle',OPENSTAX_BASE+'8-1-the-pectoral-girdle','Введение перед Clavicle: расположение и форма scapula; Scapula.')]),
 'humerus_left':dict(ru='Левая плечевая кость',lat='humerus',code='A02.4.04.001',g='b_free',sub='arm',sec='arm',sourceId='FMA23131',catalogueSourceBone='humerus',x='Кость плеча с телом и двумя концами; проксимально расположена головка.',refs=[ref('Gray (1918) — The Humerus',GRAY_URL+'#page=188','PDF с.188, The Humerus — introductory paragraph; Upper Extremity.'),ref('OpenStax — Bones of the Upper Limb',OPENSTAX_BASE+'8-2-bones-of-the-upper-limb','Humerus — proximal head and shaft; Fig.8.5.')]),
}
for v in CONTEXT_BONE_CARDS.values(): v.update(side='left',note=NOTE,localizationVerified=False)

def catalogue_codes():
    from ta98 import BONE
    return {b:list(BONE[v['catalogueSourceBone']]) for b,v in CONTEXT_BONE_CARDS.items()}

def catalogue_entries():
    from ta98 import T
    return {b:[dict(c=c,lat=T[c][0],ru=T[c][1],p=None,n=None,modelNote='Термин относится к этой кости; координаты левого экземпляра отдельно не проверены.') for c in cs] for b,cs in catalogue_codes().items()}

if __name__=='__main__':
    print(len(CONTEXT_BONE_CARDS),'cards;',sum(map(len,catalogue_codes().values())),'catalogue entries; no coordinates')
