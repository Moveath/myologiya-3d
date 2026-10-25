"""Per-owner educational decisions, never a blanket bilateral acceptance."""
from manifest_leg import BONES

REPORT = "research/stage6-mirrored-recovery-2026-10-20.md"
BASE = "models/bodyparts3d-3.0/mirrored-left-foot"
ADMITTED = ("sesamoid_pedis_left",) + tuple(
    f"toe_{kind}_{digit}_left" for kind in ("prox", "mid", "dist") for digit in (2, 3, 4))
NOTICE = ("Зеркальная учебная реконструкция по правой кости. "
          "Точная геометрия суставных поверхностей, границ и зазоров не подтверждена.")
NOTE = (NOTICE + " BodyParts3D 3.0, DBCLS, CC BY-SA 2.1 Japan. "
        "Отражение относительно X=0 учебной системы атласа; это не независимый левый образец. "
        "Крупная форма, сторона и масштаб проверены; точная срединная плоскость образца не принята. "
        "Сохранены локальные пересечения исходных сеток: они не изображают физиологический контакт. "
        "Зеркальными являются только фаланги II–IV пальцев и общий ресурс сесамоидов; остальные кости левой "
        "стопы — исходные левые модели BodyParts3D, поэтому стопа собрана из сеток разного происхождения. "
        "Координаты пинов, контуры, площади и индивидуальные маски сесамоидов не переносились.")
PENDING = {
    "talus_left": "Отражение не устранило конфликт с calcaneus (выборочно до 1,030 мм) и создаёт конфликт с действующей левой navicular (до 0,771 мм).",
    "calcaneus_left": "Сохраняется конфликт с talus (выборочно до 1,030 мм); нужна согласованная приёмка подтаранного комплекса.",
    "cuboid_left": "Конфликт с cuneiform_lat сохраняется (выборочно до 2,655 мм); отражение не восстанавливает корректное сочленение.",
    "cuneiform_lat_left": "Конфликт с cuboid сохраняется (выборочно до 2,655 мм); отражение не восстанавливает корректное сочленение.",
    "metatarsal_1_left": "Конфликт с действующей левой медиальной клиновидной сохраняется (выборочно до 1,264 мм).",
    "metatarsal_2_left": "Сохраняются конфликты основания и головки с соседями, включая проксимальную фалангу II (выборочно до 0,912 мм).",
    "metatarsal_3_left": "Конфликт с IV плюсневой сохраняется (выборочно до 1,264 мм); основание/соседние поверхности не приняты.",
    "metatarsal_4_left": "Конфликты с III/V плюсневыми сохраняются (выборочно до 1,264/1,040 мм).",
    "metatarsal_5_left": "Конфликт с IV плюсневой сохраняется (выборочно до 1,040 мм).",
    "toe_prox_1_left": "Широкое пересечение межфалангового сочленения I сохраняется (выборочно до 0,675 мм); обе поверхности требуют проверки.",
    "toe_dist_1_left": "Широкое пересечение межфалангового сочленения I сохраняется (выборочно до 0,675 мм); обе поверхности требуют проверки.",
    "toe_prox_5_left": "Пересечение с маленькой средней фалангой V (выборочно до 0,788 мм) требует независимой приёмки.",
    "toe_mid_5_left": "Пересечение с проксимальной фалангой V (выборочно до 0,788 мм) требует независимой приёмки.",
    "toe_dist_5_left": "Четыре вырожденные грани сжатого правого ресурса устранены в отдельной производной из OBJ, но две компоненты исходника и сочленение V пальца не приняты.",
}


def model_note(bone):
    if bone in ADMITTED:
        return NOTE
    if bone in PENDING:
        return ("Зеркальная пробная геометрия подготовлена, но не подключена. " + PENDING[bone] +
                " Дефект не исправлялся произвольным смещением/деформацией. Нужны согласованная "
                "сегментация, поза и независимая приёмка; прежние ограничения сохранены в отчётах. "
                "Координаты и точные поверхности не подтверждены.")


def admit(cards):
    for bone in ADMITTED:
        assert cards[bone].get("noModel"), "Do not replace a functioning model"
        right = bone.removesuffix("_left")
        cards[bone].update(noModel=False, modelStatus="educational_limited",
            modelNotice=NOTICE, modelRegionLabel="Левые фаланги II–IV и сесамоиды (зеркальная реконструкция)",
            modelFile=f"{BASE}/{bone}.glb", modelLicense=f"{BASE}/LICENSE-MODELS.txt",
            modelOrigin=dict(method="mirrored_educational_reconstruction",
                sourceBone=right, sourceSide="right", sourceFMA=BONES[right],
                sourceVersion="BodyParts3D 3.0", sourceAsset="leg-glb.txt",
                reflectionPlane=dict(normal=[1,0,0],offset=0,space="atlas_world_metres"),
                exactSpecimenPlaneAccepted=False, independentlyScannedLeft=False),
            modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT),
            note=NOTE)
        cards[bone]["refs"].append(dict(title="BodyParts3D — источник зеркальной учебной реконструкции",
            url=f"{BASE}/LICENSE-MODELS.txt", locator=", ".join(BONES[right])+"; правая исходная кость",
            scope="geometry_provenance", checked="2026-10-20"))
    for bone in PENDING:
        assert cards[bone].get("noModel")
        cards[bone].update(note=model_note(bone),
            modelReview=dict(educationalAcceptance=False, fullAnatomicalAcceptance=False,
                             report=REPORT, mirroredCandidateRejected=True))
