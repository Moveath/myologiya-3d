"""Render every muscle teaching diagram independently; preserve screenshots locally.

This is a technical visual review, never an anatomical expert acceptance.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qhead_muscle_reconstructions'
HTML='''<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#eaf0f1}canvas{display:block}#title{position:absolute;left:12px;top:8px;font:17px Arial}#labels{position:absolute;inset:0;pointer-events:none}.label{position:absolute;font:12px Arial;color:#253a45;background:#fffffff0;border:1px solid #a1b5be;border-radius:5px;padding:3px;max-width:160px;transform:translate(-50%,-50%)}</style><div id="title"></div><div id="labels"></div><script type="importmap">{"imports":{"three":"/site/vendor/three/build/three.module.js","three/addons/":"/site/vendor/three/examples/jsm/"}}</script><script type="module">
import * as THREE from 'three';import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const data=await(await fetch('/site/skull-muscle-reconstructions.json')).json();const gltf=await new GLTFLoader().loadAsync('/site/skull-muscle-reconstructions.glb');
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setSize(innerWidth,innerHeight);renderer.setClearColor(0xeaf0f1);document.body.appendChild(renderer.domElement);
const scene=new THREE.Scene();scene.add(gltf.scene);scene.add(new THREE.HemisphereLight(0xffffff,0x718198,2.5));const light=new THREE.DirectionalLight(0xffffff,2);light.position.set(3,4,6);scene.add(light);scene.add(new THREE.AmbientLight(0xffffff,.6));
const camera=new THREE.PerspectiveCamera(35,innerWidth/innerHeight,.01,100);
window.show=(id,alternate=false)=>{const e=data.entries.find(x=>x.id===id),visible=new Set([...e.nodes,...e.contextNodes]);gltf.scene.traverse(o=>{if(o.isMesh)o.visible=visible.has(o.name)});
 const box=new THREE.Box3();gltf.scene.traverse(o=>{if(o.isMesh&&o.visible)box.union(new THREE.Box3().setFromObject(o))});const center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());const d=new THREE.Vector3(...e.camera.position).sub(new THREE.Vector3(...e.camera.target)).normalize();if(alternate)d.x*=-1;
 const distance=Math.max(size.x/ camera.aspect,size.y,size.z)*2.5;camera.position.copy(center).addScaledVector(d,distance);camera.lookAt(center);camera.updateMatrixWorld();document.querySelector('#title').textContent=e.ru;document.querySelector('#labels').innerHTML='';for(const l of e.labels){const v=new THREE.Vector3(...l.p).project(camera);const el=document.createElement('div');el.className='label';el.textContent=l.ru;el.style.left=((v.x+1)*innerWidth/2)+'px';el.style.top=((-v.y+1)*innerHeight/2)+'px';document.querySelector('#labels').appendChild(el)}renderer.render(scene,camera);return {visible:[...visible],triangles:renderer.info.render.triangles};};window.ready=true;
</script>'''

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def main():
    OUT.mkdir(exist_ok=True)
    (OUT/'preview.html').write_text(HTML,encoding='utf-8')
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    data=json.loads((ROOT/'site/skull-muscle-reconstructions.json').read_text(encoding='utf-8'))
    cases=[]
    try:
        with sync_playwright() as p:
            executable=os.environ.get('ATLAS_CHROMIUM')
            if not executable:
                installed=sorted((Path(os.environ['LOCALAPPDATA'])/'ms-playwright').glob('chromium-*/chrome-win*/chrome.exe'))
                if installed:executable=str(installed[-1])
            browser=p.chromium.launch(headless=True,executable_path=executable,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
            page=browser.new_page(viewport=dict(width=700,height=550))
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/qhead_muscle_reconstructions/preview.html')
            page.wait_for_function('window.ready===true',timeout=60000)
            for e in data['entries']:
                if not e['nodes']:continue
                for alt in (False,True):
                    result=page.evaluate('([id,alt])=>window.show(id,alt)',[e['id'],alt])
                    assert result['triangles']>0,e['id']
                    file=OUT/(e['id']+('-alternate' if alt else '')+'.png')
                    page.screenshot(path=str(file))
                    cases.append(dict(id=e['id'],alternate=alt,screenshot=file.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),**result))
            assert not errors,errors
            browser.close()
    finally:server.shutdown();server.server_close()
    # Contact sheet is only a developer preview, never published as source anatomy.
    for alt in (False,True):
        thumbs=[]
        for c in cases:
            if c['alternate']!=alt:continue
            im=Image.open(ROOT/c['screenshot']).convert('RGB');im.thumbnail((350,275));thumbs.append(im)
        sheet=Image.new('RGB',(350*4,275*4),'white')
        for i,im in enumerate(thumbs):sheet.paste(im,(350*(i%4),275*(i//4)))
        sheet.save(OUT/('contact-sheet-alternate.jpg' if alt else 'contact-sheet.jpg'))
    report=ROOT/'research/muscle-reconstruction-review.json'
    review=json.loads(report.read_text(encoding='utf-8'))
    review['visual_review']=dict(status='rendered_pending_visual_inspection',views=len(cases),entries=16,
        method='All 16 independent entries rendered from saved and alternate camera. Isolated node sets, nonzero triangles, no page errors. Screenshots are developer artifacts; not source anatomy or external validation.',cases=cases)
    report.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(entries=16,views=len(cases),errors=errors,contact_sheet=str(OUT/'contact-sheet.jpg'))))

def shared_review():
    """Inspect integration against the actual shared site files."""
    OUT.mkdir(exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'site')))
    Thread(target=server.serve_forever,daemon=True).start()
    cases=[]
    with sync_playwright() as p:
        installed=sorted((Path(os.environ['LOCALAPPDATA'])/'ms-playwright').glob('chromium-*/chrome-win*/chrome.exe'))
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('ATLAS_CHROMIUM') or str(installed[-1]),args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        for width,theme in ((1280,'light'),(390,'dark')):
            page=browser.new_page(viewport=dict(width=width,height=900),color_scheme=theme)
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/skull-education.html?category=muscles&theme={theme}')
            page.wait_for_function('window.__education?.data')
            entries=page.evaluate('window.__education.data.entries.filter(e=>e.category==="muscles"&&e.models.length).map(e=>({id:e.id,models:e.models}))')
            assert len(entries)==16
            if '--alar-only' in sys.argv:
                entries=[e for e in entries if e['id'].endswith(('_alar',':alar'))]
                assert len(entries)==2
            for e in entries:
                page.evaluate('(id)=>window.__education.select(id)',e['id'])
                page.wait_for_function('window.__education?.viewer?.ready && !document.querySelector("#modelLoading").textContent')
                expected=e['models'][0]['nodes']+e['models'][0]['contextNodes']
                visible=page.evaluate('window.__education.viewer.visibleNames()')
                assert set(visible)==set(expected),e['id']
                page.locator('#viewport').scroll_into_view_if_needed()
                page.wait_for_timeout(70)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                file=OUT/(f'shared-{width}-{theme}-'+e['id'].replace(':','_')+'.png')
                page.locator('#modelSection').screenshot(path=str(file))
                cases.append(dict(id=e['id'],width=width,theme=theme,screenshot=file.relative_to(ROOT).as_posix(),visibleNodes=visible,sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
            assert not errors,errors
            page.close()
        browser.close()
    server.shutdown();server.server_close()
    for width in (1280,390):
        sheet=Image.new('RGB',(1400,1600),'white')
        for i,c in enumerate(x for x in cases if x['width']==width):
            im=Image.open(ROOT/c['screenshot']).convert('RGB');im.thumbnail((350,400));sheet.paste(im,(350*(i%4),400*(i//4)))
        sheet.save(OUT/(f'shared-{width}-contact'+('-alar.jpg' if '--alar-only' in sys.argv else '.jpg')))
    report=ROOT/'research/muscle-reconstruction-review.json'
    review=json.loads(report.read_text(encoding='utf-8'))
    if '--alar-only' in sys.argv:
        updated={(c['id'],c['width'],c['theme']) for c in cases}
        unchanged=[c for c in review.get('shared_ui_review',{}).get('cases',[]) if (c['id'],c['width'],c['theme']) not in updated]
        cases=unchanged+cases
    review['shared_ui_review']=dict(status='rendered_pending_visual_inspection',cases=cases)
    report.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(shared_views=len(cases),entries=16)))

if __name__=='__main__':
    if '--shared' in sys.argv:shared_review()
    else:main()
