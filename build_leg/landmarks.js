// Landmarks on the right lower-limb bones. Frame: x+ medial, y+ up, z+ anterior (metres).
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
function centroid(a) { const c = new THREE.Vector3(); a.forEach(v => c.add(v)); return c.multiplyScalar(1 / Math.max(1, a.length)); }
const slab = (k, y0, y1) => verts(k).filter(v => v.y >= y0 && v.y <= y1);
const axisAt = (k, y, h = 0.004) => centroid(slab(k, y - h, y + h));
const ray = new THREE.Raycaster();
function surf(k, target, dir) {
  const d = V3(dir).normalize();
  ray.set(V3(target).addScaledVector(d, 0.25), d.clone().negate());
  ray.far = 0.5;
  const h = ray.intersectObject(M[k], false)[0];
  if (!h) return null;
  return { p: h.point.clone(), n: h.face.normal.clone().transformDirection(M[k].matrixWorld) };
}
function extSurf(k, dir, filt) {
  const v = ext(k, dir, filt);
  if (!v) return null;
  const c = centroid(verts(k));
  return surf(k, v.clone().lerp(c, 0.02), dir) || { p: v, n: V3(dir).normalize() };
}
const out = [];
const W = (s) => (s && s.p ? { p: V3(s.p), n: V3(s.n) } : null);
const PK = (k, view, u, v, zb) => W(window.pick(k, view, u, v, zb));
const UB = (keys) => { const b = new THREE.Box3(); keys.forEach(k => b.expandByObject(M[k])); return [b.min.toArray(), b.max.toArray()]; };
const put = (bone, id, s) => { if (s) out.push({ bone, id, p: s.p.toArray(), n: s.n.toArray() }); else out.push({ bone, id, missing: true }); };

// ---------------- hip bone ----------------
(() => {
  const k = 'hip_bone', b = box(k);
  const cz = (b.min.z + b.max.z) / 2;
  // acetabulum: the floor of the cup seen from the side
  const acet = surf(k, [b.min.x, b.min.y + 0.345 * (b.max.y - b.min.y), b.min.z + 0.56 * (b.max.z - b.min.z)], [-1, -0.25, 0.3]);
  const ay = acet.p.y;
  const asis = extSurf(k, [0, 0.12, 1], v => v.y > ay + 0.06);
  const aiis = extSurf(k, [0, 0, 1], v => v.y > ay + 0.02 && v.y < asis.p.y - 0.03 && v.x < acet.p.x + 0.03);
  const crest = extSurf(k, [-0.15, 1, 0]);
  const psis = extSurf(k, [0, 0.2, -1], v => v.y > ay + 0.07);
  const tub = extSurf(k, [-0.2, -1, -0.8], v => v.z < cz);
  const symph = extSurf(k, [1, -0.1, 0.25], v => v.y < ay);
  const spine = extSurf(k, [0.55, 0, -1], v => v.y > tub.p.y + 0.025 && v.y < ay + 0.005);
  // posterior border profile between the spine and the posterior iliac spines: deepest point = greater sciatic notch
  let gsn = null;
  for (let y = spine.p.y + 0.012; y < psis.p.y - 0.03; y += 0.002) {
    const back = ext(k, [0, 0, -1], v => Math.abs(v.y - y) < 0.0015);
    if (back && (!gsn || back.z > gsn.z)) gsn = back;
  }
  const gsnS = gsn ? surf(k, [gsn.x - 0.002, gsn.y, gsn.z + 0.004], [-1, 0, -0.3]) : null;
  let lsn = null;
  for (let y = tub.p.y + 0.012; y < spine.p.y - 0.004; y += 0.0015) {
    const back = ext(k, [0, 0, -1], v => Math.abs(v.y - y) < 0.0012);
    if (back && (!lsn || back.z > lsn.z)) lsn = back;
  }
  const lsnS = lsn ? surf(k, [lsn.x - 0.002, lsn.y, lsn.z + 0.003], [-1, 0, -0.4]) : null;
  const tubercle = extSurf(k, [0.25, 0.6, 1], v => v.x > symph.p.x - 0.035 && v.y < ay);
  const pecten = extSurf(k, [0, 1, 0.35], v => Math.abs(v.x - (tubercle.p.x - 0.035)) < 0.004 && v.y < ay + 0.01);
  const pubBody = surf(k, [tubercle.p.x + 0.004, tubercle.p.y - 0.014, cz], [0.2, 0, 1]);
  const infRamus = surf(k, [symph.p.x - 0.012, symph.p.y - 0.028, cz], [0.25, -0.2, 1]);
  const ischRamus = surf(k, [(symph.p.x + tub.p.x) / 2 - 0.005, (symph.p.y + tub.p.y) / 2 - 0.008, cz], [0.1, -0.6, 1]);
  // obturator foramen: walk down from the acetabulum floor in the side view until the ray misses, then back to the rim
  let rim = null;
  for (let t = 0.015; t < 0.08; t += 0.001) {
    const s = surf(k, [acet.p.x, ay - t, acet.p.z + 0.008], [-1, 0, 0.25]);
    if (!s) { rim = surf(k, [acet.p.x, ay - t - 0.012, acet.p.z + 0.008], [-1, 0, 0.25]); break; }
  }
  const glPost = window.pick(k, 'lat', 0.27, 0.25), glMid = window.pick(k, 'lat', 0.46, 0.24), glLow = window.pick(k, 'lat', 0.56, 0.42);
  const fossa = window.pick(k, 'med', 0.36, 0.3), auric = window.pick(k, 'med', 0.61, 0.33), arcuate = window.pick(k, 'med', 0.44, 0.52);
  const pelvicPub = surf(k, [symph.p.x - 0.014, symph.p.y + 0.004, cz], [0.3, 0.1, -1]);
  put(k, 'iliac_crest', crest); put(k, 'asis', asis); put(k, 'aiis', aiis); put(k, 'psis', psis);
  put(k, 'gluteal_post', W(glPost)); put(k, 'gluteal_mid', W(glMid)); put(k, 'gluteal_low', W(glLow));
  put(k, 'iliac_fossa', W(fossa)); put(k, 'auricular_hip', W(auric)); put(k, 'arcuate_line', W(arcuate));
  put(k, 'acetabulum', PK(k, 'lat', 0.53, 0.66)); put(k, 'greater_sciatic_notch', PK(k, 'lat', 0.445, 0.49)); put(k, 'ischial_spine', spine);
  put(k, 'lesser_sciatic_notch', lsnS); put(k, 'ischial_tuberosity', tub); put(k, 'obturator_foramen', rim);
  put(k, 'pubic_tubercle', tubercle); put(k, 'pecten_pubis', pecten); put(k, 'pubic_body', PK(k, 'ant', 0.73, 0.77));
  put(k, 'inferior_pubic_ramus', PK(k, 'ant', 0.66, 0.86)); put(k, 'ischial_ramus', ischRamus); put(k, 'symphyseal_surface', symph);
  put(k, 'pubis_pelvic', pelvicPub);
})();

// ---------------- sacrum (with the coccyx) ----------------
(() => {
  const k = 'sacrum', b = box(k);
  const cx = (b.min.x + b.max.x) / 2;
  const mid = (v) => Math.abs(v.x - cx) < 0.008;
  const prom = extSurf(k, [0, 0.45, 1], mid);
  const base = extSurf(k, [0, 1, 0.35], mid);
  const apexCoc = extSurf(k, [0, -1, 0.2], mid);
  const H = b.max.y - b.min.y;
  const pelvic = surf(k, [cx - 0.033, b.max.y - 0.5 * H, b.max.z], [-0.15, 0.2, 1]);
  const dorsal = surf(k, [cx - 0.03, b.max.y - 0.48 * H, b.min.z], [-0.3, 0, -1]);
  const crestM = extSurf(k, [0, 0, -1], v => mid(v) && v.y < b.max.y - 0.3 * H && v.y > b.max.y - 0.55 * H);
  const lat = extSurf(k, [-1, 0, 0], v => v.y > b.max.y - 0.45 * H);
  const yc = b.min.y + 0.1 * H;
  const coc = surf(k, [cx, yc, (b.min.z + b.max.z) / 2], [-0.5, 0, -1]);
  put(k, 'sacral_base', base); put(k, 'promontory', prom); put(k, 'sacral_pelvic', pelvic);
  put(k, 'sacral_dorsal', PK(k, 'post', 0.7, 0.55)); put(k, 'median_sacral_crest', crestM); put(k, 'auricular_sacrum', lat);
  put(k, 'coccyx', PK(k, 'ant', 0.42, 0.82)); put(k, 'coccyx_apex', apexCoc);
})();

// ---------------- femur ----------------
(() => {
  const k = 'femur', b = box(k), top = b.max.y, bot = b.min.y, L = top - bot;
  const cx = axisAt(k, top - 0.15).x;
  const headTop = ext(k, [0.35, 1, 0], v => v.x > cx);
  const hc = headTop.clone().add(new THREE.Vector3(-0.008, -0.022, 0));
  const hcen = centroid(verts(k).filter(v => v.distanceTo(hc) < 0.03 && v.x > cx + 0.01));
  const head = surf(k, hcen, [0.7, 0.6, 0.5]);
  const fovea = surf(k, hcen, [1, -0.15, -0.1]);
  const gt = extSurf(k, [-0.55, 1, -0.1], v => v.x < cx);
  const lt = extSurf(k, [0.7, -0.15, -0.8], v => v.y < top - 0.055 && v.y > top - 0.12);
  const neckP = hcen.clone().lerp(new THREE.Vector3(gt.p.x, hcen.y - 0.02, hcen.z), 0.38);
  const neck = surf(k, neckP, [0, 0.3, 1]);
  const itLine = surf(k, [(gt.p.x + lt.p.x) / 2, (gt.p.y + lt.p.y) / 2 - 0.012, hcen.z], [0, 0, 1]);
  const itCrest = surf(k, [(gt.p.x + lt.p.x) / 2 - 0.004, (gt.p.y + lt.p.y) / 2 - 0.008, hcen.z], [-0.2, 0, -1]);
  const fossa = surf(k, [gt.p.x + 0.014, gt.p.y - 0.022, gt.p.z - 0.004], [0.55, 0.25, -1]);
  const glut = surf(k, axisAt(k, top - 0.13), [-0.7, 0, -1]);
  const pect = surf(k, axisAt(k, top - 0.12), [0.6, 0, -1]);
  const ymid = top - 0.48 * L;
  const la = extSurf(k, [0, 0, -1], v => Math.abs(v.y - ymid) < 0.003);
  const laLat = surf(k, [la.p.x - 0.005, la.p.y + 0.02, la.p.z + 0.003], [-0.45, 0, -1]);
  const laMed = surf(k, [la.p.x + 0.005, la.p.y + 0.02, la.p.z + 0.003], [0.45, 0, -1]);
  const antBody = surf(k, axisAt(k, top - 0.3 * L), [0, 0, 1]);
  const dist = (v) => v.y < bot + 0.075;
  const me = extSurf(k, [1, 0, 0], dist), le = extSurf(k, [-1, 0, 0], dist);
  const addT = extSurf(k, [1, 0.8, -0.2], v => v.y < me.p.y + 0.035 && v.y > me.p.y + 0.008);
  const dc = axisAt(k, bot + 0.03, 0.006);
  const mc = extSurf(k, [0.3, -1, -0.5], v => v.x > dc.x + 0.008);
  const lc = extSurf(k, [-0.3, -1, -0.5], v => v.x < dc.x - 0.008);
  const patS = surf(k, [dc.x, bot + 0.03, dc.z], [0, 0, 1]);
  const icf = surf(k, [dc.x, bot + 0.012, dc.z], [0, -0.7, -1]);
  const pop = surf(k, axisAt(k, bot + 0.085), [0, 0, -1]);
  const gmedO = surf(k, [me.p.x - 0.01, bot + 0.055, dc.z], [0.3, 0, -1]);
  const glatO = surf(k, [le.p.x + 0.008, bot + 0.055, dc.z], [-0.6, 0, -1]);
  const plan = surf(k, [le.p.x + 0.012, bot + 0.07, dc.z], [-0.3, 0, -1]);
  const popO = surf(k, [le.p.x, le.p.y - 0.013, le.p.z], [-1, -0.15, 0.1]);
  put(k, 'femoral_head', head); put(k, 'fovea_capitis', fovea); put(k, 'femoral_neck', neck);
  put(k, 'greater_trochanter', gt); put(k, 'trochanteric_fossa', fossa); put(k, 'lesser_trochanter', lt);
  put(k, 'intertrochanteric_line', itLine); put(k, 'intertrochanteric_crest', PK(k, 'post', 0.62, 0.68, [[-0.145, 0.74, 0.04], [-0.033, 0.845, 0.12]]));
  put(k, 'gluteal_tuberosity', glut); put(k, 'pectineal_line', pect);
  put(k, 'linea_aspera_lat', laLat); put(k, 'linea_aspera_med', laMed); put(k, 'femur_ant_body', antBody);
  put(k, 'popliteal_surface', pop); put(k, 'adductor_tubercle', addT);
  put(k, 'medial_epicondyle_f', me); put(k, 'lateral_epicondyle_f', le);
  put(k, 'gastroc_med_origin', PK(k, 'post', 0.2, 0.42, [[-0.145, 0.4, 0.04], [-0.033, 0.5, 0.12]])); put(k, 'gastroc_lat_origin', glatO); put(k, 'plantaris_origin', plan);
  put(k, 'popliteus_origin', popO); put(k, 'medial_condyle_f', mc); put(k, 'lateral_condyle_f', lc);
  put(k, 'patellar_surface', patS); put(k, 'intercondylar_fossa', icf);
})();

// ---------------- patella ----------------
(() => {
  const k = 'patella';
  const c = centroid(verts(k));
  put(k, 'patella_base', extSurf(k, [0, 1, 0.2]));
  put(k, 'patella_apex', extSurf(k, [0, -1, 0.2]));
  put(k, 'patella_anterior', surf(k, c, [0, 0, 1]));
  put(k, 'patella_articular', surf(k, c, [0, 0, -1]));
})();

// ---------------- tibia ----------------
(() => {
  const k = 'tibia', b = box(k), top = b.max.y, bot = b.min.y, L = top - bot;
  const prox = (v) => v.y > top - 0.045;
  const mc = extSurf(k, [1, 0, 0], prox);
  const lc = extSurf(k, [-1, 0, 0.3], prox);
  const ce = centroid(slab(k, top - 0.03, top - 0.01));
  const em = extSurf(k, [0, 1, 0], v => Math.abs(v.x - ce.x) < 0.008 && Math.abs(v.z - ce.z) < 0.012);
  const tub = extSurf(k, [0, 0, 1], v => v.y < top - 0.03 && v.y > top - 0.075);
  const gerdy = surf(k, [lc.p.x + 0.012, top - 0.028, ce.z + 0.01], [-0.5, 0, 1]);
  const pes = surf(k, axisAt(k, tub.p.y - 0.012), [1, 0, 0.55]);
  const semim = surf(k, [mc.p.x - 0.008, top - 0.028, ce.z], [0.5, 0, -1]);
  const fh = centroid(verts('fibula').filter(v => v.y > box('fibula').max.y - 0.025));
  const fibFacet = surf(k, fh, [-0.7, 0, -0.5]);
  const popI = surf(k, axisAt(k, top - 0.065), [0.35, 0, -1]);
  const soleal = surf(k, axisAt(k, top - 0.105), [-0.15, 0, -1]);
  const post = surf(k, axisAt(k, top - 0.2), [0.1, 0, -1]);
  const latS = surf(k, axisAt(k, top - 0.12), [-1, 0, 0.35]);
  const antB = extSurf(k, [0.1, 0, 1], v => Math.abs(v.y - (top - 0.2)) < 0.003);
  const medS = surf(k, axisAt(k, top - 0.22), [1, 0, 0.45]);
  const mm = extSurf(k, [0.7, -1, 0], v => v.y < bot + 0.03);
  const fd = centroid(verts('fibula').filter(v => v.y < bot + 0.055 && v.y > bot + 0.035));
  const fibNotch = surf(k, fd, [-1, 0, -0.35]);
  const infArt = surf(k, axisAt(k, bot + 0.022, 0.003), [0, -1, 0]);
  put(k, 'medial_condyle_t', mc); put(k, 'lateral_condyle_t', lc); put(k, 'intercondylar_eminence', em);
  put(k, 'gerdy_tubercle', gerdy); put(k, 'tibial_tuberosity', tub); put(k, 'pes_anserinus', pes);
  put(k, 'semimembranosus_ins', semim); put(k, 'fibular_facet', fibFacet); put(k, 'popliteus_ins', popI);
  put(k, 'soleal_line', soleal); put(k, 'tibia_posterior', post); put(k, 'tibia_lateral', latS);
  put(k, 'tibia_anterior_border', surf(k, axisAt(k, top - 0.2), [0, 0, 1])); put(k, 'tibia_medial', medS); put(k, 'medial_malleolus', mm);
  put(k, 'fibular_notch', fibNotch); put(k, 'tibia_inferior_articular', infArt);
})();

// ---------------- fibula ----------------
(() => {
  const k = 'fibula', b = box(k), top = b.max.y, bot = b.min.y;
  put(k, 'fibular_head', surf(k, axisAt(k, top - 0.012), [-1, 0.2, 0]));
  put(k, 'fibular_neck', surf(k, axisAt(k, top - 0.035), [-1, 0, 0.3]));
  put(k, 'fibula_lat_upper', surf(k, axisAt(k, top - 0.1), [-1, 0, 0]));
  put(k, 'fibula_lat_lower', surf(k, axisAt(k, top - 0.22), [-1, 0, 0]));
  put(k, 'fibula_ant_upper', surf(k, axisAt(k, top - 0.08), [0, 0, 1]));
  put(k, 'fibula_med_middle', surf(k, axisAt(k, top - 0.17), [0.5, 0, 1]));
  put(k, 'fibula_ant_lower', surf(k, axisAt(k, bot + 0.09), [0, 0, 1]));
  put(k, 'fibula_post_upper', surf(k, axisAt(k, top - 0.05), [0, 0, -1]));
  put(k, 'fibula_post_lower', surf(k, axisAt(k, top - 0.21), [-0.3, 0, -1]));
  put(k, 'fibula_medial_crest', surf(k, axisAt(k, top - 0.13), [1, 0, -0.5]));
  put(k, 'lateral_malleolus', extSurf(k, [-1, -0.5, 0], v => v.y < bot + 0.03));
})();

// ---------------- tarsus ----------------
(() => {
  const c = (k) => centroid(verts(k));
  put('talus', 'talus_trochlea', surf('talus', c('talus'), [0, 1, 0]));
  put('talus', 'talus_head', extSurf('talus', [0.25, 0, 1]));
  put('talus', 'talus_posterior', extSurf('talus', [0, -0.3, -1]));
  const C = 'calcaneus', cc = c(C), cb = box(C);
  put(C, 'calcaneal_tuberosity', extSurf(C, [0, 0.15, -1]));
  put(C, 'calc_medial_process', extSurf(C, [0.5, -1, -0.7], v => v.z < cc.z));
  put(C, 'calc_lateral_process', extSurf(C, [-0.6, -1, -0.6], v => v.z < cc.z));
  put(C, 'sustentaculum', extSurf(C, [1, 0.25, 0.2], v => v.y > cc.y - 0.005 && v.z > cc.z - 0.01));
  const ant = ext(C, [0, 0, 1]);
  const FT = ['talus', 'calcaneus', 'navicular', 'cuboid', 'cuneiform_med', 'cuneiform_int', 'cuneiform_lat', 'metatarsal_1', 'metatarsal_2', 'metatarsal_3', 'metatarsal_4', 'metatarsal_5', 'sesamoid_pedis'];
  put(C, 'calc_dorsal_anterior', PK(C, 'lat', 0.36, 0.49, UB(FT)));
  put(C, 'calc_plantar', surf(C, [cc.x, cc.y, cc.z + 0.01], [0, -1, 0]));
  put('navicular', 'navicular_tuberosity', extSurf('navicular', [1, -0.35, 0]));
  put('cuboid', 'cuboid_groove', surf('cuboid', c('cuboid'), [-0.2, -1, 0]));
  put('cuneiform_med', 'cuneiform_med_plantar', extSurf('cuneiform_med', [1, -1, 0]));
  put('cuneiform_int', 'cuneiform_int_dorsal', surf('cuneiform_int', c('cuneiform_int'), [0, 1, 0]));
  put('cuneiform_lat', 'cuneiform_lat_plantar', surf('cuneiform_lat', c('cuneiform_lat'), [0, -1, 0]));
  put('sesamoid_pedis', 'sesamoid_plantar', surf('sesamoid_pedis', c('sesamoid_pedis'), [0, -1, 0]));
})();

// ---------------- metatarsals and toes ----------------
function longPins(k, names, side) {
  const vs = verts(k), c = centroid(vs);
  const cov = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  vs.forEach(v => { const d = [v.x - c.x, v.y - c.y, v.z - c.z]; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) cov[i][j] += d[i] * d[j]; });
  let a = new THREE.Vector3(0, 0, 1);
  for (let it = 0; it < 30; it++) a = new THREE.Vector3(cov[0][0] * a.x + cov[0][1] * a.y + cov[0][2] * a.z, cov[1][0] * a.x + cov[1][1] * a.y + cov[1][2] * a.z, cov[2][0] * a.x + cov[2][1] * a.y + cov[2][2] * a.z).normalize();
  if (a.z > 0) a.negate(); // a points proximally (back toward the heel)
  let lo = Infinity, hi = -Infinity;
  vs.forEach(v => { const s = v.clone().sub(c).dot(a); lo = Math.min(lo, s); hi = Math.max(hi, s); });
  const at = (t) => c.clone().addScaledVector(a, hi - t * (hi - lo));
  const sd = V3(side); sd.addScaledVector(a, -sd.dot(a)).normalize();
  names.forEach(([id, t]) => put(k, id, surf(k, at(t), sd)));
}
const UP = [0, 1, 0.1];
for (let i = 1; i <= 5; i++) {
  longPins(`metatarsal_${i}`, [[`mt${i}_base`, 0.12], [`mt${i}_body`, 0.5], [`mt${i}_head`, 0.88]], UP);
  longPins(`toe_prox_${i}`, [[`tp${i}_base`, 0.15], [`tp${i}_body`, 0.5], [`tp${i}_head`, 0.85]], UP);
  if (i > 1) longPins(`toe_mid_${i}`, [[`tm${i}_base`, 0.2], [`tm${i}_head`, 0.8]], UP);
  longPins(`toe_dist_${i}`, [[`td${i}_base`, 0.2], [`td${i}_tuberosity`, 0.85]], UP);
}
put('metatarsal_5', 'mt5_tuberosity', extSurf('metatarsal_5', [-1, -0.15, -0.7]));
put('metatarsal_1', 'mt1_base_plantar', extSurf('metatarsal_1', [0.4, -1, -1]));

window.__pins = out;
export default out;
