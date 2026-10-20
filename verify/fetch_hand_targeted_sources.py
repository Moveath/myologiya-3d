"""Addressed public NCBI API retrieval; no metadata guessed from search snippets."""
import json, sys, time, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
out=Path(sys.argv[1]).resolve()
assert out.is_relative_to(Path(__file__).resolve().parents[1]/'research/evidence-runs')
queries=[('pmc','6535955'),('pubmed','18590848'),('pubmed','8515018,32760605')]
for db,identifier in queries:
    file=out/f'ncbi-{db}-{identifier}.xml'
    if file.exists(): raw=file.read_bytes()
    else:
        url=f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db={db}&id={identifier}&retmode=xml&tool=myologia_source_review'
        with urllib.request.urlopen(url,timeout=45) as response: raw=response.read()
        ET.fromstring(raw)
        with file.open('xb') as f:f.write(raw)
        time.sleep(.45)
    tree=ET.fromstring(raw)
    chosen=tree.findall('.//body//p') if db=='pmc' else tree.findall('.//AbstractText')
    rows=[' '.join(''.join(p.itertext()).split()) for p in chosen]
    relevant=[p for p in rows if db!='pmc' or any(w in p.lower() for w in ['insertion','middle phalan','limitations'])]
    print(json.dumps(dict(db=db,id=identifier,paragraphs=relevant),ensure_ascii=False))
