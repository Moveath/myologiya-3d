"""Bounded names/types check for the unresolved 12 muscles and 17 parts."""
import bpy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'research/evidence-runs/stage7-targeted-muscle-sources-2026-10-22T07-14-12-363Z-LR6EiF'
SOURCE=ROOT/'research/cache/stage7-z-muscles-04d15340/Z-Anatomy-Startup.blend'
terms=['auricular','depressor supercili','transversus ment','mentalis','sternalis',
       'subcost','intertransvers','orbicularis oculi','riolan','ciliar','nasalis',
       'orbicularis oris','diaphragm','multifid','rotatores']
with bpy.data.libraries.load(str(SOURCE),link=False)as(src,dst):
    dst.objects=[n for n in src.objects if any(t in n.lower() for t in terms)]
rows=[]
for obj in dst.objects:
    if obj is None:continue
    r={'name':obj.name,'type':obj.type}
    if obj.type=='MESH':
        obj.data.calc_loop_triangles()
        r.update(vertices=len(obj.data.vertices),polygons=len(obj.data.polygons),
                 triangles=len(obj.data.loop_triangles),
                 materials=[m.name if m else None for m in obj.data.materials],
                 vertex_groups=[g.name for g in obj.vertex_groups])
    rows.append(r)
with(RUN/'z-remaining-name-types.json').open('x',encoding='utf8')as f:
    json.dump({'terms':terms,'source':str(SOURCE.relative_to(ROOT)),
      'objects':rows,'note':'A group, label, definition text, vessel or insertion marker is not an individual missing muscle mesh.'},f,ensure_ascii=False,indent=2)
print(json.dumps([r for r in rows if any(x in r['name'].lower()for x in ['auricular','depressor supercili','subcost','intertransvers','orbicularis oculi','sternalis','menti'])],ensure_ascii=False))
