"""Publish only independently checked, explicitly admitted derivative bytes."""
import hashlib
import json
from pathlib import Path
import sys
from mirrored_foot_stage6 import ADMITTED, BASE, NOTICE, PENDING, REPORT
from manifest_leg import BONES

root=Path(__file__).resolve().parents[1];run=Path(sys.argv[1])
config=json.loads((run/"batch.json").read_text(encoding="utf8"))
quality=json.loads((run/"trimesh-check.json").read_text())
exported=json.loads((run/"blender-export.json").read_text())
rows={r["id"]:r for r in exported["rows"]}
ui=[]
for width in (1280,390):
    for phase in ("setup","sides",*ADMITTED):
        revision="v2" if width==390 and phase in ("setup","toe_dist_3_left","toe_dist_4_left") else "v1"
        file=f"mcp-{revision}-{width}-{phase}-result.json"
        result=json.loads((run/file).read_text())
        assert result["status"]=="passed",file
        ui.append(file)
for bone in ADMITTED:
    assert next(r for r in quality["rows"] if r["id"]==bone)["technicalPass"],bone
    reviewed=run/(bone+"-self-reviewed.json")
    check=json.loads((reviewed if reviewed.exists() else run/(bone+"-self-intersections.json")).read_text())
    assert check["complete"] and not check["counts"]["crossing"] and not check["counts"]["coplanarOverlap"]
target=root/"site"/BASE;target.mkdir(parents=True,exist_ok=True)
def write(file,data):
    if file.exists():assert file.read_bytes()==data,file
    else:
        with file.open("xb") as f:f.write(data)
files=[]
for bone in ADMITTED:
    data=(root/config["output"]/(bone+".glb")).read_bytes()
    sha=hashlib.sha256(data).hexdigest();assert sha==rows[bone]["sha256"]
    write(target/(bone+".glb"),data)
    files.append(dict(id=bone,sourceBone=config["targets"][bone],
        sourceFMA=BONES[config["targets"][bone]],sha256=sha,triangles=rows[bone]["triangles"]))
passport=dict(source="BodyParts3D 3.0, The Database Center for Life Science (DBCLS)",
    sourceAsset=config["sourceAsset"],sourceAssetSHA256=config["sourceAssetSha256"],
    license="CC BY-SA 2.1 Japan",derivativeLicense="CC BY-SA 2.1 Japan",
    sourceURL="https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/README_e.html",
    transformation=config["transform"],plane=config["plane"],
    noOriginalOrPinChanges=True,independentLeftSpecimen=False,fullAnatomicalAcceptance=False,
    report=REPORT,evidence=run.relative_to(root).as_posix(),files=files)
write(target/"provenance.json",json.dumps(passport,ensure_ascii=False,indent=2).encode())
licence=("BodyParts3D, Copyright© The Database Center for Life Science licensed by CC Attribution-Share Alike 2.1 Japan.\n"
    "Source release: BodyParts3D 3.0 / 20110915. Existing atlas GLB derived from the right-side source; hashes/FMA in provenance.json.\n"
    "Release: https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/README_e.html\n"
    "Licence: https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en\n"
    "Legal code: https://creativecommons.org/licenses/by-sa/2.1/jp/legalcode.ja\n"
    "Changes: world-space X reflection about X=0, reversed triangle winding, recalculated normals, Blender GLB export. "
    "All source triangles retained. No fitting, deformation, decimation or pin transformation.\n"
    "These derivative geometry files remain CC BY-SA 2.1 Japan. Commercial use is permitted under its terms. "
    "Preserve attribution, licence and change notices; distribute adaptations under the same licence. "
    "Do not impose incompatible legal/technical restrictions. No endorsement by DBCLS is implied.\n"
    "Educational mirrored reconstruction, not an independently scanned left specimen. "
    "Exact specimen symmetry plane, joint surfaces/gaps, cartilage and pin locations are unaccepted. "
    "Known source intersections are defects, not physiological contacts. No warranties.\n"+NOTICE+"\n")
write(target/"LICENSE-MODELS.txt",licence.encode())
decision=dict(admitted=list(ADMITTED),trialOnly=list(PENDING),browserResults=ui,files=files,
    educationalAcceptance=True,fullAnatomicalAcceptance=False,noModelExpected=20)
with (run/"admission.json").open("x",encoding="utf8") as f:json.dump(decision,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(published=len(files),triangles=sum(x["triangles"] for x in files),browserPhases=len(ui))))
