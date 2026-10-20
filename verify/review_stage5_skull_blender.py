"""Run via Blender MCP: read-only measurements for the skull review batch.

Imports a temporary byte copy in a separate scene; never exports a model or
accepts anatomical placement from surface proximity. Retains per-ID results.
"""
import hashlib
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from head_localization import positions

source = ROOT / 'build_head/head_hi.glb'
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
original_scene = bpy.context.scene
original_objects = {obj.as_pointer() for obj in bpy.data.objects}
scene = bpy.data.scenes.new('Stage 5 skull read-only review')
bpy.context.window.scene = scene


def bone_id(obj):
    while obj:
        if obj.name.startswith('b|'):
            return obj.name.split('|')[1].split('.')[0]
        obj = obj.parent
    return None


try:
    with tempfile.TemporaryDirectory(prefix='atlas-stage5-skull-') as directory:
        copy = Path(directory) / 'head.glb'
        copy.write_bytes(source.read_bytes())
        with redirect_stdout(io.StringIO()):
            bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    trees, meshes = {}, []
    for obj in scene.objects:
        bone = bone_id(obj)
        if obj.type != 'MESH' or bone is None:
            continue
        vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
        obj.data.calc_loop_triangles()
        faces = [list(t.vertices) for t in obj.data.loop_triangles]
        trees.setdefault(bone, []).append(BVHTree.FromPolygons(vertices, faces, all_triangles=True))
        meshes.append(dict(bone=bone, vertices=len(vertices), triangles=len(faces),
                           scale=list(obj.scale), determinant=obj.matrix_world.determinant()))
    records = []
    for (bone, code), row in positions().items():
        x, y, z = row['p']
        point = Vector((x, -z, y))  # glTF Y-up -> Blender Z-up, once.
        nearest = min(tree.find_nearest(point)[3] for tree in trees[bone]) * 1000
        assert nearest < 0.3, (bone, code, nearest)
        records.append(dict(id='head_' + bone + '_' + code.replace('.', '_'),
                            bone=bone, code=code, source_file=row['source_file'],
                            localization=row['localization'], distance_mm=nearest,
                            anatomical_placement_accepted=False))
    assert len(trees) == 22 and len(records) == 521
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    report = dict(status='passed', tool='Blender MCP', blender=bpy.app.version_string,
                  source=str(source.relative_to(ROOT)), source_sha256=source_hash,
                  coordinate_transform='(x,y,z) glTF -> (x,-z,y) Blender',
                  bones=len(trees), records_checked=len(records),
                  maximum_distance_mm=max(row['distance_mm'] for row in records),
                  scope='Surface-distance and import regression only; no new anatomical coordinate or extent acceptance.',
                  source_unchanged=True, meshes=meshes, records=records)
finally:
    bpy.context.window.scene = original_scene
    for obj in list(bpy.data.objects):
        if obj.as_pointer() not in original_objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.scenes.remove(scene)

assert {obj.as_pointer() for obj in bpy.data.objects} == original_objects
report['original_scene_objects_preserved'] = True
out = ROOT / 'research/stage5-skull-2026-10-16/blender-head-anchors.json'
out.parent.mkdir(exist_ok=True, parents=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: report[key] for key in ('status', 'bones', 'records_checked',
                                            'maximum_distance_mm', 'source_unchanged',
                                            'original_scene_objects_preserved')}))
