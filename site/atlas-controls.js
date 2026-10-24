import {OrbitControls} from './vendor/three/examples/jsm/controls/OrbitControls.js';

// three.js 0.170 tracks mouse and touch IDs in the same active-pointer array,
// but initializes positions only for touches. A mixed stream can leave a mouse
// as the remaining pointer on touch-up; the upstream transition then reads an
// undefined position. Keep a position for every tracked pointer. Vendor sources,
// camera math, geometry and normal single-pointer behavior remain unchanged.
export class AtlasOrbitControls extends OrbitControls {
  _addPointer(event) {
    super._addPointer(event);
    this._trackPointer(event);
  }
}

// Stable screen basis for an exactly superior/inferior view. A cross product with
// world-up alone vanishes at these poles and incorrectly shrinks the fit distance.
export function framingBasis(direction) {
  const right=direction.clone().set(0,1,0).cross(direction);
  if(right.lengthSq()<1e-12)right.set(1,0,0);
  right.normalize();
  return {right,up:direction.clone().cross(right).normalize()};
}
