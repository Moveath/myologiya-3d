// Positions of the Terminologia Anatomica (TA98) terms that landmarks.js does not already place,
// on the right lower-limb bones. Frame: x+ medial, y+ up, z+ anterior (metres).
// Run after landmarks.js (uses window.__pins for anchors). Output: window.__ta
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
// surface point hit by a ray travelling toward `target` from the side `dir` points to (first hit from outside)
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

// least-squares sphere through points
function sphere(pts) {
  const N = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], r = [0, 0, 0, 0];
  pts.forEach(v => { const a = [v.x, v.y, v.z, 1], b = -(v.x * v.x + v.y * v.y + v.z * v.z); for (let j = 0; j < 4; j++) { r[j] += a[j] * b; for (let k = 0; k < 4; k++) N[j][k] += a[j] * a[k]; } });
  for (let i = 0; i < 4; i++) { let p = i; for (let k = i + 1; k < 4; k++) if (Math.abs(N[k][i]) > Math.abs(N[p][i])) p = k; [N[i], N[p]] = [N[p], N[i]]; [r[i], r[p]] = [r[p], r[i]];
    for (let k = i + 1; k < 4; k++) { const f = N[k][i] / N[i][i]; for (let j = i; j < 4; j++) N[k][j] -= f * N[i][j]; r[k] -= f * r[i]; } }
  const x = [0, 0, 0, 0]; for (let i = 3; i >= 0; i--) { let s = r[i]; for (let j = i + 1; j < 4; j++) s -= N[i][j] * x[j]; x[i] = s / N[i][i]; }
  const c = new THREE.Vector3(-x[0] / 2, -x[1] / 2, -x[2] / 2);
  return { c, R: Math.sqrt(c.lengthSq() - x[3]) };
}

// ======================= hip bone (os coxae) =======================
(() => {
  const k = 'hip_bone';
  // femoral head sphere = centre of the acetabulum
  const fb = box('femur'), hp = OLD('femoral_head');
  const head = sphere(verts('femur').filter(v => v.distanceTo(hp) < 0.035 && v.y > fb.max.y - 0.06));
  window.HEAD = { c: head.c.toArray(), R: head.R };
  const c = head.c, R = head.R;
  // acetabular axis (opening direction) from the cup surface
  const cup = verts(k).filter(v => v.distanceTo(c) - R < 0.005);
  const A = new THREE.Vector3(); cup.forEach(v => A.add(v.clone().sub(c).normalize())); A.negate().normalize();
  const Tsup = new THREE.Vector3(0, 1, 0).addScaledVector(A, -A.y).normalize();
  const Bpost = new THREE.Vector3().crossVectors(Tsup, A).normalize(); if (Bpost.z > 0) Bpost.negate();
  // surface point of the outer surface at a given depth band (mm beyond the head sphere) in direction dir
  const band = (lo, hi, dir) => {
    let best = null, bv = -Infinity;
    for (const v of verts(k)) { const d = v.distanceTo(c) - R; if (d < lo / 1000 || d > hi / 1000) continue; const s = v.clone().sub(c).normalize().dot(dir); if (s > bv) { bv = s; best = v; } }
    return best;
  };
  const AC = { d: [-0.82, -0.3, 0.48], up: [0, 1, 0] };
  const ZA = Z(c, 0.034);
  put(k, 'cox_acetabulum', PK(k, AC, 0.43, 0.45, ZA));
  put(k, 'cox_fossa_acetabuli', PK(k, AC, 0.52, 0.55, ZA));
  put(k, 'cox_facies_lunata', PK(k, AC, 0.40, 0.30, ZA));
  put(k, 'cox_incisura_acetabuli', PK(k, AC, 0.62, 0.64, ZA));
  const rimDir = Tsup.clone().addScaledVector(Bpost, 0.35).normalize();
  const lv = band(8, 10.5, rimDir);
  put(k, 'cox_limbus_acetabuli', { p: lv.clone(), n: lv.clone().sub(c).normalize().addScaledVector(A, 0.6).normalize() });
  const sv = band(17, 22, Tsup);
  put(k, 'cox_sulcus_supraacetabularis', surf(k, sv, A.clone().multiplyScalar(0.8).add(Tsup).normalize()));
  // body of the ilium: its pelvic surface below the arcuate line, above the level of the acetabulum
  put(k, 'cox_corpus_ossis_ilii', PK(k, 'med', 0.42, 0.37, Z([-0.05, 0.835, 0.08], 0.05)));

  // wing: Ni = normal of the internal (iliac fossa) side, e1 forward, e2 up within the wing plane
  const Ni = new THREE.Vector3(0.756, 0.37, 0.541).normalize();
  const e2 = new THREE.Vector3(0, 1, 0).addScaledVector(Ni, -Ni.y).normalize();
  const e1 = new THREE.Vector3().crossVectors(Ni, e2).normalize(); // forward
  const GL = { d: Ni.clone().negate().toArray(), up: [0, 1, 0] };
  const upper = verts(k).filter(v => v.y > c.y + 0.045);
  // crest point whose in-plane outward normal makes angle deg with the forward axis (0 = forward, 90 = up)
  const crestAt = (deg) => {
    const f = deg * Math.PI / 180, U = e1.clone().multiplyScalar(Math.cos(f)).addScaledVector(e2, Math.sin(f));
    let best = null, bvv = -Infinity;
    for (const v of upper) { const s = v.dot(U); if (s > bvv) { bvv = s; best = v; } }
    return { T: best.clone(), U };
  };
  put(k, 'cox_crista_iliaca', OLDS('iliac_crest'));
  // the three parts of the crest at one cross-section, about 8 cm behind the anterior superior spine
  const cs = crestAt(68), cIn = cs.T.clone().addScaledVector(cs.U, -0.004);
  put(k, 'cox_labium_externum', surf(k, cIn, cs.U.clone().addScaledVector(Ni, -1.1)));
  put(k, 'cox_linea_intermedia', surf(k, cIn, cs.U));
  put(k, 'cox_labium_internum', surf(k, cIn, cs.U.clone().addScaledVector(Ni, 1.1)));
  // tubercle of the crest: outer lip about 5 cm behind the anterior superior spine
  const tb = crestAt(40);
  put(k, 'cox_tuberculum_iliacum', surf(k, tb.T.clone().addScaledVector(tb.U, -0.004), tb.U.clone().addScaledVector(Ni, -1.4)));
  put(k, 'cox_sias', OLDS('asis')); put(k, 'cox_siai', OLDS('aiis')); put(k, 'cox_sips', OLDS('psis'));
  // gluteal surface, picked perpendicular to the wing. Lines after Gray: anterior from the crest ~4 cm behind
  // the ASIS to the upper sciatic notch; posterior from the crest ~5 cm in front of the PSIS to the upper notch;
  // inferior from above the AIIS to the middle of the notch.
  put(k, 'cox_ala', PK(k, GL, 0.47, 0.21));
  put(k, 'cox_facies_glutea', PK(k, GL, 0.63, 0.36));
  put(k, 'cox_linea_glutea_anterior', PK(k, GL, 0.57, 0.29));
  put(k, 'cox_linea_glutea_posterior', PK(k, GL, 0.385, 0.30));
  put(k, 'cox_linea_glutea_inferior', PK(k, GL, 0.60, 0.47));
  // posterior inferior spine: lower end of the posterior border, where it turns into the greater sciatic notch
  put(k, 'cox_sipi', PK(k, GL, 0.362, 0.462));
  put(k, 'cox_incisura_ischiadica_major', OLDS('greater_sciatic_notch'));
  // internal surface
  put(k, 'cox_fossa_iliaca', OLDS('iliac_fossa'));
  put(k, 'cox_linea_arcuata', OLDS('arcuate_line'));
  const ZM = Z([-0.05, 0.885, 0.035], 0.05);
  put(k, 'cox_facies_auricularis', PK(k, 'med', 0.25, 0.40, ZM));
  put(k, 'cox_facies_sacropelvica', PK(k, 'med', 0.47, 0.30, ZM));
  put(k, 'cox_tuberositas_iliaca', PK(k, 'med', 0.44, 0.14, ZM));

  // ischium
  const ZF2 = [[-0.12, 0.74, 0.04], [-0.01, 0.85, 0.15]];
  put(k, 'cox_corpus_ossis_ischii', PK(k, AC, 0.28, 0.54, ZF2));
  put(k, 'cox_ramus_ossis_ischii', PK(k, AC, 0.37, 0.70, ZF2));
  put(k, 'cox_tuber_ischiadicum', OLDS('ischial_tuberosity'));
  put(k, 'cox_spina_ischiadica', OLDS('ischial_spine'));
  put(k, 'cox_incisura_ischiadica_minor', OLDS('lesser_sciatic_notch'));
  put(k, 'cox_ramus_ischiopubicus', PK(k, AC, 0.51, 0.71, ZF2));
  put(k, 'cox_foramen_obturatum', OLDS('obturator_foramen'));

  // pubis: superior ramus seen onto its pectineal surface (image: left = pubic tubercle, bottom edge = pecten,
  // top edge = obturator crest)
  const T = OLD('pubic_tubercle'), E0 = new THREE.Vector3(-0.052, 0.842, 0.108);
  const a = T.clone().sub(E0).normalize();
  const dP = new THREE.Vector3(-0.052, 0.787, 0.614).normalize();
  const PU2 = { d: dP.toArray(), up: new THREE.Vector3().crossVectors(a, dP).toArray() };
  const ZP = Z([-0.04, 0.825, 0.125], 0.04);
  put(k, 'cox_corpus_ossis_pubis', OLDS('pubic_body'));
  put(k, 'cox_tuberculum_pubicum', OLDS('pubic_tubercle'));
  put(k, 'cox_facies_symphysialis', OLDS('symphyseal_surface'));
  put(k, 'cox_crista_pubica', PK(k, 'sup', 0.60, 0.60, Z([-0.015, 0.81, 0.14], 0.022)));
  put(k, 'cox_ramus_superior_ossis_pubis', PK(k, PU2, 0.50, 0.47, ZP));
  put(k, 'cox_eminentia_iliopubica', PK(k, PU2, 0.70, 0.49, ZP));
  put(k, 'cox_pecten_ossis_pubis', PK(k, PU2, 0.45, 0.52, ZP));
  put(k, 'cox_crista_obturatoria', PK(k, PU2, 0.45, 0.445, ZP));
  // obturator groove between the two obturator tubercles at the upper margin of the foramen
  const ZF = [[-0.12, 0.77, 0.04], [-0.03, 0.86, 0.15]];
  const toa = PK(k, AC, 0.72, 0.555, ZF), top = PK(k, AC, 0.615, 0.553, ZF);
  const mid = toa.p.clone().lerp(top.p, 0.5), dn = new THREE.Vector3(0.1, -1, -0.35).normalize();
  put(k, 'cox_sulcus_obturatorius', surf(k, mid.clone().addScaledVector(dn, -0.004), dn, 0.016));
  put(k, 'cox_tuberculum_obturatorium_anterius', toa);
  put(k, 'cox_tuberculum_obturatorium_posterius', top);
  put(k, 'cox_ramus_inferior_ossis_pubis', PK(k, AC, 0.72, 0.60, ZF2));
})();

// ======================= sacrum (with the coccyx in one mesh) =======================
// Paired features are placed on the right side, like the rest of the right limb.
(() => {
  const k = 'sacrum';
  const ZS = Z([0.001, 0.875, 0.05], 0.065);
  const SAP = { d: [-0.015, -0.553, 0.833], up: [0, 1, 0] };  // onto the pelvic surface (image left = body right)
  const SDO = { d: [0.015, 0.553, -0.833], up: [0, 1, 0] };   // onto the dorsal surface (image right = body right)
  put(k, 'sac_basis', OLDS('sacral_base'));
  put(k, 'sac_promontorium', OLDS('promontory'));
  put(k, 'sac_ala', PK(k, SAP, 0.28, 0.31, ZS));
  put(k, 'sac_processus_articularis_superior', PK(k, SDO, 0.61, 0.24, ZS));
  put(k, 'sac_pars_lateralis', PK(k, SAP, 0.32, 0.56, ZS));
  put(k, 'sac_facies_auricularis', PK(k, 'lat', 0.47, 0.42, Z([-0.03, 0.88, 0.05], 0.06)));
  put(k, 'sac_tuberositas', PK(k, SDO, 0.69, 0.36, ZS));
  put(k, 'sac_facies_pelvica', PK(k, SAP, 0.50, 0.61, ZS));
  put(k, 'sac_lineae_transversae', PK(k, SAP, 0.50, 0.45, ZS));
  put(k, 'sac_foramina_sacralia_anteriora', PK(k, SAP, 0.385, 0.435, ZS));
  // intervertebral foramina lie inside the bone: medial wall of the right S1 tunnel between the two openings
  {
    const r = window.rayAt(k, SAP, 0.385, 0.405, ZS);
    const o = V3(r.o), d = V3(r.dir);
    const pc = new THREE.Vector3(0.0073, 0.8898, 0.0468), pn = new THREE.Vector3(0.0148, 0.553, -0.833).normalize();
    const t = pc.clone().sub(o).dot(pn) / d.dot(pn);
    const mid = o.clone().addScaledVector(d, t);  // centre of the tunnel, halfway through the bone
    M[k].material.side = THREE.DoubleSide;
    ray.set(mid, new THREE.Vector3(1, 0, 0)); ray.far = 0.03;
    const h = ray.intersectObject(M[k], false)[0];
    M[k].material.side = THREE.FrontSide;
    put(k, 'sac_foramina_intervertebralia', h ? { p: h.point.clone(), n: new THREE.Vector3(-1, 0, 0) } : null);
    window.__ivf = { mid: mid.toArray(), hit: h ? h.point.toArray() : null };
  }
  put(k, 'sac_facies_dorsalis', PK(k, SDO, 0.66, 0.50, ZS));
  put(k, 'sac_crista_sacralis_mediana', PK(k, SDO, 0.50, 0.45, ZS));
  put(k, 'sac_foramina_sacralia_posteriora', PK(k, SDO, 0.635, 0.52, ZS));
  put(k, 'sac_crista_sacralis_medialis', PK(k, SDO, 0.555, 0.56, ZS));
  put(k, 'sac_crista_sacralis_lateralis', PK(k, SDO, 0.67, 0.58, ZS));
  put(k, 'sac_cornu_sacrale', PK(k, SDO, 0.56, 0.765, ZS));
  put(k, 'sac_canalis_sacralis', PK(k, SDO, 0.50, 0.30, ZS));
  put(k, 'sac_hiatus_sacralis', PK(k, SDO, 0.505, 0.75, ZS));
  put(k, 'sac_apex', PK(k, SAP, 0.50, 0.785, ZS));
  // coccyx
  put(k, 'coc_os_coccygis', OLDS('coccyx'));
  put(k, 'coc_cornu_coccygeum', PK(k, SDO, 0.545, 0.81, ZS));
})();

// ======================= femur =======================
(() => {
  const k = 'femur', b = box(k), top = b.max.y, bot = b.min.y, L = top - bot;
  put(k, 'fem_caput', OLDS('femoral_head'));
  put(k, 'fem_fovea_capitis', OLDS('fovea_capitis'));
  put(k, 'fem_collum', OLDS('femoral_neck'));
  put(k, 'fem_trochanter_major', OLDS('greater_trochanter'));
  put(k, 'fem_fossa_trochanterica', OLDS('trochanteric_fossa'));
  put(k, 'fem_trochanter_minor', OLDS('lesser_trochanter'));
  put(k, 'fem_linea_intertrochanterica', OLDS('intertrochanteric_line'));
  const ZP = Z([-0.1, 0.77, 0.08], 0.06);
  // intertrochanteric crest: its lower half; the quadrate tubercle a little above the middle of the crest
  put(k, 'fem_crista_intertrochanterica', PK(k, 'post', 0.47, 0.55, ZP));
  put(k, 'fem_tuberculum_quadratum', PK(k, 'post', 0.555, 0.42, ZP));
  const ZS = Z([-0.105, 0.7, 0.08], 0.07);
  put(k, 'fem_trochanter_tertius', PK(k, 'post', 0.575, 0.30, ZS));
  put(k, 'fem_tuberositas_glutea', OLDS('gluteal_tuberosity'));
  put(k, 'fem_linea_pectinea', OLDS('pectineal_line'));
  put(k, 'fem_corpus', surf(k, axisAt(k, top - 0.5 * L), [0, 0, 1]));
  const ymid = top - 0.48 * L;
  put(k, 'fem_linea_aspera', extSurf(k, [0, 0, -1], v => Math.abs(v.y - ymid) < 0.003));
  put(k, 'fem_labium_laterale', OLDS('linea_aspera_lat'));
  put(k, 'fem_labium_mediale', OLDS('linea_aspera_med'));
  const ZD = Z([-0.08, 0.45, 0.07], 0.06);
  put(k, 'fem_facies_poplitea', OLDS('popliteal_surface'));
  put(k, 'fem_linea_supracondylaris_medialis', PK(k, 'post', 0.39, 0.25, ZD));
  put(k, 'fem_linea_supracondylaris_lateralis', PK(k, 'post', 0.62, 0.20, ZD));
  put(k, 'fem_condylus_medialis', OLDS('medial_condyle_f'));
  put(k, 'fem_epicondylus_medialis', OLDS('medial_epicondyle_f'));
  put(k, 'fem_tuberculum_adductorium', OLDS('adductor_tubercle'));
  put(k, 'fem_condylus_lateralis', OLDS('lateral_condyle_f'));
  put(k, 'fem_epicondylus_lateralis', OLDS('lateral_epicondyle_f'));
  // popliteal groove: from the pit below the lateral epicondyle obliquely up and back
  put(k, 'fem_sulcus_popliteus', PK(k, 'lat', 0.39, 0.63, Z([-0.08, 0.44, 0.07], 0.045)));
  put(k, 'fem_facies_patellaris', OLDS('patellar_surface'));
  put(k, 'fem_fossa_intercondylaris', OLDS('intercondylar_fossa'));
  // intercondylar line: ridge separating the fossa from the popliteal surface
  put(k, 'fem_linea_intercondylaris', PK(k, 'post', 0.46, 0.585, ZD));
})();

// ======================= patella =======================
put('patella', 'pat_basis', OLDS('patella_base'));
put('patella', 'pat_apex', OLDS('patella_apex'));
put('patella', 'pat_facies_articularis', OLDS('patella_articular'));
put('patella', 'pat_facies_anterior', OLDS('patella_anterior'));

// ======================= tibia =======================
(() => {
  const k = 'tibia', b = box(k), top = b.max.y, bot = b.min.y, L = top - bot;
  const ZT = Z([-0.077, 0.39, 0.07], 0.045);
  // plateau seen from above (image: up = back, right = medial); tubercles = the two summits of the eminence
  put(k, 'tib_facies_articularis_superior', PK(k, 'sup', 0.70, 0.45, ZT));
  put(k, 'tib_condylus_medialis', OLDS('medial_condyle_t'));
  put(k, 'tib_condylus_lateralis', OLDS('lateral_condyle_t'));
  put(k, 'tib_facies_articularis_fibularis', OLDS('fibular_facet'));
  put(k, 'tib_area_intercondylaris_anterior', PK(k, 'sup', 0.51, 0.60, ZT));
  put(k, 'tib_area_intercondylaris_posterior', PK(k, 'sup', 0.54, 0.29, ZT));
  put(k, 'tib_eminentia_intercondylaris', PK(k, 'sup', 0.54, 0.43, ZT));
  put(k, 'tib_tuberculum_intercondylare_mediale', PK(k, 'sup', 0.60, 0.43, ZT));
  put(k, 'tib_tuberculum_intercondylare_laterale', PK(k, 'sup', 0.48, 0.43, ZT));
  put(k, 'tib_corpus', surf(k, axisAt(k, top - 0.5 * L), [0.35, 0, 1]));
  put(k, 'tib_tuberositas', OLDS('tibial_tuberosity'));
  put(k, 'tib_facies_medialis', OLDS('tibia_medial'));
  put(k, 'tib_facies_posterior', OLDS('tibia_posterior'));
  put(k, 'tib_linea_musculi_solei', OLDS('soleal_line'));
  put(k, 'tib_facies_lateralis', OLDS('tibia_lateral'));
  // borders: the extreme points of a cross-section in the border's direction
  const at = (f, dir) => extSurf(k, dir, v => Math.abs(v.y - (top - f * L)) < 0.0025);
  put(k, 'tib_margo_anterior', at(0.40, [0.1, 0, 1]));
  put(k, 'tib_margo_medialis', at(0.62, [0.75, 0, -0.65]));
  put(k, 'tib_margo_interosseus', at(0.45, [-1, 0, -0.15]));
  put(k, 'tib_malleolus_medialis', OLDS('medial_malleolus'));
  const mm = OLD('medial_malleolus');
  const ym = (mm.y + 0.075) / 2;   // mid-height of the malleolus, below the ankle-joint surface
  const cm = centroid(verts(k).filter(v => Math.abs(v.y - ym) < 0.003 && v.x > mm.x - 0.02));
  put(k, 'tib_sulcus_malleolaris', surf(k, cm, [0.25, 0, -1]));
  put(k, 'tib_facies_articularis_malleoli_medialis', surf(k, cm, [-1, 0, 0]));
  put(k, 'tib_incisura_fibularis', OLDS('fibular_notch'));
  put(k, 'tib_facies_articularis_inferior', OLDS('tibia_inferior_articular'));
})();

// ======================= fibula =======================
(() => {
  const k = 'fibula', b = box(k), top = b.max.y, bot = b.min.y, L = top - bot;
  put(k, 'fib_caput', OLDS('fibular_head'));
  // articular facet of the head faces up, forward and medially toward the tibial facet
  const ff = OLD('fibular_facet'), hc = centroid(verts(k).filter(v => v.y > top - 0.025));
  put(k, 'fib_facies_articularis_capitis', surf(k, hc, ff.clone().sub(hc).normalize().add(new THREE.Vector3(0, 0.6, 0)).normalize()));
  put(k, 'fib_apex_capitis', extSurf(k, [-0.25, 1, -0.35], v => v.y > top - 0.02));
  put(k, 'fib_collum', OLDS('fibular_neck'));
  put(k, 'fib_corpus', surf(k, axisAt(k, top - 0.5 * L), [-0.6, 0, 0.8]));
  const sl = (f) => (v) => Math.abs(v.y - (top - f * L)) < 0.0025;
  put(k, 'fib_facies_lateralis', surf(k, axisAt(k, top - 0.42 * L), [-1, 0, 0.15]));
  put(k, 'fib_facies_medialis', surf(k, axisAt(k, top - 0.38 * L), [0.55, 0, 1]));
  put(k, 'fib_facies_posterior', surf(k, axisAt(k, top - 0.55 * L), [0.15, 0, -1]));
  put(k, 'fib_crista_medialis', OLDS('fibula_medial_crest'));
  put(k, 'fib_margo_anterior', extSurf(k, [-0.25, 0, 1], sl(0.32)));
  put(k, 'fib_margo_interosseus', extSurf(k, [1, 0, 0.35], sl(0.47)));
  put(k, 'fib_margo_posterior', extSurf(k, [-0.7, 0, -0.7], sl(0.62)));
  put(k, 'fib_malleolus_lateralis', OLDS('lateral_malleolus'));
  const lm = OLD('lateral_malleolus');
  const yl = lm.y + 0.012;
  const cl = centroid(verts(k).filter(v => Math.abs(v.y - yl) < 0.003));
  put(k, 'fib_facies_articularis_malleoli_lateralis', surf(k, cl, [1, 0, 0.1]));
  put(k, 'fib_fossa_malleoli_lateralis', surf(k, centroid(verts(k).filter(v => Math.abs(v.y - (lm.y + 0.004)) < 0.003)), [0.7, 0, -0.7]));
  put(k, 'fib_sulcus_malleolaris', surf(k, cl, [-0.2, 0, -1]));
})();

// ======================= talus =======================
// Facets were identified by colouring the talus by contact with the calcaneus, tibia, fibula and navicular.
(() => {
  const k = 'talus';
  const c = centroid(verts(k));
  // seen from below (image: up = front, right = medial)
  put(k, 'tal_facies_articularis_calcanea_posterior', PK(k, 'inf', 0.40, 0.68));
  put(k, 'tal_sulcus_tali', PK(k, 'inf', 0.43, 0.46));
  put(k, 'tal_facies_articularis_calcanea_media', PK(k, 'inf', 0.60, 0.42));
  put(k, 'tal_facies_articularis_calcanea_anterior', PK(k, 'inf', 0.48, 0.26));
  put(k, 'tal_facies_articularis_lig_calcaneonavicularis_plantaris', PK(k, 'inf', 0.60, 0.225));
  put(k, 'tal_facies_articularis_partis_calcaneonavicularis_lig_bifurcati', PK(k, 'inf', 0.365, 0.21));
  // seen from above (image: up = back, right = medial)
  put(k, 'tal_caput', PK(k, 'sup', 0.45, 0.86));
  put(k, 'tal_facies_articularis_navicularis', OLDS('talus_head'));
  put(k, 'tal_collum', PK(k, 'sup', 0.50, 0.755));
  put(k, 'tal_trochlea', OLDS('talus_trochlea'));
  put(k, 'tal_facies_superior', PK(k, 'sup', 0.47, 0.38));
  // sides of the body
  put(k, 'tal_facies_malleolaris_lateralis', PK(k, 'lat', 0.38, 0.42));
  put(k, 'tal_processus_lateralis', PK(k, 'lat', 0.33, 0.60));
  put(k, 'tal_facies_malleolaris_medialis', PK(k, 'med', 0.47, 0.36));
  put(k, 'tal_corpus', PK(k, 'med', 0.60, 0.50));
  // posterior process with its two tubercles and the groove for flexor hallucis longus between them
  put(k, 'tal_processus_posterior', OLDS('talus_posterior'));
  const post = (v) => v.z < c.z - 0.008;
  const tl = extSurf(k, [-0.55, -0.15, -1], post), tm = extSurf(k, [0.6, -0.25, -1], post);
  put(k, 'tal_tuberculum_laterale', tl);
  put(k, 'tal_tuberculum_mediale', tm);
  put(k, 'tal_sulcus_tendinis_m_flexoris_hallucis_longi', surf(k, tl.p.clone().lerp(tm.p, 0.5).add(new THREE.Vector3(0, 0.002, 0.004)), [0, 0, -1]));
  // os trigonum is a separate ossicle (not in the model): marked just behind the lateral tubercle
  put(k, 'tal_os_trigonum', { p: tl.p.clone().addScaledVector(tl.n, 0.0025).add(new THREE.Vector3(0, -0.0015, 0)), n: tl.n.clone() });
})();

// ======================= calcaneus =======================
(() => {
  const k = 'calcaneus';
  put(k, 'cal_tuber', OLDS('calcaneal_tuberosity'));
  put(k, 'cal_processus_medialis_tuberis', OLDS('calc_medial_process'));
  put(k, 'cal_processus_lateralis_tuberis', OLDS('calc_lateral_process'));
  // from below (image: up = front, right = medial)
  put(k, 'cal_tuberculum', PK(k, 'inf', 0.40, 0.20));
  put(k, 'cal_sustentaculum_tali', OLDS('sustentaculum'));
  // from the medial side (image: right = back): groove under the sustentaculum
  put(k, 'cal_sulcus_tendinis_m_flexoris_hallucis_longi', PK(k, 'med', 0.30, 0.36));
  // from above (image: up = back, right = medial); facets found by contact with the talus
  put(k, 'cal_facies_articularis_talaris_posterior', PK(k, 'sup', 0.40, 0.50));
  put(k, 'cal_sulcus_calcanei', PK(k, 'sup', 0.43, 0.69));
  put(k, 'cal_sinus_tarsi', PK(k, 'sup', 0.27, 0.72));
  put(k, 'cal_facies_articularis_talaris_media', PK(k, 'sup', 0.55, 0.70));
  put(k, 'cal_facies_articularis_talaris_anterior', PK(k, 'sup', 0.48, 0.86));
  // lateral surface (image: right = front)
  put(k, 'cal_trochlea_fibularis', PK(k, 'lat', 0.55, 0.50));
  put(k, 'cal_sulcus_tendinis_m_fibularis_longi', PK(k, 'lat', 0.57, 0.59));
  put(k, 'cal_facies_articularis_cuboidea', extSurf(k, [-0.25, -0.1, 1]));
})();

// ======================= navicular, cuboid =======================
put('navicular', 'nav_tuberositas', OLDS('navicular_tuberosity'));
(() => {
  const k = 'cuboid';
  // plantar surface (image: up = front, right = medial): groove in front, ridge behind it ending laterally in the tuberosity
  put(k, 'cub_sulcus_tendinis_m_fibularis_longi', PK(k, 'inf', 0.38, 0.38));
  put(k, 'cub_tuberositas', PK(k, 'inf', 0.22, 0.50));
  put(k, 'cub_processus_calcaneus', PK(k, 'inf', 0.60, 0.80));
})();

// ======================= metatarsals and toes =======================
function longAxis(k) {
  const vs = verts(k), c = centroid(vs);
  const cov = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  vs.forEach(v => { const d = [v.x - c.x, v.y - c.y, v.z - c.z]; for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) cov[i][j] += d[i] * d[j]; });
  let a = new THREE.Vector3(0, 0, 1);
  for (let it = 0; it < 30; it++) a = new THREE.Vector3(cov[0][0] * a.x + cov[0][1] * a.y + cov[0][2] * a.z, cov[1][0] * a.x + cov[1][1] * a.y + cov[1][2] * a.z, cov[2][0] * a.x + cov[2][1] * a.y + cov[2][2] * a.z).normalize();
  if (a.z > 0) a.negate(); // a points proximally (toward the heel)
  let lo = Infinity, hi = -Infinity;
  vs.forEach(v => { const s = v.clone().sub(c).dot(a); lo = Math.min(lo, s); hi = Math.max(hi, s); });
  const at = (t) => c.clone().addScaledVector(a, hi - t * (hi - lo)); // t = 0 proximal end, 1 distal end
  const side = (d) => { const s = V3(d); return s.addScaledVector(a, -s.dot(a)).normalize(); };
  return { a, at, side };
}
const DORS = [0, 1, 0.1], PLAN = [0, -1, -0.1];
for (let i = 1; i <= 5; i++) {
  const mt = `metatarsal_${i}`, A1 = longAxis(mt);
  put(mt, `mt${i}_basis`, OLDS(`mt${i}_base`));
  put(mt, `mt${i}_corpus`, OLDS(`mt${i}_body`));
  put(mt, `mt${i}_caput`, OLDS(`mt${i}_head`));
  const phal = [[`toe_prox_${i}`, `tp${i}`], ...(i > 1 ? [[`toe_mid_${i}`, `tm${i}`]] : []), [`toe_dist_${i}`, `td${i}`]];
  for (const [k, p] of phal) {
    const L = longAxis(k), dist = p.startsWith('td');
    put(k, `${p}_basis`, surf(k, L.at(0.18), L.side(DORS)));
    put(k, `${p}_corpus`, surf(k, L.at(0.5), L.side(DORS)));
    put(k, `${p}_caput`, surf(k, L.at(dist ? 0.8 : 0.84), L.side(DORS)));
    // trochlea: the pulley-shaped distal articular surface of the head; tuberosity: plantar side of the tip
    if (dist) put(k, `${p}_tuberositas`, surf(k, L.at(0.86), L.side(PLAN)));
    else put(k, `${p}_trochlea`, surf(k, L.at(0.97), L.a.clone().negate().add(L.side(PLAN).multiplyScalar(0.8)).normalize()));
  }
}
put('metatarsal_1', 'mt1_tuberositas', extSurf('metatarsal_1', [-0.45, -1, -0.8]));
put('metatarsal_5', 'mt5_tuberositas', OLDS('mt5_tuberosity'));
// attachment area without a TA term, recomputed on the plantar side
put('cuneiform_int', 'att_cuneiform_int_plantar', surf('cuneiform_int', centroid(verts('cuneiform_int')), [0, -1, 0]));

window.__ta = out;
export default out;
