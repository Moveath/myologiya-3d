// Source-bound overlays. Source vertex/index buffers and BVHs are never edited.
// A region may contain several owners; every part must match its source exactly.

export async function sha256(bytes) {
  if (!globalThis.crypto?.subtle) return null;
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
}
export async function geometryHash(geometry) {
  const p=geometry.attributes.position, idx=geometry.index, positions=[], indices=[];
  for(let i=0;i<p.count;i++) positions.push(p.getX(i),p.getY(i),p.getZ(i));
  for(let i=0;i<(idx?.count??p.count);i++) indices.push(idx?idx.getX(i):i);
  return sha256(new TextEncoder().encode(JSON.stringify({positions,indices})));
}
export async function regionBindingDigest(def) {
  const binding={id:def.id,bone:def.bone,pinIds:def.pinIds,variants:def.variants};
  return sha256(new TextEncoder().encode(JSON.stringify(binding)));
}
export async function admissionValid(def) {
  const a=def.admission;
  return !!a&&['confirmed','educational'].includes(a.level)&&a.explicit===true&&
    !!a.scope&&!!a.reviewId&&!!def.notice&&/^[0-9a-f]{64}$/.test(a.bindingHash||'')&&a.bindingHash===await regionBindingDigest(def);
}
export function regionGeometry(THREE, source, part) {
  const count=source.index?.count??source.attributes.position.count;
  const vertexCount=source.attributes.position.count;
  const index=i=>source.index?source.index.getX(i):i;
  const geometry=new THREE.BufferGeometry();
  // Copy only the selected vertices; disposing an overlay cannot free source GPU buffers.
  const positions=[], normals=[], p=source.attributes.position, n=source.attributes.normal;
  const append=i=>{positions.push(p.getX(i),p.getY(i),p.getZ(i));if(n)normals.push(n.getX(i),n.getY(i),n.getZ(i));};
  if(part.faces?.length) {
    for(const face of part.faces) {
      if(!Number.isInteger(face)||face<0||face*3+2>=count) throw Error('Invalid region face');
      for(let j=0;j<3;j++)append(index(face*3+j));
    }
  } else if(part.edges?.length) {
    for(const edge of part.edges) {
      if(edge.length!==2)throw Error('Invalid region edge');
      for(const i of edge){if(!Number.isInteger(i)||i<0||i>=vertexCount)throw Error('Invalid region vertex');append(i);}
    }
  } else throw Error('Empty region');
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  if(normals.length)geometry.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
  geometry.computeBoundingBox();geometry.computeBoundingSphere();return geometry;
}

export class AnatomicalRegions {
  constructor(manifest, THREE) {this.THREE=THREE;this.manifest=manifest;this.items=new Map();this.failures=new Map();this.selected=null;}
  definitions(pinId) {return this.manifest.regions.filter(r=>r.pinIds.includes(pinId));}
  async prepare(structures,sourceHash) {
    const THREE=this.THREE;
    for(const def of this.manifest.regions) {
      const owner=structures.get(def.bone);
      if(!owner)continue;
      try {
        if(!await admissionValid(def))throw Error('Разметка не допущена или её привязка изменилась. Черновая маска не показывается; сохранён обычный пин.');
        const variants=def.variants.filter(v=>v.sourceHash===sourceHash);
        if(!variants.length)throw Error('Исходная модель изменилась; разметка не применяется.');
        let matched=false;
        for(const v of variants) {
          const mesh=owner.meshes[v.primitive];
          if(!mesh||await geometryHash(mesh.geometry)!==v.geometryHash)continue;
          const geometry=regionGeometry(THREE,mesh.geometry,v), surface=!!v.faces?.length;
          const material=surface?new THREE.MeshBasicMaterial({color:0xd839a1,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2,depthWrite:false,side:THREE.DoubleSide}):
            new THREE.LineBasicMaterial({color:0xc52897,depthWrite:false});
          const overlay=surface?new THREE.Mesh(geometry,material):new THREE.LineSegments(geometry,material);
          overlay.name='region|'+def.id;overlay.userData.anatomicalRegion=def.id;
          overlay.raycast=()=>{};overlay.visible=false;overlay.renderOrder=3;
          mesh.add(overlay);this.items.set(def.id,{def,mesh,overlay,variant:v});matched=true;break;
        }
        if(!matched)throw Error('Геометрия не совпала с проверенной разметкой.');
      } catch(error) {this.failures.set(def.id,error.message);}
    }
  }
  update(pinId,enabled=true,side='both') {
    this.selected=enabled?pinId:null;
    for(const {def,mesh,overlay} of this.items.values()) {
      overlay.visible=!!enabled&&def.pinIds.includes(pinId)&&mesh.visible&&this.info(pinId)?.ready&&
        (side==='both'||!def.side||def.side===side);
      const m=overlay.material, opacity=mesh.material.opacity;
      const transparent=opacity<1;
      if(m.transparent!==transparent){m.transparent=transparent;m.needsUpdate=true;}
      m.opacity=opacity;
    }
  }
  info(pinId) {
    const defs=this.definitions(pinId);
    if(!defs.length)return null;
    const ready=defs.every(d=>this.items.has(d.id));
    const level=defs.some(d=>d.admission?.level==='draft')?'draft':defs.some(d=>d.admission?.level==='educational')?'educational':'confirmed';
    const admissionLabel=level==='educational'?'Предварительная учебная разметка':level==='confirmed'?'Разметка подтверждена в указанном объёме':'Разметка не допущена';
    return {ready,level,admissionLabel,label:defs.map(d=>d.label).join('; '),notice:[...new Set(defs.map(d=>d.notice))].join(' '),
      error:defs.map(d=>this.failures.get(d.id)).filter(Boolean).join(' '),
      visible:defs.some(d=>this.items.get(d.id)?.overlay.visible)};
  }
}
