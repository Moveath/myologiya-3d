"""Targeted native-source inspection jobs for already licensed acquired skulls."""
from temporal_variant_inspect import ROOT,OUT
import json,hashlib
QUEUE=OUT/'other-jobs';QUEUE.mkdir(exist_ok=True)
NODES={'01_male-cranial_maxilla':1.790,'02_female-cranial_maxilla':1.647,'nih-002448':.040}
views={'inf':{'d':[0,-1,0],'up':[0,0,1]},'xlow':{'d':[-1,0,0],'up':[0,1,0]},'xhigh':{'d':[1,0,0],'up':[0,1,0]},'internal':{'d':[0,1,0],'up':[0,0,-1]}}
rows=[]
for node,cut in NODES.items():
    for view,v in views.items():
        key=node+'-'+view
        code="window.__variantOriginalGeometry ||= {}; let m=__meshes["+json.dumps(node)+"]; window.__variantOriginalGeometry["+json.dumps(node)+"] ||= m.geometry; m.geometry=window.__variantOriginalGeometry["+json.dumps(node)+"]; "
        if view=='internal':
            code+='let g=m.geometry.clone(), p=g.attributes.position, idx=g.index.array, kept=[]; for(let i=0;i<idx.length;i+=3){if([idx[i],idx[i+1],idx[i+2]].every(n=>p.getY(n)<'+str(cut)+')) kept.push(idx[i],idx[i+1],idx[i+2]);}g.setIndex(kept);m.geometry=g;'
        code+='show('+json.dumps(node)+','+json.dumps(v)+','+json.dumps(node+' '+view+'; review only')+');true'
        (QUEUE/(key+'.job')).write_text(code,encoding='utf-8')
        rows.append({'node':node,'view':v,'key':view,'clipping':{'viewer_y_upper_m':cut,'method':'Keep only existing triangles with all vertices below limit; no caps.'} if view=='internal' else None,'screenshot':str((QUEUE/(key+'.png')).relative_to(ROOT)).replace('\\','/')})
source=ROOT/'research/cache/new-skull/review.glb'
(OUT/'other-review-inputs.json').write_text(json.dumps({'mesh':str(source.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'views':rows},indent=2),encoding='utf-8')
