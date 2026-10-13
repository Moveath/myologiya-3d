"""Inspect the full source ROI between facial segmentation ends and the IAC.

These diagnostic views are not anatomical segmentations or exported geometry.
"""
import json
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion
from temporal_channels_probe import OUT,CACHE,ras_vox,load_volume

def main():
    bone=np.load(CACHE/'bone-mask.npy',mmap_mode='r')
    points=ras_vox(trimesh.load(CACHE/'06_Facial Nerve.ply',process=False).vertices)
    lo=np.array([310,160,265]);hi=np.array([415,270,390])
    for kind in ['full','embedded']:
        volume=load_volume(kind)
        for axis in range(3):
            u,v=[a for a in range(3) if a!=axis][::-1]
            w,h=(hi-lo)[[u,v]];scale=3
            samples=np.arange(lo[axis],hi[axis],5);cols=5;rows=int(np.ceil(len(samples)/cols))
            sheet=Image.new('RGB',(cols*w*scale,rows*(h*scale+24)),(25,30,33));draw=ImageDraw.Draw(sheet)
            for panel,k in enumerate(samples):
                ix=[slice(a,b) for a,b in zip(lo,hi)];ix[axis]=k
                ct=volume[tuple(ix)];mask=bone[tuple(ix)]>0
                gray=(np.clip((ct.astype(float)+500)/3000,0,1)*255).astype('uint8');rgb=np.repeat(gray[:,:,None],3,axis=2)
                edge=mask&~binary_erosion(mask);rgb[edge]=[210,60,60]
                for q in points[np.abs(points[:,axis]-k)<.65]:
                    x,y=np.rint(q[[u,v]]-lo[[u,v]]).astype(int)
                    if 0<=x<w and 0<=y<h:rgb[y,x]=[40,240,220]
                im=Image.fromarray(rgb).resize((w*scale,h*scale),Image.Resampling.NEAREST)
                x=panel%cols*w*scale;y=panel//cols*(h*scale+24);sheet.paste(im,(x,y+24));draw.text((x+5,y+4),f'axis{axis}={k}; {kind}',fill='white')
            sheet.save(OUT/f'facial-endpoint-axis{axis}-{kind}.png')
    (OUT/'facial-endpoint-review-setup.json').write_text(json.dumps({'roi_native_zyx':[lo.tolist(),hi.tolist()],'index_planes':'Source grid axes, not declared anatomical planes','colors':{'red':'original Bone.nrrd mask boundary','cyan':'author facial nerve surface for context only'},'sampling':{'full_acquisition_mm':.25,'embedded_acquisition_mm':.125,'registered_grid_mm':.125}},indent=2)+'\n')

if __name__=='__main__':main()
