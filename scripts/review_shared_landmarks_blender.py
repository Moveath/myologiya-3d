"""Run inside Blender via MCP; writes measurements, never approves new anatomy.

Execute with __file__ set to this script's path. Imports a disposable decoded
copy into a separate scene, preserves the original scene and all source files.
The curated acceptance and screenshots remain in research/shared-landmarks-geometry.json.
"""
import base64
import hashlib
import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
review = json.loads((ROOT / 'research/shared-landmarks-geometry.json').read_text(encoding='utf-8'))
source = ROOT / review['source']
before = hashlib.sha256(source.read_bytes()).hexdigest()
assert before == review['sourceSha256'], 'Source changed; repeat the visual/anatomical review'
original_scene = bpy.context.scene
scene = bpy.data.scenes.new('Shared landmark measurement')
bpy.context.window.scene = scene


def bone_id(obj):
    while obj:
        if obj.name.startswith('b|'):
            return obj.name.split('|')[1].split('.')[0]
        obj = obj.parent
    return None


try:
    with tempfile.TemporaryDirectory(prefix='atlas-shared-review-') as directory:
        copy = Path(directory) / 'review.glb'
        copy.write_bytes(base64.b64decode(source.read_bytes()))
        with redirect_stdout(io.StringIO()):
            bpy.ops.import_scene.gltf(filepath=str(copy))
    bpy.context.view_layer.update()
    trees = {}
    for obj in scene.objects:
        bone = bone_id(obj)
        if obj.type == 'MESH' and bone in review['bones']:
            trees.setdefault(bone, []).append(BVHTree.FromPolygons(
                [obj.matrix_world @ v.co for v in obj.data.vertices],
                [list(p.vertices) for p in obj.data.polygons], all_triangles=True))
    results = []
    for pin in review['candidates']:
        x, y, z = pin['p']
        point = Vector((x, -z, y))  # Three.js Y-up -> Blender Z-up, exactly once.
        distances = {bone: min(t.find_nearest(point)[3] for t in ts) * 1000 for bone, ts in trees.items()}
        assert distances[pin['bone']] < 0.01, pin['sourcePin']
        results.append(dict(sourcePin=pin['sourcePin'], distanceMm=distances))
    assert before == hashlib.sha256(source.read_bytes()).hexdigest()
    report = dict(status='passed', tool='Blender MCP', blender=bpy.app.version_string,
                  source=review['source'], sourceSha256=before, sourceUnchanged=True,
                  method=review['method'], coordinateTransform=review['coordinateTransform'],
                  scope='Surface-distance regression only; not independent anatomical acceptance', results=results)
    (ROOT / 'verify/shared-landmark-blender-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))
finally:
    bpy.context.window.scene = original_scene
