"""Short Blender MCP inspection of the saved trial scene; restores user scene."""
import bpy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'research/evidence-runs/stage7-targeted-muscle-sources-2026-10-22T07-14-12-363Z-LR6EiF'
SOURCE=ROOT/'build_stage7/z_multifidus_trials_v1/review.blend'
original_scene=bpy.context.window.scene
try:
    with bpy.data.libraries.load(str(SOURCE),link=False)as(src,dst):
        dst.scenes=[n for n in src.scenes if n.startswith('Stage7 Z multifidus')]
    scene=next(s for s in dst.scenes if s)
    bpy.context.window.scene=scene
    bpy.context.view_layer.update()
    rows=[]
    for obj in scene.objects:
        if obj.type!='MESH':continue
        obj.data.calc_loop_triangles()
        world=[obj.matrix_world@v.co for v in obj.data.vertices]
        rows.append({'name':obj.name,'vertices':len(world),'triangles':len(obj.data.loop_triangles),
          'bounds_blender_m':[[min(v[k]for v in world)for k in range(3)],
                              [max(v[k]for v in world)for k in range(3)]],
          'determinant':obj.matrix_world.to_3x3().determinant()})
    result={'blender':bpy.app.version_string,'scene':scene.name,'originalScene':original_scene.name,
        'objects':rows,'modelStatus':'test_not_admitted',
        'scope':'Actual saved trial-scene objects only; no new anatomical acceptance and no source edits.'}
finally:
    bpy.context.window.scene=original_scene
result['userSceneRestored']=bpy.context.window.scene==original_scene
with(RUN/'mcp-z-multifidus-scene-review.json').open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'scene':result['scene'],'meshes':len(rows),
    'muscles':[r for r in rows if r['name'].startswith('m|')],
    'userSceneRestored':result['userSceneRestored']},ensure_ascii=False))
