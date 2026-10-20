"""Resolve each missing owner against source manifests, not inferred geometry."""
import json
import pathlib
import sys
import os
from collections import Counter

root=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"scripts"))
from manifest import BONES as ARM
from manifest_leg import BONES as LEG

run=pathlib.Path(sys.argv[1])
read=lambda n:json.loads((run/n).read_text(encoding="utf8"))
owners=read("missing-owners.json")
names=dict(line.split("\t",1) for line in (root/"bp/all_named.tsv").read_text(encoding="utf8").splitlines())
official=dict(line.split("\t",1) for line in (run/"official-3.0-parts.txt").read_text(encoding="utf8").splitlines()[1:])
name_ids={name:id for id,name in official.items()}
entries={pathlib.PurePosixPath(x["name"]).stem:x for x in read("official-archive-index.json")["entries"] if x["name"].endswith(".obj")}
tree=read("bp3d-mirror-tree.json")
mirror={pathlib.PurePosixPath(x["path"]).stem:x["path"] for x in tree["tree"] if x["path"].endswith(".stl")}
maps={**ARM,**LEG}
rows=[]
for b in owners:
    id=b["id"]
    base=id.removesuffix("_left")
    if id.startswith("sesamoid_mcp1_"):
        fma=None
        issue="GEO-HAND-LEFT-MODELS" if id.endswith("_left") else "GEO-HAND-MCP1-"+("R" if "_radial_" in id else "U")
    else:
        right=maps[base][0]
        fma=name_ids.get(names[right].replace("right","left"))
        assert fma is not None,(id,names[right])
        assert fma in entries,(id,fma)
        if base in ("radius","ulna"):issue="GEO-UPPER-LEFT-FOREARM"
        elif base in ("femur","patella","tibia","fibula"):issue="GEO-LOWER-LEFT-PROXIMAL"
        elif base in LEG:issue="GEO-LOWER-LEFT-FOOT"
        else:issue="GEO-HAND-LEFT-MODELS"
    row=dict(id=id,issue=issue,label=b["ru"],side="left" if id.endswith("_left") else "right",noModel=True,
             sourceId=fma,sourceName=official.get(fma),archiveEntry=entries.get(fma),
             officialArchive=read("official-archive-index.json")["url"] if fma else None,
             mirrorUrl=f"https://raw.githubusercontent.com/Kevin-Mattheus-Moerman/BodyParts3D/{tree['sha']}/{mirror[fma]}" if fma in mirror else None,
             provenance="DBCLS / BodyParts3D 3.0 (20110915); STL conversion Kevin-Mattheus-Moerman" if fma else "No accepted source in checked BodyParts3D/Z-Anatomy skeletal release",
             license="Version README: CC BY-SA 2.1 Japan; archive currently CC BY 4.0; preserve historical attribution/SA until release terms reconciled" if fma else "Not established: do not distribute a candidate without explicit rights",
             commercial="Allowed under stated CC BY-SA conditions; preserve attribution/license/change notice, not a blanket clearance of all project assets" if fma else "No accepted commercial-use source",
             confidence="Named authored left source; not proof of independent specimen segmentation or anatomical acceptance" if fma else "Anatomical card confirmed earlier; source mesh not established",
             inspection="Downloaded OBJ + Blender + trimesh" if base in ("radius","ulna") else "Archive entry/official name verified; shape/topology/registration pending" if fma else "No named thumb sesamoid in checked sources; absence elsewhere not claimed",
             transform="(x,y,z)=(bp.x,bp.z,-bp.y)/1000; preserve source origin, no mirroring" if fma else "To be determined from licensed source acquisition; never inherit opposite-side pins",
             checks="Verify named side, landmark morphology, scale/axes, adjacency, normals/degeneracy/self-intersections; preserve all source faces; GLB round-trip/IDs/bounds/BVH and mobile selection",
             integration="Separate derivative asset after specimen/placement acceptance; no application change in 6.1" if fma else "Blocked until identifiable source/segmentation and side-specific evidence",
             recovery="Use authored source, no reconstruction needed for whole-bone pilot" if fma else "Seek licensed CT/micro-CT with visible ossicles and segmentation; document voxel size and manual mask review. Blender Python may convert/smooth a reviewed mask, never invent a generic ellipsoid. Mark approximation educational.",
             blocker="Surface/coordinate acceptance and integration remain open" if fma else "No identifiable licensed side-specific MCP-I sesamoid mesh/volume in inspected sources")
    if base=="sesamoid_pedis":
        row["checks"]+="; aggregate contains sesamoids: resolve medial/lateral components by local anatomy, not global X; do not count one file as one individual bone"
    rows.append(row)
assert len(rows)==64 and len({r["id"] for r in rows})==64
source_ids={r["sourceId"] for r in rows if r["sourceId"]}
local=[]
for folder,dirs,files in os.walk(root):
    dirs[:]=[d for d in dirs if d not in {".git",".venv","node_modules","free-claude-code","publish","cache"}]
    for name in files:
        p=pathlib.Path(folder)/name
        if p.stem in source_ids and p.suffix.lower() in {".obj",".stl",".ply",".fbx",".glb",".gltf"}:
            local.append(dict(file=p.relative_to(root).as_posix(),bytes=p.stat().st_size))
result=dict(cards=64,officialCandidates=sum(bool(r["sourceId"]) for r in rows),
            distinctOfficialEntries=len(source_ids),withoutNamedSource=[r["id"] for r in rows if not r["sourceId"]],
            localNamedSourcesOutsideResearchCache=local,groups=dict(Counter(r["issue"] for r in rows)),rows=rows)
with (run/"source-matrix.json").open("x",encoding="utf8") as out:json.dump(result,out,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!="rows"},ensure_ascii=False))
