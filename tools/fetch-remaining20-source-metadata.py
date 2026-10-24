"""Bounded public metadata only; no model imports or license assumptions."""
from pathlib import Path
import hashlib
import json
import sys
import urllib.request
import urllib.parse

run = Path(sys.argv[1]).resolve()
sources = {
    "osf-node": "https://api.osf.io/v2/nodes/avq7d/",
    "osf-files": "https://api.osf.io/v2/nodes/avq7d/files/osfstorage/",
    "osf-material-labels": "https://osf.io/download/6a26dc00646ef5083d6d827c/",
    "zenodo-hand-rights": "https://zenodo.org/records/20206461/files/edm.xml?download=1",
    "bp4-is-a": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_parts_list_e.txt",
    "bp4-part-of": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/partof_parts_list_e.txt",
    "bp-download-page": "https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html",
    "bp4-elements": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_element_parts.txt",
    "bp4-readme": "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/README_e.html",
    "hegde-commit": "https://api.github.com/repos/HegdeUSA/Hand_template/commits/main",
    "hegde-contents": "https://api.github.com/repos/HegdeUSA/Hand_template/contents/",
    "sesamoid-abstracts": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42563416,41649546,24424221,28718310,37370905&retmode=xml",
}
rows = []
for key, url in sources.items():
    marker = run / (key+"-retrieval.json")
    if marker.exists():
        rows.append(json.loads(marker.read_text(encoding="utf8")))
        continue
    row = dict(id=key, url=url)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Myology3D-anatomical-source-review"})
        with urllib.request.urlopen(req, timeout=20) as response:
            data = response.read(2_000_001)
            assert len(data) <= 2_000_000, "Metadata limit exceeded; model was not requested"
            final = urllib.parse.urlsplit(response.url)
            signed = 'X-Amz-' in final.query
            stable_url = urllib.parse.urlunsplit(final._replace(query='')) if signed else response.url
            row.update(status="downloaded", finalURL=stable_url, signedRedirectQueryOmitted=signed, bytes=len(data),
                       sha256=hashlib.sha256(data).hexdigest())
        with (run/(key+".txt")).open("xb") as f:
            f.write(data)
    except Exception as e:
        row.update(status="unavailable", error=str(e))
    with marker.open("x", encoding="utf8") as f:
        json.dump(row, f, indent=2)
    rows.append(row)
    print(json.dumps(row), flush=True)
