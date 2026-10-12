// Computes landmark positions on the right upper-limb bones from their geometry.
// Frame: x+ = medial (body right is -x), y+ = superior, z+ = anterior. Units: metres.
import * as THREE from 'three';

const M = window.__meshes;
const cache = {};
const V3 = (a) => (a instanceof THREE.Vector3 ? a.clone() : new THREE.Vector3(...a));

function verts(k) {
  if (cache[k]) return cache[k];
  const m = M[k], pos = m.geometry.attributes.position, out = [];
  for (let i = 0; i < pos.count; i++) out.push(new THREE.Vector3().fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld));
  return (cache[k] = out);
}
const box = (k) => new THREE.Box3().setFromObject(M[k]);
function ext(k, dir, filt = () => true) {
  const d = V3(dir).normalize();
  let best = null, bv = -Infinity;
  for (const v of verts(k)) if (filt(v)) { const s = v.dot(d); if (s > bv) { bv = s; best = v; } }
  return best ? best.clone() : null;
}
const slab = (k, y0, y1) => verts(k).filter(v => v.y >= y0 && v.y <= y1);
function centroid(a) { const c = new THREE.Vector3(); a.forEach(v => c.add(v)); return c.multiplyScalar(1 / Math.max(1, a.length)); }
const axisAt = (k, y, h = 0.004) => centroid(slab(k, y - h, y + h));
const ray = new THREE.Raycaster();
// surface point hit by a ray travelling toward `target` from the side `dir` points to
function surf(k, target, dir) {
  const d = V3(dir).normalize();
  ray.set(V3(target).addScaledVector(d, 0.25), d.clone().negate());
  ray.far = 0.5;
  const h = ray.intersectObject(M[k], false)[0];
  if (!h) return null;
  return { p: h.point.clone(), n: h.face.normal.clone().transformDirection(M[k].matrixWorld) };
}
// surface point at an extreme vertex, approached from the same direction
function extSurf(k, dir, filt) {
  const v = ext(k, dir, filt);
  if (!v) return null;
  const c = centroid(verts(k));
  const s = surf(k, v.clone().lerp(c, 0.02), dir);
  return s || { p: v, n: V3(dir).normalize() };
}

const out = [];
const put = (bone, id, s) => { if (s) out.push({ bone, id, p: s.p.toArray(), n: s.n.toArray() }); else out.push({ bone, id, missing: true }); };

// ---------------- scapula ----------------
(() => {
  const k = 'scapula', b = box(k);
  const W = b.max.x - b.min.x;
  const infA = extSurf(k, [0, -1, 0]);
  const supA = extSurf(k, [0.25, 1, 0], v => v.x > b.min.x + 0.6 * W);
  const corTip = extSurf(k, [0, 0, 1]);
  // acromion: the lateral-most, high part
  const acrTip = ext(k, [-1, 0.25, 0], v => v.y > b.max.y - 0.03);
  const acr = surf(k, [acrTip.x + 0.012, acrTip.y, acrTip.z], [0, 1, 0]);
  const acrAngle = extSurf(k, [-1, 0, -1.1], v => v.y > b.max.y - 0.03 && v.x < acrTip.x + 0.03);
  // glenoid: the lateral-facing layer of vertices near the lateral-most point below the acromion
  const gdir = new THREE.Vector3(-1, 0, 0.15).normalize();
  const G = ext(k, gdir, v => v.y < acrTip.y - 0.025 && v.y > acrTip.y - 0.075);
  const face = verts(k).filter(v => v.distanceTo(G) < 0.03 && v.dot(gdir) > G.dot(gdir) - 0.006);
  const gcen = centroid(face);
  const gTop = Math.max(...face.map(v => v.y)), gBot = Math.min(...face.map(v => v.y));
  const glen = surf(k, [gcen.x + 0.01, (gTop + gBot) / 2, gcen.z], gdir);
  const gc = glen.p;
  const supraG = surf(k, [gc.x + 0.006, gTop + 0.003, gc.z], [-1, 0.5, 0.15]);
  const infraG = surf(k, [gc.x + 0.008, gBot - 0.005, gc.z], [-1, -0.4, 0.15]);
  const neck = surf(k, [gc.x + 0.02, gc.y - 0.004, gc.z], [0, 0, -1]);
  // spine crest: most posterior point in the middle third (medial-lateral)
  const xm0 = b.min.x + 0.45 * W, xm1 = b.min.x + 0.62 * W;
  const spine = extSurf(k, [0, 0.25, -1], v => v.x > xm0 && v.x < xm1);
  const xmid = (xm0 + xm1) / 2 + 0.01;
  const zc = (b.min.z + b.max.z) / 2;
  const supraF = window.pick(k, 'post', 0.3, 0.19);
  if (supraF) { supraF.p = V3(supraF.p); supraF.n = V3(supraF.n); }
  const infraF = surf(k, [xmid, spine.p.y - 0.06, zc], [0, 0, -1]);
  const subF = surf(k, [xmid + 0.005, spine.p.y - 0.045, zc], [0, 0, 1]);
  const medB = extSurf(k, [1, 0, 0], v => v.y < spine.p.y - 0.035 && v.y > spine.p.y - 0.05);
  const yLat = (gc.y + infA.p.y) / 2;
  const latB = extSurf(k, [-1, 0, 0.3], v => v.y < yLat + 0.006 && v.y > yLat - 0.006);
  // superior border profile from the coracoid base toward the superior angle; notch = first dip
  const prof = [];
  for (let x = corTip.p.x + 0.004; x < supA.p.x - 0.01; x += 0.002) {
    const top = ext(k, [0, 1, 0], v => v.x > x - 0.001 && v.x < x + 0.001 && v.z > zc - 0.02);
    if (top) prof.push(top);
  }
  let notch = null;
  for (let i = 1; i < prof.length - 1; i++) {
    if (prof[i].y < prof[i - 1].y && prof[i].y <= prof[i + 1].y && prof[i].x > corTip.p.x + 0.01) { notch = prof[i]; break; }
  }
  const xb = notch ? (notch.x + supA.p.x) / 2 : supA.p.x - 0.03;
  const zb = notch ? notch.z + 0.006 : zc;
  const supB = extSurf(k, [0, 1, 0], v => Math.abs(v.x - xb) < 0.003 && v.z < zb);
  put(k, 'acromion', acr); put(k, 'acromial_angle', acrAngle); put(k, 'spine', spine);
  put(k, 'supraspinous_fossa', supraF); put(k, 'infraspinous_fossa', infraF); put(k, 'subscapular_fossa', subF);
  put(k, 'coracoid', corTip); put(k, 'glenoid', glen); put(k, 'supraglenoid', supraG); put(k, 'infraglenoid', infraG);
  put(k, 'scap_neck', neck); put(k, 'scap_notch', notch ? surf(k, [notch.x, notch.y - 0.002, notch.z], [0, 1, 0]) : null);
  put(k, 'sup_angle', supA); put(k, 'inf_angle', infA); put(k, 'medial_border', medB);
  put(k, 'lateral_border', latB); put(k, 'superior_border', supB);
})();

// ---------------- clavicle ----------------
(() => {
  const k = 'clavicle', b = box(k), L = b.max.x - b.min.x;
  const at = (t) => b.min.x + t * L; // t=0 lateral end, t=1 medial end
  const sl = (t) => verts(k).filter(v => Math.abs(v.x - at(t)) < 0.003);
  const cz = (t) => centroid(sl(t));
  const zmin = (t) => Math.min(...sl(t).map(v => v.z));
  const c95 = cz(0.95), c08 = cz(0.08), c65 = cz(0.65), c50 = cz(0.5), c15 = cz(0.15), c85 = cz(0.86);
  put(k, 'sternal_end', surf(k, c95, [0.3, 0.2, 1]));
  put(k, 'acromial_end', surf(k, c08, [0, 1, 0]));
  put(k, 'clav_body', surf(k, c65, [0, 0, 1]));
  put(k, 'conoid_tubercle', surf(k, [at(0.27), cz(0.27).y, zmin(0.27) + 0.005], [0, -1, 0]));
  put(k, 'trapezoid_line', surf(k, [at(0.15), c15.y, c15.z], [0, -1, 0]));
  put(k, 'subclavian_groove', surf(k, c50, [0, -1, 0]));
  put(k, 'costoclavicular', surf(k, c85, [0, -1, 0]));
})();

// ---------------- humerus ----------------
(() => {
  const k = 'humerus', b = box(k), top = b.max.y, bot = b.min.y, L = top - bot;
  const prox = (v) => v.y > top - 0.06;
  const gt = extSurf(k, [-1, 0.15, 0], prox);
  const lt = extSurf(k, [0.15, 0, 1], v => v.y > top - 0.06 && v.y < top - 0.015);
  const hc = axisAt(k, top - 0.022, 0.012);
  const headAxis = new THREE.Vector3(1, 0.75, -0.45).normalize();
  const head = surf(k, hc, headAxis);
  const neckA = surf(k, hc, headAxis.clone().add(new THREE.Vector3(0, -1.25, 0)).normalize());
  const yS = top - 0.06;
  const surgical = surf(k, axisAt(k, yS), [-1, 0, -0.6]);
  // anterior profile at the lesser tubercle level: the groove is the deepest point lateral to it
  const yg = lt.p.y - 0.004;
  const prof = [];
  for (let x = lt.p.x; x > gt.p.x + 0.004; x -= 0.0008) {
    const s = surf(k, [x, yg, (b.min.z + b.max.z) / 2], [0, 0, 1]);
    if (s) prof.push(s);
  }
  let groove = prof[0];
  prof.forEach(s => { if (s.p.z < groove.p.z) groove = s; });
  // crests 3 cm lower: the lips either side of the groove line
  const yc = yg - 0.03;
  const zmid = (b.min.z + b.max.z) / 2;
  const crMin = surf(k, [groove.p.x + 0.008, yc, zmid], [0.25, 0, 1]);
  const crMaj = surf(k, [groove.p.x - 0.007, yc, zmid], [-0.35, 0, 1]);
  const deltoid = surf(k, axisAt(k, top - 0.42 * L), [-1, 0, 0.35]);
  const radialGroove = surf(k, axisAt(k, top - 0.5 * L), [-0.25, 0, -1]);
  const bodyMed = surf(k, axisAt(k, top - 0.48 * L), [1, 0, 0.3]);
  const bodyAnt = surf(k, axisAt(k, top - 0.68 * L), [0, 0, 1]);
  const dist = (v) => v.y < bot + 0.06;
  const me = extSurf(k, [1, 0, 0], dist);
  const le = extSurf(k, [-1, 0, 0], dist);
  const w = me.p.x - le.p.x;
  const zc = axisAt(k, bot + 0.015, 0.006).z;
  const xT = le.p.x + 0.66 * w, xC = le.p.x + 0.3 * w, xO = le.p.x + 0.55 * w;
  const troch = surf(k, [xT, bot + 0.012, zc], [0, -0.35, 1]);
  const capit = surf(k, [xC, bot + 0.016, zc], [0, -0.2, 1]);
  const corF = surf(k, [xT, bot + 0.032, zc], [0, 0, 1]);
  const radF = surf(k, [xC + 0.002, bot + 0.034, zc], [0, 0, 1]);
  const olecF = surf(k, [xO, bot + 0.027, zc], [0, 0, -1]);
  const ulnS = surf(k, [me.p.x - 0.007, me.p.y, me.p.z], [0, 0, -1]);
  const latRidge = extSurf(k, [-1, 0, 0], v => v.y > le.p.y + 0.035 && v.y < le.p.y + 0.05);
  put(k, 'hum_head', head); put(k, 'anat_neck', neckA); put(k, 'surg_neck', surgical);
  put(k, 'greater_tubercle', gt); put(k, 'lesser_tubercle', lt); put(k, 'intertubercular', groove);
  put(k, 'crest_greater', crMaj); put(k, 'crest_lesser', crMin); put(k, 'deltoid_tuberosity', deltoid);
  put(k, 'radial_groove', radialGroove); put(k, 'hum_body_med', bodyMed); put(k, 'hum_body_ant', bodyAnt);
  put(k, 'medial_epicondyle', me); put(k, 'ulnar_sulcus', ulnS); put(k, 'lateral_epicondyle', le);
  put(k, 'lat_supracondylar', latRidge); put(k, 'trochlea', troch); put(k, 'capitulum', capit);
  put(k, 'olecranon_fossa', olecF); put(k, 'coronoid_fossa', corF); put(k, 'radial_fossa', radF);
})();

// ---------------- radius ----------------
(() => {
  const k = 'radius', b = box(k), top = b.max.y, bot = b.min.y, L = top - bot;
  const head = surf(k, axisAt(k, top - 0.006), [-1, 0, 0.6]);
  const neck = surf(k, axisAt(k, top - 0.017), [-0.6, 0, 1]);
  const tub = surf(k, axisAt(k, top - 0.032, 0.006), [0.8, 0, 0.7]);
  const supin = surf(k, axisAt(k, top - 0.06), [-1, 0, -0.2]);
  const pron = surf(k, axisAt(k, top - 0.47 * L), [-1, 0, 0.2]);
  const ib = extSurf(k, [1, 0, 0], v => Math.abs(v.y - (top - 0.42 * L)) < 0.003);
  const ant = surf(k, axisAt(k, top - 0.55 * L), [0, 0, 1]);
  const post = surf(k, axisAt(k, top - 0.5 * L), [0, 0, -1]);
  const sty = extSurf(k, [-1, -1.2, 0], v => v.y < bot + 0.02);
  const lister = extSurf(k, [0, 0, -1], v => v.y > bot + 0.012 && v.y < bot + 0.028);
  const dc = axisAt(k, bot + 0.01, 0.004);
  const notch = surf(k, dc, [1, 0, 0]);
  const carp = surf(k, axisAt(k, bot + 0.006, 0.004), [0, -1, 0]);
  put(k, 'rad_head', head); put(k, 'rad_neck', neck); put(k, 'radial_tuberosity', tub); put(k, 'rad_supinator', supin);
  put(k, 'pronator_tuberosity', pron); put(k, 'rad_interosseous', ib); put(k, 'rad_anterior', ant); put(k, 'rad_posterior', post);
  put(k, 'rad_styloid', sty); put(k, 'dorsal_tubercle', lister); put(k, 'ulnar_notch', notch); put(k, 'carpal_surface', carp);
})();

// ---------------- ulna ----------------
(() => {
  const k = 'ulna', b = box(k), top = b.max.y, bot = b.min.y, L = top - bot;
  const olec = surf(k, axisAt(k, top - 0.01), [0, 0.5, -1]);
  const tn = surf(k, axisAt(k, top - 0.022, 0.003), [0, 0, 1]);
  const cor = extSurf(k, [0, -0.2, 1], v => v.y > top - 0.055 && v.y < top - 0.025);
  const rn = surf(k, [axisAt(k, cor.p.y + 0.003).x, cor.p.y + 0.003, cor.p.z - 0.008], [-1, 0, 0]);
  const tub = surf(k, axisAt(k, cor.p.y - 0.014), [0, 0, 1]);
  const supCrest = surf(k, axisAt(k, cor.p.y - 0.022), [-1, 0, -0.7]);
  const postB = extSurf(k, [0, 0, -1], v => Math.abs(v.y - (top - 0.4 * L)) < 0.003);
  const ib = extSurf(k, [-1, 0, 0], v => Math.abs(v.y - (top - 0.45 * L)) < 0.003);
  const ant = surf(k, axisAt(k, top - 0.42 * L), [0, 0, 1]);
  const post = surf(k, axisAt(k, top - 0.6 * L), [-0.6, 0, -1]);
  const distAnt = surf(k, axisAt(k, bot + 0.035), [0, 0, 1]);
  const headU = surf(k, axisAt(k, bot + 0.012, 0.004), [-0.6, 0, 1]);
  const sty = extSurf(k, [0.25, -1, -0.25], v => v.y < bot + 0.015);
  put(k, 'olecranon', olec); put(k, 'trochlear_notch', tn); put(k, 'coronoid_process', cor); put(k, 'radial_notch', rn);
  put(k, 'ulnar_tuberosity', tub); put(k, 'supinator_crest', supCrest); put(k, 'uln_posterior_border', postB);
  put(k, 'uln_interosseous', ib); put(k, 'uln_anterior', ant); put(k, 'uln_posterior', post); put(k, 'uln_distal_anterior', distAnt);
  put(k, 'uln_head', headU); put(k, 'uln_styloid', sty);
})();

// ---------------- carpus ----------------
(() => {
  const c = (k) => centroid(verts(k));
  put('scaphoid', 'scaphoid_tubercle', extSurf('scaphoid', [-0.3, -0.4, 1]));
  put('lunate', 'lunate_proximal', surf('lunate', c('lunate'), [0, 1, 0.1]));
  put('triquetrum', 'triquetrum_pisiform', surf('triquetrum', c('triquetrum'), [0, 0, 1]));
  put('pisiform', 'pisiform_apex', extSurf('pisiform', [0, 0, 1]));
  put('trapezium', 'trapezium_tubercle', extSurf('trapezium', [0.3, 0, 1]));
  const mc1 = axisAt('metacarpal_1', box('metacarpal_1').max.y - 0.006, 0.004);
  const toMc1 = mc1.clone().sub(c('trapezium')).normalize();
  put('trapezium', 'trapezium_saddle', surf('trapezium', c('trapezium'), toMc1));
  const mc2 = axisAt('metacarpal_2', box('metacarpal_2').max.y - 0.004, 0.003);
  put('trapezoid', 'trapezoid_distal', surf('trapezoid', c('trapezoid'), mc2.clone().sub(c('trapezoid')).normalize()));
  put('capitate', 'capitate_head', surf('capitate', c('capitate'), [0, 1, 0]));
  put('hamate', 'hamate_hook', extSurf('hamate', [0.1, 0, 1]));
})();

// ---------------- metacarpals and phalanges ----------------
function longPins(k, names) {
  const vs = verts(k);
  const c = centroid(vs);
  // principal axis by power iteration on the covariance
  const cov = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  vs.forEach(v => { const d = [v.x - c.x, v.y - c.y, v.z - c.z]; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) cov[i][j] += d[i] * d[j]; });
  let a = new THREE.Vector3(0, 1, 0);
  for (let it = 0; it < 30; it++) {
    a = new THREE.Vector3(cov[0][0] * a.x + cov[0][1] * a.y + cov[0][2] * a.z, cov[1][0] * a.x + cov[1][1] * a.y + cov[1][2] * a.z, cov[2][0] * a.x + cov[2][1] * a.y + cov[2][2] * a.z).normalize();
  }
  if (a.y < 0) a.negate(); // a points proximally (up)
  let lo = Infinity, hi = -Infinity;
  vs.forEach(v => { const s = v.clone().sub(c).dot(a); lo = Math.min(lo, s); hi = Math.max(hi, s); });
  const at = (t) => c.clone().addScaledVector(a, hi - t * (hi - lo)); // t=0 proximal tip, 1 distal tip
  const side = new THREE.Vector3(0, 0, 1).addScaledVector(a, -a.z).normalize(); // palmar, perpendicular to the axis
  names.forEach(([id, t]) => put(k, id, surf(k, at(t), side)));
}
for (let i = 1; i <= 5; i++) {
  longPins(`metacarpal_${i}`, [[`mc${i}_base`, 0.12], [`mc${i}_body`, 0.5], [`mc${i}_head`, 0.86]]);
  longPins(`phalanx_prox_${i}`, [[`pp${i}_base`, 0.14], [`pp${i}_body`, 0.5], [`pp${i}_head`, 0.86]]);
  if (i > 1) longPins(`phalanx_mid_${i}`, [[`pm${i}_base`, 0.15], [`pm${i}_body`, 0.5], [`pm${i}_head`, 0.85]]);
  longPins(`phalanx_dist_${i}`, [[`pd${i}_base`, 0.18], [`pd${i}_body`, 0.5], [`pd${i}_tuberosity`, 0.86]]);
}

// ---------------- connective tissue ----------------
put('interosseous_membrane', 'membrane_mid', surf('interosseous_membrane', centroid(verts('interosseous_membrane')), [0, 0, 1]));
put('flexor_retinaculum', 'retinaculum_mid', surf('flexor_retinaculum', centroid(verts('flexor_retinaculum')), [0, 0, 1]));

window.__pins = out;
export default out;
