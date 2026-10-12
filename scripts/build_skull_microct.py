"""Build a browser surface from Kirchner's openly licensed Halle segmentation.

The independent specimen is never registered to BodyParts3D or its landmark
coordinates. Input voxels are binary, not individual bone labels. Memory is
bounded by streamed decompression and slabs during marching cubes.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import numpy as np
from skimage.measure import marching_cubes
import trimesh

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT/'research/cache/skull-microct'
parser = argparse.ArgumentParser()
parser.add_argument('--stride', type=int, default=2)
parser.add_argument('--ratio', type=float, default=.035)
parser.add_argument('--error', type=float, default=.001)
args = parser.parse_args()
assert args.stride in (1, 2, 3, 4)
source = CACHE/'halle_skull_segmented.nrrd'
record = json.loads((CACHE/'record.json').read_text(encoding='utf-8'))
entry = next(f for f in record['files'] if f['key'] == source.name)
assert 'md5:'+hashlib.md5(source.read_bytes()).hexdigest() == entry['checksum']
nx, ny, nz = 1150, 1700, 1400
step = args.stride
shape = tuple((n+step-1)//step for n in (nz, ny, nx))
mask_file = CACHE/f'segmentation-stride-{step}.u8'
if not mask_file.exists() or mask_file.stat().st_size != np.prod(shape):
    # Publish the cache only after every source slice was read successfully.
    # A cancelled decode must not look like a complete, reusable memmap.
    partial_mask = mask_file.with_suffix('.partial')
    mask = np.memmap(partial_mask, dtype='uint8', mode='w+', shape=shape)
    with source.open('rb') as f:
        header = []
        while line := f.readline().strip():
            header.append(line.decode('ascii'))
        assert 'type: short' in header and 'encoding: gzip' in header
        g = gzip.GzipFile(fileobj=f)
        for z in range(nz):
            raw = g.read(nx*ny*2)
            assert len(raw) == nx*ny*2, ('Truncated input', z)
            if z % step == 0:
                slab = np.frombuffer(raw, dtype='<i2').reshape(ny, nx)
                assert slab.min() >= 0 and slab.max() <= 1
                mask[z//step] = slab[::step, ::step]
            if z % 200 == 0:
                print('Decoded', z, '/', nz, flush=True)
    mask.flush()
    del mask
    partial_mask.replace(mask_file)
mask = np.memmap(mask_file, dtype='uint8', mode='r', shape=shape)
out = ROOT/'build_head/detail_microct'
out.mkdir(parents=True, exist_ok=True)
scene = trimesh.Scene()
raw_faces = 0
slab_depth = 40
for start in range(0, shape[0]-1, slab_depth):
    end = min(start+slab_depth+1, shape[0])
    slab = np.array(mask[start:end], dtype=np.uint8)
    if slab.max() == 0:
        continue
    v, f, _, _ = marching_cubes(slab, level=.5, allow_degenerate=False)
    v[:, 0] += start
    raw_faces += len(f)
    # Stored array axes k,j,i -> Three i,k,j. Anterior storage direction was
    # checked from the sagittal projection; the declared LPS header is wrong.
    v = v[:, [2, 0, 1]] * (.000125*step)
    part = trimesh.Trimesh(vertices=v, faces=f, process=False)
    del v, f
    # The axis permutation is even; marching-cubes winding is retained.
    # Do not infer a slab's outward winding from signed volume: slabs are open.
    raw_file = out/f'slab-{start}-raw.glb'
    reduced_file = out/f'slab-{start}.glb'
    part.export(raw_file)
    print('Surface slab', start, 'faces', len(part.faces), flush=True)
    del part, slab
    subprocess.run(['node',str(ROOT/'tools/node_modules/gltfpack/cli.js'),
        '-i',str(raw_file),'-o',str(reduced_file),'-si',str(args.ratio),
        '-se',str(args.error),'-slb','-noq'],check=True,
        stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    reduced = trimesh.load(reduced_file,force='scene')
    for i, node in enumerate(reduced.graph.nodes_geometry):
        matrix, name = reduced.graph[node]
        mesh = reduced.geometry[name].copy()
        mesh.apply_transform(matrix)
        scene.add_geometry(mesh,node_name=f'specimen|halle_skull_{start}_{i}')
    print('Reduced slab', start, 'faces',sum(len(m.faces) for m in reduced.geometry.values()),flush=True)
    del reduced
del mask
scene.export(out/'skull-microct-hi.glb')
target = ROOT/'site/skull-microct.glb'
subprocess.run(['node',str(ROOT/'tools/node_modules/gltfpack/cli.js'),
    '-i',str(out/'skull-microct-hi.glb'),'-o',str(target),'-cc','-kn','-ke','-vp','16'],
    check=True,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
nfaces = sum(len(m.faces) for m in scene.geometry.values())
nvertices = sum(len(m.vertices) for m in scene.geometry.values())
metadata = {
    'title':'Микро-КТ черепа, Halle',
    'source':'https://zenodo.org/records/6108435',
    'paper':'https://arxiv.org/abs/2202.11519',
    'author':'Thomas Kirchner, Martin-Luther-Universität Halle-Wittenberg',
    'license':'CC BY 4.0',
    'license_url':'https://creativecommons.org/licenses/by/4.0/',
    'geometry':{'file':target.name,'bytes':target.stat().st_size,
                'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},
    'source_md5':entry['checksum'],
    'original_voxel_mm':.125, 'surface_sampling_mm':.125*step,
    'original_surface_triangles':raw_faces,
    'browser_triangles':nfaces, 'browser_vertices':nvertices,
    'bounds_m':scene.bounds.tolist(),
    'orientation':{'array_to_three':'[i,j,k] -> [i,k,j], metres',
                   'header_discrepancy':'NRRD declares LPS; sagittal projection and independent TUBA processing identify +j as anterior (LAS).',
                   'reference':'https://github.com/pinton-lab/tuba/blob/main/src/tuba/species/human.py',
                   'laterality':'Not independently certified by matching the described parietal defect; lateral views intentionally unnamed.'},
    'processing':['Проверена контрольная сумма исходной сегментации.',
                  f'Выборка бинарной маски с шагом {.125*step} мм; marching cubes, уровень 0,5.',
                  'Упрощение meshoptimizer по блокам с заблокированными граничными вершинами; щели между блоками не создаются намеренно.',
                  f'Целевая доля треугольников {args.ratio}; предел ошибки алгоритма {args.error} от размера блока. Это не оценка анатомической точности.',
                  'Мелкие детали могут быть потеряны при выборке и упрощении.'],
    'limitations':['Отдельный препарат без нижней челюсти, не совмещён с BodyParts3D.',
                   'На препарате есть подготовительный распил и небольшое трепанационное отверстие, описанные автором.',
                   'Исходная маска не разделена на отдельные кости и не задаёт названия всех каналов.',
                   'Открытая плоскость среза в просмотрщике — сечение оболочки, а не изображение плотности КТ.']
}
(ROOT/'site/skull-microct.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'faces':nfaces,'vertices':nvertices,'bounds':scene.bounds.tolist()}),flush=True)
