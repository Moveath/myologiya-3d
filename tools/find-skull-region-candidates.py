"""Enumerate source-edge silhouette cycles, NOT anatomical acceptance.

No pin coordinates, interpolation, or smoothing. All outputs are immutable run evidence.
"""
import json, sys
from pathlib import Path
import numpy as np
import trimesh

def cycles(edges):
    graph={}
    for a,b in edges:
        graph.setdefault(int(a),set()).add(int(b)); graph.setdefault(int(b),set()).add(int(a))
    result=[];remaining=set(graph)
    while remaining:
        root=min(remaining);stack=[root];pred={root:root};used={root:set()}
        while stack:
            z=stack.pop();zused=used[z]
            for nbr in sorted(graph[z]):
                if nbr not in used:
                    pred[nbr]=z;stack.append(nbr);used[nbr]={z}
                elif nbr not in zused:
                    pn=used[nbr];cycle=[nbr,z];p=pred[z]
                    while p not in pn:cycle.append(p);p=pred[p]
                    cycle.append(p);result.append(cycle);used[nbr].add(z)
        remaining-=set(pred)
    return result

def main():
    run=Path(sys.argv[1]);data=json.loads((run/'head-glb-source.json').read_text(encoding='utf8'))
    out=[];inventory=[]
    for r in data['rows']:
        v=np.array(r['positions']).reshape(-1,3);f=np.array(r['indices']).reshape(-1,3)
        mesh=trimesh.Trimesh(v,f,process=False)
        inventory.append(dict(bone=r['bone'],vertices=len(v),faces=len(f),components=len(mesh.split(only_watertight=False)),watertight=mesh.is_watertight,winding=mesh.is_winding_consistent,euler=mesh.euler_number,materials=r['materials']))
        for label,d in [('inferior',[0,-1,0]),('anterior',[0,0,1]),('lateral',[1,0,0]),('oblique',[1,.3,-1])]:
            a=mesh.face_adjacency;sign=mesh.face_normals@np.array(d)>=0
            edges=mesh.face_adjacency_edges[sign[a[:,0]]!=sign[a[:,1]]]
            for loop in cycles(edges):
                if not 8<=len(loop)<=240:continue
                p=v[loop];bbox=[p.min(0).tolist(),p.max(0).tolist()]
                out.append(dict(id=f'{r["bone"]}-{label}-{len(out)}',bone=r['bone'],view=d,edges=[[loop[i],loop[(i+1)%len(loop)]] for i in range(len(loop))],bounds=bbox,center=p.mean(0).tolist()))
    for name,value in [('geometry-inventory.json',inventory),('candidate-cycles.json',out)]:
        with (run/name).open('x',encoding='utf8') as stream:json.dump(value,stream)
    print(json.dumps(inventory))
    print('Cycles saved for review:',len(out))
if __name__=='__main__':main()
