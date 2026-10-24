"""Publish admitted derivatives only; originals and previous outputs are immutable."""
from pathlib import Path
import hashlib
import json
import sys

root = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1])
config = json.loads((run / "batch.json").read_text(encoding="utf8"))
decision = json.loads((run / "admission.json").read_text(encoding="utf8"))
exported = json.loads((run / "blender-export.json").read_text(encoding="utf8"))
target = root / config["publication"]
target.mkdir(parents=True, exist_ok=True)


def write(path, data):
    if path.exists():
        assert path.read_bytes() == data, f"Refusing to overwrite {path}"
    else:
        with path.open("xb") as f:
            f.write(data)


passport = dict(release="BodyParts3D 3.0 / 20110915 / OBJ 95%",
    author="The Database Center for Life Science (DBCLS)",
    archive="https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip",
    license="CC BY-SA 2.1 Japan", derivativeLicense="CC BY-SA 2.1 Japan",
    licenseURL="https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en",
    transform="[bp.x,bp.z,-bp.y]/1000; no reflection, fitting, mesh repair or decimation",
    evidence=run.relative_to(root).as_posix() if run.is_absolute() else run.as_posix(),
    files=exported["rows"], fullAnatomicalAcceptance=False, productionInstalled=False)
write(root / config["output"] / "provenance.json",
      (json.dumps(passport, ensure_ascii=False, indent=2)+"\n").encode("utf8"))
rows = [r for r in exported["rows"] if r["id"] in decision["admitted"]]
assert len(rows) == len(decision["admitted"])
for row in rows:
    data = (root / row["derivative"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == row["derivativeSHA256"]
    write(target / (row["id"] + ".glb"), data)
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
licence += "\nFiles: " + "; ".join(r["id"]+".glb ("+r["sourceId"]+")" for r in rows) + "\n"
licence += "Batch limitations: " + decision["limitation"] + "\n"
write(target / "LICENSE-MODELS.txt", licence.encode("utf8"))
published = dict(passport, files=rows, productionInstalled=True, educationalAcceptance=True,
                 report=decision["report"], admission=decision)
write(target / "provenance.json", (json.dumps(published, ensure_ascii=False, indent=2)+"\n").encode("utf8"))
print(json.dumps(dict(published=decision["admitted"], trialOnly=decision["trialOnly"])))
