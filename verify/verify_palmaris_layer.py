"""Addressed layer review of the saved prototype, without moving its vertices.

Directional envelope differences are not penetration distances or attachment maps.
The exact original triangles and the saved hand frame are used, not new landmarks.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]

def write(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

def review(build, run):
    spec = json.loads((build/'recipe.json').read_text(encoding='utf8'))
    context = ROOT/spec['source_context']
    assert hashlib.sha256(context.read_bytes()).hexdigest() == spec['context_sha256']
    rows = json.loads(context.read_text(encoding='utf8'))
    origin = np.array(spec['frame']['origin_m'])
    basis = np.array(spec['frame']['basis_columns'])
    points = np.array(spec['positions']).reshape(-1, 3)
    local = (points-origin)@basis*1000
    n = (spec['parameters']['nu']+1)*(spec['parameters']['nv']+1)
    checks = []
    def check(condition, name):
        assert condition, name
        checks.append(name)
    check(len(points) == 2*n, 'Two saved vertex layers identified')
    check(np.allclose(local[:n,:2], local[n:,:2]), 'Paired layers share local radial/distal positions')
    check(np.allclose(local[:n,2]-local[n:,2], spec['parameters']['thickness_mm']), 'Saved directional thickness retained')
    result = []
    envelopes = []
    for row in rows:
        if row['id'] not in spec['support_ids']:
            continue
        vertices = np.array(row['positions']).reshape(-1,3)
        faces = np.array(row['indices']).reshape(-1,3)
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        # Index seams do not represent physical holes. Report both exact and
        # coordinate-welded topology, without exporting or modifying the source.
        welded = mesh.copy()
        welded.merge_vertices(digits_vertex=9)
        tri = ((vertices-origin)@basis*1000)[faces]
        a = tri[:,0]; b = tri[:,1]-a; c = tri[:,2]-a
        det = b[:,0]*c[:,1]-b[:,1]*c[:,0]
        valid = np.abs(det)>1e-9
        heights = np.full(n, np.nan)
        for j, (x,y,_) in enumerate(local[:n]):
            dx=x-a[:,0]; dy=y-a[:,1]
            u=np.divide(dx*c[:,1]-dy*c[:,0],det,out=np.zeros_like(det),where=valid)
            v=np.divide(b[:,0]*dy-b[:,1]*dx,det,out=np.zeros_like(det),where=valid)
            hit=valid&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)
            if hit.any():
                heights[j]=np.max(a[hit,2]+u[hit]*b[hit,2]+v[hit]*c[hit,2])
        envelopes.append(heights)
        hit=np.isfinite(heights)
        bottom=local[n:,2]-heights
        top=local[:n,2]-heights
        result.append(dict(id=row['id'], name=row['name'], triangles=len(faces),
            raw_watertight=bool(mesh.is_watertight), welded_watertight=bool(welded.is_watertight),
            winding_consistent=bool(welded.is_winding_consistent), volume_mm3=float(welded.volume*1e9),
            supported_grid_vertices=int(hit.sum()), bottom_below_envelope=int((bottom < -1e-5).sum()),
            both_layers_below_envelope=int((top < -1e-5).sum()),
            max_directional_bottom_shortfall_mm=float(max(0,-np.nanmin(bottom))),
            max_directional_top_shortfall_mm=float(max(0,-np.nanmin(top))),
            examples=[dict(grid_index=int(j), local_radial_distal_mm=local[j,:2].tolist(),
                           bottom_gap_mm=float(bottom[j]),top_gap_mm=float(top[j]))
                      for j in np.argsort(np.nan_to_num(top,nan=np.inf))[:5]]))
    e=np.array(envelopes)
    supported=np.isfinite(e).any(axis=0)
    highest=np.max(np.where(np.isfinite(e),e,-np.inf),axis=0)
    check(len(result)==4, 'All four support meshes reviewed')
    check(np.isfinite(local).all(), 'Finite unchanged coordinates')
    check(np.allclose(basis.T@basis,np.eye(3)), 'Saved frame remains orthonormal')
    sources={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
             for p in [context,build/'recipe.json',build/'palmaris_brevis-trial.glb',ROOT/'site/arm-glb.txt']}
    output=dict(status='passed',checks=checks,method='Exact directional triangle-envelope query at all saved paired grid vertices; topology on a diagnostic coordinate-welded copy. Not a volume fraction or anatomical boundary.',
        hashes=sources,grid_vertices_per_layer=n,unsupported_grid_vertices=int((~supported).sum()),
        envelope_bottom_shortfall_count=int(((local[n:,2]-highest < -1e-5)&supported).sum()),
        envelope_both_layers_below_count=int(((local[:n,2]-highest < -1e-5)&supported).sum()),
        surfaces=result,anatomical_admission=False)
    write(run/'layer-review.json',output)
    print(json.dumps({k:v for k,v in output.items() if k not in ['hashes','method','surfaces']}))
    print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('build'); p.add_argument('run'); a=p.parse_args()
    review((ROOT/a.build).resolve(),(ROOT/a.run).resolve())
