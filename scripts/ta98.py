# Terminologia Anatomica (TA98, IFAA) — bone features used by the atlas.
# Source of codes and Latin: IFAA TA98 lists (ifaa.unifr.ch, units TAH769, TAH894, TAH1027).
# Russian: Международная анатомическая терминология (рус. экв., под ред. Л. Л. Колесникова, 2003),
# with the traditional textbook name added in parentheses where it differs.
# Entry: code -> (latin, russian, flags)   flags: 'inc' = inconstant (in parentheses in TA98)

T = {}
G = {}  # code -> group label (part of a bone the term belongs to)


def add(prefix, rows, group=None):
    for num, lat, ru, *fl in rows:
        code = f"A{prefix}.{num:03d}"
        T[code] = (lat, ru, fl[0] if fl else "")
        if group:
            G[code] = group


# ---------------- vertebral column: sacrum, coccyx (A02.2.05, A02.2.06) ----------------
add("02.2.05", [
    (2, "basis ossis sacri", "Основание крестца"),
    (3, "promontorium", "Мыс"),
    (4, "ala ossis sacri", "Крыло крестца"),
    (5, "processus articularis superior", "Верхний суставной отросток"),
    (6, "pars lateralis", "Латеральная часть"),
    (7, "facies auricularis", "Ушковидная поверхность"),
    (8, "tuberositas ossis sacri", "Крестцовая бугристость"),
    (9, "facies pelvica", "Тазовая поверхность"),
    (10, "lineae transversae", "Поперечные линии"),
    (11, "foramina intervertebralia", "Межпозвоночные отверстия"),
    (12, "foramina sacralia anteriora", "Передние крестцовые отверстия"),
    (13, "facies dorsalis", "Дорсальная поверхность"),
    (14, "crista sacralis mediana", "Срединный крестцовый гребень"),
    (15, "foramina sacralia posteriora", "Задние крестцовые отверстия"),
    (16, "crista sacralis medialis", "Медиальный крестцовый гребень"),
    (17, "crista sacralis lateralis", "Латеральный крестцовый гребень"),
    (18, "cornu sacrale", "Крестцовый рог"),
    (19, "canalis sacralis", "Крестцовый канал"),
    (20, "hiatus sacralis", "Крестцовая щель"),
    (21, "apex ossis sacri", "Верхушка крестца"),
], "Крестец")
add("02.2.06", [
    (1, "os coccygis", "Копчик", "part"),
    (2, "cornu coccygeum", "Копчиковый рог"),
], "Копчик")

# ---------------- upper limb (A02.4) ----------------
add("02.4.01", [
    (2, "facies costalis; facies anterior", "Рёберная (передняя) поверхность"),
    (3, "fossa subscapularis", "Подлопаточная ямка"),
    (4, "facies posterior", "Задняя поверхность"),
    (5, "spina scapulae", "Ость лопатки"),
    (6, "tuberculum deltoideum", "Дельтовидный бугорок"),
    (7, "fossa supraspinata", "Надостная ямка"),
    (8, "fossa infraspinata", "Подостная ямка"),
    (9, "acromion", "Акромион"),
    (10, "facies articularis clavicularis", "Ключичная суставная поверхность"),
    (11, "angulus acromii", "Угол акромиона"),
    (12, "margo medialis", "Медиальный край"),
    (13, "margo lateralis", "Латеральный край"),
    (14, "margo superior", "Верхний край"),
    (15, "incisura scapulae", "Вырезка лопатки"),
    (16, "angulus inferior", "Нижний угол"),
    (17, "angulus lateralis", "Латеральный угол"),
    (18, "angulus superior", "Верхний угол"),
    (19, "cavitas glenoidalis", "Суставная впадина"),
    (20, "tuberculum supraglenoidale", "Надсуставной бугорок"),
    (21, "tuberculum infraglenoidale", "Подсуставной бугорок"),
    (22, "collum scapulae", "Шейка лопатки"),
    (23, "processus coracoideus", "Клювовидный отросток"),
])
add("02.4.02", [
    (2, "extremitas sternalis", "Грудинный конец"),
    (3, "facies articularis sternalis", "Грудинная суставная поверхность"),
    (4, "impressio ligamenti costoclavicularis", "Вдавление рёберно-ключичной связки"),
    (5, "corpus claviculae", "Тело ключицы"),
    (6, "sulcus musculi subclavii", "Борозда подключичной мышцы"),
    (7, "extremitas acromialis", "Акромиальный конец"),
    (8, "facies articularis acromialis", "Акромиальная суставная поверхность"),
    (9, "tuberositas ligamenti coracoclavicularis", "Бугристость клювовидно-ключичной связки"),
    (10, "tuberculum conoideum", "Конусовидный бугорок"),
    (11, "linea trapezoidea", "Трапециевидная линия"),
])
add("02.4.04", [
    (2, "caput humeri", "Головка плечевой кости"),
    (3, "collum anatomicum", "Анатомическая шейка"),
    (4, "collum chirurgicum", "Хирургическая шейка"),
    (5, "tuberculum majus", "Большой бугорок"),
    (6, "tuberculum minus", "Малый бугорок"),
    (7, "sulcus intertubercularis", "Межбугорковая борозда"),
    (8, "crista tuberculi majoris", "Гребень большого бугорка"),
    (9, "crista tuberculi minoris", "Гребень малого бугорка"),
    (10, "corpus humeri", "Тело плечевой кости"),
    (11, "facies anteromedialis", "Передняя медиальная поверхность"),
    (12, "facies anterolateralis", "Передняя латеральная поверхность"),
    (13, "facies posterior", "Задняя поверхность"),
    (14, "sulcus nervi radialis", "Борозда лучевого нерва"),
    (15, "margo medialis", "Медиальный край"),
    (16, "crista supraepicondylaris medialis", "Медиальный надмыщелковый гребень"),
    (17, "processus supracondylaris", "Надмыщелковый отросток", "inc"),
    (18, "margo lateralis", "Латеральный край"),
    (19, "crista supraepicondylaris lateralis", "Латеральный надмыщелковый гребень"),
    (20, "tuberositas deltoidea", "Дельтовидная бугристость"),
    (21, "condylus humeri", "Мыщелок плечевой кости"),
    (22, "capitulum humeri", "Головка мыщелка плечевой кости"),
    (23, "trochlea humeri", "Блок плечевой кости"),
    (24, "fossa olecrani", "Ямка локтевого отростка"),
    (25, "fossa coronoidea", "Венечная ямка"),
    (26, "fossa radialis", "Лучевая ямка"),
    (27, "epicondylus medialis", "Медиальный надмыщелок"),
    (28, "sulcus nervi ulnaris", "Борозда локтевого нерва"),
    (29, "epicondylus lateralis", "Латеральный надмыщелок"),
])
add("02.4.05", [
    (2, "caput radii", "Головка лучевой кости"),
    (3, "fovea articularis", "Суставная ямка"),
    (4, "circumferentia articularis", "Суставная окружность"),
    (5, "collum radii", "Шейка лучевой кости"),
    (6, "corpus radii", "Тело лучевой кости"),
    (7, "tuberositas radii", "Бугристость лучевой кости"),
    (8, "facies anterior", "Передняя поверхность"),
    (9, "facies posterior", "Задняя поверхность"),
    (10, "facies lateralis", "Латеральная поверхность"),
    (11, "tuberositas pronatoria", "Пронаторная бугристость"),
    (12, "margo interosseus", "Межкостный край"),
    (13, "margo anterior", "Передний край"),
    (14, "margo posterior", "Задний край"),
    (15, "processus styloideus radii", "Шиловидный отросток лучевой кости"),
    (16, "crista suprastyloidea", "Надшиловидный гребень"),
    (17, "tuberculum dorsale", "Дорсальный бугорок"),
    (18, "sulci tendinum musculorum extensorum", "Борозды сухожилий мышц-разгибателей"),
    (19, "incisura ulnaris", "Локтевая вырезка"),
    (20, "facies articularis carpalis", "Запястная суставная поверхность"),
])
add("02.4.06", [
    (2, "olecranon", "Локтевой отросток"),
    (3, "processus coronoideus", "Венечный отросток"),
    (4, "tuberositas ulnae", "Бугристость локтевой кости"),
    (5, "incisura radialis", "Лучевая вырезка"),
    (6, "incisura trochlearis", "Блоковидная вырезка"),
    (7, "corpus ulnae", "Тело локтевой кости"),
    (8, "facies anterior", "Передняя поверхность"),
    (9, "facies posterior", "Задняя поверхность"),
    (10, "facies medialis", "Медиальная поверхность"),
    (11, "margo interosseus", "Межкостный край"),
    (12, "margo anterior", "Передний край"),
    (13, "margo posterior", "Задний край"),
    (14, "crista musculi supinatoris", "Гребень супинатора"),
    (15, "caput ulnae", "Головка локтевой кости"),
    (16, "circumferentia articularis", "Суставная окружность"),
    (17, "processus styloideus ulnae", "Шиловидный отросток локтевой кости"),
])
add("02.4.08", [
    (2, "os centrale", "Центральная кость", "inc"),
    (4, "tuberculum ossis scaphoidei", "Бугорок ладьевидной кости"),
    (9, "tuberculum ossis trapezii", "Бугорок кости-трапеции"),
    (13, "hamulus ossis hamati", "Крючок крючковидной кости"),
    (14, "sulcus carpi", "Борозда запястья"),
])
add("02.4.09", [
    (2, "basis ossis metacarpi", "Основание пястной кости"),
    (3, "corpus ossis metacarpi", "Тело пястной кости"),
    (4, "caput ossis metacarpi", "Головка пястной кости"),
    (5, "processus styloideus ossis metacarpi tertii [III]", "Шиловидный отросток III пястной кости"),
])
add("02.4.10", [
    (5, "tuberositas phalangis distalis", "Бугристость дистальной фаланги"),
    (6, "basis phalangis", "Основание фаланги"),
    (7, "corpus phalangis", "Тело фаланги"),
    (8, "caput phalangis", "Головка фаланги"),
    (9, "trochlea phalangis", "Блок фаланги"),
])

# ---------------- lower limb (A02.5) ----------------
add("02.5.01", [
    (2, "acetabulum", "Вертлужная впадина"),
    (3, "limbus acetabuli; margo acetabuli", "Край вертлужной впадины"),
    (4, "fossa acetabuli", "Ямка вертлужной впадины"),
    (5, "incisura acetabuli", "Вырезка вертлужной впадины"),
    (6, "facies lunata", "Полулунная поверхность"),
    (7, "ramus ischiopubicus", "Седалищно-лобковая ветвь"),
    (8, "foramen obturatum", "Запирательное отверстие"),
    (9, "incisura ischiadica major", "Большая седалищная вырезка"),
], "Тазовая кость в целом")
add("02.5.01", [
    (102, "corpus ossis ilii", "Тело подвздошной кости"),
    (103, "sulcus supraacetabularis", "Надвертлужная борозда"),
    (104, "ala ossis ilii", "Крыло подвздошной кости"),
    (105, "linea arcuata", "Дугообразная линия"),
    (106, "crista iliaca", "Подвздошный гребень"),
    (107, "labium externum", "Наружная губа"),
    (108, "tuberculum iliacum", "Подвздошный бугорок"),
    (109, "linea intermedia", "Промежуточная линия"),
    (110, "labium internum", "Внутренняя губа"),
    (111, "spina iliaca anterior superior", "Верхняя передняя подвздошная ость"),
    (112, "spina iliaca anterior inferior", "Нижняя передняя подвздошная ость"),
    (113, "spina iliaca posterior superior", "Верхняя задняя подвздошная ость"),
    (114, "spina iliaca posterior inferior", "Нижняя задняя подвздошная ость"),
    (115, "fossa iliaca", "Подвздошная ямка"),
    (116, "facies glutea", "Ягодичная поверхность"),
    (117, "linea glutea anterior", "Передняя ягодичная линия"),
    (118, "linea glutea posterior", "Задняя ягодичная линия"),
    (119, "linea glutea inferior", "Нижняя ягодичная линия"),
    (120, "facies sacropelvica", "Крестцово-тазовая поверхность"),
    (121, "facies auricularis", "Ушковидная поверхность"),
    (122, "tuberositas iliaca", "Подвздошная бугристость"),
], "Подвздошная кость (os ilium)")
add("02.5.01", [
    (202, "corpus ossis ischii", "Тело седалищной кости"),
    (203, "ramus ossis ischii", "Ветвь седалищной кости"),
    (204, "tuber ischiadicum", "Седалищный бугор"),
    (205, "spina ischiadica", "Седалищная ость"),
    (206, "incisura ischiadica minor", "Малая седалищная вырезка"),
], "Седалищная кость (os ischii)")
add("02.5.01", [
    (302, "corpus ossis pubis", "Тело лобковой кости"),
    (303, "tuberculum pubicum", "Лобковый бугорок"),
    (304, "facies symphysialis", "Симфизиальная поверхность"),
    (305, "crista pubica", "Лобковый гребень"),
    (306, "ramus superior ossis pubis", "Верхняя ветвь лобковой кости"),
    (307, "eminentia iliopubica", "Подвздошно-лобковое возвышение"),
    (308, "pecten ossis pubis", "Гребень лобковой кости"),
    (309, "crista obturatoria", "Запирательный гребень"),
    (310, "sulcus obturatorius", "Запирательная борозда"),
    (311, "tuberculum obturatorium anterius", "Передний запирательный бугорок"),
    (312, "tuberculum obturatorium posterius", "Задний запирательный бугорок", "inc"),
    (313, "ramus inferior ossis pubis", "Нижняя ветвь лобковой кости"),
], "Лобковая кость (os pubis)")
add("02.5.04", [
    (2, "caput femoris", "Головка бедренной кости"),
    (3, "fovea capitis femoris", "Ямка головки бедренной кости"),
    (4, "collum femoris", "Шейка бедренной кости"),
    (5, "trochanter major", "Большой вертел"),
    (6, "fossa trochanterica", "Вертельная ямка"),
    (7, "trochanter minor", "Малый вертел"),
    (8, "trochanter tertius", "Третий вертел", "inc"),
    (9, "linea intertrochanterica", "Межвертельная линия"),
    (10, "crista intertrochanterica", "Межвертельный гребень"),
    (11, "tuberculum quadratum", "Квадратный бугорок"),
    (12, "corpus femoris", "Тело бедренной кости"),
    (13, "linea aspera", "Шероховатая линия"),
    (14, "labium laterale", "Латеральная губа"),
    (15, "labium mediale", "Медиальная губа"),
    (16, "linea pectinea", "Гребенчатая линия"),
    (17, "tuberositas glutea", "Ягодичная бугристость"),
    (18, "facies poplitea", "Подколенная поверхность"),
    (19, "linea supracondylaris medialis", "Медиальная надмыщелковая линия"),
    (20, "linea supracondylaris lateralis", "Латеральная надмыщелковая линия"),
    (21, "condylus medialis", "Медиальный мыщелок"),
    (22, "epicondylus medialis", "Медиальный надмыщелок"),
    (23, "tuberculum adductorium", "Приводящий бугорок"),
    (24, "condylus lateralis", "Латеральный мыщелок"),
    (25, "epicondylus lateralis", "Латеральный надмыщелок"),
    (26, "sulcus popliteus", "Подколенная борозда"),
    (27, "facies patellaris", "Надколенниковая поверхность"),
    (28, "fossa intercondylaris", "Межмыщелковая ямка"),
    (29, "linea intercondylaris", "Межмыщелковая линия"),
])
add("02.5.05", [
    (2, "basis patellae", "Основание надколенника"),
    (3, "apex patellae", "Верхушка надколенника"),
    (4, "facies articularis", "Суставная поверхность"),
    (5, "facies anterior", "Передняя поверхность"),
])
add("02.5.06", [
    (2, "facies articularis superior", "Верхняя суставная поверхность"),
    (3, "condylus medialis", "Медиальный мыщелок"),
    (4, "condylus lateralis", "Латеральный мыщелок"),
    (5, "facies articularis fibularis", "Малоберцовая суставная поверхность"),
    (6, "area intercondylaris anterior", "Переднее межмыщелковое поле"),
    (7, "area intercondylaris posterior", "Заднее межмыщелковое поле"),
    (8, "eminentia intercondylaris", "Межмыщелковое возвышение"),
    (9, "tuberculum intercondylare mediale", "Медиальный межмыщелковый бугорок"),
    (10, "tuberculum intercondylare laterale", "Латеральный межмыщелковый бугорок"),
    (11, "corpus tibiae", "Тело большеберцовой кости"),
    (12, "tuberositas tibiae", "Бугристость большеберцовой кости"),
    (13, "facies medialis", "Медиальная поверхность"),
    (14, "facies posterior", "Задняя поверхность"),
    (15, "linea musculi solei", "Линия камбаловидной мышцы"),
    (16, "facies lateralis", "Латеральная поверхность"),
    (17, "margo anterior", "Передний край"),
    (18, "margo medialis", "Медиальный край"),
    (19, "margo interosseus", "Межкостный край"),
    (20, "malleolus medialis", "Медиальная лодыжка"),
    (21, "sulcus malleolaris", "Лодыжковая борозда"),
    (22, "facies articularis malleoli medialis", "Суставная поверхность медиальной лодыжки"),
    (23, "incisura fibularis", "Малоберцовая вырезка"),
    (24, "facies articularis inferior", "Нижняя суставная поверхность"),
])
add("02.5.07", [
    (2, "caput fibulae", "Головка малоберцовой кости"),
    (3, "facies articularis capitis fibulae", "Суставная поверхность головки малоберцовой кости"),
    (4, "apex capitis fibulae", "Верхушка головки малоберцовой кости"),
    (5, "collum fibulae", "Шейка малоберцовой кости"),
    (6, "corpus fibulae", "Тело малоберцовой кости"),
    (7, "facies lateralis", "Латеральная поверхность"),
    (8, "facies medialis", "Медиальная поверхность"),
    (9, "facies posterior", "Задняя поверхность"),
    (10, "crista medialis", "Медиальный гребень"),
    (11, "margo anterior", "Передний край"),
    (12, "margo interosseus", "Межкостный край"),
    (13, "margo posterior", "Задний край"),
    (14, "malleolus lateralis", "Латеральная лодыжка"),
    (15, "facies articularis malleoli lateralis", "Суставная поверхность латеральной лодыжки"),
    (16, "fossa malleoli lateralis", "Ямка латеральной лодыжки"),
    (17, "sulcus malleolaris", "Лодыжковая борозда"),
])
add("02.5.10", [
    (2, "caput tali", "Головка таранной кости"),
    (3, "facies articularis navicularis", "Ладьевидная суставная поверхность"),
    (4, "facies articularis ligamenti calcaneonavicularis plantaris", "Суставная поверхность подошвенной пяточно-ладьевидной связки"),
    (5, "facies articularis partis calcaneonavicularis ligamenti bifurcati", "Суставная поверхность пяточно-ладьевидной части раздвоенной связки"),
    (6, "facies articularis calcanea anterior", "Передняя пяточная суставная поверхность"),
    (7, "collum tali", "Шейка таранной кости"),
    (8, "facies articularis calcanea media", "Средняя пяточная суставная поверхность"),
    (9, "sulcus tali", "Борозда таранной кости"),
    (10, "corpus tali", "Тело таранной кости"),
    (11, "trochlea tali", "Блок таранной кости"),
    (12, "facies superior", "Верхняя поверхность"),
    (13, "facies malleolaris lateralis", "Латеральная лодыжковая поверхность"),
    (14, "processus lateralis tali", "Латеральный отросток таранной кости"),
    (15, "facies malleolaris medialis", "Медиальная лодыжковая поверхность"),
    (16, "processus posterior tali", "Задний отросток таранной кости"),
    (17, "sulcus tendinis musculi flexoris hallucis longi", "Борозда сухожилия длинного сгибателя большого пальца стопы"),
    (18, "tuberculum laterale", "Латеральный бугорок"),
    (19, "tuberculum mediale", "Медиальный бугорок"),
    (20, "facies articularis calcanea posterior", "Задняя пяточная суставная поверхность"),
    (21, "os trigonum", "Треугольная кость", "inc"),
])
add("02.5.11", [
    (2, "tuber calcanei", "Пяточный бугор"),
    (3, "processus medialis tuberis calcanei", "Медиальный отросток пяточного бугра"),
    (4, "processus lateralis tuberis calcanei", "Латеральный отросток пяточного бугра"),
    (5, "tuberculum calcanei", "Пяточный бугорок"),
    (6, "sustentaculum tali", "Опора таранной кости"),
    (7, "sulcus tendinis musculi flexoris hallucis longi", "Борозда сухожилия длинного сгибателя большого пальца стопы"),
    (8, "sulcus calcanei", "Борозда пяточной кости"),
    (9, "sinus tarsi", "Пазуха предплюсны"),
    (10, "facies articularis talaris anterior", "Передняя таранная суставная поверхность"),
    (11, "facies articularis talaris media", "Средняя таранная суставная поверхность"),
    (12, "facies articularis talaris posterior", "Задняя таранная суставная поверхность"),
    (13, "sulcus tendinis musculi fibularis longi", "Борозда сухожилия длинной малоберцовой мышцы"),
    (14, "trochlea fibularis", "Малоберцовый блок"),
    (15, "facies articularis cuboidea", "Кубовидная суставная поверхность"),
])
add("02.5.12", [(2, "tuberositas ossis navicularis", "Бугристость ладьевидной кости")])
add("02.5.16", [
    (2, "sulcus tendinis musculi fibularis longi", "Борозда сухожилия длинной малоберцовой мышцы"),
    (3, "tuberositas ossis cuboidei", "Бугристость кубовидной кости"),
    (4, "processus calcaneus", "Пяточный отросток"),
])
add("02.5.17", [
    (2, "basis ossis metatarsi", "Основание плюсневой кости"),
    (3, "corpus ossis metatarsi", "Тело плюсневой кости"),
    (4, "caput ossis metatarsi", "Головка плюсневой кости"),
    (5, "tuberositas ossis metatarsi primi [I]", "Бугристость I плюсневой кости"),
    (6, "tuberositas ossis metatarsi quinti [V]", "Бугристость V плюсневой кости"),
])
add("02.5.18", [
    (5, "tuberositas phalangis distalis", "Бугристость дистальной фаланги"),
    (6, "basis phalangis", "Основание фаланги"),
    (7, "corpus phalangis", "Тело фаланги"),
    (8, "caput phalangis", "Головка фаланги"),
    (9, "trochlea phalangis", "Блок фаланги"),
])


def rng(prefix, a, b):
    return [f"A{prefix}.{i:03d}" for i in range(a, b + 1)]


# which TA codes each modelled bone must show (exactly these, no more, no fewer)
BONE = {
    "hip_bone": rng("02.5.01", 2, 9) + rng("02.5.01", 102, 122) + rng("02.5.01", 202, 206) + rng("02.5.01", 302, 313),
    "sacrum": rng("02.2.05", 2, 21) + rng("02.2.06", 1, 2),
    "femur": rng("02.5.04", 2, 29),
    "patella": rng("02.5.05", 2, 5),
    "tibia": rng("02.5.06", 2, 24),
    "fibula": rng("02.5.07", 2, 17),
    "talus": rng("02.5.10", 2, 21),
    "calcaneus": rng("02.5.11", 2, 15),
    "navicular": ["A02.5.12.002"],
    "cuboid": rng("02.5.16", 2, 4),
    "cuneiform_med": [], "cuneiform_int": [], "cuneiform_lat": [], "sesamoid_pedis": [],
    "scapula": rng("02.4.01", 2, 23),
    "clavicle": rng("02.4.02", 2, 11),
    "humerus": rng("02.4.04", 2, 29),
    "radius": rng("02.4.05", 2, 20),
    "ulna": rng("02.4.06", 2, 17),
    "scaphoid": ["A02.4.08.004"], "trapezium": ["A02.4.08.009"], "hamate": ["A02.4.08.013"],
    "lunate": [], "triquetrum": [], "pisiform": [], "trapezoid": [], "capitate": [],
}
for i in range(1, 6):
    BONE[f"metatarsal_{i}"] = rng("02.5.17", 2, 4) + (["A02.5.17.005"] if i == 1 else ["A02.5.17.006"] if i == 5 else [])
    BONE[f"metacarpal_{i}"] = rng("02.4.09", 2, 4) + (["A02.4.09.005"] if i == 3 else [])
    for k, pre in (("toe", "02.5.18"), ("phalanx", "02.4.10")):
        prox, mid, dist = (f"toe_prox_{i}", f"toe_mid_{i}", f"toe_dist_{i}") if k == "toe" else (f"phalanx_prox_{i}", f"phalanx_mid_{i}", f"phalanx_dist_{i}")
        BONE[prox] = [f"A{pre}.006", f"A{pre}.007", f"A{pre}.008", f"A{pre}.009"]
        if i > 1:
            BONE[mid] = [f"A{pre}.006", f"A{pre}.007", f"A{pre}.008", f"A{pre}.009"]
        BONE[dist] = [f"A{pre}.006", f"A{pre}.007", f"A{pre}.008", f"A{pre}.005"]
# carpal terms that belong to the carpus as a whole (shown with every carpal bone, counted once)
CARPUS_SHARED = ["A02.4.08.014", "A02.4.08.002"]

# Skull source tables are maintained separately, but participate in the same contract.
from head_terms import T as HEAD_TERMS, BONE_CODES as HEAD_BONE_CODES
from manifest_head import SINGLE_BONES as HEAD_SINGLE, PAIRED_BONES as HEAD_PAIRED
T.update(HEAD_TERMS)
for _bone in HEAD_SINGLE:
    BONE[_bone] = list(HEAD_BONE_CODES[_bone])
for _bone in HEAD_PAIRED:
    for _side in ('right', 'left'):
        BONE[f'{_bone}_{_side}'] = list(HEAD_BONE_CODES[_bone])
