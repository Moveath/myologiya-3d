"""Export only diagnostic thoracic multifidus derivatives; never production.

Positive rigid transform from labelled-vertebra registration. The authored left
reflection has its triangle winding corrected. No decimation or deformation.
"""
import bpy
import json
from pathlib import Path
from mathutils import Vector
from math import radians

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'research/evidence-runs/stage7-targeted-muscle-sources-2026-10-22T07-14-12-363Z-LR6EiF'
OUT=ROOT/'build_stage7/z_multifidus_trials_v1'
OUT.mkdir(exist_ok=False)
source=json.loads((RUN/'z-target-arrays-v2.json').read_text(encoding='utf8'))
atlas=json.loads((RUN/'atlas-multifidus-context.json').read_text(encoding='utf8'))
fits=json.loads((RUN/'z-multifidus-registration.json').read_text(encoding='utf8'))
fit=next(x for x in fits if x['kind']=='rigid')
scene=bpy.data.scenes.new('Stage7 Z multifidus — TEST NOT ADMITTED')
bpy.context.window.scene=scene
from mathutils import Matrix
matrix=Matrix(fit['matrix_source_blender_to_atlas_three'])

def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
bone=material('Review bone',(.65,.62,.52))
muscles=[material('Right authored part',(.72,.12,.1)),material('Left authored mirror',(.1,.45,.67))]
models=[]
def make(name,vertices,faces,mat):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj);obj.data.materials.append(mat)
    return obj

for row in atlas:
    if row['name'].startswith('b|'):
        make(row['name'],[(x,-z,y)for x,y,z in row['vertices']],row['faces'],bone)
for i,(side,suffix)in enumerate([('right','r'),('left','l')]):
    row=next(x for x in source if x['name']==f'Multifidus thoracis muscle.{suffix}')
    points=[matrix@Vector(v)for v in row['vertices']]
    faces=[(f[0],f[2],f[1])if row['determinant']<0 else f for f in row['faces']]
    obj=make(f'm|thorax_multifidus_{side}|thoracic',[(v.x,-v.z,v.y)for v in points],faces,muscles[i])
    for o in scene.objects:o.select_set(False)
    obj.select_set(True);bpy.context.view_layer.objects.active=obj
    target=OUT/f'thorax_multifidus_{side}-thoracic-test.glb'
    bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,
        use_active_scene=True,export_yup=True,export_normals=True,export_materials='EXPORT',
        export_cameras=False,export_lights=False)
    models.append({'issue':f'MP-thorax_multifidus_{side}-thoracic','file':str(target.relative_to(ROOT)),
        'source_object':row['name'],'triangles':len(faces),'vertices':len(points),
        'modelStatus':'test_not_admitted','side':side,'source_is_mirrored':side=='left',
        'winding_reversed':row['determinant']<0})

scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1100;scene.render.resolution_y=850
scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Review world')
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH';scene.display.shading.show_object_outline=True
scene.display.shading.background_type='WORLD';scene.world.color=(.045,.045,.05)
camdata=bpy.data.cameras.new('Review camera');cam=bpy.data.objects.new('Review camera',camdata)
scene.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=.40
center=Vector((0,-.04,1.245))
for label,offset in [('posterior',(0,.7,.05)),('right_oblique',(-.5,.5,.05)),('left_oblique',(.5,.5,.05))]:
    cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(RUN/f'z-multifidus-{label}.png');bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(OUT/'review.blend'),{scene})
with(OUT/'provenance.json').open('x',encoding='utf8')as f:
    json.dump({'source_archive':'Z-Anatomy/Models-of-human-anatomy@04d15340bad66394659c0e3b3ff9d9bb0924f6ca',
      'models':models,'transform':fit,'license':'CC BY-SA 4.0',
      'attribution':['Z-Anatomy — Gauthier Kervyn (design, 3D, anatomy), Marcin Zielinski (Blender), contributors',
                     'BodyParts3D — The Database Center for Life Science — CC BY-SA 2.1 Japan'],
      'method':'Source local-to-world, source Blender to atlas Three rigid registration, authored reflection winding correction only; no decimation/deformation.',
      'admitted':False,
      'blockers':['533 crossing triangle pairs and one duplicate per side require interpretation',
                  'Bone registration is not confirmed muscle-attachment registration',
                  'Sampled bone penetration reaches 1.92 mm right and 2.11 mm left',
                  'Overlays duplicate an existing whole muscle; no production replacement authorized by this diagnostic export']},f,ensure_ascii=False,indent=2)
print(json.dumps(models,ensure_ascii=False))
