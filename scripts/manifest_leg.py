# Right lower limb + pelvis: BodyParts3D parts by English name (resolved to file ids below).
import os

_here = os.path.dirname(os.path.abspath(__file__))
_tsv = os.path.join(_here, '..', 'bp', 'all_named.tsv')
NAME2ID = {}
for line in open(_tsv, encoding='utf-8'):
    i, n = line.rstrip('\n').split('\t')
    NAME2ID.setdefault(n, i)

def ids(*names):
    out = []
    for n in names:
        if n not in NAME2ID:
            raise KeyError(n)
        out.append(NAME2ID[n])
    return out

M = {
    # таз: внутренние
    "iliopsoas": [("right psoas major", "psoas"), ("right iliacus", "iliacus")],
    "obturator_internus": [("right obturator internus", None)],
    "piriformis": [("right piriformis", None)],
    # таз: наружные
    "gluteus_maximus": [("right gluteus maximus", None)],
    "gluteus_medius": [("right gluteus medius", None)],
    "gluteus_minimus": [("right gluteus minimus", None)],
    "tensor_fasciae_latae": [("right tensor fasciae latae", None)],
    "quadratus_femoris": [("right quadratus femoris", None)],
    "obturator_externus": [("right obturator externus", None)],
    "gemellus_superior": [("right gemellus superior", None)],
    "gemellus_inferior": [("right gemellus inferior", None)],
    # бедро
    "sartorius": [("right sartorius", None)],
    "quadriceps_femoris": [("right rectus femoris", "rectus"), ("right vastus lateralis", "vlat"),
                           ("right vastus medialis", "vmed"), ("right vastus intermedius", "vint")],
    "pectineus": [("right pectineus", None)],
    "adductor_longus": [("right adductor longus", None)],
    "adductor_brevis": [("right adductor brevis", None)],
    "adductor_magnus": [("right adductor magnus", "main"), ("right adductor minimus", "minimus")],
    "gracilis": [("right gracilis", None)],
    "biceps_femoris": [("long head of right biceps femoris", "long"), ("short head of right biceps femoris", "short")],
    "semitendinosus": [("right semitendinosus", None)],
    "semimembranosus": [("right semimembranosus", None)],
    # голень
    "tibialis_anterior": [("right tibialis anterior", None)],
    "extensor_digitorum_longus": [("right extensor digitorum longus", None)],
    "fibularis_tertius": [("right fibularis tertius", None)],
    "extensor_hallucis_longus": [("right extensor hallucis longus", None)],
    "fibularis_longus": [("right fibularis longus", None)],
    "fibularis_brevis": [("right fibularis brevis", None)],
    "triceps_surae": [("medial head of right gastrocnemius", "gmed"), ("lateral head of right gastrocnemius", "glat"), ("right soleus", "soleus")],
    "plantaris": [("right plantaris", None)],
    "popliteus": [("right popliteus", None)],
    "flexor_digitorum_longus": [("right flexor digitorum longus", None)],
    "tibialis_posterior": [("right tibialis posterior", None)],
    "flexor_hallucis_longus": [("right flexor hallucis longus", None)],
    # стопа
    "extensor_digitorum_brevis": [("right extensor digitorum brevis", None)],
    "extensor_hallucis_brevis": [("right extensor hallucis brevis", None)],
    "abductor_hallucis": [("right abductor hallucis", None)],
    "flexor_hallucis_brevis": [("medial head of right flexor hallucis brevis", "medh"), ("lateral head of right flexor hallucis brevis", "lath")],
    "adductor_hallucis": [("oblique head of right adductor hallucis", "obl"), ("transverse head of right adductor hallucis", "transv")],
    "abductor_digiti_minimi_pedis": [("abductor digiti minimi of right foot", None)],
    "flexor_digiti_minimi_brevis_pedis": [("flexor digiti minimi brevis of right foot", None)],
    "opponens_digiti_minimi_pedis": [("opponens digiti minimi of right foot", None)],
    "flexor_digitorum_brevis": [("right flexor digitorum brevis", None)],
    "quadratus_plantae": [("right flexor accessorius", None)],
    "lumbricals_pedis": [("first lumbrical of right foot", "l1"), ("second lumbrical of right foot", "l2"),
                         ("third lumbrical of right foot", "l3"), ("fourth lumbrical of right foot", "l4")],
    "plantar_interossei": [("first plantar interosseous of right foot", "p1"), ("second plantar interosseous of right foot", "p2"),
                           ("third plantar interosseous of right foot", "p3")],
    "dorsal_interossei_pedis": [("set of dorsal interossei of right foot", None)],
    # тазовое дно
    "levator_ani": [("right pubococcygeus", "pubo"), ("right iliococcygeus", "ilio")],
    "coccygeus": [("right coccygeus", None)],
}

TOE = ["big toe", "second toe", "third toe", "fourth toe", "little toe"]
B = {
    "hip_bone": ["right hip bone"], "sacrum": ["sacrum"],
    "femur": ["right femur"], "patella": ["right patella"], "tibia": ["right tibia"], "fibula": ["right fibula"],
    "talus": ["right talus"], "calcaneus": ["right calcaneus"], "navicular": ["navicular bone of right foot"],
    "cuboid": ["right cuboid bone"], "cuneiform_med": ["right medial cuneiform bone"],
    "cuneiform_int": ["right intermediate cuneiform bone"], "cuneiform_lat": ["right lateral cuneiform bone"],
    "sesamoid_pedis": ["sesamoid bone of right foot"],
}
ORD = ["first", "second", "third", "fourth", "fifth"]
for i in range(5):
    B[f"metatarsal_{i+1}"] = [f"right {ORD[i]} metatarsal bone"]
    B[f"toe_prox_{i+1}"] = [f"proximal phalanx of right {TOE[i]}"]
    if i > 0:
        B[f"toe_mid_{i+1}"] = [f"middle phalanx of right {TOE[i]}"]
    B[f"toe_dist_{i+1}"] = [f"distal phalanx of right {TOE[i]}"]

O = {
    "iliotibial_tract": ["right iliotibial tract"],
    "inguinal_ligament": ["right inguinal ligament"],
    "long_plantar_ligament": ["right long plantar ligament"],
    "calcaneal_tendon": ["right calcaneal tendon"],
}

CTX = ["left hip bone", "twelfth thoracic vertebra", "first lumbar vertebra", "second lumbar vertebra",
       "third lumbar vertebra", "fourth lumbar vertebra", "fifth lumbar vertebra",
       "intervertebral disk of first lumbar vertebra", "intervertebral disk of second lumbar vertebra",
       "intervertebral disk of third lumbar vertebra", "intervertebral disk of fourth lumbar vertebra",
       "intervertebral disk of fifth lumbar vertebra"]

MUSCLES = {k: [(ids(n)[0], p) for n, p in v] for k, v in M.items()}
BONES = {k: ids(*v) for k, v in B.items()}
OTHER = {k: ids(*v) for k, v in O.items()}
CONTEXT = ids(*CTX)

def all_ids():
    out = []
    for parts in MUSCLES.values():
        out += [p for p, _ in parts]
    for v in list(BONES.values()) + list(OTHER.values()):
        out += v
    return out + CONTEXT

if __name__ == "__main__":
    print("\n".join(all_ids()))
