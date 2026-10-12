"""Extract a scan-derived inspection ROI at the original 0.125 mm sampling.
No new holes, morphology, closing, interpolation, or anatomical segmentation.
The crop boundaries are artificial, never anatomical landmarks.
"""
from pathlib import Path
import gzip, json, hashlib
import numpy as np
from skimage.measure import marching_cubes
import trimesh
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build_head/face_features';OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'research/cache/skull-microct/halle_skull_segmented.nrrd'
assert hashlib.md5(SOURCE.read_bytes()).hexdigest()=='7ae22945a353069bdb695b63fa2f20bd'
# Three axes x=i, y=k, z=j, metres. Crop around the palate/maxillary region, selected
# from the independently viewed whole-specimen geometry, not TA marker guesses.
lo=np.array([.028,.006,.135]);hi=np.array([.116,.059,.210])
ijk_lo=np.floor(lo[[0,2,1]]/.000125).astype(int)
ijk_hi=np.ceil(hi[[0,2,1]]/.000125).astype(int)
a,b,c=ijk_lo;d,e,f=ijk_hi
shape=(f-c,e-b,d-a)
mask=np.empty(shape,dtype=np.uint8)
with SOURCE.open('rb') as file:
 while file.readline().strip():pass
 stream=gzip.GzipFile(fileobj=file)
 for k in range(f):
  raw=stream.read(1150*1700*2)
  assert len(raw)==1150*1700*2
  if k>=c:mask[k-c]=np.frombuffer(raw,dtype='<i2').reshape(1700,1150)[b:e,a:d]
  if k%100==0:print(k,flush=True)
np.save(OUT/'halle-face-roi-mask.npy',mask)
v,faces,_,_=marching_cubes(mask,level=.5,allow_degenerate=False)
v+=np.array([c,b,a]);v=v[:,[2,0,1]]*.000125
mesh=trimesh.Trimesh(vertices=v,faces=faces,process=False)
scene=trimesh.Scene();scene.add_geometry(mesh,node_name='b|specimen')
scene.export(OUT/'halle-face-roi.glb')
(OUT/'halle-face-roi-provenance.json').write_text(json.dumps({'source':'https://zenodo.org/records/6108435','md5':'7ae22945a353069bdb695b63fa2f20bd','license':'CC BY 4.0','sampling_mm':.125,'bounds_m':[lo.tolist(),hi.tolist()],'index_bounds_ijk':[ijk_lo.tolist(),ijk_hi.tolist()],'faces':len(faces),'vertices':len(v),'processing':'Original binary mask; crop only; marching cubes 0.5; no filtering, simplification or morphology. Artificial rectangular crop borders are not anatomical boundaries.'},indent=2))
print(len(v),len(faces),flush=True)
