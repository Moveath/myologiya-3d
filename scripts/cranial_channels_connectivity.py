"""Inspect a visually identified air corridor against both native mask and CT.

The straight line is a measurement probe, never a synthetic canal surface.
Oblique mask sections use nearest-voxel sampling and are diagnostic only.
"""
from cranial_channels_inspect import volume,LO,SP,OUT
from scipy.ndimage import map_coordinates,label,distance_transform_edt
import numpy as np,json
from PIL import Image,ImageDraw,ImageFont
mask=volume();ct=np.load(OUT/'base-ct.npy',mmap_mode='r')
a=np.array([61.,40.,101.]);b=np.array([49.,40.,108.]);d=(b-a)/np.linalg.norm(b-a)
up=np.array([0.,1.,0.]);right=np.cross(up,d)
steps=np.arange(0,np.linalg.norm(b-a)+.0001,.125)
rows=[];sections=[]
uv=np.arange(-7,7.001,.125);uu,vv=np.meshgrid(uv,uv)
for n,t in enumerate(steps):
 center=a+d*t
 xyz=center[None,None,:]+uu[:,:,None]*right+vv[:,:,None]*up
 ijk=((xyz*.001-LO)/SP).transpose(2,0,1)[[1,2,0]]
 plane=map_coordinates(mask,ijk,order=0,mode='nearest',prefilter=False)
 raw=map_coordinates(ct,ijk,order=0,mode='nearest',prefilter=False)
 labels,count=label(plane==0);v=labels[56,56]
 selected=labels==v if v else np.zeros_like(plane,dtype=bool)
 closed=v!=0 and not(any(selected[0]) or any(selected[-1]) or any(selected[:,0]) or any(selected[:,-1]))
 rows.append({'distanceFromProbeStart_mm':round(float(t),3),'point_mm':center.tolist(),'maskAtPoint':int(plane[56,56]),'ctAtPoint':int(raw[56,56]),'sectionAirComponentEnclosed':bool(closed),'enclosedSectionArea_mm2':float(selected.sum()*.125**2) if closed else None})
 if n%12==0:
  pixels=np.clip((raw.astype(float)+500)/2300*255,0,255).astype('uint8');rgb=np.repeat(pixels[:,:,None],3,axis=2)
  if closed:rgb[selected,1]=np.maximum(rgb[selected,1],80)
  sections.append((t,center,closed,Image.fromarray(rgb).resize((300,300),Image.Resampling.NEAREST)))
assert all(r['maskAtPoint']==0 for r in rows),'Measurement line crosses source bone'
closed=[r for r in rows if r['sectionAirComponentEnclosed']]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);image=Image.new('RGB',(4*320,((len(sections)+3)//4)*350),'#222');draw=ImageDraw.Draw(image)
for n,(t,p,c,im) in enumerate(sections):
 x=n%4*320;y=n//4*350;image.paste(im,(x,y+35));draw.text((x+3,y+3),f's={t:.2f} mm; closed={c}',fill='white',font=font)
image.save(OUT/'candidate-oblique-ct.png')
report={'candidate':'Canalis nervi hypoglossi; independently identified above the anterior occipital condyle in wide foramen-magnum context','probeEndpoints_mm':[a.tolist(),b.tolist()],'probeExplanation':'Measurement probe in source air; no line/tube is exported as anatomy.','nativeMaskResolution_mm':.125,'CTWindow_nativeUnits':[-500,1800],'sourceCTExpectedMD5':'2b46ca394084ab84af20bc267114e75f','processing':'Nearest-voxel diagnostic oblique sections; original native bone mesh is independent and unchanged.','continuousMaskAirProbe':True,'probeCTRange':[min(r['ctAtPoint'] for r in rows),max(r['ctAtPoint'] for r in rows)],'closedSections':len(closed),'closedRange_mm':[closed[0]['distanceFromProbeStart_mm'],closed[-1]['distanceFromProbeStart_mm']] if closed else None,'sections':rows}
(OUT/'candidate-connectivity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Probe points',len(rows),'all air; closed sections',len(closed),'range',report['closedRange_mm'],'CT',report['probeCTRange'])
