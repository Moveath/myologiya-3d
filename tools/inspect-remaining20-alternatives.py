"""Small, pinned research-only candidates; no exports or application changes."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import urllib.request
import zipfile
spec = importlib.util.spec_from_file_location('source_ranges', Path(__file__).with_name('inspect-stage6-sources.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
RemoteZip = module.RemoteZip

run = Path(sys.argv[1]).resolve()
def save(name, data):
    with (run/name).open('xb') as f:
        f.write(data)
    return dict(file=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

commit = json.loads((run/'hegde-commit.txt').read_text(encoding='utf8'))['sha']
records=[]
for name, limit in [('LICENSE',10000),('3D_model_of_segmented_bones.zip',10_000_000)]:
    target='hegde-'+name
    url=f'https://raw.githubusercontent.com/HegdeUSA/Hand_template/{commit}/{name}'
    if (run/target).exists():
        data=(run/target).read_bytes()
    else:
        with urllib.request.urlopen(url,timeout=30) as r:
            data=r.read(limit+1)
        assert len(data)<=limit
        save(target,data)
    record=dict(url=url,commit=commit,file=target,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    if name.endswith('.zip'):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            record['entries']=[dict(name=i.filename,bytes=i.file_size,crc=i.CRC) for i in z.infolist()]
            for i in z.infolist():
                if i.filename.lower().endswith('.stl') and not i.filename.startswith('__MACOSX/'):
                    assert i.file_size<150_000_000
                    stl=z.read(i.filename)
                    output='hegde-bones-'+Path(i.filename).name
                    if not (run/output).exists(): save(output,stl)
    records.append(record)
    print(json.dumps(dict(file=target,bytes=len(data))),flush=True)
if not (run/'hegde-candidate-files.json').exists():
    save('hegde-candidate-files.json',json.dumps(records,indent=2).encode())

html=(run/'bp-download-page.txt').read_text(encoding='utf8')
url=re.findall(r'href="([^"]*/isa_BP3D_4\.0_obj_99\.zip)"',html)[0]
archive=RemoteZip(url,budget=3_000_000)
with zipfile.ZipFile(archive) as z:
    records=[]
    elements=(run/'bp4-elements.txt').read_text(encoding='utf8').splitlines()
    for fma in ['FMA24465','FMA24469']:
        mapping=[x.split('\t') for x in elements if x.startswith(fma+'\t')]
        assert len(mapping)==1
        name=mapping[0][2]
        entry=[n for n in z.namelist() if Path(n).name==name+'.obj']
        assert len(entry)==1,(name,entry)
        data=z.read(entry[0]);record=save('bp4-'+name+'.obj',data)
        records.append(dict(**record,fma=fma,mapping=mapping[0],entry=entry[0],crc=z.getinfo(entry[0]).CRC))
    save('bp4-extraction.json',json.dumps(dict(url=url,archiveBytes=archive.size,
        rangeBytesRead=archive.used,files=records),indent=2).encode())
    print(json.dumps(dict(bp4Files=len(records),rangeBytesRead=archive.used)),flush=True)
