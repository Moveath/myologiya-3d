"""Contralateral-baseline educational admissions: native left BP3D owners, never full acceptance."""
from left_carpals1_stage6 import NOTICE

REPORT = "research/stage6-left-baseline-admission-2026-10-25.md"
BASE = "models/bodyparts3d-3.0/left-baseline"
FOOT = {
    "talus_left": "FMA24483", "calcaneus_left": "FMA24498", "cuboid_left": "FMA24529",
    "cuneiform_lat_left": "FMA24526", "metatarsal_1_left": "FMA24508", "metatarsal_2_left": "FMA24510",
    "metatarsal_3_left": "FMA24512", "metatarsal_4_left": "FMA24514", "metatarsal_5_left": "FMA24516",
    "toe_prox_1_left": "FMA43254", "toe_dist_1_left": "FMA32651", "toe_prox_5_left": "FMA32641",
    "toe_mid_5_left": "FMA230988", "toe_dist_5_left": "FMA32659",
}
HAND = {"metacarpal_1_left": "FMA24465", "metacarpal_3_left": "FMA24469"}
SOURCES = {**FOOT, **HAND}
NOTE = (NOTICE + " BodyParts3D 3.0/95%, DBCLS; исходная левая кость без отражения, подгонки и ремонта; "
        "сторона, нумерация, масштаб и крупная форма проверены. Учебный допуск 25.10.2026 по контрольной стороне: "
        "та же выборочная диагностика на уже принятой правой модели того же источника дала те же пересечения "
        "соседних сеток (различие до 0,09 мм). Пересечения сохранены и не изображают физиологический контакт; "
        "крупнейшие — кубовидная/латеральная клиновидная около 2,66 мм, таранная/пяточная около 1,0 мм, "
        "I пястная/трапеция около 1,15 мм. Точные фасетки, хрящи, суставные щели, пины и sinus tarsi не приняты; "
        "независимое сканирование левого образца не подтверждено.")
MIXED = ("Левая стопа смешанная: фаланги II–IV пальцев и сесамоиды — зеркальная учебная реконструкция, "
         "поэтому на четырёх стыках с ними (I плюсневая/сесамоиды, II–IV плюснефаланговые) глубина отличается "
         "от правой пары до 0,41 мм, оставаясь в пределах принятых правых плюснефаланговых пар.")
LABEL = {"foot": "Левая стопа (исходные модели BodyParts3D)", "hand": "Левая пясть"}


def note(bone):
    return NOTE + (" " + MIXED if bone in FOOT else "") if bone in SOURCES else None


def admit(cards, region):
    owners = FOOT if region == "foot" else HAND
    for bone, source in owners.items():
        assert cards[bone].get("noModel") is True, "Do not replace a functioning model"
        cards[bone].update(noModel=False, sourceId=source, modelStatus="educational_limited",
            modelNotice=NOTICE, modelRegionLabel=LABEL[region],
            modelFile=f"{BASE}/{bone}.glb", modelLicense=f"{BASE}/LICENSE-MODELS.txt",
            modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT,
                             admissionRule="contralateral_baseline_same_source"),
            note=note(bone))
        cards[bone]["refs"].append(dict(title="BodyParts3D 3.0 — DBCLS, CC BY-SA 2.1 Japan",
            url=f"{BASE}/LICENSE-MODELS.txt", locator=source + "; производная GLB, учебный допуск по контрольной стороне",
            scope="geometry_provenance", checked="2026-10-25"))
