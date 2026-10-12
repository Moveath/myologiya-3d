// Positions of every Terminologia Anatomica (TA98) term on the right upper-limb bones.
// Frame: x+ medial (body right is -x), y+ up, z+ anterior (palm faces forward). Metres.
// Run after landmarks.js (window.__pins = older landmark positions reused here). Output: window.__ta
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
function centroid(a) { const c = new THREE.Vector3(); a.forEach(v => c.add(v)); return c.multiplyScalar(1 / Math.max(1, a.length)); }
function ext(k, dir, filt = () => true) {
  const d = V3(dir).normalize();
  let best = null, bv = -Infinity;
  for (const v of verts(k)) if (filt(v)) { const s = v.dot(d); if (s > bv) { bv = s; best = v; } }
  return best ? best.clone() : null;
}
const slab = (k, y0, y1) => verts(k).filter(v => v.y >= y0 && v.y <= y1);
const axisAt = (k, y, h = 0.004) => centroid(slab(k, y - h, y + h));
const ray = new THREE.Raycaster();
function surf(k, target, dir, from = 0.25) {
  const d = V3(dir).normalize();
  ray.set(V3(target).addScaledVector(d, from), d.clone().negate());
  ray.far = from * 2;
  const h = ray.intersectObject(M[k], false)[0];
  if (!h) return null;
  return { p: h.point.clone(), n: h.face.normal.clone().transformDirection(M[k].matrixWorld) };
}
function extSurf(k, dir, filt) {
  const v = ext(k, dir, filt);
  if (!v) return null;
  return surf(k, v.clone().lerp(centroid(verts(k)), 0.02), dir) || { p: v, n: V3(dir).normalize() };
}
const W = (s) => (s && s.p ? { p: V3(s.p), n: V3(s.n) } : null);
const PK = (k, view, u, v, zb) => W(window.pick(k, view, u, v, zb));
const Z = (c, r) => { c = V3(c); return [[c.x - r, c.y - r, c.z - r], [c.x + r, c.y + r, c.z + r]]; };
const OLD = (id) => { const q = window.__pins.find(p => p.id === id); return q ? V3(q.p) : null; };
const OLDS = (id) => { const q = window.__pins.find(p => p.id === id && !p.missing); return q ? { p: V3(q.p), n: V3(q.n) } : null; };
const out = [];
const put = (bone, id, s) => { if (s) out.push({ bone, id, p: s.p.toArray().map(x => +x.toFixed(5)), n: s.n.toArray().map(x => +x.toFixed(3)) }); else out.push({ bone, id, missing: true }); };

// ======================= scapula =======================
(() => {
  const k = 'scapula', b = box(k), W = b.max.x - b.min.x;
  put(k, 'sca_facies_costalis', PK(k, 'ant', 0.73, 0.55));
  put(k, 'sca_fossa_subscapularis', OLDS('subscapular_fossa'));
  put(k, 'sca_facies_posterior', PK(k, 'post', 0.33, 0.72));
  put(k, 'sca_spina', OLDS('spine'));
  // deltoid tubercle: crest of the spine just lateral to its root at the medial border
  const sp = OLD('spine');
  const xt = b.max.x - 0.2 * W;
  put(k, 'sca_tuberculum_deltoideum', extSurf(k, [0, -0.15, -1], v => Math.abs(v.x - xt) < 0.003 && Math.abs(v.y - (sp.y - 0.004)) < 0.02));
  put(k, 'sca_fossa_supraspinata', OLDS('supraspinous_fossa'));
  put(k, 'sca_fossa_infraspinata', OLDS('infraspinous_fossa'));
  put(k, 'sca_acromion', OLDS('acromion'));
  // clavicular facet: medial edge of the acromion (found by contact with the clavicle)
  const cf = PK(k, 'sup', 0.50, 0.50, Z([-0.15, 1.35, 0.06], 0.03));
  put(k, 'sca_facies_articularis_clavicularis', cf ? surf(k, cf.p.clone().add(new THREE.Vector3(-0.002, -0.003, 0)), [1, 0.35, 0]) : null);
  put(k, 'sca_angulus_acromii', OLDS('acromial_angle'));
  put(k, 'sca_margo_medialis', OLDS('medial_border'));
  put(k, 'sca_margo_lateralis', OLDS('lateral_border'));
  put(k, 'sca_margo_superior', OLDS('superior_border'));
  put(k, 'sca_incisura', OLDS('scap_notch'));
  put(k, 'sca_angulus_inferior', OLDS('inf_angle'));
  put(k, 'sca_angulus_lateralis', PK(k, 'ant', 0.355, 0.37));
  put(k, 'sca_angulus_superior', OLDS('sup_angle'));
  put(k, 'sca_cavitas_glenoidalis', OLDS('glenoid'));
  put(k, 'sca_tuberculum_supraglenoidale', OLDS('supraglenoid'));
  put(k, 'sca_tuberculum_infraglenoidale', OLDS('infraglenoid'));
  put(k, 'sca_collum', OLDS('scap_neck'));
  put(k, 'sca_processus_coracoideus', OLDS('coracoid'));
})();

// ======================= clavicle =======================
(() => {
  const k = 'clavicle', b = box(k), L = b.max.x - b.min.x;
  put(k, 'cla_extremitas_sternalis', OLDS('sternal_end'));
  put(k, 'cla_facies_articularis_sternalis', extSurf(k, [1, -0.15, 0]));
  put(k, 'cla_impressio_lig_costoclavicularis', OLDS('costoclavicular'));
  put(k, 'cla_corpus', OLDS('clav_body'));
  put(k, 'cla_sulcus_m_subclavii', OLDS('subclavian_groove'));
  put(k, 'cla_extremitas_acromialis', OLDS('acromial_end'));
  put(k, 'cla_facies_articularis_acromialis', extSurf(k, [-1, -0.1, 0]));
  const ct = OLD('conoid_tubercle'), tl = OLD('trapezoid_line');
  put(k, 'cla_tuberositas_lig_coracoclavicularis', surf(k, ct.clone().lerp(tl, 0.5).add(new THREE.Vector3(0, 0.003, 0)), [0, -1, 0]));
  put(k, 'cla_tuberculum_conoideum', OLDS('conoid_tubercle'));
  put(k, 'cla_linea_trapezoidea', OLDS('trapezoid_line'));
})();

// ======================= humerus =======================
(() => {
  const k = 'humerus', b = box(k), top = b.max.y, bot = b.min.y, L = top - bot;
  put(k, 'hum_caput', OLDS('hum_head'));
  put(k, 'hum_collum_anatomicum', OLDS('anat_neck'));
  put(k, 'hum_collum_chirurgicum', OLDS('surg_neck'));
  put(k, 'hum_tuberculum_majus', OLDS('greater_tubercle'));
  put(k, 'hum_tuberculum_minus', OLDS('lesser_tubercle'));
  put(k, 'hum_sulcus_intertubercularis', OLDS('intertubercular'));
  put(k, 'hum_crista_tuberculi_majoris', OLDS('crest_greater'));
  put(k, 'hum_crista_tuberculi_minoris', OLDS('crest_lesser'));
  put(k, 'hum_corpus', surf(k, axisAt(k, top - 0.5 * L), [-0.2, 0, 1]));
  put(k, 'hum_facies_anteromedialis', OLDS('hum_body_med'));
  put(k, 'hum_facies_anterolateralis', surf(k, axisAt(k, top - 0.6 * L), [-1, 0, 0.75]));
  put(k, 'hum_facies_posterior', surf(k, axisAt(k, top - 0.66 * L), [0.1, 0, -1]));
  put(k, 'hum_sulcus_n_radialis', OLDS('radial_groove'));
  const at = (f, dir) => extSurf(k, dir, v => Math.abs(v.y - (top - f * L)) < 0.0025);
  put(k, 'hum_margo_medialis', at(0.6, [1, 0, 0.05]));
  const me = OLD('medial_epicondyle'), le = OLD('lateral_epicondyle');
  put(k, 'hum_crista_supraepicondylaris_medialis', extSurf(k, [1, 0, 0], v => Math.abs(v.y - (me.y + 0.04)) < 0.0025));
  // inconstant supracondylar process: anteromedial surface about 5 cm above the medial epicondyle
  put(k, 'hum_processus_supracondylaris', surf(k, axisAt(k, me.y + 0.055), [0.75, 0, 0.65]));
  put(k, 'hum_margo_lateralis', at(0.6, [-1, 0, 0.05]));
  put(k, 'hum_crista_supraepicondylaris_lateralis', OLDS('lat_supracondylar'));
  put(k, 'hum_tuberositas_deltoidea', OLDS('deltoid_tuberosity'));
  // the condyle as a whole: front of the distal end between capitulum and trochlea
  const ca = OLD('capitulum'), tr = OLD('trochlea');
  put(k, 'hum_condylus', surf(k, ca.clone().lerp(tr, 0.5).add(new THREE.Vector3(0, 0.004, -0.004)), [0, -0.1, 1]));
  put(k, 'hum_capitulum', OLDS('capitulum'));
  put(k, 'hum_trochlea', OLDS('trochlea'));
  put(k, 'hum_fossa_olecrani', OLDS('olecranon_fossa'));
  put(k, 'hum_fossa_coronoidea', OLDS('coronoid_fossa'));
  put(k, 'hum_fossa_radialis', OLDS('radial_fossa'));
  put(k, 'hum_epicondylus_medialis', OLDS('medial_epicondyle'));
  put(k, 'hum_sulcus_n_ulnaris', OLDS('ulnar_sulcus'));
  put(k, 'hum_epicondylus_lateralis', OLDS('lateral_epicondyle'));
})();

// ======================= radius =======================
(() => {
  const k = 'radius', b = box(k), top = b.max.y, bot = b.min.y, L = top - bot;
  put(k, 'rad_caput', OLDS('rad_head'));
  const hc = axisAt(k, top - 0.003, 0.002);
  put(k, 'rad_fovea_articularis', surf(k, hc, [0, 1, 0]));
  put(k, 'rad_circumferentia_articularis', surf(k, axisAt(k, top - 0.007), [1, 0, 0.25]));
  put(k, 'rad_collum', OLDS('rad_neck'));
  put(k, 'rad_corpus', surf(k, axisAt(k, top - 0.5 * L), [-0.5, 0, 1]));
  put(k, 'rad_tuberositas', OLDS('radial_tuberosity'));
  put(k, 'rad_facies_anterior', OLDS('rad_anterior'));
  put(k, 'rad_facies_posterior', OLDS('rad_posterior'));
  put(k, 'rad_facies_lateralis', surf(k, axisAt(k, top - 0.66 * L), [-1, 0, 0]));
  put(k, 'rad_tuberositas_pronatoria', OLDS('pronator_tuberosity'));
  put(k, 'rad_margo_interosseus', OLDS('rad_interosseous'));
  const at = (f, dir) => extSurf(k, dir, v => Math.abs(v.y - (top - f * L)) < 0.0025);
  put(k, 'rad_margo_anterior', at(0.6, [-0.45, 0, 1]));
  put(k, 'rad_margo_posterior', at(0.55, [-0.45, 0, -1]));
  put(k, 'rad_processus_styloideus', OLDS('rad_styloid'));
  put(k, 'rad_crista_suprastyloidea', surf(k, axisAt(k, bot + 0.028), [-1, 0, 0.1]));
  put(k, 'rad_tuberculum_dorsale', OLDS('dorsal_tubercle'));
  const lt = OLD('dorsal_tubercle');
  put(k, 'rad_sulci_tendinum', surf(k, new THREE.Vector3(lt.x + 0.009, lt.y, lt.z + 0.004), [0.15, 0, -1]));
  put(k, 'rad_incisura_ulnaris', OLDS('ulnar_notch'));
  put(k, 'rad_facies_articularis_carpalis', OLDS('carpal_surface'));
})();

// ======================= ulna =======================
(() => {
  const k = 'ulna', b = box(k), top = b.max.y, bot = b.min.y, L = top - bot;
  put(k, 'uln_olecranon', OLDS('olecranon'));
  put(k, 'uln_processus_coronoideus', OLDS('coronoid_process'));
  put(k, 'uln_tuberositas', OLDS('ulnar_tuberosity'));
  put(k, 'uln_incisura_radialis', OLDS('radial_notch'));
  put(k, 'uln_incisura_trochlearis', OLDS('trochlear_notch'));
  put(k, 'uln_corpus', surf(k, axisAt(k, top - 0.52 * L), [0.5, 0, 1]));
  put(k, 'uln_facies_anterior', OLDS('uln_anterior'));
  put(k, 'uln_facies_posterior', OLDS('uln_posterior'));
  put(k, 'uln_facies_medialis', surf(k, axisAt(k, top - 0.6 * L), [1, 0, 0]));
  put(k, 'uln_margo_interosseus', OLDS('uln_interosseous'));
  put(k, 'uln_margo_anterior', extSurf(k, [0.6, 0, 1], v => Math.abs(v.y - (top - 0.42 * L)) < 0.0025));
  put(k, 'uln_margo_posterior', OLDS('uln_posterior_border'));
  put(k, 'uln_crista_m_supinatoris', OLDS('supinator_crest'));
  put(k, 'uln_caput', surf(k, axisAt(k, bot + 0.012, 0.004), [0.4, 0, -1]));
  put(k, 'uln_circumferentia_articularis', surf(k, axisAt(k, bot + 0.012, 0.004), [-1, 0, 0.3]));
  put(k, 'uln_processus_styloideus', OLDS('uln_styloid'));
})();

// ======================= carpus =======================
(() => {
  put('scaphoid', 'scaph_tuberculum', OLDS('scaphoid_tubercle'));
  put('trapezium', 'trapz_tuberculum', OLDS('trapezium_tubercle'));
  put('hamate', 'ham_hamulus', OLDS('hamate_hook'));
  const c = (k) => centroid(verts(k));
  // carpal groove: deepest point of the palmar concavity, over the capitate
  put('capitate', 'carp_sulcus_carpi', surf('capitate', c('capitate'), [0, -0.1, 1]));
  // inconstant os centrale: dorsally between scaphoid, trapezoid and capitate (not in the model)
  const cs = c('scaphoid'), cc = c('capitate'), ct = c('trapezoid');
  let best = null, bv = Infinity;
  for (const v of verts('scaphoid')) { if (v.z > cs.z) continue; const d = v.distanceTo(cc) + v.distanceTo(ct); if (d < bv) { bv = d; best = v; } }
  const s = best ? surf('scaphoid', best, best.clone().sub(cs).normalize().add(new THREE.Vector3(0, 0, -0.6)).normalize(), 0.02) : null;
  put('scaphoid', 'carp_os_centrale', s ? { p: s.p.clone().addScaledVector(s.n, 0.0015), n: s.n } : null);
})();

// ======================= metacarpals and phalanges =======================
function longAxis(k) {
  const vs = verts(k), c = centroid(vs);
  const cov = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  vs.forEach(v => { const d = [v.x - c.x, v.y - c.y, v.z - c.z]; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) cov[i][j] += d[i] * d[j]; });
  let a = new THREE.Vector3(0, 1, 0);
  for (let it = 0; it < 30; it++) a = new THREE.Vector3(cov[0][0] * a.x + cov[0][1] * a.y + cov[0][2] * a.z, cov[1][0] * a.x + cov[1][1] * a.y + cov[1][2] * a.z, cov[2][0] * a.x + cov[2][1] * a.y + cov[2][2] * a.z).normalize();
  if (a.y < 0) a.negate(); // a points proximally (up)
  let lo = Infinity, hi = -Infinity;
  vs.forEach(v => { const s = v.clone().sub(c).dot(a); lo = Math.min(lo, s); hi = Math.max(hi, s); });
  const at = (t) => c.clone().addScaledVector(a, hi - t * (hi - lo)); // t = 0 proximal end, 1 distal end
  const side = (d) => { const s = V3(d); return s.addScaledVector(a, -s.dot(a)).normalize(); };
  return { a, at, side };
}
const PALM = [0, 0, 1], DORS = [0, 0, -1];
for (let i = 1; i <= 5; i++) {
  const mc = `metacarpal_${i}`;
  put(mc, `mc${i}_basis`, OLDS(`mc${i}_base`));
  put(mc, `mc${i}_corpus`, OLDS(`mc${i}_body`));
  put(mc, `mc${i}_caput`, OLDS(`mc${i}_head`));
  const phal = [[`phalanx_prox_${i}`, `pp${i}`], ...(i > 1 ? [[`phalanx_mid_${i}`, `pm${i}`]] : []), [`phalanx_dist_${i}`, `pd${i}`]];
  for (const [k, p] of phal) {
    const L = longAxis(k), dist = p.startsWith('pd');
    put(k, `${p}_basis`, OLDS(`${p}_base`));
    put(k, `${p}_corpus`, OLDS(`${p}_body`));
    if (dist) {
      put(k, `${p}_caput`, surf(k, L.at(0.8), L.side(DORS)));
      put(k, `${p}_tuberositas`, OLDS(`${p}_tuberosity`));
    } else {
      put(k, `${p}_caput`, OLDS(`${p}_head`));
      put(k, `${p}_trochlea`, surf(k, L.at(0.97), L.a.clone().negate().add(L.side(PALM).multiplyScalar(0.8)).normalize()));
    }
  }
}
// styloid process of the 3rd metacarpal: dorsal radial corner of its base
(() => {
  const k = 'metacarpal_3', b = box(k);
  put(k, 'mc3_processus_styloideus', extSurf(k, [-0.55, 0.45, -0.7], v => v.y > b.max.y - 0.012));
})();

// ======================= muscle attachment areas without a TA term =======================
(() => {
  const c = (k) => centroid(verts(k));
  const cap = c('capitate');
  put('capitate', 'att_capitate_palmar', surf('capitate', cap.clone().add(new THREE.Vector3(0, -0.005, 0)), [0, 0, 1]));
  put('trapezoid', 'att_trapezoid_palmar', surf('trapezoid', c('trapezoid'), [0, 0, 1]));
})();

// ======================= soft tissue (kept from landmarks.js) =======================
put('interosseous_membrane', 'membrane_mid', OLDS('membrane_mid'));
put('flexor_retinaculum', 'retinaculum_mid', OLDS('retinaculum_mid'));

window.__ta = out;
export default out;
