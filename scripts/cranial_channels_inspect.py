"""Source-mask ROI and diagnostic sections; no anatomical interpolation."""
from pathlib import Path
import argparse, gzip, hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build_head/cranial_channels';OUT.mkdir(parents=True,exist_ok=True)
SRC=ROOT/'research/cache/skull-microct/halle_skull_segmented.nrrd'
LO=np.array([.030,.030,.070]);HI=np.array([.115,.105,.185])
SP=.000125
def volume():
    path=OUT/'base-mask.npy'
    ilo=np.rint(LO[[0,2,1]]/SP).astype(int);ihi=np.rint(HI[[0,2,1]]/SP).astype(int)
    shape=tuple(map(int,(ihi-ilo)[[2,1,0]]))
    if not path.exists():
        assert hashlib.md5(SRC.read_bytes()).hexdigest()=='7ae22945a353069bdb695b63fa2f20bd'
        tmp=OUT/'base-mask.partial.npy'
        mask=np.lib.format.open_memmap(tmp,mode='w+',dtype=np.uint8,shape=shape)
        with SRC.open('rb') as f:
            while f.readline().strip(): pass
            stream=gzip.GzipFile(fileobj=f)
            for k in range(ihi[2]):
                data=stream.read(1150*1700*2)
                assert len(data)==1150*1700*2
                if k>=ilo[2]:
                    arr=np.frombuffer(data,dtype='<i2').reshape(1700,1150)
                    mask[k-ilo[2]]=arr[ilo[1]:ihi[1],ilo[0]:ihi[0]]
                if k%200==0:print('slice',k,flush=True)
        mask.flush();del mask;tmp.replace(path)
        (OUT/'base-mask-provenance.json').write_text(json.dumps({'source':str(SRC.relative_to(ROOT)),'sourceMD5':'7ae22945a353069bdb695b63fa2f20bd','spacing_mm':.125,'arrayAxes':'y,z,x = source k,j,i','bounds_m':[LO.tolist(),HI.tolist()],'processing':'Crop at original binary-mask resolution only.'},indent=2))
    return np.load(path,mmap_mode='r')
def sections(axis,values,bounds,name,ct=False):
    if ct:
        path=OUT/'base-ct.npy'
        if not path.exists():path=OUT/'base-ct.partial.npy'
        mask=np.load(path,mmap_mode='r')
    else:mask=volume()
    lo=np.array(bounds[:3])*.001;hi=np.array(bounds[3:])*.001
    start=np.rint((lo-LO)/SP).astype(int);end=np.rint((hi-LO)/SP).astype(int)
    index={'x':2,'y':0,'z':1}[axis];physical={'x':0,'y':1,'z':2}[axis]
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    cell=420;cols=min(4,len(values));rows=(len(values)+cols-1)//cols
    image=Image.new('RGB',(cols*cell,rows*(cell+40)),(30,30,30));d=ImageDraw.Draw(image)
    for n,val in enumerate(values):
        sl=[slice(start[1],end[1]),slice(start[2],end[2]),slice(start[0],end[0])]
        sl[index]=int(round((val*.001-LO[physical])/SP));data=np.array(mask[tuple(sl)])
        # Vertical image increases source coordinate; all axes are explicitly labelled.
        pixels=np.clip((data.astype(float)+500)/2300*255,0,255).astype('uint8') if ct else data*255
        im=Image.fromarray(pixels).convert('RGB');scale=min(cell/im.width,cell/im.height);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
        xx=n%cols*cell;yy=n//cols*(cell+40)
        image.paste(im,(xx,yy+40));d.text((xx+5,yy+5),f'{axis}={val:g} mm',font=font,fill='white')
        haxis='z' if axis=='x' else 'x';vaxis='y' if axis!='y' else 'z'
        d.text((xx+5,yy+cell+16),f'right +{haxis}, down +{vaxis}',font=font,fill='#00dddd')
    image.save(OUT/(name+'.png'))
    (OUT/(name+'.json')).write_text(json.dumps({'axis':axis,'values_mm':values,'bounds_mm':bounds,'imageRowsPositiveSourceAxis':True,'data':'Original int16 CT; display window -500..1800 native units, no spatial interpolation.' if ct else 'Original binary segmentation'},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--axis',default='y');p.add_argument('--values',nargs='+',type=float,default=[40,45,50,55,60,65,70,75]);p.add_argument('--bounds',nargs=6,type=float,default=[30,30,70,115,105,185]);p.add_argument('--name',default='base-horizontal');p.add_argument('--ct',action='store_true');a=p.parse_args();sections(a.axis,a.values,a.bounds,a.name,a.ct)
