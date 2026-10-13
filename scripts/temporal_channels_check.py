"""Verify compressed surfaces are only original selected bone-mask triangles."""
import json,hashlib
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import map_coordinates
from PIL import Image
from temporal_channels_probe import ROOT,OUT,CACHE,ORIGIN
from temporal_channels_build import viewer

def indices(v):
    v=np.asarray(v)*1000
    return np.stack([(v[:,1]-ORIGIN[2])/.125,(v[:,2]+ORIGIN[1])/.125,(ORIGIN[0]-v[:,0])/.125],axis=1)

def main():
    data=json.loads((OUT/'compressed-geometry.json').read_text());bone=np.load(CACHE/'bone-mask.npy',mmap_mode='r');checks=[]
    for part,decoded in data.items():
        selection=np.load(OUT/(part+'-source-selection.npz'));sv=selection['source_vertices_zyx'];sf=selection['source_faces'][selection['selected_faces']]
        v=np.array(decoded['vertices']);f=np.array(decoded['faces']).reshape(-1,3)
        distances,index=cKDTree(viewer(sv)).query(v)
        original={tuple(sorted(x)) for x in sf}
        introduced=sum(tuple(sorted(x)) not in original for x in index[f])
        assert introduced==0,(part,'new triangle',introduced)
        assert distances.max()*1000<.003,(part,'vertex displacement')
        tri=v[f];center=tri.mean(axis=1);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.linalg.norm(normal,axis=1)[:,None]
        a=map_coordinates(bone,indices(center-normal*.0001).T,order=0)>0;b=map_coordinates(bone,indices(center+normal*.0001).T,order=0)==0
        assert np.all(a&b),(part,'normal/mask',int(np.sum(~(a&b))))
        check={'id':part,'compressed_vertices':len(v),'compressed_triangles':len(f),'unrecognized_triangles':introduced,
               'maximum_vertex_quantization_error_mm':float(distances.max()*1000),'all_face_normals_point_from_bone_to_void':bool(np.all(a&b)),
               'normal_test_offset_mm':.1,'source_mask_matches':int(np.sum(a&b)),'caps_added':False}
        checks.append(check)
    slices=json.loads((OUT/'skull-temporal-channel-slices.json').read_text(encoding='utf-8'));frame_count=0;page_count=0
    sources={s['id']:s for s in slices['sources']}
    for series in slices['series']:
        pages={p['file']:p for p in series['pages']}
        for filename,p in pages.items():
            assert hashlib.sha256((OUT/filename).read_bytes()).hexdigest()==p['sha256']
            with Image.open(OUT/filename) as im:assert im.size==(p['width'],p['height'])
            page_count+=1
        for frame in series['frames']:
            p=pages[frame['image']]
            for key in ['rawRect','overlayRect']:
                x,y,w,h=frame[key];assert min(x,y)>=0 and w>0 and h>0 and x+w<=p['width'] and y+h<=p['height']
            assert frame['source_acquisition_step_mm']==sources[frame['source_id']]['acquisition_step_mm']
            assert frame['registered_grid_step_mm']==.125
            u,v,n=map(np.asarray,[frame['u'],frame['v'],frame['normal']])
            assert np.allclose([np.linalg.norm(u),np.linalg.norm(v),np.linalg.norm(n)],1)
            assert np.allclose(np.cross(u,v),n)
            frame_count+=1
    result={'status':'passed','geometry_sha256':hashlib.sha256((OUT/'skull-temporal-channels.glb').read_bytes()).hexdigest(),
            'slice_atlases':{'pages':page_count,'frames':frame_count,'hashes_rectangles_source_steps_and_vectors_checked':True},
            'checks':checks,'limits':'Geometric source identity does not establish complete anatomical channels. Source CBCT slices and anatomical references are reviewed separately.'}
    (OUT/'source-geometry-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)

if __name__=='__main__':main()
