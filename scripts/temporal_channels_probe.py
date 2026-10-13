"""Inspect original OpenEar CBCT and bone mask around named author segments.

The author soft-tissue models only locate the inspection region. They are never
used as a substitute for a bony channel or as the output segmentation.
"""
from pathlib import Path
import argparse, gzip, json
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build_head/temporal_channels'
CACHE=ROOT/'research/cache/complete-temporal/zeta'
ORIGIN=np.array([19.806900024414063,7.7452301979064941,-1.7357300519943237])

def ras_vox(v):
    v=np.asarray(v)
    return np.stack([(v[:,2]-ORIGIN[2])/.125,(v[:,1]+ORIGIN[1])/.125,(v[:,0]+ORIGIN[0])/.125],axis=1)

def load_volume(kind='full'):
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/f'cbct-{kind}.npy'
    if not path.exists():
        raw=(ROOT/'build_head/temporal_features'/('CBCT_Unembedded.nrrd' if kind=='full' else 'CBCT_Embedded.nrrd')).read_bytes()
        stop=raw.index(b'\n\n')+2
        assert 'sizes: 668 587 625' in raw[:stop].decode()
        v=np.frombuffer(gzip.decompress(raw[stop:]),dtype='<i2').reshape((625,587,668))
        np.save(path,v)
    return np.load(path,mmap_mode='r')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--part',choices=['carotid','facial'],default='carotid');parser.add_argument('--axis',type=int,default=0);parser.add_argument('--kind',choices=['full','embedded'],default='full');args=parser.parse_args()
    volume=load_volume(args.kind);bone=np.load(CACHE/'bone-mask.npy',mmap_mode='r')
    filename='12_Carotis Interna.ply' if args.part=='carotid' else '06_Facial Nerve.ply'
    mesh=trimesh.load(CACHE/filename,process=False);vox=ras_vox(mesh.vertices)
    axis=args.axis;u,v=[a for a in range(3) if a!=axis][::-1]
    lo=np.floor(vox.min(axis=0)-40).astype(int);hi=np.ceil(vox.max(axis=0)+40).astype(int)
    w,h=(hi-lo)[[u,v]];scale=2
    samples=np.arange(int(vox[:,axis].min())-12,int(vox[:,axis].max())+13,8)
    cols=5;rows=int(np.ceil(len(samples)/cols))
    sheet=Image.new('RGB',(cols*w*scale,rows*(h*scale+25)),(25,30,33));d=ImageDraw.Draw(sheet)
    for panel,k in enumerate(samples):
        ix=[slice(lo[a],hi[a]) for a in range(3)];ix[axis]=k
        ct=volume[tuple(ix)];mask=bone[tuple(ix)]>0
        gray=(np.clip((ct.astype(float)+500)/3000,0,1)*255).astype('uint8')
        rgb=np.repeat(gray[:,:,None],3,axis=2)
        edge=mask&~binary_erosion(mask);rgb[edge]=[210,60,60]
        near=vox[np.abs(vox[:,axis]-k)<.65]
        for q in near:
            x,y=np.rint(q[[u,v]]-lo[[u,v]]).astype(int)
            if 0<=x<w and 0<=y<h:rgb[y,x]=[40,240,220]
        im=Image.fromarray(rgb).resize((w*scale,h*scale),Image.Resampling.NEAREST)
        x=(panel%cols)*w*scale;y=(panel//cols)*(h*scale+25)
        sheet.paste(im,(x,y+25));d.text((x+5,y+5),f'{args.part} axis {axis} = {k}; {args.kind}',fill='white')
    path=OUT/f'{args.part}-axis{axis}-{args.kind}.png';sheet.save(path)
    (OUT/f'{args.part}-probe.json').write_text(json.dumps({'filename':filename,'axis':axis,'vox_bounds':[lo.tolist(),hi.tolist()],'samples':samples.tolist(),'colors':{'red':'original bone mask boundary','cyan':'author soft tissue surface context only'}} ,indent=2))
    print(path)

if __name__=='__main__':main()
