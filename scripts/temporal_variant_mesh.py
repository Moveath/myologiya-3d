"""Halle surface extraction only; no smoothing, filling, or registration."""
from temporal_variant_inspect import ROOT,OUT,LO,SP
import argparse,json
import numpy as np
import trimesh
from skimage.measure import marching_cubes

p=argparse.ArgumentParser();p.add_argument('--bounds',nargs=6,type=float,required=True);p.add_argument('--name',required=True);p.add_argument('--context',action='store_true');a=p.parse_args()
lo=np.array(a.bounds[:3]);hi=np.array(a.bounds[3:])
if a.context:
    data=np.memmap(ROOT/'research/cache/skull-microct/segmentation-stride-2.u8',mode='r',dtype=np.uint8,shape=(700,850,575));origin=np.zeros(3);sp=.25
else:data=np.load(OUT/'mastoid-mask.npy',mmap_mode='r');origin=LO;sp=SP
i=np.rint((lo-origin)/sp).astype(int);j=np.rint((hi-origin)/sp).astype(int)
mask=np.array(data[i[1]:j[1],i[2]:j[2],i[0]:j[0]])
v,f,_,_=marching_cubes(mask,.5,allow_degenerate=False)
v=(v[:,[2,0,1]]*sp+lo)*.001;f=f[:,::-1]
mesh=trimesh.Trimesh(vertices=v,faces=f,process=False)
scene=trimesh.Scene();scene.add_geometry(mesh,node_name='b|specimen');scene.export(OUT/(a.name+'.glb'))
(OUT/(a.name+'.json')).write_text(json.dumps({'bounds_mm':a.bounds,'source_step_mm':.125,'surface_grid_step_mm':sp,'vertices':len(v),'triangles':len(f),'source':'Halle 6108435 binary mask','processing':'Level 0.5 marching cubes, winding corrected; no smoothing or caps; ROI edges artificial.'},indent=2),encoding='utf-8')
print(len(v),len(f),flush=True)
