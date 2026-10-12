# AGENTS.md — как устроен проект и как его менять

Сначала прочитай README.md (цель, правила точности, бэклог). Здесь — техника.

## Правила (обязательно)

- Весь текст интерфейса и карточек — на русском, латынь — по TA98. Не выдумывать анатомические факты: любое новое утверждение сверить минимум с двумя независимыми источниками; если источники расходятся — написать об этом в карточке (поле `note` у мышцы или в описании точки).
- Точки на костях: на каждой кости ровно официальный список TA98. Таблица терминов — `scripts/ta98.py` (код → латынь, русский, флаги); какие коды обязаны быть на какой кости — словарь `BONE` там же. `make_pins*.py` падают с ошибкой, если на кости не хватает или есть лишний термин. После правок запускать `python3 verify/verify_ta98.py` (ожидается ровно 3 известных расхождения, они описаны в самом скрипте).
- `site/pins.js` и `site/pins-leg.js` руками не править — они генерируются (см. ниже). Тексты точек правятся в `scripts/make_pins.py` / `scripts/make_pins_leg.py`.
- Ничего не брать из платных атласов/приложений. 3D-модели — только из открытых источников с совместимой лицензией (BodyParts3D — CC BY-SA 2.1 JP: указывать авторство, производные — под той же лицензией).
- Проверять вёрстку на ширине 390 px (телефон) и 1280 px, в светлой и тёмной теме.

## Сайт (`site/`)

- `index.html` — вся страница в одном файле (CSS + разметка + JS-модуль). Это **фрагмент** без `<!doctype>`/`<html>`: так требует хост Claude Artifacts. Для обычного хостинга и локального запуска: `python3 scripts/make_local.py site/index.html site/local.html`.
- three.js 0.170.0 подключается через importmap с cdn.jsdelivr.net (OrbitControls, GLTFLoader, MeshoptDecoder).
- Модели: `arm-glb.txt`, `leg-glb.txt` — GLB (сжатие meshopt) в base64; если не загрузились — `arm-q-glb.txt` / `leg-q-glb.txt` (без `-cc`). Base64 — потому что хост артефактов не отдаёт `.glb`; на обычном хостинге можно перейти на `.glb` (поменять `fetchModel`).
- Имена узлов в GLB: `m|<мышца>|<часть>`, `b|<кость>`, `o|<связка/перепонка>`, `c|<id>` (кости-контекст). gltfpack кладёт имена на родительские узлы — при обходе сцены идти вверх по родителям (так сделано в `register`).
- Система координат: BodyParts3D (мм, Z вверх, −Y вперёд) → three.js: `x = x`, `y = z`, `z = −y`, в метрах. Правая сторона тела = −x; для правой конечности +x — медиально, +z — вперёд.
- Основное в `index.html`: `SECTIONS` (разделы и подразделы), `GLOSS` (словарик), `fetchModel/register/loadSection`, `visState/applyVisibility/paint` (видимость: 0 скрыто, 1 бледно, 2 видно), `frame/frameBox/framePart/frameSub`, точки: `currentPins/buildPins/positionPins/computeOcclusion/flyToPin/activatePin`, карточка: `renderSheet`, `bonePinSect` (список образований TA98 по группам), `pinMeta`, навигация: `select`, `goTo`, `setSub`, `enterSection`, `showHome`, список: `renderList`, тест: `quizPool/nextQuestion/renderQuiz`, стартовый экран: `renderHome/renderFigure/layoutFigure`.
- Для отладки на странице есть `window.__atlas = { enterSection, setSub, select, goTo, activatePin, showHome, state }` и `window.__ready`.

### Форматы данных

- `window.ATLAS.groups`: `{id, title, sec, region}`; `boneGroups`: `{id, title, sec}`.
- Мышца (`ATLAS.muscles[id]`): `lat, ru, g` (группа), `d` (слой 1–3), `v` (ракурс), `L` (подпись слоя), `o, i, a, n, s` (начало, прикрепление, функция, иннервация, кровоснабжение), `note`, `noModel`, `parts: {ключ: {ru, lat, o, i, a, n, x}}` — ключ части совпадает с `<часть>` в имени узла модели.
- Кость (`ATLAS.bones[id]`): `ru, lat, g, sub` (подраздел), `x` (описание).
- Точка (`ATLAS.pins[]`): `b` (кость), `id`, `t` (`ta` — термин TA98, `att` — место прикрепления без термина, `soft` — точка на связке/перепонке), `c` (код TA98), `ru`, `lat`, `x` (описание), `p` (координаты), `n` (нормаль), `m` (`[[мышца, 'o'|'i', часть?]]`), `g` (часть кости, например «Подвздошная кость (os ilium)»), `inc: 1` (непостоянное), `sh` (список костей, если термин общий — борозда запястья), `part: 1` (сама кость-часть, например копчик; в счёт не входит).

## Конвейер сборки

Зависимости: Python 3 (`pip install numpy trimesh fast-simplification pillow scipy playwright`, затем `python3 -m playwright install chromium`), Node.js (`cd tools && npm install` — three@0.170.0 и gltfpack).

1. STL-файлы BodyParts3D (в репозиторий не входят, ~270 МБ):
   ```
   python3 scripts/fetch_stl.py manifest stl_dl
   python3 scripts/fetch_stl.py manifest_leg stl_leg
   python3 scripts/fetch_stl.py body stl_body
   ```
   Состав моделей — `scripts/manifest.py` (рука) и `scripts/manifest_leg.py` (нога; названия → id через `bp/all_named.tsv`).
2. Модели (кости — полное разрешение, мышцы упрощаются):
   ```
   BONE_RATIO=1.0 BONE_MAX=20000 python3 scripts/build_glb.py scripts stl_dl build/arm_hi.glb build/meta.json manifest
   BONE_RATIO=1.0 BONE_MAX=20000 python3 scripts/build_glb.py scripts stl_leg build_leg/leg_hi.glb build_leg/meta.json manifest_leg
   node tools/node_modules/gltfpack/cli.js -i build/arm_hi.glb -o build/arm.glb -cc -kn -km
   node tools/node_modules/gltfpack/cli.js -i build/arm_hi.glb -o build/arm_q.glb -kn -km
   (то же для build_leg/leg_hi.glb → leg.glb, leg_q.glb)
   python3 -c "import base64,sys; open(sys.argv[2],'w').write(base64.b64encode(open(sys.argv[1],'rb').read()).decode())" build/arm.glb site/arm-glb.txt
   (то же для arm_q → arm-q-glb.txt, leg → leg-glb.txt, leg_q → leg-q-glb.txt)
   ```
3. Координаты точек (нужны только если менялись модели или добавляются кости). Инструмент — `build/pintool.html` (рука) и `build_leg/pintool.html` (нога): ортографические виды кости с сеткой u/v, `pick(кость, вид, u, v, zoomBox)` бросает луч на поверхность. Расчёт: `landmarks.js` (старый набор ориентиров, используется как опорные точки) и `landmarks_ta.js` (все термины TA98 + места прикрепления).
   ```
   NM=$PWD/tools/node_modules python3 scripts/driver.py build "pintool.html?f=arm_hi.glb" qarm 8773 &
   python3 scripts/export_positions.py qarm pins/ta.json pins/old_hi.json
   NM=$PWD/tools/node_modules python3 scripts/driver.py build_leg "pintool.html?f=leg_hi.glb" qleg 8772 &
   python3 scripts/export_positions.py qleg pins_leg/ta.json pins_leg/old_hi.json
   ```
   Визуальная проверка (картинка появится в `qarm/v1.png`): `python3 scripts/q.py qarm v1 "showTA('scapula','post')"`. Виды: `ant, post, lat, med, sup, inf` или свой `{d:[x,y,z], up:[x,y,z]}`. Остановить драйвер: `touch qarm/_STOP`. Позиции в `landmarks_ta.js` подобраны под эти модели — после пересборки моделей обязательно пересмотреть снимки каждой кости.
4. Точки → сайт (с проверкой полноты списков TA98 по каждой кости):
   ```
   python3 scripts/make_pins.py pins/ta.json pins/old_hi.json site/pins.js
   python3 scripts/make_pins_leg.py pins_leg/ta.json pins_leg/old_hi.json site/pins-leg.js
   python3 verify/verify_ta98.py
   ```
5. Фигура стартового экрана (менять редко):
   ```
   python3 scripts/build_body.py skeleton_parts.json stl_body body/body.glb
   NM=$PWD/tools/node_modules python3 scripts/render_body.py body body/out 560 1240
   ONLY=mask NM=$PWD/tools/node_modules python3 scripts/render_body.py body body/out 1120 2480
   python3 scripts/compose_body.py body/out site
   ```
6. Проверка страницы в headless Chromium (скриншоты `shots/x_N.png`, ошибки консоли печатаются):
   ```
   python3 scripts/make_local.py site/index.html site/local.html
   NM=$PWD/tools/node_modules python3 scripts/shot.py site local.html shots/x 1280 860 "window.__atlas.enterSection('leg').then(()=>1)" "window.__atlas.goTo('hip_bone'); 1"
   ```

`scripts/parts_patch.py` — разовая миграция `data.js` (части мышц), повторно не запускать.

## Как добавить новый раздел (например, мочеполовую систему)

1. Манифест структур (как `manifest_leg.py`) + `fetch_stl.py` + `build_glb.py` → `site/<раздел>-glb.txt`.
2. Данные карточек — новый `site/data-<раздел>.js` (группы с `sec: '<раздел>'`, структуры, тексты с проверкой по 2+ источникам), подключить в `index.html`.
3. Запись в `SECTIONS` (id, ru, hint, `ready: true`, `file`, `subs`, `tries`) и, если нужно, новые группы в `register`/`visState`.
4. Образования по TA98 — дописать коды и русские термины в `scripts/ta98.py`, требуемые списки — в `BONE`, позиции — через pintool, описания — в новом `make_pins_<раздел>.py`.
5. Обновить «Как пользоваться» (диалог `#about`) и счётчики, проверить на телефоне и в тёмной теме.
