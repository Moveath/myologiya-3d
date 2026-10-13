"""Package actual oblique CBCT sections with explicit native plane coordinates."""
import json,hashlib
import numpy as np
from scipy.ndimage import map_coordinates,binary_erosion,label
from PIL import Image,ImageDraw,ImageFont
from temporal_channels_probe import ROOT,OUT,CACHE,load_volume
from temporal_channels_build import CONFIG,viewer

def vec_view(v):return np.array([-v[2],v[0],v[1]])

def main():
    volume=load_volume();embedded=load_volume('embedded');bone=np.load(CACHE/'bone-mask.npy',mmap_mode='r')
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
    output={'source':'OpenEar ZETA: две зарегистрированные КТ; источник указан у каждого кадра',
            'sources':[{'id':'full','file':'CBCT_Unembedded.nrrd','label':'КТ полного препарата','acquisition_step_mm':.25,'sha256':hashlib.sha256((ROOT/'build_head/temporal_features/CBCT_Unembedded.nrrd').read_bytes()).hexdigest()},
                       {'id':'embedded','file':'CBCT_Embedded.nrrd','label':'КТ подготовленного препарата','acquisition_step_mm':.125,'sha256':hashlib.sha256((ROOT/'build_head/temporal_features/CBCT_Embedded.nrrd').read_bytes()).hexdigest()}],
            'license':'CC BY 4.0','attribution':'Daniel Manuel Sieber et al., OpenEar (2019), ZETA; doi:10.5281/zenodo.1473724',
            'source_acquisition_step_mm':None,'registered_grid_step_mm':.125,
            'type':'oblique_reslice','standard_anatomical_plane':False,'intensities_are_calibrated_HU':False,
            'window_raw_values':[-500,2500],'ct_interpolation':'linear','mask_interpolation':'nearest',
            'caption':'Косые срезы исходной КТ; вид съёмки и её исходный шаг указаны у каждого кадра. Слева — КТ; справа — тот же срез и граница исходной костной маски красным. Голубой цвет обозначает связную область просвета на замкнутом контуре маски. Это не модель нерва. Направления плоскости сохранены для каждого кадра.',
            'series':[]}
    for part,cfg in CONFIG.items():
        data=json.loads((OUT/f'{part}-oblique.json').read_text());first,last=cfg['interval'];records=data['records'];radius=32 if part=='facial' else 48
        w=2*radius+1;scale=2;tile_w=2*w*scale+8;tile_h=w*scale+24;cols=4;per_page=24;frames=[];pages=[]
        for start in range(first,last+1,per_page):
            samples=list(range(start,min(start+per_page,last+1)));rows=int(np.ceil(len(samples)/cols));sheet=Image.new('RGB',(tile_w*cols,tile_h*rows),'#1d2524');d=ImageDraw.Draw(sheet)
            filename=f'skull-channel-{part}-slices-{len(pages)+1}.png'
            for panel,i in enumerate(samples):
                row=records[i];p=np.array(row['guide_native_zyx']);u=np.array(row['plane_u']);v=np.array(row['plane_v']);a,b=np.meshgrid(np.arange(-radius,radius+1),np.arange(-radius,radius+1));coords=p[:,None,None]+u[:,None,None]*a+v[:,None,None]*b
                acquisition='embedded' if part=='facial' and i>=145 else 'full'
                acquired_step=.125 if acquisition=='embedded' else .25
                scan=embedded if acquisition=='embedded' else volume
                ct=map_coordinates(scan,coords,order=1,mode='constant',cval=-3024);mask=map_coordinates(bone,coords,order=0,mode='constant',cval=0)>0
                gray=(np.clip((ct.astype(float)+500)/3000,0,1)*255).astype('uint8');rgb=np.repeat(gray[:,:,None],3,axis=2);over=rgb.copy();edge=mask&~binary_erosion(mask);over[edge]=[230,70,70]
                labels,n=label(~mask,np.ones((3,3)));region=labels==labels[radius,radius] if not mask[radius,radius] else np.zeros_like(mask)
                closed=region.any() and not (region[0].any() or region[-1].any() or region[:,0].any() or region[:,-1].any())
                if closed:over[region]=((over[region].astype(float)+[20,150,220])/2).astype('uint8')
                x=panel%cols*tile_w;y=panel//cols*tile_h
                for col,array in enumerate([rgb,over]):sheet.paste(Image.fromarray(array).resize((w*scale,w*scale),Image.Resampling.NEAREST),(x+col*(w*scale+4),y+24))
                title=('Лицевой' if part=='facial' else 'Сонный')+f' канал · {i} · '+('КТ 0,125' if acquisition=='embedded' else 'КТ 0,25')
                d.text((x+4,y+4),title,font=font,fill='white')
                frames.append({'index':i,'image':filename,'rect':[x,y,tile_w,tile_h], 'rawRect':[x,y+24,w*scale,w*scale], 'overlayRect':[x+w*scale+4,y+24,w*scale,w*scale],
                               'source_id':acquisition,'source_file':'CBCT_Embedded.nrrd' if acquisition=='embedded' else 'CBCT_Unembedded.nrrd',
                               'source_label':'КТ подготовленного препарата' if acquisition=='embedded' else 'КТ полного препарата','source_acquisition_step_mm':acquired_step,'registered_grid_step_mm':.125,
                               'center_native_zyx':p.tolist(),'center_m':viewer(p[None,:])[0].tolist(),'u':vec_view(u).tolist(),'v':vec_view(v).tolist(),'normal':np.cross(vec_view(u),vec_view(v)).tolist(),'pixel_step_mm':.125,'display_scale':scale,'field_mm':w*.125,'closed_source_mask_contour':bool(closed)})
            sheet.save(OUT/filename);pages.append({'file':filename,'width':sheet.width,'height':sheet.height,'sha256':hashlib.sha256((OUT/filename).read_bytes()).hexdigest()})
        output['series'].append({'id':cfg['id'],'ru':'Лицевой канал: выбранные стенки' if part=='facial' else 'Сонный канал: выбранные стенки','kind':'oblique_reslice','pages':pages,'frames':frames,'selectedSlice':frames[len(frames)//2]['index'],'complete_channel':False})
    (OUT/'skull-temporal-channel-slices.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Prepared slice atlases',[(s['id'],len(s['frames']),len(s['pages'])) for s in output['series']])

if __name__=='__main__':main()
