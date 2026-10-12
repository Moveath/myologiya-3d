// Manually selected anatomical regions, 2026-10-12.
// Reproduce in build_head/pintool.html; original source geometry is never changed.
// 'projection' means the location is supported by anatomy but the small feature
// itself cannot be resolved on the BodyParts3D mesh. It is not a measured foramen.
window.__faceExtra = [];
window.__faceMiss = [];
const FACE_NOTE = {
 surface: 'Маркер выбран на видимой поверхности или крае образования; он обозначает один участок, а не всю протяжённость.',
 projection: 'Показана анатомическая область по источникам. Мелкий рельеф или просвет этого образования на сетке BodyParts3D достоверно не различим; это ориентировочная проекция, а не подтверждение его формы.',
 variant: 'Показано типичное место варианта. Наличие этого варианта у человека, по которому создана модель, не установлено; отдельное образование здесь не моделировалось.'
};
function faceAdd(bone, prefix, rows, reflect=false, half=false) {
 for(const [num,view0,u0,v,localization='surface',note] of rows){
  const view=reflect?({lat:'med',med:'lat'}[view0]||view0):view0;
  let u=reflect?1-u0:u0, pickedV=v;
  // Actual left mesh differs from the right: inspect and pick independently.
  const corrections = {'maxilla_left:A02.1.00.062':[.153,.297], 'maxilla_left:37':[.562,.650], 'maxilla_left:38':[.540,.518], 'maxilla_left:39':[.556,.602], 'palatine_left:5':[.366,.315], 'palatine_left:18':[.221,.740], 'zygomatic_left:8':[.546,.444], 'lacrimal_left:2':[.455,.550], 'inferior_concha_left:2':[.213,.323], 'inferior_concha_left:4':[.411,.333]};
  if(corrections[bone+':'+num])[u,pickedV]=corrections[bone+':'+num];
  const hit=window.pick(bone,view,u,pickedV);
  const code=typeof num==='string'?num:`A${prefix}.${String(num).padStart(3,'0')}`;
  if(!hit){window.__faceMiss.push({bone,code,view,u,v});continue;}
  window.__faceExtra.push({bone,code,...hit,localization,modelNote:note||FACE_NOTE[localization],
   evidence:{method:'orthographic-raycast',view,uv:[u,pickedV],half,source:'build_head/landmarks_face_extra.js'}});
 }
}
function facePaired(bone,prefix,rows){faceAdd(bone+'_right',prefix,rows);faceAdd(bone+'_left',prefix,rows,true);}

facePaired('maxilla','02.1.12',[
 [4,'sup',.445,.435,'projection','Подглазничный канал находится внутри кости. Маркер на глазничной поверхности показывает проекцию его переднего участка; стенки и просвет канала в модели не выделены.'],
 [5,'sup',.447,.265,'projection'],
 [12,'ant',.287,.486,'surface','Маркер на краю скулового отростка обозначает участок соединения со скуловой костью; весь шов не обведён.'],
 [14,'post',.599,.606,'projection'],
 [15,'post',.609,.662,'projection','Альвеолярные каналы проходят в толще верхней челюсти. Здесь показана их область в задней стенке, а не реконструкция отдельных просветов.'],
 [18,'med',.438,.591,'surface'], [19,'med',.316,.545,'projection'],
 [20,'post',.335,.335,'surface'], [22,'med',.761,.681,'projection'],
 [25,'ant',.650,.349,'surface'], [26,'sup',.624,.630,'projection'],
 [27,'med',.310,.321,'projection'],
 [31,'inf',.773,.249,'projection','Маркер обозначает резцовую часть верхней челюсти. Отдельная резцовая кость и её самостоятельные границы на этой взрослой модели не выделены.'],
 ['A02.1.00.061','med',.274,.783,'projection','Проекция резцового канала в переднем отделе нёбного отростка. Просвет канала не реконструирован.'],
 [32,'inf',.665,.303,'variant','Показана область возможного резцового шва между резцовой частью и остальной верхней челюстью. Отдельная линия этого шва на данной сетке не подтверждена.'],
 [33,'inf',.623,.620,'projection'], [34,'inf',.663,.620,'projection'],
 [37,'inf',.466,.632,'surface','Маркер перенесён внутрь зубной альвеолы; показана поверхность лунки одного моляра, а не весь ряд альвеол.'],
 [38,'inf',.472,.535,'surface'], [39,'inf',.501,.599,'surface'],
 ['A02.1.00.062','inf',.849,.295,'projection','Маркер у срединного края нёбного отростка показывает область резцовых отверстий позади резцов. Их отдельные просветы в модели не подтверждены.'],
]);
facePaired('zygomatic','02.1.14',[
 [7,'med',.389,.224,'projection'], [8,'lat',.432,.365,'projection'],
 [9,'med',.390,.462,'projection'], [10,'lat',.565,.616,'projection'],
 [11,'med',.385,.648,'projection'],
]);
facePaired('palatine','02.1.13',[
 [5,'med',.594,.371,'surface','Маркер расположен у нижнего края клиновидно-нёбной вырезки между верхними отростками; середина просвета не является поверхностью кости.'],
 [6,'lat',.520,.653,'surface'],
 [8,'inf',.385,.585,'projection','Область малых нёбных каналов в пирамидальном отростке. Модель не воспроизводит их отдельные внутрикостные просветы.'],
 [9,'med',.398,.677,'projection'], [10,'med',.512,.365,'projection'],
 [12,'med',.770,.221,'surface'], [16,'inf',.303,.590,'projection'],
 [17,'post',.237,.750,'surface'], [18,'sup',.795,.723,'surface'],
 [19,'inf',.618,.483,'projection'],
]);
facePaired('lacrimal','02.1.09',[
 [2,'lat',.505,.550,'surface','Маркер перенесён с переднего участка пластинки на разделяющий её вертикальный гребень; он обозначает один участок гребня.'],
 [3,'lat',.644,.519,'projection'], [4,'lat',.468,.802,'projection'],
]);
facePaired('nasal','02.1.10',[
 [2,'post',.466,.555,'projection'], [3,'ant',.505,.449,'projection'],
]);
facePaired('inferior_concha','02.1.08',[
 [2,'lat',.716,.296,'surface'], [3,'lat',.479,.515,'projection'], [4,'lat',.597,.296,'surface'],
]);
faceAdd('vomer','02.1.11',[
 [3,'lat',.540,.511,'projection'],
 [4,'lat',.245,.443,'projection','Ориентировочная область под углом крыльев сошника. Граница соответствует описанию Marušić и соавт.; учебные источники по-разному определяют хоанный гребень (см. примечание). Рельеф гребня на сетке не подтверждён.'],
 [5,'lat',.176,.463,'projection','Ориентировочная задняя область сошника, позади предполагаемого хоанного гребня по Marušić и соавт. Точная граница клиновидной части на сетке не различима.'],
]);
// Midline landmarks are selected on the complete mandible.
faceAdd('mandible','02.1.15',[
 [4,'ant',.496,.746,'surface'], [9,'post',.450,.824,'surface'],
 [10,'post',.500,.763,'projection'], [11,'post',.500,.805,'projection'],
 [19,'sup',.314,.691,'surface'], [20,'sup',.275,.562,'surface'],
]);
// Hide the opposite half only while picking the right medial cortex. This makes
// the actual inner surface accessible without accidentally hitting the left ramus.
const fm=window.__meshes.mandible, fg=fm.geometry, fh=fg.clone();
const fp=fh.attributes.position, fi=fh.index.array, kept=[], vv=new THREE.Vector3();
for(let i=0;i<fi.length;i+=3){let x=0;for(let j=0;j<3;j++)x+=vv.fromBufferAttribute(fp,fi[i+j]).applyMatrix4(fm.matrixWorld).x;if(x/3<0)kept.push(...fi.slice(i,i+3));}
fh.setIndex(kept);fh.computeBoundingBox();fm.geometry=fh;
faceAdd('mandible','02.1.15',[
 [12,'med',.466,.610,'surface'],
 [13,'med',.281,.699,'variant'],
 [14,'med',.242,.754,'surface'], [15,'med',.462,.728,'surface'],
 [22,'med',.442,.585,'surface'], [23,'med',.469,.558,'surface'],
 [27,'med',.757,.582,'surface'], [28,'med',.702,.426,'surface'],
 [29,'med',.693,.372,'surface'],
 [30,'med',.682,.516,'projection','Канал проходит внутри ветви и тела под зубными альвеолами. Точка на медиальной кортикальной поверхности обозначает проекцию начального отдела; его просвет не вырезан в сетке.'],
 [31,'med',.670,.499,'projection'], [33,'med',.503,.444,'surface'],
 [38,'med',.851,.205,'surface'],
],false,true);
fm.geometry=fg;fh.dispose();
