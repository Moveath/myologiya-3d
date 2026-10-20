"""Fetch only three registration controls, never install them in the atlas."""
import hashlib
import json
import pathlib
import sys
import zipfile
import runpy

RemoteZip = runpy.run_path(str(pathlib.Path(__file__).with_name("inspect-stage6-sources.py")))["RemoteZip"]

run = pathlib.Path(sys.argv[1])
cache = pathlib.Path("research/cache/stage6-sources")
url = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip"
remote = RemoteZip(url)
rows = []
with zipfile.ZipFile(remote) as archive:
    for fma in ("FMA23131", "FMA24436", "FMA24438"):
        name, = [n for n in archive.namelist() if pathlib.PurePosixPath(n).name == fma + ".obj"]
        data = archive.read(name)
        target = cache / (fma + ".obj")
        if target.exists():
            assert target.read_bytes() == data
        else:
            target.write_bytes(data)
        rows.append(dict(id=fma, entry=name, sha256=hashlib.sha256(data).hexdigest(),
                         bytes=len(data), purpose="registration reference only; not installed"))
with (run / "registration-sources.json").open("x", encoding="utf8") as out:
    json.dump(dict(url=url, rows=rows, rangeBytes=remote.used), out, indent=2)
print(json.dumps(dict(controls=len(rows), rangeBytes=remote.used)))
