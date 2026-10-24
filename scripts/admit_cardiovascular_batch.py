"""Record the explicitly reviewed first batch; never discover/admit new files."""
import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];run=pathlib.Path(sys.argv[1])
reviewed='''cv_heart cv_valve_tricuspid cv_valve_mitral cv_valve_pulmonary
cv_a_aorta_ascending cv_a_aorta_arch cv_a_aorta_descending cv_a_pulmonary_arteries
cv_a_coronary_right cv_a_coronary_left cv_a_coronary_anterior_interventricular cv_a_coronary_circumflex
cv_a_brachiocephalic cv_a_carotid_common_right cv_a_carotid_common_left cv_a_subclavian_right cv_a_subclavian_left
cv_a_celiac cv_a_mesenteric_superior cv_a_mesenteric_inferior cv_a_renal_right cv_a_renal_left
cv_a_iliac_common_right cv_a_iliac_common_left cv_a_iliac_external_right cv_a_iliac_external_left cv_a_iliac_internal_right cv_a_iliac_internal_left
cv_v_cava_superior cv_v_cava_inferior cv_v_pulmonary_veins cv_v_brachiocephalic_right cv_v_brachiocephalic_left
cv_v_jugular_internal_right cv_v_jugular_internal_left cv_v_subclavian_right cv_v_subclavian_left
cv_v_renal_right cv_v_renal_left cv_v_iliac_common_right cv_v_iliac_common_left cv_v_iliac_external_right cv_v_iliac_external_left cv_v_iliac_internal_right cv_v_iliac_internal_left
cv_v_splenic cv_v_mesenteric_superior cv_a_gastric_left cv_a_hepatic_common cv_a_splenic'''.split()
assert len(reviewed)==50 and len(set(reviewed))==50
assert json.loads((run/'node-trial.json').read_text())['status']=='passed'
evidence=[(run/'node-trial.json').relative_to(ROOT).as_posix(),(run/'geometry-measurements.json').relative_to(ROOT).as_posix(),
 'build_cardiovascular/blender-import.json','build_cardiovascular/review-final.blend','build_cardiovascular/heart-anterior.png','build_cardiovascular/heart-posterior.png','build_cardiovascular/heart-thorax-context.png','build_cardiovascular/valves-oblique.png','build_cardiovascular/abdominal-pelvic.png']
assert all((ROOT/p).exists()for p in evidence)
result={}
for id in reviewed:
    r=json.loads((ROOT/'build_cardiovascular/bp3d-3.0-v1'/(id+'.json')).read_text())
    result[id]=dict(status='educational_limited',sha256=r['sha256'],evidence=evidence,
      basis='BP3D 3.0 source identity; unchanged specimen axes/scale; Blender views in existing thorax frame; gross form and sided arrangement; exact GLB triangle roundtrip and native/BVH rays. Not exact junction/attachment acceptance.',
      limitation='Показан исходный фрагмент BodyParts3D. Полная протяжённость, просвет, точность стенки и места соединений не подтверждены; срезанные окончания не являются естественными границами.')
    if r['degenerate']or r['duplicateFaces']:
        result[id]['technicalExceptions']=dict(degenerateRetained=r['degenerate'],duplicateFacesRetained=r['duplicateFaces'],normalFallbackVertices=r['normalFallbackVertices'],decision='Source triangles retained; scale-stable shading normals only. Exterior readable in multi-view review; not suitable for exact interior morphometry. Local defects remain open.')
        result[id]['limitation']+=' Сохранены локальные дефекты исходной сетки; модель не предназначена для точной морфометрии.'
with(ROOT/'scripts/cardiovascular_admissions.json').open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
print('Explicit educational admissions:',len(result))
