"""Publish native Halle bone around the reviewed hypoglossal canal and real CT.

No canal-shaped solid is constructed. The exported surface is the author's
binary bone segmentation, and every CT pixel comes from the original volume.
"""
from pathlib import Path
import hashlib, json, subprocess
import numpy as np
import trimesh
from scipy.ndimage import map_coordinates, binary_erosion, label
from PIL import Image
from cranial_channels_inspect import ROOT, OUT, LO, SP, volume

SITE=ROOT/'site'
ID='halle_hypoglossal'
SOURCE='https://zenodo.org/records/6108435'
CT_MD5='2b46ca394084ab84af20bc267114e75f'
MASK_MD5='7ae22945a353069bdb695b63fa2f20bd'
ATTR='Thomas Kirchner, Martin-Luther-Universität Halle-Wittenberg; Halle skull micro-CT, Zenodo 6108435 (2022).'
mask=volume()
ct=np.load(OUT/'base-ct.npy',mmap_mode='r')

def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(path,method='sha256'):
    h=hashlib.new(method)
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

checks=[]
for name,md5 in [('halle_skull.nrrd',CT_MD5),('halle_skull_segmented.nrrd',MASK_MD5)]:
    p=ROOT/'research/cache/skull-microct'/name
    actual=digest(p,'md5');assert actual==md5,(name,actual)
    checks.append({'file':name,'bytes':p.stat().st_size,'MD5':actual,'wholeFileVerified':True})
prov=json.loads((OUT/'base-ct-provenance.json').read_text('utf-8'))
prov.update(requiresWholeFileChecksumVerification=False,wholeFileMD5Verified=True,actualMD5=CT_MD5)
save(OUT/'base-ct-provenance.json',prov)

def normal_check(mesh,context=False):
    ix=np.linspace(0,len(mesh.faces)-1,min(20000,len(mesh.faces)),dtype=int)
    p=mesh.triangles_center[ix];n=mesh.face_normals[ix]
    if context:
        m=np.memmap(ROOT/'research/cache/skull-microct/segmentation-stride-2.u8',dtype=np.uint8,mode='r',shape=(700,850,575))
        origin=np.zeros(3);sp=.00025
    else:m=mask;origin=LO;sp=SP
    vals=[map_coordinates(m,((p+s*n*sp*.8-origin)/sp)[:,[1,2,0]].T,order=0,mode='nearest') for s in [-1,1]]
    outward=float(((vals[0]==1)&(vals[1]==0)).mean())
    inward=float(((vals[0]==0)&(vals[1]==1)).mean())
    return {'sampledTriangles':len(ix),'outwardMaskTransitionFraction':outward,'inwardMaskTransitionFraction':inward}

meshes=[]
for src,node,stem,context in [('channel-native.glb',ID,'skull-cranial-channels',False),('occipital-context.glb','halle_occipital_context','skull-cranial-channels-context',True)]:
    mesh=trimesh.load(OUT/src).to_geometry()
    before=normal_check(mesh,context)
    reverse=before['inwardMaskTransitionFraction']>before['outwardMaskTransitionFraction']
    if reverse:mesh=trimesh.Trimesh(vertices=mesh.vertices,faces=mesh.faces[:,::-1],process=False)
    after=normal_check(mesh,context)
    # Open ROI borders and thin trabeculae can yield same-label pairs; compare
    # the directed transitions rather than treating those samples as failures.
    assert after['outwardMaskTransitionFraction']>.8 and after['outwardMaskTransitionFraction']>20*after['inwardMaskTransitionFraction'],after
    mesh.visual=trimesh.visual.ColorVisuals(mesh,vertex_colors=[218,196,143,255])
    scene=trimesh.Scene();scene.add_geometry(mesh,node_name='channels|'+node,geom_name=node)
    raw=OUT/(stem+'-raw.glb');scene.export(raw)
    final=SITE/(stem+'.glb')
    subprocess.run(['node',str(ROOT/'tools/node_modules/gltfpack/cli.js'),'-i',str(raw),'-o',str(final),'-cc','-kn','-km','-noq'],check=True)
    meshes.append({'node':'channels|'+node,'file':final.name,'sha256':digest(final),'sourceROI':src,'vertices':len(mesh.vertices),'triangles':len(mesh.faces),'normalsReversed':reverse,'normalCheckBefore':before,'normalCheckAfter':after,'bounds_m':mesh.bounds.tolist(),'sampling_mm':.25 if context else .125,'decimated':False,'positionQuantization':False})

# Oblique diagnostic stack perpendicular to the visually reviewed real lumen.
# This line is a sampling probe, not an anatomical centerline or exported mesh.
a=np.array([61.,40.,101.]);b=np.array([49.,40.,108.]);d=(b-a)/np.linalg.norm(b-a)
up=np.array([0.,1.,0.]);right=np.cross(up,d)
uv=np.arange(-7,7.001,.125);uu,vv=np.meshgrid(uv,uv);side=len(uv)
steps=np.arange(0,np.linalg.norm(b-a)+.0001,.125)
frames=[];pages=[];measure=[];cols=4;rows=6;perpage=cols*rows
for page_index,start in enumerate(range(0,len(steps),perpage)):
    count=min(perpage,len(steps)-start)
    page=Image.new('RGB',(cols*side*2,((count+cols-1)//cols)*side))
    filename=f'skull-cranial-channel-slices-{page_index+1}.png'
    for offset,n in enumerate(range(start,start+count)):
        center=a+d*steps[n]
        xyz=center[None,None,:]+uu[:,:,None]*right+vv[:,:,None]*up
        ijk=((xyz*.001-LO)/SP).transpose(2,0,1)[[1,2,0]]
        plane=map_coordinates(mask,ijk,order=0,mode='nearest',prefilter=False)
        raw=map_coordinates(ct,ijk,order=0,mode='nearest',prefilter=False)
        pixels=np.clip((raw.astype(float)+500)/2300*255,0,255).astype(np.uint8)
        rawrgb=np.repeat(pixels[:,:,None],3,axis=2);overlay=rawrgb.copy()
        edge=(plane>0)&~binary_erosion(plane>0)
        overlay[edge]=[244,90,78]
        labels,_=label(plane==0);value=labels[side//2,side//2]
        component=labels==value if value else np.zeros_like(plane,dtype=bool)
        closed=bool(value and not(component[0].any() or component[-1].any() or component[:,0].any() or component[:,-1].any()))
        if closed:
            overlay[component]=(overlay[component].astype(float)*.55+np.array([55,178,218])*.45).astype(np.uint8)
        x=offset%cols*side*2;y=offset//cols*side
        page.paste(Image.fromarray(rawrgb),(x,y));page.paste(Image.fromarray(overlay),(x+side,y))
        frames.append({'index':n,'image':filename,'rect':[x,y,side*2,side],'rawRect':[x,y,side,side],'overlayRect':[x+side,y,side,side],'source_id':'halle','source_file':'halle_skull.nrrd','source_label':'Микро-КТ Halle, исходный препарат','source_acquisition_step_mm':.125,'registered_grid_step_mm':.125,'center_m':(center*.001).tolist(),'center_native_zyx':(center[[1,2,0]]/.125).tolist(),'u':right.tolist(),'v':up.tolist(),'normal':d.tolist(),'pixel_step_mm':.125,'field_mm':14.125,'display_scale':1,'distanceAlongSamplingProbe_mm':round(float(steps[n]),3),'closed_source_mask_contour':closed})
        measure.append({'index':n,'distance_mm':round(float(steps[n]),3),'maskAtProbe':int(plane[side//2,side//2]),'ctAtProbe':int(raw[side//2,side//2]),'closedContour':closed})
    path=SITE/filename;page.save(path,optimize=True)
    pages.append({'file':filename,'width':page.width,'height':page.height,'sha256':digest(path)})
assert all(m['maskAtProbe']==0 for m in measure)
slices={'source':'Halle: исходная микро-КТ и полуавтоматическая костная сегментация одного препарата','sourceUrl':SOURCE,'sources':[{'id':'halle','file':'halle_skull.nrrd','label':'Микро-КТ Halle','acquisition_step_mm':.125,'md5':CT_MD5,'wholeFileVerified':True}],'license':'CC BY 4.0','attribution':ATTR,'source_acquisition_step_mm':.125,'registered_grid_step_mm':.125,'type':'oblique_reslice','standard_anatomical_plane':False,'intensities_are_calibrated_HU':False,'window_raw_values':[-500,1800],'ct_interpolation':'nearest','mask_interpolation':'nearest','caption':'Косые срезы исходной микро-КТ поперёк проверенного просвета. Слева — исходные плотности; справа — тот же кадр с границей костной маски красным. Голубым выделена связная область воздуха, только если контур маски замкнут. Это не модель нерва. Пиксели выбраны из исходного объёма без усреднения; открытые контуры не исправлялись. Оси соответствуют препарату, сторона тела не присваивалась.','series':[{'id':ID,'ru':'Канал подъязычного нерва: КТ вдоль просвета','kind':'oblique_reslice','pages':pages,'frames':frames,'selectedSlice':48,'complete_channel':False,'continuous_lumen_confirmed':True}]}
save(SITE/'skull-cranial-channel-slices.json',slices);save(OUT/'skull-cranial-channel-slices.json',slices)

refs=[{'title':'Gray, Anatomy of the Human Body (1918), The Occipital Bone','url':'https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf','locator':'PDF, с. 79: Lateral Parts (pars lateralis). Канал начинается над большим отверстием и проходит над основанием мыщелка латерально и вперёд; мыщелковый канал описан отдельно позади мыщелка.','scope':'anatomy'},{'title':'Anatomy Standard: Occipital bone','url':'https://www.anatomystandard.com/ossa-et-juncturae/cranium/os-occipitale.html','locator':'Иллюстрации Front и Back: canalis nervi hypoglossi над condylus occipitalis; canalis condylaris расположен отдельно сзади.','scope':'anatomy'}]
geometryrefs=[{'title':'Thomas Kirchner: Micro-CT data of a human skull (2022)','url':SOURCE,'locator':'halle_skull.nrrd и halle_skull_segmented.nrrd; шаг 0,125 мм. Обе полные контрольные суммы MD5 сверены с записью Zenodo.','scope':'geometry'}]
evidence={'continuous_lumen_confirmed':True,'apertures_reviewed':2,'complete_wall_claim':False,'native_step_mm':.125,'probeEndpoints_mm':[a.tolist(),b.tolist()],'probe_is_anatomical_centerline':False,'probe_sample_count':len(measure),'probe_ct_range':[min(m['ctAtProbe'] for m in measure),max(m['ctAtProbe'] for m in measure)],'all_probe_samples_mask_air':True,'closed_oblique_contours':sum(m['closedContour'] for m in measure),'contour_plane_count':len(measure),'mesh':meshes[0],'wholeSourceChecksums':checks,'anatomical_review':'Независимо подтверждён canalis nervi hypoglossi по расположенному над передней частью мыщелка ходу у переднелатерального края большого отверстия. Кандидат не расположен позади мыщелка, где ожидается canalis condylaris.','review_images':['build_head/cranial_channels/candidate-hypoglossal-ct.png','build_head/cranial_channels/hypoglossal-horizontal-ct.png','build_head/cranial_channels/hypoglossal-coronal-ct.png','build_head/cranial_channels/jobs-context/inferior.png','build_head/cranial_channels/jobs-context/internal.png'],'source_mesh_artificial_crop_boundaries':True,'caps_added':False,'holes_filled':False,'smoothed':False,'synthetic_channel_surface':False}
structure={'id':ID,'node':'channels|'+ID,'ru':'Канал подъязычного нерва — костный блок','lat':'canalis nervi hypoglossi','ta98':'A02.1.04.016','description':'Канал подъязычного нерва проходит над основанием затылочного мыщелка. Его внутричерепное отверстие находится над краем большого отверстия; ход направлен латерально и вперёд. В этом препарате просвет прослежен между двумя отверстиями по исходной микро-КТ.','modelNote':'Показана настоящая костная ткань вокруг канала, выделенная из исходной сегментации при шаге 0,125 мм. Просвет виден в отверстиях, при вращении, срезе и на последовательных КТ-кадрах. Маска местами не замыкает тонкую стенку: эти разрывы сохранены, а все микродетали не объявлены завершёнными. Прямоугольные края блока — границы выборки, а не анатомические отверстия. Сторона тела не присвоена из-за неоднозначной исходной декларации ориентации.','refs':refs,'geometryRefs':geometryrefs,'view':{'d':[12,0,-7],'up':[0,1,0],'distance':.055,'target':[.055,.04,.1045]},'views':[{'id':'intracranial','ru':'Со стороны большого отверстия','d':[12,0,-7],'up':[0,1,0],'distance':.055,'target':[.055,.04,.1045]},{'id':'extracranial','ru':'Наружное отверстие','d':[-12,0,7],'up':[0,1,0],'distance':.055,'target':[.055,.04,.1045]}],'color':'#d7ab5c','scope':'channel_bone_roi','completeFeatureGeometry':False,'continuousLumenConfirmed':True,'source':'Halle micro-CT','specimen':'halle_skull','side':None,'evidence':evidence,'slices':ID}
metadata={'title':'Канал подъязычного нерва: микро-КТ Halle','mode':'cranial_channels','file':meshes[0]['file'],'sha256':meshes[0]['sha256'],'contextFile':meshes[1]['file'],'contextSha256':meshes[1]['sha256'],'slicesFile':'skull-cranial-channel-slices.json','source':'Halle micro-CT','sourceUrl':SOURCE,'license':'CC BY 4.0','attribution':ATTR,'coordinateFrame':'Original source i,j,k -> viewer [i,k,j] metres at 0.000125 m/voxel; no registration to BodyParts3D. Anatomical anterior is viewer +z based on skull context; laterality intentionally unassigned.','complete_channel_geometry_claim':False,'continuous_lumen_confirmed':True,'context':{'id':'halle_occipital_context','node':'channels|halle_occipital_context','ru':'Затылочная область: большое отверстие и мыщелки','lat':'Os occipitale','context':True,'modelNote':'Широкая выборка того же препарата с шагом 0,25 мм для ориентации. Маска не разделена по отдельным костям. Края блока искусственно обрезаны; крышки не добавлялись.'},'structures':[structure],'changes':['Из бинарной сегментации выделена изоповерхность уровня 0,5; основной блок при исходном шаге 0,125 мм, контекст при шаге 0,25 мм.','Координаты переведены в метры и переставлены оси. Порядок вершин треугольников согласован с направлением из кости в воздух; геометрическая форма не менялась.','Не выполнялись сглаживание, децимация, заделка отверстий, добавление крышек или моделирование просвета цилиндром.','GLB упакован meshopt без квантования координат. КТ-кадры получены выборкой ближайшего исходного вокселя в явно указанной косой плоскости.'],'limitations':['Подтверждён сквозной ход и две апертуры в одном препарате; полное сохранение всех тонких стенок и микроветвей не заявлено.','Разрыв сегментации сам по себе не доказывает анатомический дефект кости.','Шаг 0,125 мм — шаг исходной сетки, а не измеренная анатомическая точность.'],'sourceChecksums':checks,'meshReports':meshes}
save(SITE/'skull-cranial-channels.json',metadata);save(OUT/'skull-cranial-channels.json',metadata)
save(ROOT/'pins_head/cranial-channels.json',{'source':'Halle micro-CT','specimen':'halle_skull','structures':[structure],'not_main_atlas_markers':True})
save(ROOT/'research/cranial-channel-review.json',{'source':SOURCE,'license':'CC BY 4.0','complete_skull_geometry_claim':False,'sourceChecksums':checks,'confirmed':[{'ta98':'A02.1.04.016','status':'source_ct_continuous_lumen_and_native_bone_roi','evidence':evidence,'refs':refs}],'candidateLimitations':[{'ta98':'A02.1.05.021','name':'canalis opticus','status':'not_promoted','reason':'Полный ход ещё не прослежен на исходной КТ; видимое отверстие не равно подтверждённому каналу.'},{'name':'canalis pterygoideus','status':'not_promoted','reason':'Имеющиеся маркеры апертур не заменяют проверку внутрикостного хода.'}],'source_meshes':meshes,'samplingProbe':measure})
print(json.dumps({'meshes':meshes,'frames':len(frames),'pages':len(pages),'closedContours':sum(m['closedContour'] for m in measure)},ensure_ascii=False,indent=2))
