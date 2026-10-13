"""Review small ossicle features against original registered CBCT, without edits.

Raw nearest grid slices are shown beside the same slices with original PLY
section lines. The author surface may be smoother than the CBCT samples.
"""
import json
import hashlib
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from temporal_channels_probe import load_volume, ras_vox, ORIGIN, CACHE
from openear_landmarks_completion import ROOT, OUT

def main():
    picks=json.loads((OUT/'picks.json').read_text(encoding='utf-8'))
    volume=load_volume('embedded')
    source_nrrd=ROOT/'build_head/temporal_features/CBCT_Embedded.nrrd'
    source_sha=hashlib.file_digest(source_nrrd.open('rb'),'sha256').hexdigest()
    reports=[]
    for marker in picks:
        if marker['id'] not in ('malleus_anterior_process','incus_lenticular_process'):continue
        source={'malleus':'03_Malleus.ply','incus':'04_Incus.ply'}[marker['b']]
        mesh=trimesh.load(CACHE/source,process=False)
        mesh.vertices=ras_vox(mesh.vertices)
        p=np.array(marker['p'])*1000
        center=np.array([(p[1]-ORIGIN[2])/.125,(p[2]+ORIGIN[1])/.125,(ORIGIN[0]-p[0])/.125])
        half=24;scale=5;cell=half*2*scale;head=28
        sheet=Image.new('RGB',(5*cell,6*(cell+head)),(22,28,31));draw=ImageDraw.Draw(sheet)
        frames=[]
        for axis in range(3):
            v,u=[i for i in range(3) if i!=axis]
            lo=np.rint(center).astype(int)-half
            for col,delta in enumerate((-2,-1,0,1,2)):
                k=round(center[axis])+delta
                idx=[slice(int(lo[i]),int(lo[i]+half*2)) for i in range(3)];idx[axis]=k
                ct=volume[tuple(idx)]
                assert ct.shape==(half*2,half*2)
                raw=(255*np.clip((ct.astype(float)+500)/3000,0,1)).astype('uint8')
                base=Image.fromarray(raw).convert('RGB').resize((cell,cell),Image.Resampling.NEAREST)
                overlay=base.copy();od=ImageDraw.Draw(overlay)
                origin=center.copy();origin[axis]=k
                normal=np.eye(3)[axis]
                lines=trimesh.intersections.mesh_plane(mesh,plane_origin=origin,plane_normal=normal)
                for line in lines:
                    xy=[((q[u]-lo[u]+.5)*scale,(q[v]-lo[v]+.5)*scale) for q in line]
                    od.line(xy,fill=(0,225,245),width=2)
                for row,image in ((axis*2,base),(axis*2+1,overlay)):
                    x=col*cell;y=row*(cell+head)
                    sheet.paste(image,(x,y+head))
                    draw.text((x+5,y+5),f'axis {axis}, index {k}; '+('raw' if row%2==0 else 'PLY contour'),fill='white')
                frames.append({'axis_native_zyx':axis,'index':k,'row_raw':axis*2,'row_overlay':axis*2+1,'column':col,'voxel_roi_min_zyx':lo.tolist(),'u_voxel_axis':u,'v_voxel_axis':v})
        filename=marker['id']+'-embedded-ct.png';sheet.save(OUT/filename)
        reports.append({'id':marker['id'],'image':filename,'source':'ZETA/CBCT_Embedded.nrrd','source_sha256':source_sha,'original_ply':source,'original_ply_sha256':hashlib.sha256((CACHE/source).read_bytes()).hexdigest(),'source_acquisition_step_mm':.125,'registered_grid_step_mm':.125,'point_native_voxel_zyx':center.tolist(),'field_mm':6,'window_native_values':[-500,2500],'rendering':'nearest samples; cyan = section of original author PLY, not an added segmentation','frames':frames})
    (OUT/'cbct-review.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Wrote two raw/PLY CBCT review sheets, 15 planes per feature')

if __name__=='__main__':main()
