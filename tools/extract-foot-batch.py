"""Extract only selected official OBJ entries; never replace cached originals."""
import hashlib
import json
import pathlib
import sys
import zipfile
import zlib
from importlib.util import spec_from_file_location, module_from_spec

root = pathlib.Path(__file__).resolve().parents[1]
spec = spec_from_file_location("source_reader", root / "tools/inspect-stage6-sources.py")
reader = module_from_spec(spec)
spec.loader.exec_module(reader)
run = pathlib.Path(sys.argv[1])
config = json.loads((run / "batch.json").read_text(encoding="utf8"))
old = root / "research/evidence-runs/stage6-source-recovery-2026-10-20T04-55-12-346Z-sIUkha"
index = json.loads((old / "official-archive-index.json").read_text())
entries = {pathlib.PurePosixPath(e["name"]).name: e for e in index["entries"]}
rows = []
source = None
archive = None
try:
    for fma in dict.fromkeys([*config["targets"].values(), *config["controls"].values()]):
        target = root / "research/cache/stage6-sources" / (fma + ".obj")
        entry = entries[target.name]
        cached = target.exists()
        if cached:
            data = target.read_bytes()
        else:
            if archive is None:
                source = reader.RemoteZip(index["url"])
                archive = zipfile.ZipFile(source)
            data = archive.read(entry["name"])
            assert len(data) == entry["bytes"] and zlib.crc32(data) == entry["crc"]
            with target.open("xb") as f:
                f.write(data)
        assert len(data) == entry["bytes"] and zlib.crc32(data) == entry["crc"], fma
        rows.append(dict(sourceId=fma, sha256=hashlib.sha256(data).hexdigest(),
                         bytes=len(data), crc=entry["crc"], cached=cached))
        # Each completed source survives an interrupted subsequent download.
        evidence = run / (fma + "-source.json")
        if evidence.exists():
            prior = json.loads(evidence.read_text(encoding="utf8"))
            assert all(prior[k] == rows[-1][k] for k in ("sourceId", "sha256", "bytes", "crc"))
            rows[-1] = prior
        else:
            with evidence.open("x", encoding="utf8") as f:
                json.dump(rows[-1], f, indent=2)
finally:
    if archive:
        archive.close()
with (run / "source-extraction.json").open("x", encoding="utf8") as f:
    json.dump(dict(url=index["url"], rows=rows, requestedBytes=source.used if source else 0,
                   license="CC BY-SA 2.1 Japan", release="3.0 / 20110915 / obj_95"), f, indent=2)
print(json.dumps(dict(verified=len(rows), downloaded=sum(not x["cached"] for x in rows))))
