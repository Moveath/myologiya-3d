"""Run by Blender MCP with RUN set to the allocated evidence directory.
Creates a separate review scene. This is not a muscle-part mask or admission.
"""
import bpy
import json
from pathlib import Path
from mathutils import Vector

run = Path(RUN)
data = json.loads((run/'blender-review-arrays.json').read_text(encoding='utf8'))
profiles = json.loads((run/'source-shape-profiles.json').read_text(encoding='utf8'))
old_scene = bpy.context.window.scene
scene = bpy.data.scenes.new('Omohyoid_Diagnostic_NotAdmitted')
bpy.context.window.scene = scene
try:
    def material(name, color, alpha=1):
        m=bpy.data.materials.new(name);m.diffuse_color=(*color,alpha)
        return m
    bone=material('Diagnostic_context_bone',(0.65,0.61,0.52))
    whole=material('Whole_omohyoid_no_part_assignment',(0.65,0.20,0.17))
    scm=material('SCM_context',(0.34,0.39,0.42))
    marker=material('Geometric_minimum_NOT_tendon_boundary',(1.0,0.74,0.05))
    objects=[]
    for row in data['rows']:
        p=row['positions'];indices=row['indices']
        vertices=[(p[i],-p[i+2],p[i+1]) for i in range(0,len(p),3)]
        faces=[tuple(indices[i:i+3]) for i in range(0,len(indices),3)]
        mesh=bpy.data.meshes.new('Review_'+row['name']);mesh.from_pydata(vertices,[],faces);mesh.update()
        ob=bpy.data.objects.new('Review_'+row['name'],mesh);scene.collection.objects.link(ob);objects.append(ob)
        ob.data.materials.append(whole if 'omohyoid' in row['name'] else scm if 'sternocleidomastoid' in row['name'] else bone)
        ob['diagnostic_only']=True
        ob['source_asset']=data['source'];ob['source_sha256']=data['sha256']
        if 'sternocleidomastoid' in row['name']:ob.hide_render=True
    for row in profiles['rows']:
        level=row['candidate_internal_minimum']['level']
        profile=min(row['profiles'],key=lambda x:abs(x['level']-level))
        curve=bpy.data.curves.new('GeometricMinimum_'+row['name'],'CURVE');curve.dimensions='3D';curve.bevel_depth=.00035;curve.bevel_resolution=1
        for segment in profile['segments_mm']:
            spline=curve.splines.new('POLY');spline.points.add(1)
            for p,q in zip(spline.points,segment):p.co=(*[x/1000 for x in q],1)
        ob=bpy.data.objects.new('NOT_ANATOMICAL_BOUNDARY_'+row['name'],curve);scene.collection.objects.link(ob);curve.materials.append(marker)
        ob['anatomical_admission']=False;ob['purpose']='Shape minimum review only; no tendon tissue label'
    scene['review_status']='Diagnostic geometry: no anatomical part mask admitted'
    scene['license']='BodyParts3D DBCLS, CC BY-SA 2.1 Japan'
    print(json.dumps(dict(scene=scene.name,objects=len(objects),diagnostic_contours=2,anatomical_masks=0,source=data['source'],source_sha256=data['sha256'])))
finally:
    bpy.context.window.scene=old_scene
