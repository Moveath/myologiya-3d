"""Background Blender: reduce left BP3D muscle STLs to the face budget of the accepted right part.

blender -b --factory-startup --python scripts/blender_decimate_left_muscles.py -- RUN OUT [CACHE]
Source millimetre coordinates are kept (no axis change, reflection or fitting); only collapse
decimation is applied, matching the browser simplification already used for the right side.
CACHE defaults to the left limb muscle sources; the left soft tissues pass their own cache.
Rows name their file by leftFMA (left limb pipelines) or fma (abdominal muscles, both sides,
whose budget is the default muscle rule of build_glb.py); the output keeps the row's own keys.
"""
import bmesh
import bpy
import json
import numpy as np
import sys
from pathlib import Path

args = sys.argv[sys.argv.index('--') + 1:]
run, out = (Path(a).resolve() for a in args[:2])
root = Path(__file__).resolve().parents[1]
cache = Path(args[2]).resolve() if len(args) > 2 else root / 'research/cache/left-limb-muscles'
out.mkdir(parents=True, exist_ok=True)
rows, results = json.loads((run / 'decimation-targets.json').read_text(encoding='utf8')), []
for row in rows:
    fma = row.get('fma') or row['leftFMA']
    target = out / (fma + '.npz')
    if target.exists():
        raise FileExistsError(target)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=str(cache / (fma + '.stl')),
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
    ident = dict(fma=fma, id=row['id']) if 'fma' in row else dict(leftFMA=fma, left=row['left'])
    results.append(dict(ident, part=row['part'], sourceTriangles=row.get('sourceTriangles', row.get('leftSourceTriangles')),
                        weldedFaces=welded, target=row['target'], ratio=modifier.ratio, triangles=int(len(faces)),
                        vertices=int(len(vertices)), output=target.relative_to(root).as_posix()))
with (run / 'blender-decimation.json').open('x', encoding='utf8') as f:
    json.dump(dict(blender=bpy.app.version_string, method='STL import (Y forward, Z up, scale 1) -> exact weld 1e-4 mm -> Decimate COLLAPSE (triangulate) to the target face count of decimation-targets.json',
                   rows=results), f, ensure_ascii=False, indent=1)
print(json.dumps(dict(parts=len(results), triangles=sum(r['triangles'] for r in results))))
