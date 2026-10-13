"""Build full-source selectable supplements for former context-only bones.

Existing arm/leg/neck/thorax assets and all landmark coordinates stay untouched.
Run with the project's Python (numpy/trimesh) and local Node/gltfpack installed.
"""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build_context_bones'
SOURCES={
    'arm':{'clavicle_left':'FMA13323','scapula_left':'FMA13396','humerus_left':'FMA23131'},
    'leg':{**{f'lumbar_{i}':f'FMA{13071+i}' for i in range(1,6)},'hip_bone_left':'FMA16587'},
}
NAMES=dict(line.rstrip('\n').split('\t') for line in (ROOT/'bp/all_named.tsv').open(encoding='utf8'))
LICENSE='https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en'
MIRROR='https://github.com/Kevin-Mattheus-Moerman/BodyParts3D'

def source_path(fid):
    for directory in ('stl_thorax','stl_leg','stl_neck','stl_dl'):
        path=ROOT/directory/(fid+'.stl')
        if path.exists(): return path
    raise FileNotFoundError(fid)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def mesh_for(fid):
    mesh=trimesh.load(source_path(fid),process=True)
    count=len(mesh.faces)
    mesh.vertices=mesh.vertices[:,[0,2,1]]*np.array([1,1,-1])/1000
    assert len(mesh.faces)==count
    _=mesh.vertex_normals
    return mesh

def save_scene(scene,path):
    scene.export(path,file_type='glb',include_normals=True)

def main():
    OUT.mkdir(exist_ok=True)
    inspection=trimesh.Scene()
    report=dict(source='BodyParts3D 3.0 / 20110915, The Database Center for Life Science (DBCLS)',
                sourceMirror=MIRROR,license='CC BY-SA 2.1 Japan',licenseUrl=LICENSE,
                transformation='Original source millimetres [x,y,z] to metres [x,z,-y]/1000. No registration, reflection or generated boundaries.',
                processing='No decimation: all original source STL triangles retained before meshopt compression and quantization. Equivalent BONE_RATIO=1.0 with no triangle cap.',
                geometryCompleteClaim=False,newLandmarks=False,bones={},assets={})
    for section,bones in SOURCES.items():
        scene=trimesh.Scene()
        for bone,fid in bones.items():
            mesh=mesh_for(fid)
            name='b|'+bone
            scene.add_geometry(mesh,node_name=name,geom_name=name)
            inspection.add_geometry(mesh.copy(),node_name=name,geom_name=name)
            source=source_path(fid)
            report['bones'][bone]=dict(ownerSection=section,sourceFid=fid,sourceName=NAMES[fid],
                sourceFile=source.relative_to(ROOT).as_posix(),sourceSha256=sha(source),
                sourceUrl=f'https://raw.githubusercontent.com/Kevin-Mattheus-Moerman/BodyParts3D/main/assets/BodyParts3D_data/stl/{fid}.stl',
                sourceTriangles=len(mesh.faces),builtTriangles=len(mesh.faces),decimation=False,
                boundsMetres=mesh.bounds.tolist())
        high=OUT/f'{section}_extra_hi.glb'
        save_scene(scene,high)
        for suffix,flags in [('', ['-cc']),('_q',[])]:
            packed=OUT/f'{section}_extra{suffix}.glb'
            subprocess.run(['node',str(ROOT/'tools/node_modules/gltfpack/cli.js'),'-i',str(high),'-o',str(packed),*flags,'-kn','-km'],check=True,cwd=ROOT)
            destination=ROOT/'site'/f'{section}-extra{("-q" if suffix else "")}-glb.txt'
            destination.write_text(base64.b64encode(packed.read_bytes()).decode('ascii'),encoding='ascii')
            report['assets'][destination.name]=dict(sha256=sha(destination),bytes=destination.stat().st_size,
                glbSha256=sha(packed),sourceGlbSha256=sha(high),bones=list(bones))
    sacrum=mesh_for('FMA16202')
    inspection.add_geometry(sacrum,node_name='b|sacrum_audit',geom_name='b|sacrum_audit')
    save_scene(inspection,OUT/'inspection.glb')
    report['sacrumSourceAudit']=dict(fid='FMA16202',sourceName=NAMES['FMA16202'],
        sourceFile=source_path('FMA16202').relative_to(ROOT).as_posix(),sourceSha256=sha(source_path('FMA16202')),
        sourceTriangles=len(sacrum.faces),connectedComponents=len(sacrum.split(only_watertight=False)),
        separateCoccyxNamedInSourceCatalog=any(name.lower()=='coccyx' for name in NAMES.values()),
        separateCoccyxGeometryCreated=False,
        note='FMA16202 is named sacrum in the source catalog. Component count is not an anatomical segmentation. See the separate visual review before making any claim about coccygeal coverage.')
    review=ROOT/'research/context-coccyx-visual-review.json'
    if review.exists(): report['sacrumSourceAudit']['visualReview']=json.loads(review.read_text(encoding='utf8'))
    (ROOT/'research/context-bone-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    license_text=(
        'Дополнительные модели прежних контекстных костей (arm-extra, leg-extra)\n\n'
        'BodyParts3D, (c) The Database Center for Life Science licensed under CC Attribution-Share Alike 2.1 Japan.\n'
        'Модели и производные GLB: Creative Commons Attribution-ShareAlike 2.1 Japan.\n'+LICENSE+'\n'
        'Исходные STL BodyParts3D 3.0 / 20110915: '+MIRROR+'\n'
        'Mitsuhashi N et al. BodyParts3D: 3D structure database for anatomical concepts. Nucleic Acids Res. 2009;37:D782-5. https://doi.org/10.1093/nar/gkn613\n\n'
        'Обработка для атласа: преобразование единиц и осей координат, имена объектов, GLB и сжатие/квантование meshopt. Децимации костей, зеркального копирования и дорисованных образований нет.\n'
        'Производные модели распространяются на тех же условиях CC BY-SA 2.1 Japan.\n'
        'Состав, исходные FMA ID, контрольные суммы и границы проверки: research/context-bone-provenance.json в репозитории проекта.\n')
    (ROOT/'site/LICENSE-CONTEXT-BONES.txt').write_text(license_text,encoding='utf8')
    print('Context supplements:',len(report['bones']),'bones;',sum(r['sourceTriangles'] for r in report['bones'].values()),'source triangles; no decimation')

if __name__=='__main__': main()
