async (page) => {
 await page.goto('http://127.0.0.1:8782/local.html?theme=light',{waitUntil:'networkidle'});
 const rows=await page.evaluate(async names=>{
  const {GLTFLoader}=await import('/vendor/three/examples/jsm/loaders/GLTFLoader.js');
  const {MeshoptDecoder}=await import('/vendor/three/examples/jsm/libs/meshopt_decoder.module.js');
  const loader=new GLTFLoader().setMeshoptDecoder(MeshoptDecoder),rows=[];
  for(const name of names){
   const response=await fetch('/'+name);if(!response.ok)throw Error(name+': '+response.status);
   let bytes;if(name.endsWith('.txt')){const raw=atob(await response.text());bytes=Uint8Array.from(raw,c=>c.charCodeAt(0)).buffer}else bytes=await response.arrayBuffer();
   const gltf=await loader.parseAsync(bytes,location.origin+'/');let meshes=0,triangles=0;const textures=new Set(),materials=new Set();
   gltf.scene.traverse(o=>{if(!o.isMesh)return;meshes++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;
    for(const m of Array.isArray(o.material)?o.material:[o.material]){materials.add(m);for(const value of Object.values(m))if(value?.isTexture)textures.add(value)}
    o.geometry.dispose();
   });
   rows.push({file:name,status:'loaded',meshes,triangles,textures:textures.size});
   for(const t of textures){t.image?.close?.();t.dispose()}for(const m of materials)m.dispose();
  }return rows;
 },["arm-glb.txt","leg-glb.txt","head-glb.txt","neck-glb.txt","thorax-glb.txt","arm-extra-glb.txt","leg-extra-glb.txt","arm-q-glb.txt","leg-q-glb.txt","head-q-glb.txt","neck-q-glb.txt","thorax-q-glb.txt","arm-extra-q-glb.txt","leg-extra-q-glb.txt","skull-z-detail.glb","skull-educational-bones.glb","skull-muscle-reconstructions.glb","skull-microct.glb","skull-openear.glb","skull-cranial-channels-context.glb","skull-cranial-channels.glb","skull-temporal-channels-context.glb","skull-temporal-channels.glb"]);
 if(rows.length!==23)throw Error('Missing packages');
 return {status:'passed',scope:'Browser GLTF parsing and image decoding; no claim of visual or anatomical acceptance',assets:rows};
}
