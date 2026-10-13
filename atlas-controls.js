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
