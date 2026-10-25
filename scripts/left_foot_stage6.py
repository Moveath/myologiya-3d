"""Foot educational admission is per owner; trial geometry stays outside the atlas."""
from left_carpals1_stage6 import NOTICE

REPORT = "research/stage6-left-tarsals-report-2026-10-20.md"
SOURCES = {
    "navicular_left": "FMA24501",
    "cuneiform_med_left": "FMA24522",
    "cuneiform_int_left": "FMA24524",
}
BASE = "models/bodyparts3d-3.0/left-tarsals"
NOTE = (NOTICE + " BodyParts3D 3.0/95%, DBCLS; сохранены исходные левая сторона, масштаб и система координат. "
        "Точные суставные поверхности, хрящи, зазоры и локализация пинов не приняты. "
        "Таранная, пяточная, кубовидная и латеральная клиновидная модели подключены 25.10.2026 отдельной "
        "партией по контрольной правой стороне; пересечения исходных сеток сохранены. Модели не отражались "
        "и не подгонялись; независимый левый скан не подтверждён.")
TRIAL = {
    "talus_left": "Таранная и пяточная сетки пересекаются: 329 пар треугольников, выборочная глубина до 1,004 мм.",
    "calcaneus_left": "Таранная и пяточная сетки пересекаются: 329 пар треугольников, выборочная глубина до 1,004 мм.",
    "cuboid_left": "Кубовидная и латеральная клиновидная сетки пересекаются: 247 пар треугольников, выборочная глубина до 2,663 мм.",
    "cuneiform_lat_left": "Кубовидная и латеральная клиновидная сетки пересекаются: 247 пар треугольников, выборочная глубина до 2,663 мм.",
    "metatarsal_1_left": "Есть пересечения с медиальной клиновидной (280 пар, выборочно до 1,197 мм), группой сесамоидов и проксимальной фалангой I.",
    "metatarsal_2_left": "Есть пересечения с III плюсневой, медиальной/латеральной клиновидными и проксимальной фалангой II (191 пара, выборочно до 0,915 мм).",
    "metatarsal_3_left": "Есть пересечения с II/IV плюсневыми и проксимальной фалангой III; для пары III–IV выборочная глубина до 1,263 мм.",
    "metatarsal_4_left": "Есть пересечения с III/V плюсневыми, кубовидной и проксимальной фалангой IV; для пары III–IV выборочная глубина до 1,263 мм.",
    "metatarsal_5_left": "Есть пересечения с IV плюсневой, кубовидной и проксимальной фалангой V; для пары IV–V выборочная глубина до 0,997 мм.",
}


def model_note(bone, fallback):
    from left_baseline_stage6 import note as baseline_note
    from mirrored_foot_stage6 import model_note as mirrored_note
    reviewed = baseline_note(bone) or mirrored_note(bone)
    if reviewed:
        return reviewed
    if bone in SOURCES:
        return NOTE
    if bone in TRIAL:
        return ("Пробная GLB подготовлена, но не подключена к основному атласу. " + TRIAL[bone] +
                " Нужна независимая проверка сопряжённых поверхностей и исходной сегментации; "
                + ("координаты и контуры не подтверждены." if bone.startswith("metatarsal_") else
                   "координаты, контуры и sinus tarsi не подтверждены."))
    return fallback


def admit(cards):
    for bone, source in SOURCES.items():
        cards[bone].update(noModel=False, sourceId=source, modelStatus="educational_limited",
            modelNotice=NOTICE, modelRegionLabel="Левая стопа (исходные модели BodyParts3D)",
            modelFile=f"{BASE}/{bone}.glb", modelLicense=f"{BASE}/LICENSE-MODELS.txt",
            modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT),
            note=NOTE)
        cards[bone]["refs"].append(dict(title="BodyParts3D 3.0 — DBCLS, CC BY-SA 2.1 Japan",
            url=f"{BASE}/LICENSE-MODELS.txt", locator=source+"; производная GLB, учебный допуск",
            scope="geometry_provenance", checked="2026-10-20"))
    for bone in TRIAL:
        cards[bone].update(note=model_note(bone, ""),
            modelReview=dict(educationalAcceptance=False, fullAnatomicalAcceptance=False,
                report="research/stage6-left-metatarsals-report-2026-10-20.md" if bone.startswith("metatarsal_") else REPORT))
    from mirrored_foot_stage6 import admit as admit_mirrored
    admit_mirrored(cards)
    from left_baseline_stage6 import admit as admit_baseline
    admit_baseline(cards, "foot")
