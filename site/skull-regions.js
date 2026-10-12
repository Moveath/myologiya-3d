// Teaching views of existing source geometry. These presets do not create anatomy.
const pair = id => [id+'_right',id+'_left'];
const base = ['frontal','occipital','sphenoid','ethmoid',...pair('temporal')];
const face = ['frontal','sphenoid','ethmoid','vomer',...['nasal','lacrimal','inferior_concha','palatine','maxilla','zygomatic'].flatMap(pair)];
const earView = {d:[1,0,0],up:[0,0,-1]};
export const REGIONS = [
  {id:'whole',ru:'Кости черепа',hint:'Начни с целого: цвет, название, положение.',mode:'z',badge:'22 кости',presets:[
    {id:'all',ru:'Весь череп',view:'antlat'},
    {id:'brain',ru:'Мозговой отдел',parts:[...base,...pair('parietal')],view:'antlat'},
    {id:'face',ru:'Лицевой отдел',parts:['vomer','mandible',...['nasal','lacrimal','inferior_concha','palatine','maxilla','zygomatic'].flatMap(pair)],view:'antlat'}]},
  {id:'base',ru:'Основание черепа',hint:'Посмотри изнутри, снизу и сбоку на срезе.',mode:'z',badge:'3 готовых вида',presets:[
    {id:'inside',ru:'Изнутри',parts:base,view:'sup',cut:{plane:'axial',value:.59,reverse:true}},
    {id:'below',ru:'Снизу',parts:base,view:'inf'},
    {id:'section',ru:'Боковой срез',parts:base,view:'right',cut:{plane:'sagittal',value:.5,reverse:false}}]},
  {id:'face',ru:'Глазницы и полость носа',hint:'Убери окружающие кости и рассмотри глубже.',mode:'z',badge:'Кости по отдельности',presets:[
    {id:'front',ru:'Спереди',parts:face,view:'ant'},
    {id:'nose',ru:'Носовая полость',parts:['ethmoid','vomer',...pair('inferior_concha'),...pair('palatine')],view:'antlat'},
    {id:'section',ru:'На срезе',parts:face,view:'right',cut:{plane:'sagittal',value:.5,reverse:false}}]},
  {id:'sinuses',ru:'Пазухи и ячейки',hint:'Цветные объёмы полостей внутри прозрачных костей.',mode:'z',badge:'8 объёмов',presets:[
    {id:'context',ru:'В костях',parts:['frontal','sphenoid','ethmoid'],includeCavities:true,cavities:true,translucent:true,view:'antlat'},
    {id:'spaces',ru:'Только полости',parts:[],includeCavities:true,cavities:true,view:'antlat'}]},
  {id:'jaws',ru:'Челюсти',hint:'Сравни общий вид и отдельную нижнюю челюсть.',mode:'z',badge:'Верхняя и нижняя',presets:[
    {id:'all',ru:'Вместе',parts:['mandible',...pair('maxilla')],view:'antlat'},
    {id:'mandible',ru:'Нижняя челюсть',parts:['mandible'],view:'antlat'},
    {id:'maxilla',ru:'Верхние челюсти',parts:pair('maxilla'),view:'antlat'}]},
  {id:'ear',ru:'Ухо и височная кость',hint:'Крупные планы косточек, лабиринта и нервов.',mode:'openear',badge:'Отдельный препарат',presets:[
    {id:'ossicles',ru:'Слуховые косточки',parts:['malleus','incus','stapes'],view:earView},
    {id:'labyrinth',ru:'Лабиринт',parts:['scala_tympani','vestibular_space'],cavities:true,view:{d:[1,.4,.5],up:[0,0,-1]}},
    {id:'nerves',ru:'Нервы',parts:['facial_nerve','chorda_tympani','vestibulocochlear_nerve'],view:earView},
    {id:'context',ru:'Весь препарат',cavities:true,translucent:true,view:earView}]},
  {id:'muscles',ru:'Мышцы головы',hint:'Мимические и жевательные мышцы: слои и карточки.',action:'muscles',badge:'Основной атлас'},
  {id:'variants',ru:'Варианты строения',hint:'Отдельный каталог с объяснением каждого маркера.',action:'variants',badge:'Геометрия не подтверждена'}
];
export const regionById = id => REGIONS.find(region=>region.id===id);
