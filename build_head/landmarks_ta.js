// Surface landmarks inspected on the full-resolution BodyParts3D skull.
// The catalogue includes unlocalized terms separately; never invent a hit for a missing feature.
// Coordinates are orthographic screen picks in pintool.html, not arbitrary world coordinates.
window.__ta = [];
function add(bone, prefix, rows, reflect = false) {
  for (const [num, originalView, originalU, v] of rows) {
    const view = reflect ? ({lat: 'med', med: 'lat'}[originalView] || originalView) : originalView;
    const u = reflect ? 1 - originalU : originalU;
    const point = window.pick(bone, view, u, v);
    const code = 'A' + prefix + '.' + String(num).padStart(3, '0');
    window.__ta.push({bone, code, id: 'head_' + bone + '_' + String(num).padStart(3, '0'),
      view, uv: [u, v], ...(point || {missing: true})});
  }
}
function paired(bone, prefix, rows) {
  add(bone + '_right', prefix, rows);
  add(bone + '_left', prefix, rows, true);
}

add('frontal', '02.1.03', [
  [2,'ant',.5,.35], [3,'ant',.57,.49], [4,'ant',.29,.40],
  [5,'ant',.29,.71], [6,'ant',.5,.716], [8,'ant',.265,.765],
  [11,'lat',.585,.60], [12,'post',.28,.17], [13,'ant',.16,.46],
  [14,'ant',.128,.763], [15,'post',.32,.42], [16,'post',.495,.66],
  [17,'post',.484,.24], [19,'ant',.5,.824], [21,'ant',.502,.856],
  [22,'inf',.30,.565], [23,'inf',.30,.60],
]);
paired('parietal','02.1.02',[
  [2,'med',.5,.50], [7,'lat',.53,.37], [10,'lat',.38,.37],
  [11,'lat',.12,.45], [12,'lat',.59,.717], [13,'sup',.70,.45],
  [14,'lat',.84,.39], [15,'lat',.79,.175],
  [17,'lat',.89,.66], [18,'lat',.295,.785],
]);
add('occipital','02.1.04',[
  [2,'sup',.43,.75],
  [5,'sup',.50,.865], [6,'sup',.505,.85], [9,'sup',.715,.655],
  [10,'post',.50,.43], [11,'post',.85,.67], [12,'post',.265,.278],
  [14,'inf',.382,.486], [22,'post',.495,.666], [23,'post',.504,.746],
  [25,'post',.35,.695], [27,'post',.50,.335], [28,'ant',.50,.43],
  [29,'ant',.495,.445], [30,'ant',.493,.565],
  [31,'ant',.28,.452], [36,'ant',.367,.327], [37,'ant',.275,.593],
]);
add('sphenoid','02.1.05',[
  [2,'ant',.505,.47], [3,'sup',.50,.561], [6,'sup',.495,.406],
  [7,'sup',.5,.447], [9,'sup',.5,.407], [10,'sup',.495,.331],
  [14,'ant',.501,.438], [15,'ant',.50,.559],
  [20,'ant',.694,.339], [24,'ant',.819,.402],
  [25,'sup',.733,.448], [26,'lat',.665,.33], [27,'inf',.75,.595],
  [29,'ant',.723,.517], [30,'ant',.734,.417],
  [31,'ant',.863,.45], [32,'ant',.826,.289], [34,'post',.875,.405],
  [36,'inf',.282,.612], [42,'ant',.327,.63], [43,'ant',.272,.666],
  [44,'post',.393,.69], [46,'post',.333,.638],
  [51,'post',.401,.744],
]);
paired('temporal','02.1.06',[
  [4,'lat',.28,.695],
  [47,'lat',.509,.795], [54,'lat',.496,.55],
  [61,'lat',.59,.327], [62,'lat',.54,.179],
  [65,'lat',.655,.36], [67,'lat',.823,.59],
  [78,'med',.34,.324],
]);
add('ethmoid','02.1.07',[
  [2,'sup',.41,.5], [4,'ant',.503,.16], [6,'ant',.46,.76],
  [7,'ant',.276,.454], [11,'lat',.536,.465],
]);
paired('maxilla','02.1.12',[
  [2,'ant',.447,.648], [3,'sup',.467,.482], [6,'ant',.44,.446],
  [7,'ant',.468,.637], [8,'ant',.425,.565], [9,'ant',.448,.665],
  [10,'ant',.652,.712], [11,'ant',.777,.757],
  [13,'post',.56,.60], [16,'post',.616,.715], [17,'med',.35,.636],
  [21,'med',.571,.463], [23,'med',.631,.531], [24,'ant',.677,.211],
  [28,'ant',.27,.534], [29,'inf',.58,.57], [30,'med',.31,.758],
  [35,'ant',.524,.837], [36,'inf',.352,.576], [37,'inf',.345,.571],
  [40,'ant',.608,.871],
]);
paired('zygomatic','02.1.14',[
  [2,'lat',.581,.711], [3,'med',.444,.713], [4,'med',.453,.339],
  [5,'lat',.252,.659], [6,'ant',.474,.201],
]);
paired('palatine','02.1.13',[
  [2,'med',.474,.484], [3,'med',.497,.549], [4,'lat',.564,.497],
  [5,'ant',.569,.225], [7,'ant',.287,.788], [11,'ant',.471,.192],
  [13,'ant',.661,.793], [14,'sup',.728,.623],
  [15,'inf',.631,.329],
]);
paired('lacrimal','02.1.09',[
  [2,'ant',.503,.578],
]);
add('vomer','02.1.11',[
  [2,'sup',.468,.137],
]);
add('mandible','02.1.15',[
  [2,'ant',.494,.76], [3,'ant',.481,.826], [5,'ant',.494,.794],
  [6,'ant',.427,.817], [7,'ant',.303,.725], [8,'ant',.26,.633],
  [16,'ant',.445,.694], [17,'sup',.474,.81], [18,'sup',.252,.525],
  [21,'ant',.357,.713],
  [24,'lat',.282,.463], [25,'lat',.264,.684], [26,'lat',.245,.587],
  [32,'lat',.531,.211], [34,'lat',.393,.287], [35,'lat',.143,.206],
  [36,'lat',.122,.115], [37,'lat',.153,.25],
]);
