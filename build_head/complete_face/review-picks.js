// Reproducible manual picks, 2026-10-12. No coordinates inferred from bounds.
// Load in the standard pintool with BP or the separately exported Z scene.
window.completeFacePicks = () => [
 ['inferior_concha_right','A02.1.08.003','lat',.5,.43],
 ['inferior_concha_left','A02.1.08.003','med',.49,.397],
 ['lacrimal_right','A02.1.09.003','lat',.62,.52],
 ['lacrimal_left','A02.1.09.003','med',.39,.52],
 ['palatine_right','A02.1.13.009','med',.4,.64],
 ['palatine_left','A02.1.13.009','lat',.638,.626]
].map(([bone,code,view,u,v])=>({bone,code,view,uv:[u,v],
 ...window.pick(window.__meshes['bp_'+bone]?'bp_'+bone:bone,view,u,v)}));

window.completeZMylohyoid = side => {
 if(!['left','right'].includes(side))throw Error('Unknown side');
 const key=window.__meshes.z_mandible?'z_mandible':'mandible';
 const m=window.__meshes[key],original=m.geometry,g=original.clone();
 const pos=g.attributes.position,idx=g.index.array,out=[],v=new THREE.Vector3();
 for(let i=0;i<idx.length;i+=3){
  let x=0;for(let j=0;j<3;j++)x+=v.fromBufferAttribute(pos,idx[i+j]).applyMatrix4(m.matrixWorld).x;
  if(side==='right'?x/3<0:x/3>0)out.push(...idx.slice(i,i+3));
 }
 g.setIndex(out);g.computeBoundingBox();m.geometry=g;
 const view=side==='right'?'med':'lat',u=side==='right'?.648:.352;
 const p=window.pick(key,view,u,.56);
 window.show(key,view);window.pins([{p:p.p,t:'A02.1.15.031'}]);
 m.geometry=original;g.dispose();
 return {side,view,uv:[u,.56],...p};
};
