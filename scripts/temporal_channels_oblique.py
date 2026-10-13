"""Look for actual bony rings in planes aligned to author context segments.

Centerlines are navigation guides only. Bony contours are independently selected
from Bone.nrrd; missing boundaries are not closed by the context mesh.
"""
import argparse,json
import numpy as np
import trimesh
from scipy.ndimage import map_coordinates,label,binary_erosion,gaussian_filter1d
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from skimage.morphology import skeletonize
from PIL import Image,ImageDraw
from temporal_channels_probe import ROOT,OUT,CACHE,ras_vox,load_volume

def guide(part):
    file=CACHE/('12_Carotis Interna.ply' if part=='carotid' else '06_Facial Nerve.ply')
    mesh=trimesh.load(file,process=False)
    grid=mesh.voxelized(.125).fill()
    skeleton=skeletonize(grid.matrix)
    points=grid.indices_to_points(np.argwhere(skeleton));vox=ras_vox(points)
    pairs=cKDTree(vox).query_pairs(1.75,output_type='ndarray');weights=np.linalg.norm(vox[pairs[:,0]]-vox[pairs[:,1]],axis=1)
    g=csr_matrix((np.r_[weights,weights],(np.r_[pairs[:,0],pairs[:,1]],np.r_[pairs[:,1],pairs[:,0]])),shape=(len(vox),len(vox)))
    ends=np.flatnonzero(np.diff(g.indptr)==1)
    distance=dijkstra(g,indices=ends)
    distance[~np.isfinite(distance)]=-1
    a,b=np.unravel_index(distance.argmax(),distance.shape);start=ends[a]
    if part=='facial':
        # The longest author-nerve branch is not anatomical proof of the
        # labyrinthine endpoint. Source CBCT review identifies the short branch
        # continuing toward the IAC; the other branch remains unclassified.
        start=ends[np.argmin(vox[ends,0])]
        b=ends[np.argmin(np.linalg.norm(vox[ends]-[325,205,347],axis=1))]
    dist,pre=dijkstra(g,indices=start,return_predecessors=True)
    path=[b]
    while path[-1]!=start:path.append(pre[path[-1]])
    path=vox[path[::-1]]
    if part=='facial':
        # Navigation samples individually checked in embedded CBCT and Bone.
        # These points do not generate wall coordinates or fill any gaps.
        # Stop before the widening into the internal acoustic meatus.
        path=np.vstack([path,[[325,205,x] for x in range(347,336,-1)]])
    path=gaussian_filter1d(path,2,axis=0,mode='nearest')
    length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(path,axis=0),axis=1))]
    target=np.arange(0,length[-1],1.)
    path=np.stack([np.interp(target,length,path[:,a]) for a in range(3)],axis=1)
    return path,file.name

def plane(path,i,radius):
    normal=path[min(i+3,len(path)-1)]-path[max(i-3,0)];normal/=np.linalg.norm(normal)
    reference=np.eye(3)[np.argmin(abs(normal))]
    u=np.cross(normal,reference);u/=np.linalg.norm(u);v=np.cross(normal,u)
    a,b=np.meshgrid(np.arange(-radius,radius+1),np.arange(-radius,radius+1))
    coords=path[i][:,None,None]+u[:,None,None]*a+v[:,None,None]*b
    return coords,u,v

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--part',choices=['carotid','facial'],default='carotid');args=parser.parse_args()
    volume=load_volume();bone=np.load(CACHE/'bone-mask.npy',mmap_mode='r')
    path,file=guide(args.part);radius=48 if args.part=='carotid' else 24
    width=2*radius+1;scale=3 if args.part=='carotid' else 5
    masks=[];records=[]
    for i in range(len(path)):
        coords,u,v=plane(path,i,radius)
        mask=map_coordinates(bone,coords,order=0,mode='constant',cval=0)>0
        labels,n=label(~mask,np.ones((3,3)))
        region=labels==labels[radius,radius] if not mask[radius,radius] else np.zeros_like(mask)
        opened=bool(np.any(region[0]) or np.any(region[-1]) or np.any(region[:,0]) or np.any(region[:,-1]))
        record={'slice':i,'guide_native_zyx':path[i].tolist(),'plane_u':u.tolist(),'plane_v':v.tolist(),'bone_at_guide':bool(mask[radius,radius]),'closed_bone_ring':bool(region.any() and not opened),'lumen_area_mm2':float(region.sum()*.125**2) if not opened else None}
        records.append(record);masks.append((mask,region,coords))
    samples=list(range(0,len(path),4));cols=6;rows=int(np.ceil(len(samples)/cols));sheet=Image.new('RGB',(cols*width*scale,rows*(width*scale+24)),(25,30,33));d=ImageDraw.Draw(sheet)
    for panel,i in enumerate(samples):
        mask,region,coords=masks[i];ct=map_coordinates(volume,coords,order=1,mode='constant',cval=-3024)
        gray=(np.clip((ct.astype(float)+500)/3000,0,1)*255).astype('uint8');rgb=np.repeat(gray[:,:,None],3,axis=2)
        edge=mask&~binary_erosion(mask);rgb[edge]=[210,60,60]
        if records[i]['closed_bone_ring']:rgb[region]=((rgb[region].astype(float)+[20,180,255])/2).astype('uint8')
        im=Image.fromarray(rgb).resize((width*scale,width*scale),Image.Resampling.NEAREST);x=panel%cols*width*scale;y=panel//cols*(width*scale+24);sheet.paste(im,(x,y+24));d.text((x+5,y+4),f'{args.part} {i}: '+('closed' if records[i]['closed_bone_ring'] else 'OPEN'),fill='white')
    sheet.save(OUT/f'{args.part}-oblique-overview.png')
    report={'context_file':file,'context_role':'Navigation planes only; does not supply bony geometry.','source_mask':'Bone.nrrd','scan':'CBCT_Unembedded.nrrd','native_grid_mm':.125,'full_cbct_acquisition_mm':.25,'records':records}
    if args.part=='facial':
        report['terminal_navigation_review']={'selected_author_branch_endpoint_native_zyx':[325,205,347],
          'additional_source_void_samples_native_zyx':[[325,205,x] for x in range(347,336,-1)],
          'source':'CBCT_Embedded.nrrd, acquisition 0.125 mm; registered Bone.nrrd',
          'images':['facial-endpoint-axis1-embedded.png','facial-endpoint-axis2-embedded.png','facial-proximal-candidate.png'],
          'limit':'Stop within the narrow proximal passage, before its widening into the IAC. No claim of complete endpoint aperture. The longer author nerve branch is not accepted as the facial canal endpoint.'}
    (OUT/f'{args.part}-oblique.json').write_text(json.dumps(report,indent=2)+'\n')
    good=[x['slice'] for x in records if x['closed_bone_ring']]
    print(args.part,'closed rings',len(good),'/',len(records),'indices',good,flush=True)

if __name__=='__main__':main()
