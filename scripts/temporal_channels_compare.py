"""Compare both original CBCT acquisitions over the entire remaining course."""
import argparse,json
import numpy as np
from scipy.ndimage import map_coordinates,binary_erosion
from PIL import Image,ImageDraw,ImageFont
from temporal_channels_probe import OUT,CACHE,load_volume

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--part',default='facial',choices=['facial','carotid']);parser.add_argument('--first',type=int,default=145);parser.add_argument('--last',type=int);parser.add_argument('--step',type=int,default=3);args=parser.parse_args()
    full=load_volume();embedded=load_volume('embedded');bone=np.load(CACHE/'bone-mask.npy',mmap_mode='r')
    records=json.loads((OUT/f'{args.part}-oblique.json').read_text())['records'];last=args.last or len(records)-1
    radius=32 if args.part=='facial' else 48;w=radius*2+1;scale=2;tw=w*scale*3+8;th=w*scale+24;cols=3;samples=list(range(args.first,last+1,args.step));rows=int(np.ceil(len(samples)/cols));sheet=Image.new('RGB',(cols*tw,rows*th),'#1d2524');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
    for panel,i in enumerate(samples):
        r=records[i];p=np.array(r['guide_native_zyx']);u=np.array(r['plane_u']);v=np.array(r['plane_v']);a,b=np.meshgrid(np.arange(-radius,radius+1),np.arange(-radius,radius+1));coords=p[:,None,None]+u[:,None,None]*a+v[:,None,None]*b
        mask=map_coordinates(bone,coords,order=0,mode='constant',cval=0)>0;edge=mask&~binary_erosion(mask)
        f=map_coordinates(full,coords,order=1,mode='constant',cval=-3024);e=map_coordinates(embedded,coords,order=1,mode='constant',cval=-3024)
        rgbs=[]
        for ct in [f,e,e]:
            gray=(np.clip((ct.astype(float)+500)/3000,0,1)*255).astype('uint8');rgbs.append(np.repeat(gray[:,:,None],3,axis=2))
        rgbs[-1][edge]=[230,70,70]
        x=panel%cols*tw;y=panel//cols*th
        for col,rgb in enumerate(rgbs):sheet.paste(Image.fromarray(rgb).resize((w*scale,w*scale),Image.Resampling.NEAREST),(x+col*(w*scale+2),y+24))
        d.text((x+4,y+4),f'{args.part} {i}: full .25 | embedded .125 | mask',font=font,fill='white')
    path=OUT/f'{args.part}-compare-{args.first}-{last}.png';sheet.save(path);print(path)

if __name__=='__main__':main()
