"""Background Blender: reduce left BP3D muscle STLs to the face budget of the accepted right part.

blender -b --factory-startup --python scripts/blender_decimate_left_muscles.py -- RUN OUT
Source millimetre coordinates are kept (no axis change, reflection or fitting); only collapse
decimation is applied, matching the browser simplification already used for the right side.
"""
import bmesh
import bpy
import json
import numpy as np
import sys
from pathlib import Path

run, out = (Path(a).resolve() for a in sys.argv[sys.argv.index('--') + 1:][:2])
root = Path(__file__).resolve().parents[1]
out.mkdir(parents=True, exist_ok=True)
rows, results = json.loads((run / 'decimation-targets.json').read_text(encoding='utf8')), []
for row in rows:
    target = out / (row['leftFMA'] + '.npz')
    if target.exists():
        raise FileExistsError(target)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=str(root / 'research/cache/left-limb-muscles' / (row['leftFMA'] + '.stl')),
                          forward_axis='Y', up_axis='Z', global_scale=1.0)
    obj = bpy.context.selected_objects[0]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # Exact-coincidence weld only (STL stores corners per facet); 1e-4 mm cannot merge distinct vertices.
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.to_mesh(obj.data)
    bm.free()
    welded = len(obj.data.polygons)
    modifier = obj.modifiers.new('reduce', 'DECIMATE')
    modifier.decimate_type = 'COLLAPSE'
    modifier.ratio = min(1.0, row['target'] / welded)
    modifier.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier='reduce')
    mesh = obj.data
    mesh.calc_loop_triangles()
    vertices = np.array([v.co[:] for v in mesh.vertices], dtype=np.float64)
    faces = np.array([t.vertices[:] for t in mesh.loop_triangles], dtype=np.int64)
    np.savez(target, vertices=vertices, faces=faces)
    results.append(dict(leftFMA=row['leftFMA'], left=row['left'], part=row['part'], sourceTriangles=row['leftSourceTriangles'],
                        weldedFaces=welded, target=row['target'], ratio=modifier.ratio, triangles=int(len(faces)),
                        vertices=int(len(vertices)), output=target.relative_to(root).as_posix()))
with (run / 'blender-decimation.json').open('x', encoding='utf8') as f:
    json.dump(dict(blender=bpy.app.version_string, method='STL import (Y forward, Z up, scale 1) -> exact weld 1e-4 mm -> Decimate COLLAPSE (triangulate) to right-part face count',
                   rows=results), f, ensure_ascii=False, indent=1)
print(json.dumps(dict(parts=len(results), triangles=sum(r['triangles'] for r in results))))
