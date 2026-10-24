"""Targeted read-only exports from a pinned Z-Anatomy source for registration."""
import bpy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'research/evidence-runs/stage7-targeted-muscle-sources-2026-10-22T07-14-12-363Z-LR6EiF'
SOURCE=ROOT/'research/cache/stage7-z-muscles-04d15340/Z-Anatomy-Startup.blend'
names=['Vertebra '+kind+str(n) for kind,nums in [('C',[7]),('T',range(1,13)),('L',[1])] for n in nums]
names += ['Multifidus thoracis muscle.l','Multifidus thoracis muscle.r',
          'Diaphragm','Nasalis muscle.l','Nasalis muscle.r','Orbicularis oris muscle.l',
          'Orbicularis oris muscle.r','Rotatores.l','Rotatores.r']
with bpy.data.libraries.load(str(SOURCE),link=False) as (source,destination):
    destination.objects=[n for n in names if n in source.objects]
rows=[]
for obj in destination.objects:
    if obj is None or obj.type!='MESH':continue
    bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.update()
for obj in destination.objects:
    if obj is None or obj.type!='MESH':continue
    mesh=obj.data
    mesh.calc_loop_triangles()
    groups={g.index:g.name for g in obj.vertex_groups}
    # Preserve authored winding; consumer corrects reflections only in derivatives.
    rows.append({'name':obj.name,'vertices':[list(obj.matrix_world@v.co) for v in mesh.vertices],
      'faces':[list(t.vertices)for t in mesh.loop_triangles],
      'triangle_materials':[mesh.polygons[t.polygon_index].material_index for t in mesh.loop_triangles],
      'materials':[m.name if m else None for m in mesh.materials],
      'vertex_groups':groups,
      'weighted_vertices':[{'i':v.index,'groups':{groups[g.group]:g.weight for g in v.groups}} for v in mesh.vertices if len(v.groups)],
      'determinant':obj.matrix_world.to_3x3().determinant(),
      'modifiers':[{'name':m.name,'type':m.type}for m in obj.modifiers]})
with (RUN/'z-target-arrays-v2.json').open('x',encoding='utf8')as f:json.dump(rows,f,ensure_ascii=False)
with bpy.data.libraries.load(str(SOURCE),link=False) as (source,destination):
    destination.texts=[n for n in ['Multifidus thoracis muscle','Multifidus muscles','Diaphragm','Rotatores'] if n in source.texts]
with (RUN/'z-authored-descriptions.json').open('x',encoding='utf8')as f:
    json.dump({t.name:t.as_string() for t in destination.texts if t},f,ensure_ascii=False,indent=2)
print(json.dumps([{'name':x['name'],'vertices':len(x['vertices']),'triangles':len(x['faces']),
                  'vertex_groups':x['vertex_groups'],'materials':x['materials']}for x in rows],ensure_ascii=False))
