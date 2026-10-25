import {Controls, MathUtils, Spherical, Vector3} from 'three';
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
  // Drop leftover damping so a mode switch does not keep spinning the camera.
  stopMotion() {
    this._sphericalDelta.set(0, 0, 0);
    this._panOffset.set(0, 0, 0);
    this._scale = 1;
  }
}

// Free camera: look around from the camera, fly forward/back, sideways and
// vertically. Camera and orbit target move together, so the orbit controls'
// update(), framing tweens and pin occlusion keep working on the same target.
// Directions: x = right, y = world up, z = along the view.
const FLY_AXES = {forward: [0, 0, 1], back: [0, 0, -1], left: [-1, 0, 0], right: [1, 0, 0], up: [0, 1, 0], down: [0, -1, 0]};
const FLY_KEYS = {KeyW: 'forward', ArrowUp: 'forward', KeyS: 'back', ArrowDown: 'back', KeyA: 'left', ArrowLeft: 'left',
  KeyD: 'right', ArrowRight: 'right', KeyE: 'up', Space: 'up', PageUp: 'up', KeyQ: 'down', KeyC: 'down', PageDown: 'down'};
const WORLD_UP = new Vector3(0, 1, 0);
const _offset = new Vector3(), _forward = new Vector3(), _right = new Vector3(), _up = new Vector3(), _step = new Vector3(),
  _wish = new Vector3(), _spherical = new Spherical();

export class AtlasFlyControls extends Controls {
  constructor(object, target, domElement) {
    super(object, domElement);
    this.enabled = false;
    this.target = target;
    this.lookSpeed = 2.4;     // radians per screen height of drag
    this.speedFactor = 0.4;   // metres per second for each metre between camera and target
    this.minSpeed = 0.02;
    this.maxSpeed = 1;
    this.keyFilter = null;    // event => false keeps a key for the page
    this._held = new Map();   // source -> direction
    this._fast = false;
    this._moving = false;
    this._velocity = new Vector3();
    this._pointers = new Map();
    this._pan = false;
    this._onPointerDown = this._onPointerDown.bind(this);
    this._onPointerMove = this._onPointerMove.bind(this);
    this._onPointerUp = this._onPointerUp.bind(this);
    this._onWheel = this._onWheel.bind(this);
    this._onContextMenu = this._onContextMenu.bind(this);
    this._onKeyDown = this._onKeyDown.bind(this);
    this._onKeyUp = this._onKeyUp.bind(this);
    this._onBlur = this._onBlur.bind(this);
    if (domElement) this.connect();
  }
  connect() {
    const el = this.domElement, win = el.ownerDocument.defaultView;
    el.addEventListener('pointerdown', this._onPointerDown);
    el.addEventListener('pointermove', this._onPointerMove);
    el.addEventListener('pointerup', this._onPointerUp);
    el.addEventListener('pointercancel', this._onPointerUp);
    el.addEventListener('wheel', this._onWheel, {passive: false});
    el.addEventListener('contextmenu', this._onContextMenu);
    win.addEventListener('keydown', this._onKeyDown);
    win.addEventListener('keyup', this._onKeyUp);
    win.addEventListener('blur', this._onBlur);
  }
  disconnect() {
    const el = this.domElement, win = el.ownerDocument.defaultView;
    el.removeEventListener('pointerdown', this._onPointerDown);
    el.removeEventListener('pointermove', this._onPointerMove);
    el.removeEventListener('pointerup', this._onPointerUp);
    el.removeEventListener('pointercancel', this._onPointerUp);
    el.removeEventListener('wheel', this._onWheel);
    el.removeEventListener('contextmenu', this._onContextMenu);
    win.removeEventListener('keydown', this._onKeyDown);
    win.removeEventListener('keyup', this._onKeyUp);
    win.removeEventListener('blur', this._onBlur);
  }
  dispose() { this.disconnect(); }
  // Speed follows the viewing distance: an overview crosses the body quickly, a close-up moves slowly.
  speed() {
    return MathUtils.clamp(this.object.position.distanceTo(this.target) * this.speedFactor, this.minSpeed, this.maxSpeed);
  }
  hold(source, direction) {
    if (!this.enabled || !FLY_AXES[direction]) return;
    if (!this._held.size && !this._moving) this.dispatchEvent({type: 'start'});
    this._held.set(source, direction);
  }
  release(source) { this._held.delete(source); }
  get moving() { return this._moving || this._held.size > 0 || this._pointers.size > 0; }
  // One fixed step, for keyboard activation of an on-screen button.
  nudge(direction) {
    if (!this.enabled || !FLY_AXES[direction]) return;
    this.dispatchEvent({type: 'start'});
    this._translate(this._toWorld(_wish.fromArray(FLY_AXES[direction]), this.speed() * 0.3));
    this.dispatchEvent({type: 'end'});
  }
  update(delta = 0) {
    if (!this.enabled) {
      this._held.clear(); this._pointers.clear(); this._velocity.set(0, 0, 0); this._moving = false;
      return false;
    }
    _wish.set(0, 0, 0);
    for (const direction of this._held.values()) _wish.add(_step.fromArray(FLY_AXES[direction]));
    if (_wish.lengthSq()) _wish.normalize().multiplyScalar(this.speed() * (this._fast ? 3 : 1));
    this._velocity.lerp(_wish, 1 - Math.exp(-delta * 10));
    // stop crisply once the glide is slower than 1% of the flying speed
    if (!this._held.size && this._velocity.length() < this.speed() * 0.01) {
      this._velocity.set(0, 0, 0);
      if (this._moving) { this._moving = false; this.dispatchEvent({type: 'end'}); }
      return false;
    }
    this._moving = true;
    const length = this._velocity.length() * delta;
    if (length > 0) this._translate(this._toWorld(_wish.copy(this._velocity).normalize(), length));
    return length > 0;
  }
  // local (right, world up, view) -> world displacement of the given length
  _toWorld(local, length) {
    _forward.subVectors(this.target, this.object.position).normalize();
    _right.crossVectors(_forward, WORLD_UP);
    if (_right.lengthSq() < 1e-10) _right.set(1, 0, 0).applyQuaternion(this.object.quaternion);
    _right.normalize();
    return _step.set(0, 0, 0).addScaledVector(_right, local.x).addScaledVector(WORLD_UP, local.y)
      .addScaledVector(_forward, local.z).multiplyScalar(length);
  }
  _translate(move) {
    this.object.position.add(move);
    this.target.add(move);
    this.dispatchEvent({type: 'change'});
  }
  // Drag moves the view like a photo sphere: the scene follows the pointer.
  _look(dx, dy) {
    const k = this.lookSpeed / (this.domElement.clientHeight || 1);
    _offset.subVectors(this.target, this.object.position);
    _spherical.setFromVector3(_offset);
    _spherical.theta += dx * k;
    _spherical.phi = MathUtils.clamp(_spherical.phi - dy * k, 0.1, Math.PI - 0.1);
    _offset.setFromSpherical(_spherical);
    this.target.copy(this.object.position).add(_offset);
    this.dispatchEvent({type: 'change'});
  }
  // metres per screen pixel at the target's depth, so a drag moves the scene with the pointer
  _pixel() {
    const distance = MathUtils.clamp(this.object.position.distanceTo(this.target), 0.05, 1.5);
    return 2 * distance * Math.tan(MathUtils.degToRad(this.object.fov) / 2) / (this.domElement.clientHeight || 1);
  }
  _strafe(dx, dy) {
    const pixel = this._pixel();
    _right.set(1, 0, 0).applyQuaternion(this.object.quaternion);
    _up.set(0, 1, 0).applyQuaternion(this.object.quaternion);
    this._translate(_offset.set(0, 0, 0).addScaledVector(_right, -dx * pixel).addScaledVector(_up, dy * pixel));
  }
  _advance(length) {
    _forward.subVectors(this.target, this.object.position).normalize();
    this._translate(_offset.copy(_forward).multiplyScalar(length));
  }
  _pair() {
    const [a, b] = this._pointers.values();
    return {x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, d: Math.hypot(a.x - b.x, a.y - b.y)};
  }
  _onPointerDown(event) {
    if (!this.enabled) return;
    try { this.domElement.setPointerCapture(event.pointerId); } catch { /* synthetic or already released pointer */ }
    this._pointers.set(event.pointerId, {x: event.clientX, y: event.clientY});
    this._pan = event.pointerType !== 'touch' && (event.button === 1 || event.button === 2 || event.shiftKey || event.ctrlKey || event.metaKey);
    if (this._pointers.size === 1) this.dispatchEvent({type: 'start'});
  }
  _onPointerMove(event) {
    const pointer = this._pointers.get(event.pointerId);
    if (!this.enabled || !pointer) return;
    if (this._pointers.size === 1) {
      const dx = event.clientX - pointer.x, dy = event.clientY - pointer.y;
      pointer.x = event.clientX; pointer.y = event.clientY;
      if (this._pan) this._strafe(dx, dy); else this._look(dx, dy);
      return;
    }
    const before = this._pair();
    pointer.x = event.clientX; pointer.y = event.clientY;
    const after = this._pair();
    this._strafe(after.x - before.x, after.y - before.y);
    this._advance((after.d - before.d) * this._pixel() * 2);
  }
  _onPointerUp(event) {
    if (!this._pointers.delete(event.pointerId)) return;
    try { this.domElement.releasePointerCapture(event.pointerId); } catch { /* already released */ }
    if (!this._pointers.size) this.dispatchEvent({type: 'end'});
  }
  _onWheel(event) {
    if (!this.enabled) return;
    event.preventDefault();
    const dy = event.deltaY * (event.deltaMode === 1 ? 33 : event.deltaMode === 2 ? 400 : 1);
    this.dispatchEvent({type: 'start'});
    this._advance(-MathUtils.clamp(dy, -240, 240) / 100 * this.speed() * 0.15);
    this.dispatchEvent({type: 'end'});
  }
  _onContextMenu(event) { if (this.enabled) event.preventDefault(); }
  _onKeyDown(event) {
    if (event.key === 'Shift') this._fast = true;
    const direction = FLY_KEYS[event.code];
    if (!this.enabled || !direction || event.ctrlKey || event.metaKey || event.altKey) return;
    const target = event.target;
    if (target?.closest?.('input,select,textarea,[contenteditable="true"]')) return;
    if (event.code === 'Space' && target?.closest?.('button,a,summary')) return;
    if (this.keyFilter && !this.keyFilter(event)) return;
    event.preventDefault();
    this._fast = event.shiftKey;
    this.hold(event.code, direction);
  }
  _onKeyUp(event) {
    if (event.key === 'Shift') this._fast = false;
    this.release(event.code);
  }
  _onBlur() { this._held.clear(); this._fast = false; }
}

// Stable screen basis for an exactly superior/inferior view. A cross product with
// world-up alone vanishes at these poles and incorrectly shrinks the fit distance.
export function framingBasis(direction) {
  const right=direction.clone().set(0,1,0).cross(direction);
  if(right.lengthSq()<1e-12)right.set(1,0,0);
  right.normalize();
  return {right,up:direction.clone().cross(right).normalize()};
}
