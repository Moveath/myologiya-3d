"""Attach attribution to research derivatives as well as admitted site models."""
from pathlib import Path
import hashlib
import json
import sys
root=Path(__file__).resolve().parents[1]
license_text=(root/"site/models/bodyparts3d-3.0/mirrored-left-foot/LICENSE-MODELS.txt").read_text(encoding="utf8")
for arg in sys.argv[1:]:
    run=Path(arg).resolve();config=json.loads((run/"batch.json").read_text(encoding="utf8"))
    exports=json.loads((run/"blender-export.json").read_text())
    output=root/config["output"]
    for row in exports["rows"]:
        assert hashlib.sha256((output/(row["id"]+".glb")).read_bytes()).hexdigest()==row["sha256"]
    obj=dict(source="BodyParts3D 3.0 — DBCLS",license="CC BY-SA 2.1 Japan",
        sourceAsset=config["sourceAsset"],sourceAssetSHA256=config["sourceAssetSha256"],
        transform=config["transform"],files=exports["rows"],
        evidence=run.relative_to(root).as_posix(),status="research derivative; per-owner admission is separate",
        fullAnatomicalAcceptance=False)
    if config.get("sourceId"):obj["sourceFMA"]=config["sourceId"]
    for file,data in [(output/"provenance.json",json.dumps(obj,ensure_ascii=False,indent=2).encode()),
                      (output/"LICENSE-MODELS.txt",license_text.encode())]:
        if file.exists():assert file.read_bytes()==data
        else:
            with file.open("xb") as f:f.write(data)
    if config.get("sourceId"):
        # The shared licence also describes the normal packed-GLB workflow.
        # This exception was rebuilt directly from the documented original OBJ.
        file=output/"SOURCE-NOTICE.txt"
        data=(f"Exact source for this derivative: {config['sourceAsset']}\n"
              f"FMA: {config['sourceId']}; SHA256: {config['sourceAssetSha256']}\n"
              "This derivative uses the original OBJ directly, not the packed atlas GLB. "
              "The packed-GLB source sentence in the shared LICENSE-MODELS.txt does not apply "
              "to this file. Copyright, attribution, CC BY-SA 2.1 Japan and educational "
              "limitations remain unchanged. See provenance.json for the transformation.\n").encode()
        if file.exists():assert file.read_bytes()==data
        else:
            with file.open("xb") as f:f.write(data)
print("Trial derivative attribution preserved.")
