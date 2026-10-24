"""Blender MCP read-only review: new scene, unchanged source triangle copies.

RUN is an exclusive evidence directory. No source mesh or anatomy point is edited.
"""
import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]; run=ROOT/RUN
build=ROOT/'build_stage7/palmaris_brevis_v1'
spec=json.loads((build/'recipe.json').read_text(encoding='utf8'))
review=json.loads((run/'contact-review.json').read_text(encoding='utf8'))
rows=json.loads((ROOT/spec['source_context']).read_text(encoding='utf8'))
old=bpy.context.window.scene
coord=lambda v:Vector((v[0],-v[2],v[1]))
colors={'abductor_digiti_minimi':(.7,.23,.15,1),'flexor_digiti_minimi_brevis':(.65,.46,.14,1),
        'opponens_digiti_minimi':(.42,.23,.5,1),'flexor_retinaculum':(.2,.55,.26,1),'palmaris_brevis':(.03,.72,.85,1)}
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=color;return m
def mesh_object(scene,name,positions,indices,color):
    data=bpy.data.meshes.new(name)
    data.from_pydata([coord(positions[i:i+3]) for i in range(0,len(positions),3)],[],
                    [indices[i:i+3] for i in range(0,len(indices),3)])
    data.update(); o=bpy.data.objects.new(name,data);scene.collection.objects.link(o)
    data.materials.append(material(name,color));return o
def prepare_scene(name):
    s=bpy.data.scenes.new(name);bpy.context.window.scene=s;s.unit_settings.system='METRIC'
    s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL'
    s.display.shading.show_cavity=True;s.display.shading.show_shadows=True
    s.world=bpy.data.worlds.new(name);s.world.color=(.065,.07,.08)
    s.display.shading.background_type='WORLD'
    s.render.resolution_x=900;s.render.resolution_y=800;s.render.resolution_percentage=100
    c=bpy.data.objects.new('Diagnostic camera',bpy.data.cameras.new('Diagnostic camera'))
    s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';return s,c
def camera_view(c,target,direction,up,scale):
    c.data.ortho_scale=scale;c.location=target+coord(direction).normalized()*.3
    forward=(target-c.location).normalized();right=forward.cross(coord(up)).normalized();u=right.cross(forward)
    c.rotation_euler=Matrix((right,u,-forward)).transposed().to_euler()
def render(s,name):
    path=run/(name+'.png');assert not path.exists();s.render.filepath=str(path);bpy.ops.render.render(write_still=True)

try:
    scene,camera=prepare_scene('PB admission diagnostic — NO ANATOMICAL ADMISSION')
    selected=[r for r in rows if r['id'] in spec['support_ids']+['pisiform','hamate','metacarpal_5']]
    for r in selected:mesh_object(scene,r['name'],r['positions'],r['indices'],colors.get(r['id'],(.7,.67,.56,1)))
    model=mesh_object(scene,'PB existing canonical geometry',review['geometry']['positions'],review['geometry']['indices'],colors['palmaris_brevis'])
    model.data.materials.append(material('Crossing faces, NOT anatomical mask',(.95,.03,.06,1)))
    affected={i for r in review['contacts'] for i in r['crossingFaces']}
    for p in model.data.polygons:p.material_index=int(p.index in affected)
    basis=Matrix(spec['frame']['basis_columns']);radial,distal,palmar=[basis.col[i] for i in range(3)]
    origin=Vector(spec['frame']['origin_m']);target=coord(origin+distal*.021+palmar*.007)
    for name,direction in [('palmar',palmar),('ulnar',palmar*.2-radial)]:
        camera_view(camera,target,direction,-distal,.052);render(scene,'blender-contacts-'+name)
    section,cam=prepare_scene('PB layer section at diagnostic d=16mm — not anatomy contour')
    all_rows=[*selected,dict(id='palmaris_brevis',name='PB',**review['geometry'])]
    segment_counts={}
    for row in all_rows:
        pts=[Vector(row['positions'][i:i+3]) for i in range(0,len(row['positions']),3)]
        heights=[(p-origin).dot(distal)-.016 for p in pts];segments=[]
        for i in range(0,len(row['indices']),3):
            ids=row['indices'][i:i+3];hits=[]
            for a,b in zip(ids,ids[1:]+ids[:1]):
                ha,hb=heights[a],heights[b]
                if ha*hb<0:hits.append(pts[a].lerp(pts[b],ha/(ha-hb)))
            if len(hits)==2:segments.append(hits)
        segment_counts[row['id']]=len(segments)
        data=bpy.data.curves.new(row['name']+' diagnostic section','CURVE');data.dimensions='3D';data.bevel_depth=.000045;data.bevel_resolution=1
        for pair in segments:
            s=data.splines.new('POLY');s.points.add(1)
            for p,v in zip(s.points,pair):p.co=(*coord(v),1)
        o=bpy.data.objects.new(row['name']+' section',data);section.collection.objects.link(o)
        data.materials.append(material(row['name']+' section',colors.get(row['id'],(.7,.67,.56,1))))
    camera_view(cam,coord(origin+distal*.016+palmar*.009),distal,palmar,.045)
    render(section,'blender-layer-section-16mm')
    path=run/'contact-review.blend';assert not path.exists();bpy.data.libraries.write(str(path),{scene,section},fake_user=True)
    model.data.calc_loop_triangles()
    result=dict(status='passed',blender=bpy.app.version_string,triangles=len(model.data.loop_triangles),
        markedCrossingFaces=len(affected),section_distal_mm=16,sectionSegmentCounts=segment_counts,
        source_glb_sha256=hashlib.sha256((build/'palmaris_brevis-trial.glb').read_bytes()).hexdigest(),
        sourceModified=False,anatomicalAdmission=False,views=3,
        note='Colored faces and section polylines are diagnostics, not accepted muscle/attachment masks.')
    with (run/'blender-contact-review.json').open('x',encoding='utf8')as f:json.dump(result,f,indent=2)
finally:
    bpy.context.window.scene=old
print(json.dumps(result))
