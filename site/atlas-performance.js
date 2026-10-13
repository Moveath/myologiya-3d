import {MeshBVH, acceleratedRaycast} from './vendor/three-mesh-bvh/build/index.module.js';

// An acceleration index only: indirect mode preserves every vertex, triangle and
// original index/face ID. No simplification, remeshing or anatomical changes.
export async function prepareRaycasts(root) {
  const meshes=[];
  root.traverse(mesh=>{if(mesh.isMesh&&!mesh.isSkinnedMesh&&!mesh.morphTargetInfluences?.length)meshes.push(mesh);});
  let sliceStart=performance.now();
  for(const mesh of meshes) {
    const geometry=mesh.geometry;
    if(!geometry.boundsTree)geometry.boundsTree=new MeshBVH(geometry,{indirect:true,maxLeafTris:10});
    mesh.raycast=acceleratedRaycast;
    // Let the loading UI paint between large bones; one index is reused on return.
    if(performance.now()-sliceStart>8){await new Promise(resolve=>setTimeout(resolve,0));sliceStart=performance.now();}
  }
}

// Reduce raster work only while the camera moves; restore the original crisp
// image when it settles. Triangle data, markers, camera and canvas CSS never change.
export function createRenderQuality(renderer) {
  let lastMotion=-Infinity,previous=0,samples=0,total=0,pending=false;
  let motionRatio=Math.min(devicePixelRatio||1,1.25),applied=renderer.getPixelRatio();
  const canvas=renderer.domElement;
  return {
    motion(){pending=true;},
    update(now,moving) {
      moving ||= pending;pending=false;
      const full=Math.min(devicePixelRatio||1,2);
      if(moving) {
        if(now-lastMotion<100&&previous&&now-previous<250){total+=now-previous;samples++;}
        if(samples>=12){if(total/samples>30)motionRatio=Math.max(Math.min(full,.75),motionRatio*.8);samples=0;total=0;}
        lastMotion=now;
      } else if(now-lastMotion>180){samples=0;total=0;}
      previous=now;
      const pixels=Math.max(1,canvas.clientWidth*canvas.clientHeight);
      const ratio=now-lastMotion<180?Math.min(full,motionRatio,Math.sqrt(1500000/pixels)):full;
      if(Math.abs(applied-ratio)<.01)return false;
      applied=ratio;renderer.setPixelRatio(ratio);return true;
    }
  };
}
