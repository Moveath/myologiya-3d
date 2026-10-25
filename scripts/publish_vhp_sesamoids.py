"""Publish the four MCP-I sesamoid candidates of scripts/vhp_thumb_sesamoids.py (educational only).

Checks each candidate against the evidence run hash, packs it losslessly (meshopt, no quantisation)
and writes provenance and the NLM terms notice. Refuses to overwrite different bytes.
Usage: python scripts/publish_vhp_sesamoids.py RUN
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from vhp_sesamoids_stage6 import BASE, BONES, REPORT

ROOT = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
OUT = ROOT / 'site' / BASE
OUT.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
placement = {r['bone']: r for side in json.loads((run / 'placement.json').read_text(encoding='utf8')).values() for r in side}
registration = json.loads((run / 'registration.json').read_text(encoding='utf8'))
headers = json.loads((run / 'headers.json').read_text(encoding='utf8'))


def write(path, data):
    if path.exists():
        assert path.read_bytes() == data, f'Refusing to overwrite {path}'
    else:
        with path.open('xb') as f:
            f.write(data)


files = []
for bone in BONES:
    row = placement[bone]
    candidate = ROOT / row['candidateFile']
    assert sha(candidate) == row['candidateSHA256'], bone
    packed = OUT / f'{bone}.glb'
    if not packed.exists():
        subprocess.run(['node', str(ROOT / 'tools/package-geometry-safe.mjs'), str(candidate), str(packed)], cwd=ROOT, check=True,
                       stdout=subprocess.DEVNULL)
    report = json.loads(Path(str(packed) + '.validation.json').read_text(encoding='utf8'))
    assert not report['errors'] and sum(m['faces'] for m in report['output']['meshes']) == row['triangles'], bone
    side = 'left' if bone.endswith('_left') else 'right'
    files.append(dict(id=bone, file=f'{BASE}/{bone}.glb', sha256=sha(packed), bytes=packed.stat().st_size,
                      candidateSHA256=row['candidateSHA256'], triangles=row['triangles'], ctNodule=row['nodule'],
                      extentsMM=row['extentsMM'], volumeMM3=row['volumeMM3'],
                      registration={k: registration[side][k] for k in ('target', 'medianMM', 'p95MM', 'scale', 'bestRoll')}))

licence = """Thumb MCP-I sesamoid models (4 files) — educational reconstruction.
Source data: Courtesy of the U.S. National Library of Medicine. Visible Human Project, Male,
radiological/frozenCT PNG slices 1700-1849 (https://www.nlm.nih.gov/research/visible/getting_data.html).
Use and redistribution follow the NLM Terms and Conditions
(https://www.nlm.nih.gov/databases/download/terms_and_conditions.html): acknowledge NLM with the phrase
above; NLM does not endorse this atlas; these files do not represent the most current or accurate data.
Changes: visual identification of the two nodules at each thumb MCP joint; seeded watershed segmentation;
cubic upsampling to half a CT voxel and marching-tetrahedra isosurface at the local half-maximum; Taubin smoothing; largest
shell kept; similarity registration of the CT I metacarpal to the BodyParts3D I metacarpal of the same side
(placement only — no BodyParts3D geometry is contained in these files); gltfpack meshopt without quantisation.
Educational visualisation only: articular facets, palmar plate, exact shape and clinical accuracy are unaccepted.
Учебная реконструкция по КТ другого тела; точная форма и фасетки не подтверждены.
""" + 'Files: ' + '; '.join(f"{f['id']}.glb (CT nodule {f['ctNodule']})" for f in files) + '\n'
write(OUT / 'LICENSE-MODELS.txt', licence.encode('utf8'))
passport = dict(dataset=headers['dataset'], url=headers['url'], terms=headers['terms'],
                attribution='Courtesy of the U.S. National Library of Medicine', slices=headers['slices'],
                pixelMM=headers['pixelMM'], sliceMM=headers['sliceMM'], evidence=run.relative_to(ROOT).as_posix(),
                report=REPORT, files=files, educationalAcceptance=True, fullAnatomicalAcceptance=False)
write(OUT / 'provenance.json', (json.dumps(passport, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps(dict(published=len(files), triangles=sum(f['triangles'] for f in files), kilobytes=round(sum(f['bytes'] for f in files) / 1024, 1))))
