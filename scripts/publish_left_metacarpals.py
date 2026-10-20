"""Publish byte-identical pilot GLBs and their licence; never overwrite model files."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "build_stage6/left_metacarpals_v1"
TARGET = ROOT / "site/models/bodyparts3d-3.0/left-metacarpals"
TARGET.mkdir(parents=True, exist_ok=True)
passport = json.loads((SOURCE / "provenance.json").read_text(encoding="utf8"))


def write_new_or_identical(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"Refusing to replace existing asset: {path}")
    else:
        with path.open("xb") as stream:
            stream.write(data)


trial_files = passport["files"]
passport["files"] = [r for r in trial_files if r["id"] in {"metacarpal_2_left", "metacarpal_4_left", "metacarpal_5_left"}]
assert len(passport["files"]) == 3
for row in passport["files"]:
    data = (ROOT / row["derivative"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == row["derivativeSHA256"], row["id"]
    write_new_or_identical(TARGET / (row["id"] + ".glb"), data)

licence = """BodyParts3D, Copyright© The Database Center for Life Science licensed by CC Attribution-Share Alike 2.1 Japan.
Title/release: BodyParts3D 3.0 / 20110915 / OBJ 95%.
Files: metacarpal_2_left.glb (FMA24467); metacarpal_4_left.glb (FMA24471); metacarpal_5_left.glb (FMA24473).
Source: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip
Release terms: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/README_e.html
Licence: https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en
Legal code: https://creativecommons.org/licenses/by-sa/2.1/jp/legalcode.ja
Changes: OBJ to GLB in Blender 5.2.2; coordinates [bp.x,bp.z,-bp.y]/1000 (mm to metres, Z-up to Y-up). No additional decimation, reflection, mesh repair or fitted registration. The source archive was already reduced by its author.
These derivative geometry files remain CC BY-SA 2.1 Japan. Commercial use is permitted under its terms. Preserve attribution, licence and change notices; distribute adaptations under the same licence. Do not impose incompatible legal/technical restrictions on this geometry. No endorsement by DBCLS is implied.
Educational visualisation only. Exact joint surfaces and gaps, pin locations and clinical accuracy are not accepted. Source-mesh intersections are documented for metacarpal II/trapezium and metacarpal IV/V. Nine previous carpal pairs remain unresolved. Metacarpals I and III are not included in the production atlas because their base alignment needs separate acceptance; these are not physiological contacts. No warranties are given.
Учебная 3D-модель. Точная геометрия суставных поверхностей и зазоров не подтверждена.
"""
write_new_or_identical(TARGET / "LICENSE-MODELS.txt", licence.encode("utf8"))
published = dict(passport,
    acceptedScope="educational visualisation with explicit limitations; full anatomical acceptance remains open",
    educationalAcceptance=True, fullAnatomicalAcceptance=False, productionInstalled=True,
    report="research/stage6-left-metacarpals-report-2026-10-20.md",
    publishedFiles=[dict(id=r["id"], file=r["id"]+".glb", sha256=r["derivativeSHA256"])
                    for r in passport["files"]])
write_new_or_identical(TARGET / "provenance.json",
    (json.dumps(published, ensure_ascii=False, indent=2)+"\n").encode("utf8"))
print(json.dumps(dict(published=[r["id"] for r in passport["files"]],
                      originalModelsUnmodified=True, exportRepeated=False)))
