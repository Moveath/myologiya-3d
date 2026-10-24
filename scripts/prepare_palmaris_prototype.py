"""Prepare an explicitly unadmitted lamina experiment; never write atlas data/pins.

The hand frame is measured, but the patch boundary and clearance are hypotheses.
This is not segmentation, an attachment map, or automatic anatomical admission.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from scipy.interpolate import RBFInterpolator

ROOT = Path(__file__).resolve().parents[1]

def write(path, data):
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def prepare(run, out, overrides=None):
    rows = json.loads((run/'hand-context.json').read_text())
    pts = {r['id']:np.asarray(r['positions']).reshape(-1,3) for r in rows}
    origin = pts['pisiform'].mean(0)
    distal = pts['metacarpal_5'].mean(0)-origin; distal /= np.linalg.norm(distal)
    radial = pts['metacarpal_2'].mean(0)-pts['metacarpal_5'].mean(0)
    radial -= distal*np.dot(radial,distal); radial /= np.linalg.norm(radial)
    palmar = np.cross(radial,distal); basis = np.stack((radial,distal,palmar),axis=1)
    assert np.linalg.det(basis) > .999 and palmar[2] > .9
    # Numerical test domain, NOT a measured origin/insertion/skin boundary.
    config = dict(radial_mm=[-11,10], distal_mm=[9,33], clearance_mm=1.0,
                  thickness_mm=.89, nu=32, nv=24, edge_taper=.12)
    if overrides:
        assert not (set(overrides)-set(config)), 'Unknown parameter'
        config.update(overrides)
    r0,r1=config['radial_mm']; d0,d1=config['distal_mm']
    assert r0<r1 and d0<d1 and 0<config['thickness_mm']<10
    assert 0<=config['edge_taper']<.5 and 0<=config['clearance_mm']<10
    assert all(isinstance(config[k],int) and 4<=config[k]<=128 for k in ['nu','nv'])
    support_ids=['abductor_digiti_minimi','flexor_digiti_minimi_brevis','opponens_digiti_minimi','flexor_retinaculum']
    triangles=[]
    for r in rows:
        if r['id'] in support_ids:
            local=(pts[r['id']]-origin)@basis*1000
            triangles.extend(local[np.asarray(r['indices']).reshape(-1,3)])
    tri=np.asarray(triangles); a=tri[:,0]; b=tri[:,1]-a; c=tri[:,2]-a
    det=b[:,0]*c[:,1]-b[:,1]*c[:,0]; good=np.abs(det)>1e-9
    def height(x,y):
        dx=x-a[:,0];dy=y-a[:,1]
        s=np.divide(dx*c[:,1]-dy*c[:,0],det,out=np.zeros_like(det),where=good)
        t=np.divide(b[:,0]*dy-b[:,1]*dx,det,out=np.zeros_like(det),where=good)
        mask=good&(s>=0)&(t>=0)&(s+t<=1)
        return float(np.max(a[mask,2]+s[mask]*b[mask,2]+t[mask]*c[mask,2])) if mask.any() else None
    uv=np.array([[x,y] for y in np.linspace(d0,d1,13) for x in np.linspace(r0,r1,17)])
    heights=[height(x,y) for x,y in uv]; ok=np.array([v is not None for v in heights])
    fit=RBFInterpolator(uv[ok],np.array([v for v in heights if v is not None]),kernel='thin_plate_spline',smoothing=2)
    nu,nv=config['nu'],config['nv']; local=[]; grid=[]
    for j in range(nv+1):
        v=j/nv
        for i in range(nu+1):
            u=i/nu
            # Rounded, tapered quadrilateral: a numerical family, not a traced border.
            width=(r1-r0)*(1-config['edge_taper']*(2*v-1)**2)
            x=(r0+r1)/2+(u-.5)*width; y=d0+(d1-d0)*v
            grid.append((x,y))
    top=fit(np.array(grid))
    # Fixed documented clearance; no fitting to remove detected intersections.
    for sign in [1,-1]:
        for (x,y),z in zip(grid,top):
            local.append([x,y,float(z)+config['clearance_mm']+sign*config['thickness_mm']/2])
    local=np.array(local); world=local/1000@basis.T+origin
    faces=[]; layer=(nu+1)*(nv+1)
    for j in range(nv):
        for i in range(nu):
            a0=j*(nu+1)+i; b0=a0+1; c0=a0+nu+2; d0=a0+nu+1
            faces.extend([[a0,b0,c0],[a0,c0,d0],[a0+layer,c0+layer,b0+layer],[a0+layer,d0+layer,c0+layer]])
    boundary=list(range(nu+1))+[j*(nu+1)+nu for j in range(1,nv+1)]+[nv*(nu+1)+i for i in range(nu-1,-1,-1)]+[j*(nu+1) for j in range(nv-1,0,-1)]
    for a0,b0 in zip(boundary,boundary[1:]+boundary[:1]):faces.extend([[a0,a0+layer,b0+layer],[a0,b0+layer,b0]])
    fibers=[world[j*(nu+1):(j+1)*(nu+1)].tolist() for j in range(3,nv,4)]
    out.mkdir(parents=True,exist_ok=False)
    spec=dict(schema=1,id='palmaris_brevis',issue='MG-palmaris_brevis',side='right',status='technical_prototype_not_admitted',
        notice='Тестовый прототип. Границы, глубина и прикрепления не подтверждены. Не учебно допущенная модель.',
        algorithm='Measured hand frame + RBF envelope of existing hypothenar/retinaculum surfaces + closed parametric lamina',
        source_context=str((run/'hand-context.json').relative_to(ROOT)).replace('\\','/'),
        context_sha256=hashlib.sha256((run/'hand-context.json').read_bytes()).hexdigest(),
        frame=dict(origin_m=origin.tolist(),basis_columns=basis.tolist(),axes=['radial','distal','palmar']),
        parameters=config,
        parameter_evidence={
          'thickness_mm':'0.89 mm is a cadaveric sample mean from Nam et al. 2022, PMID35037581 (30 hands, SD0.16). Applied only as a test extrusion, not a validated thickness of this subject.',
          'radial_mm/distal_mm/edge_taper/clearance_mm':'Explicit design assumptions. No anatomical measurement or pin. These values forbid automatic educational admission.',
          'frame':'Derived from world-space pisiform and metacarpal II/V vertex centroids. Not attachment coordinates.',
          'surface':'Envelope interpolation of adjacent meshes is a technical support surface, not skin, fascia, or palmaris brevis segmentation.',
          'fibers':'Schematic transverse direction only; no individual fascicles or histological reconstruction.'},
        support_ids=support_ids,support_samples=len(uv),support_hits=int(ok.sum()),
        unsupported_samples=uv[~ok].tolist(),
        blocking_requirements=['Skin deep boundary and ulnar insertion curve in the same hand frame',
          'Ulnar palmar-aponeurosis boundary and retinacular origin footprint',
          'Proximal/distal muscle outline and resting thickness map from registered ultrasound/MRI/dissection',
          'Anatomist review of relations to ulnar canal, skin and hypothenar muscles'],
        sources=['https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/TA98%20EN/04.6.02%20TA98%20EN.htm',
          'https://pubmed.ncbi.nlm.nih.gov/35037581/','https://pmc.ncbi.nlm.nih.gov/articles/PMC5696130/',
          'https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/anatomy-tables/muscle-tables/muscles-of-the-upper-limb/',
          'https://www.ncbi.nlm.nih.gov/books/NBK546622/'],
        provenance={'author':'Миология 3D — procedural research prototype, 2026',
          'context_author':'BodyParts3D 3.0, © DBCLS', 'license':'CC BY-SA 2.1 Japan',
          'license_url':'https://creativecommons.org/licenses/by-sa/2.1/jp/',
          'scope':'Conservative ShareAlike for prototype derived from context envelopes and context copies. No paper/reference images or meshes copied.'},
        positions=world.reshape(-1).tolist(),indices=np.asarray(faces).reshape(-1).tolist(),fibers=fibers)
    write(out/'recipe.json',spec)
    write(run/'preparation.json',{k:v for k,v in spec.items() if k not in ['positions','indices','fibers']})
    print(json.dumps(dict(vertices=len(world),triangles=len(faces),support_hits=int(ok.sum()),support_samples=len(uv),out=str(out))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('out');p.add_argument('--parameters');a=p.parse_args()
    overrides=json.loads((ROOT/a.parameters).read_text(encoding='utf8')) if a.parameters else None
    prepare((ROOT/a.run).resolve(),(ROOT/a.out).resolve(),overrides)
