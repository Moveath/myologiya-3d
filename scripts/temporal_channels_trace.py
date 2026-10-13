"""Diagnostic candidate path from the short facial branch toward the IAC.

No candidate produced here is an anatomical label or exported model. The path
must be inspected in both density volumes and against source bone walls.
"""
import json
import numpy as np
from scipy.ndimage import distance_transform_edt,map_coordinates,binary_erosion
from skimage.graph import MCP_Geometric
from PIL import Image,ImageDraw
from temporal_channels_probe import OUT,CACHE,load_volume
from temporal_channels_oblique import plane

def main():
    lo=np.array([306,188,284]);hi=np.array([398,261,365]);seed=np.array([325,205,347]);end=np.array([365,225,302])
    bone=np.load(CACHE/'bone-mask.npy',mmap_mode='r');ct=load_volume('embedded');mask=np.asarray(bone[tuple(slice(a,b) for a,b in zip(lo,hi))])>0
    distances=distance_transform_edt(~mask);cost=1+2/(distances+.5);cost[mask]=np.inf
    solver=MCP_Geometric(cost,fully_connected=True);solver.find_costs([tuple(seed-lo)],[tuple(end-lo)])
    path=np.array(solver.traceback(tuple(end-lo)))+lo
    records=[];radius=32;width=65;scale=3;samples=list(range(0,len(path),2));cols=6;rows=int(np.ceil(len(samples)/cols));sheet=Image.new('RGB',(cols*width*scale,rows*(width*scale+24)),(25,30,33));d=ImageDraw.Draw(sheet)
    for panel,i in enumerate(samples):
        coords,u,v=plane(path.astype(float),i,radius);m=map_coordinates(bone,coords,order=0)>0;raw=map_coordinates(ct,coords,order=1)
        gray=(np.clip((raw.astype(float)+500)/3000,0,1)*255).astype('uint8');rgb=np.repeat(gray[:,:,None],3,axis=2);rgb[m&~binary_erosion(m)]=[210,60,60];rgb[radius,radius]=[20,240,100]
        im=Image.fromarray(rgb).resize((width*scale,width*scale),Image.Resampling.NEAREST);x=panel%cols*width*scale;y=panel//cols*(width*scale+24);sheet.paste(im,(x,y+24));d.text((x+5,y+4),f'candidate {i}; embedded .125',fill='white')
        records.append({'index':i,'native_zyx':path[i].tolist(),'distance_to_bone_mm':float(distances[tuple(path[i]-lo)]*.125)})
    sheet.save(OUT/'facial-proximal-candidate.png');np.save(OUT/'facial-proximal-candidate.npy',path)
    (OUT/'facial-proximal-candidate.json').write_text(json.dumps({'review_only':True,'bone_void_path_not_anatomical_proof':True,'points':records},indent=2)+'\n')
    print('Candidate path',len(path),'samples, distance',np.linalg.norm(np.diff(path,axis=0),axis=1).sum()*.125,'mm')

if __name__=='__main__':main()
