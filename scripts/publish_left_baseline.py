"""Publish the contralateral-baseline admissions; originals and earlier outputs are immutable."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import trimesh

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1])
config = json.loads((run / "batch.json").read_text(encoding="utf8"))
decision = json.loads((run / "admission.json").read_text(encoding="utf8"))
target = root / config["publication"]
target.mkdir(parents=True, exist_ok=True)
EXPORTS = ["research/evidence-runs/stage6-left-tarsals-2026-10-20T11-22-52-873Z-6rEIlo/blender-export.json",
           "research/evidence-runs/stage6-left-metatarsals-2026-10-20T11-37-52-033Z-JqSVPJ/blender-export.json",
           "research/evidence-runs/stage6-left-metacarpals-2026-10-20T09-46-20-675Z-MCCbpl/blender-export.json",
           (run / "blender-export.json").relative_to(root).as_posix() if run.is_absolute() else (run / "blender-export.json").as_posix()]
ARRAYS = root / "research/evidence-runs/stage6-remaining20-2026-10-20T13-36-25-228Z-lOkasj/comparison-arrays.json"


def write(path, data):
    if path.exists():
        assert path.read_bytes() == data, f"Refusing to overwrite {path}"
    else:
        with path.open("xb") as f:
            f.write(data)


rows = {}
for name in EXPORTS:
    for row in json.loads((root / name).read_text(encoding="utf8"))["rows"]:
        if row["id"] in decision["admitted"]:
            rows[row["id"]] = dict(row, exportRecord=name)
assert sorted(rows) == sorted(decision["admitted"])
arrays = json.loads(ARRAYS.read_text(encoding="utf8"))
for bone, row in rows.items():
    data = (root / row["derivative"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == row["derivativeSHA256"], bone
    # The compared diagnostic geometry must be the very triangles that are published.
    native = arrays["native__" + bone]
    mesh = trimesh.load(root / row["derivative"], force="mesh", process=False)
    source = np.array(native["vertices"]).reshape(-1, 3)[np.array(native["faces"]).reshape(-1, 3)]
    assert len(mesh.faces) == len(source) == row["triangles"], bone
    assert np.abs(np.sort(mesh.triangles.reshape(-1, 3), axis=0) - np.sort(source.reshape(-1, 3), axis=0)).max() < 1e-6, bone
    write(target / (bone + ".glb"), data)
files = [rows[b] for b in decision["admitted"]]
licence = """BodyParts3D, Copyright© The Database Center for Life Science licensed by CC Attribution-Share Alike 2.1 Japan.
Title/release: BodyParts3D 3.0 / 20110915 / OBJ 95%.
Source: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip
Release terms: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/README_e.html
Licence: https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en
Legal code: https://creativecommons.org/licenses/by-sa/2.1/jp/legalcode.ja
Changes: OBJ to GLB with Blender; [bp.x,bp.z,-bp.y]/1000 (mm to metres, Z-up to Y-up).
No additional decimation, reflection, mesh repair, deformation or fitted registration.
The original archive was already reduced by its author. Source version and hashes: provenance.json.
These derivative geometry files remain CC BY-SA 2.1 Japan. Commercial use is permitted under its terms.
Preserve attribution, licence and change notices; distribute adaptations under the same licence.
Do not impose incompatible legal/technical restrictions on this geometry. No endorsement by DBCLS is implied.
Educational visualisation only; exact joint surfaces/gaps, cartilage, pin locations and clinical accuracy are unaccepted.
Source intersections are not physiological contacts. No independent left scan is established. No warranties.
Учебная 3D-модель. Точная геометрия суставных поверхностей, границ и зазоров не подтверждена.
"""
licence += "\nFiles: " + "; ".join(r["id"] + ".glb (" + r["sourceId"] + ")" for r in files) + "\n"
licence += "Admission rule: " + decision["rule"] + "\n"
licence += "Batch limitations: " + decision["limitation"] + "\n"
write(target / "LICENSE-MODELS.txt", licence.encode("utf8"))
passport = dict(release="BodyParts3D 3.0 / 20110915 / OBJ 95%",
    author="The Database Center for Life Science (DBCLS)",
    archive="https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip",
    license="CC BY-SA 2.1 Japan", derivativeLicense="CC BY-SA 2.1 Japan",
    licenseURL="https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en",
    transform="[bp.x,bp.z,-bp.y]/1000; no reflection, fitting, mesh repair or decimation",
    evidence=run.as_posix(), files=files, productionInstalled=True, educationalAcceptance=True,
    fullAnatomicalAcceptance=False, report=decision["report"], admission=decision)
write(target / "provenance.json", (json.dumps(passport, ensure_ascii=False, indent=2) + "\n").encode("utf8"))
print(json.dumps(dict(published=decision["admitted"], triangles=sum(r["triangles"] for r in files))))
