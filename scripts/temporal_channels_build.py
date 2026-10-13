"""Extract inspected channel-wall patches, without inventing tube geometry.

Every exported triangle is an unchanged triangle of a marching-cubes surface of
the original Bone.nrrd mask. Selection has open ends; no caps or hole filling.
"""
import json,hashlib,subprocess
import numpy as np
import trimesh
from scipy.ndimage import map_coordinates,label
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes
from temporal_channels_probe import ROOT,OUT,CACHE,ORIGIN

CONFIG={
 'facial':{'id':'facial_canal_wall','interval':[2,225],'radius':20,'color':'#d7ab5c'},
 'carotid':{'id':'carotid_canal_wall','interval':[0,102],'radius':50,'color':'#cf8580'},
}

def viewer(vox):
    v=np.asarray(vox)
    return np.stack([ORIGIN[0]-.125*v[:,2],ORIGIN[2]+.125*v[:,0],-.0-ORIGIN[1]+.125*v[:,1]],axis=1)*.001

def original_patch(bone,path,records,config):
    radius=config['radius'];first,last=config['interval']
    lo=np.floor(path.min(axis=0)-radius-3).astype(int);hi=np.ceil(path.max(axis=0)+radius+4).astype(int)
    crop=np.array(bone[tuple(slice(a,b) for a,b in zip(lo,hi))],dtype=np.uint8)
    v,f,_,_=marching_cubes(crop,.5,allow_degenerate=False)
    v+=lo
    tri=v[f];center=tri.mean(axis=1)
    outward=-np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);outward/=np.linalg.norm(outward,axis=1)[:,None]
    distance,index=cKDTree(path).query(center)
    direction=path[index]-center;direction/=np.maximum(np.linalg.norm(direction,axis=1)[:,None],1e-8)
    local_radius=np.where(index>=208,10,radius) if config['id']=='facial_canal_wall' else radius
    keep=(index>=first)&(index<=last)&(distance<local_radius)&(np.sum(direction*outward,axis=1)>.1)
    if config['id']=='facial_canal_wall':
        # Do not reinclude the unclassified long terminal branch merely because
        # its source wall lies near the inspected common geniculate region.
        keep &= ~((center[:,0]>330)&(center[:,1]<218)&(center[:,2]>351))
    # Both sides are checked in the actual source mask. We retain the original
    # topology and coordinates; this is a surface selection, never a new tube.
    inside=map_coordinates(bone,(center-outward*.8).T,order=0)>0
    outside=map_coordinates(bone,(center+outward*.8).T,order=0)==0
    keep &= inside&outside
    # Reject a farther surface if the line from the reviewed guide to it crosses
    # an intervening bone wall. This only selects existing triangles.
    candidates=np.flatnonzero(keep)
    for alpha in np.linspace(.05,.85,10):
        pos=path[index[candidates]]*(1-alpha)+center[candidates]*alpha
        keep[candidates] &= map_coordinates(bone,pos.T,order=0)==0
    selected=np.flatnonzero(keep)
    np.savez_compressed(OUT/(config['id']+'-voxel-roi.npz'),
                        original_bone_mask=crop,origin_native_zyx=lo,
                        selected_bone_boundary_voxels=np.unique(np.rint(center[selected]-outward[selected]*.8).astype(np.int32),axis=0),
                        selected_void_boundary_voxels=np.unique(np.rint(center[selected]+outward[selected]*.8).astype(np.int32),axis=0))
    native=trimesh.Trimesh(vertices=viewer(v),faces=f[selected],process=False)
    native.remove_unreferenced_vertices()
    native.visual=trimesh.visual.ColorVisuals(native,vertex_colors=trimesh.visual.color.hex_to_rgba(config['color']))
    np.savez_compressed(OUT/(config['id']+'-source-selection.npz'),source_vertices_zyx=v,source_faces=f,selected_faces=selected,roi_bounds_zyx=np.array([lo,hi]))
    # Select a stable centroid on the inner wall for a native marker.
    middle=(first+last)//2
    scores=np.abs(index[selected]-middle)+.05*distance[selected]
    chosen=selected[np.argmin(scores)];p=viewer(center[chosen:chosen+1])[0]
    normal_vox=outward[chosen]
    normal=np.array([-normal_vox[2],normal_vox[0],normal_vox[1]])
    _,component_count=label(crop==0)
    report={'id':config['id'],'source':'07_3D_Models/Bone.nrrd','roi_native_zyx':[lo.tolist(),hi.tolist()],
            'guide_selected_interval':config['interval'],'guide_count':len(path),'triangles':len(native.faces),'vertices':len(native.vertices),
            'bounds_m':native.bounds.tolist(),'marker':{'p':p.tolist(),'n':normal.tolist()},
            'selection':'Only original source-mask triangles facing the reviewed canal region, with an unobstructed local path to that region. No nerve/artery triangles exported.',
            'source_triangle_coordinates_retained':True,'caps_added':False,'holes_filled':False,'decimated':False,
            'closed_source_contours_in_interval':sum(records[i]['closed_bone_ring'] for i in range(first,last+1)),
            'reviewed_interval_planes':last-first+1,
            'approximate_guide_span_mm':float(np.linalg.norm(np.diff(path[first:last+1],axis=0),axis=1).sum()*.125),
            'complete_channel':False}
    if config['id']=='facial_canal_wall':
        report['terminal_selection_limit']={'reduced_radius_from_guide_index':208,'terminal_radius_voxels':10,'excluded_terminal_region_native_zyx':'k>330, j<218, i>351; unclassified long branch','review':'Short source-nerve branch and additional existing source void toward IAC reviewed in embedded CBCT. No endpoint-aperture completeness claim.'}
    return native,report

def main():
    bone=np.load(CACHE/'bone-mask.npy',mmap_mode='r');scene=trimesh.Scene();reports=[];paths=[]
    for part,cfg in CONFIG.items():
        data=json.loads((OUT/f'{part}-oblique.json').read_text());records=data['records'];path=np.array([x['guide_native_zyx'] for x in records]);paths.append(path)
        mesh,report=original_patch(bone,path,records,cfg)
        scene.add_geometry(mesh,node_name='channels|'+cfg['id'],geom_name=cfg['id']);reports.append(report)
    # A cropped context retains actual bone faces and intentionally has open
    # cut edges. It contains no fabricated planar faces at the ROI boundary.
    path=np.concatenate(paths);lo=np.floor(path.min(axis=0)-55).astype(int);hi=np.ceil(path.max(axis=0)+56).astype(int)
    volume=np.array(bone[tuple(slice(a,b) for a,b in zip(lo,hi))],dtype=np.uint8)
    v,f,_,_=marching_cubes(volume,.5,allow_degenerate=False);v+=lo
    context=trimesh.Trimesh(vertices=viewer(v),faces=f,process=False)
    context.visual=trimesh.visual.ColorVisuals(context,vertex_colors=trimesh.visual.color.hex_to_rgba('#cdbf9f'))
    context_scene=trimesh.Scene();context_scene.add_geometry(context,node_name='channels|temporal_context',geom_name='temporal_context')
    for name,sc in [('skull-temporal-channels',scene),('skull-temporal-channels-context',context_scene)]:
        high=OUT/(name+'-hi.glb');high.write_bytes(sc.export(file_type='glb'));dest=OUT/(name+'.glb')
        subprocess.run(['node',str(ROOT/'tools/node_modules/gltfpack/cli.js'),'-i',str(high),'-o',str(dest),'-cc','-kn','-ke','-vp','16'],check=True)
    report={'source':'OpenEar ZETA','license':'CC BY 4.0','coordinate_frame':'OpenEar native viewer metres; [RASx,RASy,RASz] -> [-RASx,RASz,RASy]; no registration to BodyParts3D.',
            'bone_nrrd_sha256':hashlib.sha256((CACHE/'Bone.nrrd').read_bytes()).hexdigest(),
            'geometry_file':'skull-temporal-channels.glb','geometry_sha256':hashlib.sha256((OUT/'skull-temporal-channels.glb').read_bytes()).hexdigest(),
            'context_file':'skull-temporal-channels-context.glb','context_sha256':hashlib.sha256((OUT/'skull-temporal-channels-context.glb').read_bytes()).hexdigest(),
            'context_roi_native_zyx':[lo.tolist(),hi.tolist()],'context_triangles':len(f),'context_added_caps':False,
            'structures':reports,'complete_channel_geometry_claim':False}
    (OUT/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()
