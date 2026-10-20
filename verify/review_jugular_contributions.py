"""Blender MCP: inspect each jugular contribution separately, never trace a contour."""
from pathlib import Path
import bpy,bmesh,json,io
from contextlib import redirect_stdout
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/stage4-2026-10-16'; SHOTS=ROOT/'shots/stage4-2026-10-16';SHOTS.mkdir(exist_ok=True)
scene=bpy.data.scenes.get('Shared landmark measurement')
assert scene is not None,'Run the existing jugular import first.'
def owner(obj):
    while obj:
        if obj.name.startswith('b|'):return obj.name.split('|')[1].split('.')[0]
        obj=obj.parent
original_scene=bpy.context.scene
visibility={o:o.hide_render for o in scene.objects}
old_camera=scene.camera
records=[];images=[]
try:
    bpy.context.window.scene=scene
    camera=bpy.data.objects.new('Stage4 separated contributions camera',bpy.data.cameras.new('Stage4 separated contributions camera'))
    scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=.05
    scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=820;scene.render.resolution_y=720;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_cavity=True
    pins=json.loads((ROOT/'research/shared-landmarks-geometry.json').read_text(encoding='utf8'))['candidates']
    for pin in pins:
        side='right' if pin['bone'].endswith('right') else 'left'
        x,y,z=pin['p'];center=Vector((x,-z,y))
        for bone in [pin['bone'],'occipital']:
            objects=[o for o in scene.objects if o.type=='MESH' and owner(o)==bone]
            for obj in scene.objects:obj.hide_render=obj not in objects
            metrics=[]
            for obj in objects:
                bm=bmesh.new();bm.from_mesh(obj.data)
                vertices=[obj.matrix_world@v.co for v in obj.data.vertices]
                tree=BVHTree.FromPolygons(vertices,[list(p.vertices) for p in obj.data.polygons],all_triangles=True)
                closest,normal,face,distance=tree.find_nearest(center)
                bm.normal_update()
                metrics.append(dict(object=obj.name,vertices=len(bm.verts),faces=len(bm.faces),
                    boundary_edges=sum(e.is_boundary for e in bm.edges),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),
                    noncontiguous_two_face_edges=sum(e.is_manifold and not e.is_contiguous for e in bm.edges),
                    nearest_imported_face=int(face),anchor_distance_mm=distance*1000,
                    note='Face index is Blender-import-local, not stable GLB faceIndex. A nearest face is not an anatomical boundary label.'))
                bm.free()
            camera.location=center+Vector((-.35 if side=='right' else .35,.25,-1)).normalized()*.3
            camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
            path=SHOTS/f'jugular-{side}-{bone}-separate.png';scene.render.filepath=str(path)
            with redirect_stdout(io.StringIO()):bpy.ops.render.render(write_still=True)
            images.append(str(path.relative_to(ROOT)).replace('\\','/'))
            records.append(dict(side=side,bone=bone,measurements=metrics))
finally:
    for obj,hidden in visibility.items():obj.hide_render=hidden
    scene.camera=old_camera;bpy.context.window.scene=original_scene
(OUT/'jugular-separated-blender.json').write_text(json.dumps(dict(tool='Blender MCP',version=bpy.app.version_string,records=records,images=images,exactContourAccepted=False,dimensionsAccepted=False),indent=2)+'\n',encoding='utf8')
print(json.dumps({'records':records,'images':images}))

