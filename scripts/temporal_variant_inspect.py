"""Targeted read-only Halle CT review for the mastoid emissary passage.

Native CT and segmentation are never modified. Viewer axes are x=i,y=k,z=j;
laterality remains unassigned until anatomy independently supports it.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build_head/temporal_variants';OUT.mkdir(exist_ok=True,parents=True)
LO=np.array([0.,35.,30.]);SP=.125

def sections(axis,values,bounds,name,mask=False):
    source=OUT/('mastoid-mask.npy' if mask else 'mastoid-ct.npy')
    data=np.load(source,mmap_mode='r');lo=np.array(bounds[:3]);hi=np.array(bounds[3:])
    start=np.rint((lo-LO)/SP).astype(int);end=np.rint((hi-LO)/SP).astype(int)
    index={'x':2,'y':0,'z':1}[axis];physical={'x':0,'y':1,'z':2}[axis]
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    cell=550;cols=min(3,len(values));rows=(len(values)+cols-1)//cols
    image=Image.new('RGB',(cols*cell,rows*(cell+50)),(25,25,25));d=ImageDraw.Draw(image)
    frames=[]
    for n,val in enumerate(values):
        sl=[slice(start[1],end[1]),slice(start[2],end[2]),slice(start[0],end[0])]
        sl[index]=int(round((val-LO[physical])/SP));raw=np.array(data[tuple(sl)])
        pixels=raw*255 if mask else np.clip((raw.astype(float)+500)/2300*255,0,255).astype('uint8')
        im=Image.fromarray(pixels).convert('RGB');scale=min(cell/im.width,cell/im.height)
        im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
        xx=n%cols*cell;yy=n//cols*(cell+50);image.paste(im,(xx,yy+32))
        haxis='z' if axis=='x' else 'x';vaxis='y' if axis!='y' else 'z'
        d.text((xx+5,yy+4),f'{axis}={val:g} mm; right +{haxis}, down +{vaxis}',font=font,fill='white')
        # Coordinate grid is only an inspection aid, not anatomical labeling.
        horizontal=2 if axis=='x' else 0;vertical=1 if axis!='y' else 2
        for a in np.arange(np.ceil(lo[horizontal]/5)*5,hi[horizontal],5):
            px=xx+(a-lo[horizontal])/SP*scale;d.line((px,yy+32,px,yy+32+im.height),fill=(55,85,85),width=1)
            d.text((px+2,yy+36),str(int(a)),font=font,fill='#00cccc')
        for a in np.arange(np.ceil(lo[vertical]/5)*5,hi[vertical],5):
            py=yy+32+(a-lo[vertical])/SP*scale;d.line((xx,py,xx+im.width,py),fill=(55,85,85),width=1)
            d.text((xx+2,py+2),str(int(a)),font=font,fill='#00cccc')
        frames.append({'axis':axis,'value_mm':val,'imageRect':[xx,yy+32,im.width,im.height]})
    target=OUT/(name+'.png');image.save(target)
    meta={'source':'Halle, Zenodo 6108435','sourceFile':source.name,'original_ct_md5':'2b46ca394084ab84af20bc267114e75f',
          'source_step_mm':.125,'viewer_axes':'x=i,y=k,z=j; laterality not assigned','bounds_mm':bounds,'frames':frames,
          'display':'Original int16 CT, window -500..1800 native units; nearest pixel resize; no spatial interpolation' if not mask else 'Original binary segmentation',
          'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (OUT/(name+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--axis',default='y');p.add_argument('--values',nargs='+',type=float,required=True)
    p.add_argument('--bounds',nargs=6,type=float,default=[30,30,70,115,105,150]);p.add_argument('--name',required=True);p.add_argument('--mask',action='store_true')
    a=p.parse_args();sections(a.axis,a.values,a.bounds,a.name,a.mask)
