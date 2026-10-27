"""Read-only export of Z-Anatomy cardiovascular objects and reference bones (CV-GEO-MISSING, LOG-20261026-03).

Run in background Blender:
  blender -b --factory-startup --python scripts/export_z_cardiovascular.py -- OUT.json
Scripts embedded in the .blend are not executed. Meshes are exported in Blender world space as stored;
vessel curves are exported twice: as their authored centreline (control points, radii, bevel settings) and as
the surface Blender evaluates from that curve. No vertex is edited, smoothed, decimated or re-fitted here.
"""
import json
import sys
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/cache/stage7-z-muscles-04d15340/Z-Anatomy-Startup.blend'
out = Path(sys.argv[sys.argv.index('--') + 1])
HEART = ['Left atrium', 'Left ventricle', 'Right atrium', 'Right ventricle', 'Left coronary leaflet', 'Right coronary leaflet',
         'Non-coronary leaflet', 'Pulmonary trunk', 'Anterior papillary muscle of right ventricle', 'Inferior papillary muscle of right ventricle',
         'Septal papillary muscle of right ventricle', 'Inferior papillary muscle of left ventricle',
         'Posterior leaflet of left atrioventricular valve', 'Septal leaflet of right atrioventricular valve',
         'Inferior leaflet of right atrioventricular valve', 'Anterior semilunar leaflet of pulmonary valve',
         'Left semilunar leaflet of pulmonary valve', 'Right semilunar leaflet of pulmonary valve']
VESSELS = ['Ascending aorta', 'Thoracic aorta', 'Abdominal aorta', 'Brachiocephalic trunk', 'Coronary sinus', 'Great cardiac vein',
           'Middle cardiac vein', 'Azygos vein', 'Hemi-azygos vein', 'Accessory hemi-azygos vein', 'Hepatic portal vein',
           'Inferior vena cava (abdominal part)', 'Inferior vena cava (thoracic part)', 'Right brachiocephalic vein', 'Left brachiocephalic vein',
           'Right pulmonary artery', 'Left pulmonary artery', 'Bifurcation of pulmonary trunk']
for side in ('l', 'r'):
    VESSELS += [f'{n}.{side}' for n in ('Axillary artery', 'Brachial artery', 'Radial artery', 'Ulnar artery', 'Femoral artery', 'Popliteal artery',
                                         'Anterior tibial artery', 'Posterior tibial artery', 'Fibular artery', 'Axillary vein', 'Cephalic vein',
                                         'Basilic vein', 'Brachial veins', 'Femoral vein', 'Popliteal vein', 'Great saphenous vein', 'Small saphenous vein',
                                         'Subclavian artery', 'Subclavian vein', 'Common carotid artery', 'Internal jugular vein',
                                         'Common iliac artery', 'External iliac artery', 'Internal iliac artery', 'Common iliac vein',
                                         'External iliac vein', 'Internal iliac vein', 'Renal artery', 'Renal vein', 'Deep femoral artery',
                                         'Deep brachial artery', 'Anterior tibial veins', 'Posterior tibial veins', 'Fibular veins')]
ORD = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth', 'Eleventh', 'Twelfth']
BONES = ['Body of sternum', 'Manubrium of sternum', 'Sacrum']
for side in ('l', 'r'):
    BONES += [f'{n}.{side}' for n in ('Humerus', 'Radius', 'Ulna', 'Clavicle', 'Scapula', 'Femur', 'Tibia', 'Fibula', 'Hip bone',
                                      'Talus', 'Calcaneus', 'Navicular bone', 'Cuboid bone', 'Medial cuneiform bone', 'First metatarsal bone',
                                      'Scaphoid bone', 'Lunate bone', 'Triquetrum bone', 'Pisiform bone', 'Trapezium bone', 'Hamate bone',
                                      'Capitate bone', 'First metacarpal bone', 'Second metacarpal bone', 'Fifth metacarpal bone')]
    BONES += [f'{o} rib.{side}' for o in ORD]

bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
depsgraph = bpy.context.evaluated_depsgraph_get()


def mesh_record(obj):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    m = obj.matrix_world
    record = dict(vertices=[[round(c, 6) for c in (m @ v.co)] for v in mesh.vertices],
                  faces=[list(t.vertices) for t in mesh.loop_triangles])
    evaluated.to_mesh_clear()
    return record


rows, missing = {}, []
for name in HEART + VESSELS + BONES:
    obj = bpy.data.objects.get(name)
    if obj is None:
        missing.append(name)
        continue
    row = dict(type=obj.type, collections=[c.name for c in obj.users_collection], parent=obj.parent.name if obj.parent else None,
               determinant=obj.matrix_world.to_3x3().determinant())
    if obj.type == 'CURVE':
        c = obj.data
        row['curve'] = dict(bevel_depth=c.bevel_depth, bevel_resolution=c.bevel_resolution, bevel_mode=c.bevel_mode,
                            resolution_u=c.resolution_u, extrude=c.extrude, use_fill_caps=c.use_fill_caps,
                            taper=c.taper_object.name if c.taper_object else None, bevel_object=c.bevel_object.name if c.bevel_object else None,
                            modifiers=[md.type for md in obj.modifiers],
                            splines=[dict(type=s.type, cyclic=s.use_cyclic_u,
                                          points=[dict(co=[round(x, 6) for x in (obj.matrix_world @ (p.co.xyz if s.type != 'BEZIER' else p.co))],
                                                       radius=p.radius) for p in (s.bezier_points if s.type == 'BEZIER' else s.points)])
                                     for s in c.splines])
    row.update(mesh_record(obj))
    rows[name] = row
out.write_text(json.dumps(dict(source=str(SOURCE.relative_to(ROOT).as_posix()), blender=bpy.app.version_string, objects=rows, missing=missing),
                          ensure_ascii=False), encoding='utf8')
print(json.dumps(dict(exported=len(rows), missing=missing)))
