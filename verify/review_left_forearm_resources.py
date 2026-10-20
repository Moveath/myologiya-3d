"""Read-only GLB identity inventory, plus world-space trimesh arm inventory."""
import base64, hashlib, io, json, re, struct, sys
from pathlib import Path
import trimesh
ROOT = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]).resolve()
assert out.is_relative_to(ROOT/'research/evidence-runs') and out.is_dir()
files = sorted(p for p in ROOT.rglob('*') if p.is_file() and
    (p.suffix.lower()=='.glb' or p.name.endswith('-glb.txt')) and
    not any(x in p.parts for x in ('node_modules','.venv','evidence-runs','.git')))
rows=[]
for p in files:
    raw=p.read_bytes(); data=base64.b64decode(raw) if p.suffix=='.txt' else raw
    assert data[:4]==b'glTF',p
    size,kind=struct.unpack_from('<II',data,12); assert kind==0x4e4f534a
    doc=json.loads(data[20:20+size]); nodes=doc.get('nodes',[])
    parents={c:i for i,n in enumerate(nodes) for c in n.get('children',[])}
    names=[n.get('name','') for n in nodes]
    matches=[n for n in names if re.search(r'23465|23468|radius[_ -]?left|ulna[_ -]?left|left.*(?:radius|ulna)|(?:radius|ulna).*left',n,re.I)]
    anonymous=[]
    for i,n in enumerate(nodes):
        if 'mesh' not in n:continue
        cur=i; ancestry=[]
        while True:
            ancestry.append(nodes[cur].get('name',''))
            if cur not in parents:break
            cur=parents[cur]
        if not any(re.match(r'^[bmoc]\|',v) for v in ancestry):anonymous.append(dict(node=i,ancestry=ancestry,mesh=n['mesh']))
    rows.append(dict(file=str(p.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),nodes=len(nodes),
        meshes=len(doc.get('meshes',[])),matches=matches,anonymousMeshNodes=anonymous,names=names))
inventory=[]
for file in ('site/arm-q-glb.txt','build_context_bones/arm_extra_hi.glb'):
    raw=(ROOT/file).read_bytes(); data=base64.b64decode(raw) if file.endswith('.txt') else raw
    scene=trimesh.load(io.BytesIO(data),file_type='glb',process=False,force='scene')
    for name in scene.graph.nodes_geometry:
        matrix,key=scene.graph[name]; mesh=scene.geometry[key]; bounds=trimesh.transform_points(mesh.vertices,matrix)
        cur=name; chain=[]
        while cur is not None:
            chain.append(str(cur));cur=scene.graph.transforms.parents.get(cur)
        inventory.append(dict(file=file,node=str(name),ancestry=chain,vertices=len(mesh.vertices),faces=len(mesh.faces),
            boundsM=[bounds.min(axis=0).tolist(),bounds.max(axis=0).tolist()]))
source_files=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and re.search(r'23465|23468',p.name)]
result=dict(resources=rows,trimeshMeshes=inventory,matchingSourceFiles=source_files,
    limits='Dictionary identity or surface bounds are not anatomical identification. Anonymous geometry is not approved for reuse. No reconstruction or reflection.')
with (out/'left-forearm-resources.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(resources=len(rows),uniqueHashes=len({r['sha256'] for r in rows}),matches=sum(len(r['matches']) for r in rows),
    trimeshMeshes=len(inventory),matchingSourceFiles=source_files)))
