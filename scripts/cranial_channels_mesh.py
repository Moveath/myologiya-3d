"""Extract the level-0.5 source-mask surface, without smoothing or simplification."""
from cranial_channels_inspect import volume,LO,SP,OUT,ROOT
import argparse,json
import numpy as np
import trimesh
from skimage.measure import marching_cubes
p=argparse.ArgumentParser();p.add_argument('--bounds',nargs=6,type=float,required=True);p.add_argument('--name',required=True);p.add_argument('--context',action='store_true',help='Use pre-existing 0.25-mm whole-mask sampling only for wider anatomical context.');a=p.parse_args()
lo=np.array(a.bounds[:3])*.001;hi=np.array(a.bounds[3:])*.001
spacing=.00025 if a.context else SP
origin=np.zeros(3) if a.context else LO
i=np.rint((lo-origin)/spacing).astype(int);j=np.rint((hi-origin)/spacing).astype(int)
data=np.memmap(ROOT/'research/cache/skull-microct/segmentation-stride-2.u8',mode='r',dtype=np.uint8,shape=(700,850,575)) if a.context else volume()
mask=np.array(data[i[1]:j[1],i[2]:j[2],i[0]:j[0]])
v,f,_,_=marching_cubes(mask,level=.5,allow_degenerate=False)
v=v[:,[2,0,1]]*spacing+lo
# skimage's default face winding points into the foreground for this mask.
# Reverse orientation only; preserve all vertex positions and triangles.
f=f[:,::-1]
mesh=trimesh.Trimesh(vertices=v,faces=f,process=False)
scene=trimesh.Scene();scene.add_geometry(mesh,node_name='b|specimen');scene.export(OUT/(a.name+'.glb'))
(OUT/(a.name+'.json')).write_text(json.dumps({'bounds_mm':a.bounds,'sourceSpacing_mm':.125,'surfaceSampling_mm':spacing*1000,'vertices':len(v),'faces':len(f),'sourceGeometry':'Original Halle binary segmentation, level 0.5 isosurface. No smoothing or simplification. ROI has artificial open crop boundaries.','contextOnly':a.context},indent=2));print(len(v),len(f))
