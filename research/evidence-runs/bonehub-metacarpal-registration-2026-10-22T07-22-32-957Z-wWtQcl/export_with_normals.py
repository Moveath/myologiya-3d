"""Re-export saved rigid arrays with explicit normals. No registration rerun."""
import pathlib,json,hashlib
import numpy as np
import trimesh
run=pathlib.Path(__file__).resolve().parent
rows=[]
for owner in ['metacarpal_1_left','metacarpal_3_left']:
    a=json.loads((run/(owner+'-registered-arrays.json')).read_text())
    m=trimesh.Trimesh(np.asarray(a['vertices']).reshape(-1,3),np.asarray(a['faces']).reshape(-1,3),process=False)
    m.visual=trimesh.visual.ColorVisuals(m,vertex_colors=[175,150,80,255])
    scene=trimesh.Scene();scene.add_geometry(m,node_name='b|'+owner,geom_name='trial_bonehub_'+owner)
    data=trimesh.exchange.gltf.export_glb(scene,include_normals=True)
    file=run/(owner+'-rigid-trial-v2.glb');file.open('xb').write(data)
    rows.append({'owner':owner,'file':file.name,'sha256':hashlib.sha256(data).hexdigest(),'triangles':len(m.faces),'method':'Saved rigid test positions/indices unchanged; explicit vertex normals generated from same triangles; no registration rerun, no geometry repair.','license':'CC BY4.0','status':'test_only'})
(run/'trial-v2-export.json').open('x',encoding='utf8').write(json.dumps(rows,indent=2))
print(json.dumps(rows))
