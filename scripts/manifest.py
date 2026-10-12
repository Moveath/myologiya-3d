# Which BodyParts3D files make up each structure (right upper limb).
# kind: muscle / bone / other (selectable) ; context (faint, not selectable)

MUSCLES = {
    # мышцы плечевого пояса
    "deltoid": [("FMA34680", "clav"), ("FMA34682", "acrom"), ("FMA34684", "spin")],
    "supraspinatus": [("FMA32544", None)],
    "infraspinatus": [("FMA32547", None)],
    "teres_minor": [("FMA32553", None)],
    "teres_major": [("FMA32551", None)],
    "subscapularis": [("FMA13414", None)],
    # плечо
    "coracobrachialis": [("FMA37665", None)],
    "biceps_brachii": [("FMA37686", "long"), ("FMA37684", "short")],
    "brachialis": [("FMA37668", None)],
    "triceps_brachii": [("FMA37699", "long"), ("FMA37697", "lat"), ("FMA37695", "med")],
    "anconeus": [("FMA37705", None)],
    # предплечье, передняя группа
    "pronator_teres": [("FMA38560", "hum"), ("FMA38562", "uln")],
    "flexor_carpi_radialis": [("FMA38460", None)],
    "palmaris_longus": [("FMA38463", None)],
    "flexor_carpi_ulnaris": [("FMA38617", "hum"), ("FMA38619", "uln")],
    "flexor_digitorum_superficialis": [("FMA38638", "humuln"), ("FMA38640", "rad")],
    "flexor_digitorum_profundus": [("FMA38479", None)],
    "flexor_pollicis_longus": [("FMA38482", None)],
    "pronator_quadratus": [("FMA38454", None)],
    # предплечье, задняя группа
    "brachioradialis": [("FMA38486", None)],
    "extensor_carpi_radialis_longus": [("FMA38495", None)],
    "extensor_carpi_radialis_brevis": [("FMA38498", None)],
    "extensor_digitorum": [("FMA38501", None)],
    "extensor_digiti_minimi": [("FMA38504", None)],
    "extensor_carpi_ulnaris": [("BP45", "hum"), ("BP47", "uln")],
    "supinator": [("FMA38513", None)],
    "abductor_pollicis_longus": [("FMA38516", None)],
    "extensor_pollicis_brevis": [("FMA38519", None)],
    "extensor_pollicis_longus": [("FMA38522", None)],
    "extensor_indicis": [("FMA38525", None)],
    # кисть
    "abductor_pollicis_brevis": [("FMA37386", None)],
    "flexor_pollicis_brevis": [("FMA65198", "sup"), ("FMA46110", "deep")],
    "opponens_pollicis": [("FMA37390", None)],
    "adductor_pollicis": [("FMA46121", "obl"), ("FMA46123", "transv")],
    "abductor_digiti_minimi": [("FMA37396", None)],
    "flexor_digiti_minimi_brevis": [("FMA37398", None)],
    "opponens_digiti_minimi": [("FMA37400", None)],
    "lumbricals": [("FMA42398", None)],
    "palmar_interossei": [("FMA42402", None)],
    "dorsal_interossei": [("FMA42404", None)],
    # мышцы туловища, действующие на плечевой пояс и плечо
    "pectoralis_major": [("FMA34690", "clav"), ("FMA79979", "stern"), ("FMA45874", "abd")],
    "pectoralis_minor": [("FMA13375", None)],
    "subclavius": [("FMA13412", None)],
    "serratus_anterior": [("FMA13398", None)],
    "latissimus_dorsi": [("FMA13358", None)],
    "trapezius": [("FMA33586", "desc"), ("FMA33584", "transv"), ("FMA33581", "asc")],
    "rhomboid_major": [("FMA13381", None)],
    "rhomboid_minor": [("FMA13383", None)],
    "levator_scapulae": [("FMA32540", None)],
}

BONES = {
    "clavicle": ["FMA13322"], "scapula": ["FMA13395"], "humerus": ["FMA23130"],
    "radius": ["FMA23464"], "ulna": ["FMA23467"],
    "scaphoid": ["FMA24435"], "lunate": ["FMA24437"], "triquetrum": ["FMA24439"],
    "pisiform": ["FMA24441"], "trapezium": ["FMA24443"], "trapezoid": ["FMA23725"],
    "capitate": ["FMA24446"], "hamate": ["FMA24448"],
    "metacarpal_1": ["FMA24464"], "metacarpal_2": ["FMA24466"], "metacarpal_3": ["FMA24468"],
    "metacarpal_4": ["FMA24470"], "metacarpal_5": ["FMA24472"],
    "phalanx_prox_1": ["FMA24450"], "phalanx_prox_2": ["FMA24451"], "phalanx_prox_3": ["FMA24452"],
    "phalanx_prox_4": ["FMA24453"], "phalanx_prox_5": ["FMA24454"],
    "phalanx_mid_2": ["FMA24455"], "phalanx_mid_3": ["FMA24456"], "phalanx_mid_4": ["FMA24457"],
    "phalanx_mid_5": ["FMA24458"],
    "phalanx_dist_1": ["FMA24459"], "phalanx_dist_2": ["FMA24460"], "phalanx_dist_3": ["FMA24461"],
    "phalanx_dist_4": ["FMA24462"], "phalanx_dist_5": ["FMA24463"],
}

OTHER = {
    "interosseous_membrane": ["FMA23707"],
    "flexor_retinaculum": ["FMA40120"],
}

CONTEXT = [
    # грудина, рёбра и хрящи справа, позвонки
    "FMA7486", "FMA7487", "FMA7488",
    "FMA7857", "FMA7882", "FMA7909", "FMA7957", "FMA8066", "FMA8175", "FMA8229", "FMA8283",
    "FMA8364", "FMA8445", "FMA8531", "FMA8533",
    "FMA7875", "FMA7886", "FMA7913", "FMA7976", "FMA8070", "FMA8194", "FMA8248", "BP28",
    "FMA12519", "FMA12520", "FMA12521", "FMA12522", "FMA12523", "FMA12524", "FMA12525",
    "FMA9165", "FMA9187", "FMA9209", "FMA9248", "FMA9922", "FMA9945", "FMA9968", "FMA9991",
    "FMA10014", "FMA10037", "FMA10059", "FMA10081",
]


def all_ids():
    ids = []
    for parts in MUSCLES.values():
        ids += [p for p, _ in parts]
    for v in BONES.values():
        ids += v
    for v in OTHER.values():
        ids += v
    ids += CONTEXT
    return ids


if __name__ == "__main__":
    print("\n".join(all_ids()))
