"""Extract a scan-derived inspection ROI at the original 0.125 mm sampling.
No new holes, morphology, closing, interpolation, or anatomical segmentation.
The crop boundaries are artificial, never anatomical landmarks.
"""
from pathlib import Path
import argparse, gzip, json, hashlib
import numpy as np
from skimage.measure import marching_cubes
import trimesh
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build_head/cranial_features';OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'research/cache/skull-microct/halle_skull_segmented.nrrd'
parser=argparse.ArgumentParser()
parser.add_argument('--broad',action='store_true',help='Also recreate the large parent surface (14 million triangles).')
args=parser.parse_args()
assert hashlib.md5(SOURCE.read_bytes()).hexdigest()=='7ae22945a353069bdb695b63fa2f20bd'
# Three axes x=i, y=k, z=j, metres. Crop around ethmoid/sphenoid, selected
# from the independently viewed whole-specimen geometry, not TA marker guesses.
lo=np.array([.045,.045,.105]);hi=np.array([.110,.110,.190])
ijk_lo=np.floor(lo[[0,2,1]]/.000125).astype(int)
ijk_hi=np.ceil(hi[[0,2,1]]/.000125).astype(int)
a,b,c=ijk_lo;d,e,f=ijk_hi
shape=(f-c,e-b,d-a)
cache=OUT/'halle-roi-mask.npy'
if cache.exists():
 mask=np.load(cache,mmap_mode='r')
 assert mask.shape==shape and mask.dtype==np.uint8
else:
 mask=np.empty(shape,dtype=np.uint8)
 with SOURCE.open('rb') as file:
  while file.readline().strip():pass
  stream=gzip.GzipFile(fileobj=file)
  for k in range(f):
   raw=stream.read(1150*1700*2)
   assert len(raw)==1150*1700*2
   if k>=c:mask[k-c]=np.frombuffer(raw,dtype='<i2').reshape(1700,1150)[b:e,a:d]
   if k%100==0:print(k,flush=True)
 np.save(cache,mask)
surface_lo=lo if args.broad else np.array([.065,.065,.140])
surface_hi=hi if args.broad else np.array([.090,.100,.180])
start=np.rint((surface_lo-lo)[[1,2,0]]/.000125).astype(int)
end=np.rint((surface_hi-lo)[[1,2,0]]/.000125).astype(int)
ka,ja,ia=start;kb,jb,ib=end
v,faces,_,_=marching_cubes(np.array(mask[ka:kb,ja:jb,ia:ib]),level=.5,allow_degenerate=False)
v=v[:,[2,0,1]]*.000125+surface_lo
mesh=trimesh.Trimesh(vertices=v,faces=faces,process=False)
scene=trimesh.Scene();scene.add_geometry(mesh,node_name='b|specimen')
stem='halle-roi' if args.broad else 'halle-ethmoid-roi'
scene.export(OUT/(stem+'.glb'))
(OUT/(stem+'-provenance.json')).write_text(json.dumps({'source':'https://zenodo.org/records/6108435','md5':'7ae22945a353069bdb695b63fa2f20bd','license':'CC BY 4.0','sampling_mm':.125,'mask_bounds_m':[lo.tolist(),hi.tolist()],'surface_bounds_m':[surface_lo.tolist(),surface_hi.tolist()],'mask_index_bounds_ijk':[ijk_lo.tolist(),ijk_hi.tolist()],'faces':len(faces),'vertices':len(v),'processing':'Original binary mask; crop only; marching cubes 0.5; no filtering, simplification or morphology. Artificial rectangular crop borders are not anatomical boundaries.'},indent=2))
print(len(v),len(faces),flush=True)
