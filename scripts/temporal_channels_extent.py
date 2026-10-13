"""Reconcile observed temporal extents without equating marker count and shape.

This does not modify models or marker localization. Whole visible ossicle parts
are judged on the native source scale; two small-process microdetails remain
partial. Temporal-bone channel reports supersede the earlier capability audit.
"""
from pathlib import Path
import json
from openear_landmarks_completion import FEATURES

ROOT=Path(__file__).resolve().parents[1]

def main():
    native=json.loads((ROOT/'pins_head/openear-native.json').read_text(encoding='utf-8'))
    channel=json.loads((ROOT/'research/temporal-channel-review.json').read_text(encoding='utf-8'))
    prior=json.loads((ROOT/'research/temporal-feature-review.json').read_text(encoding='utf-8'))
    rows=[]
    for m in native['markers']:
        partial=m['c'] in ('A15.3.02.041','A15.3.02.048')
        observed={
            'A15.3.02.034':'Головка стремени полностью видна как собственное расширение у схождения двух ножек; суставная поверхность и противоположная сторона осмотрены.',
            'A15.3.02.035':'Передняя ножка непрерывно прослеживается от схождения под головкой до основания на двух противоположных видах. Межножковое отверстие отделяет её от задней ножки.',
            'A15.3.02.036':'Задняя дугообразная ножка непрерывно прослеживается от схождения под головкой до основания на двух противоположных видах.',
            'A15.3.02.037':'Пластинка основания с обеими сторонами и наружным контуром присутствует в исходной сетке. Её сопряжения с двумя ножками видимы.',
            'A15.3.02.039':'Расширенное тело наковальни осмотрено с четырёх направлений; переходы в обе ножки и поверхность со стороны головки молоточка присутствуют.',
            'A15.3.02.040':'Ход длинной ножки от тела до дистального изгиба виден с четырёх направлений; неопределённая микрограница чечевицеобразной пластинки не включена в утверждение полноты её терминального рельефа.',
            'A15.3.02.041':FEATURES['incus_lenticular_process']['observed'],
            'A15.3.02.042':'Короткая ножка от тела до собственного закруглённого конца видна с четырёх направлений и в исходном взаимном положении косточек.',
            'A15.3.02.044':'Рукоятка от корня до собственного дистального расширения видна с четырёх направлений; её исходное положение относительно барабанной перепонки сохранено.',
            'A15.3.02.045':'Головка молоточка полностью присутствует в авторской поверхности; суставная и противоположная стороны сопоставлены с наковальней.',
            'A15.3.02.046':'Сужение шейки между головкой и корнем рукоятки присутствует со всех осмотренных сторон; искусственное отделение или достройка не выполнялись.',
            'A15.3.02.047':FEATURES['malleus_lateral_process']['observed'],
            'A15.3.02.048':FEATURES['malleus_anterior_process']['observed'],
        }[m['c']]
        rows.append({'code':m['c'],'ru':m['ru'],'lat':m['lat'],'source':'OpenEar ZETA','object':m['b'],
                     'native_marker':m['id'],'extent_status':'partial-source-detail' if partial else 'whole-visible-part-at-source-scale',
                     'observed':observed,
                     'limit':m['modelNote'] if partial else 'Полнота относится к видимому макрорельефу названной части в данной авторской сетке. Микроскопические края, хрящ, связки и гистология не включены; точной отдельной сегментации границы части нет.',
                     'view':m['view'],'screenshots':m['evidence'].get('screenshots',[m['evidence']['screenshot']]),
                     'refs':m['refs'],'complete_microscopic_geometry_claim':False})
    for r in prior['outcomes']:
        row={'code':r['code'],'ru':r['ru'],'lat':r['lat'],'source':'OpenEar ZETA',
             'extent_status':'local-surface-or-aperture-only' if r.get('native_marker') else 'not-yet-demonstrated',
             'observed':r['finding'],'limit':r['remaining_work'],'refs':r['anatomical_refs'],
             'complete_feature_geometry_claim':False}
        if r.get('geometry_evidence'):
            evidence=r['geometry_evidence']
            row.update(native_marker=r['native_marker'],view=evidence.get('view'),screenshots=[evidence[k] for k in ('screenshot','crossScreenshot','scanScreenshot') if k in evidence])
        if r['code'] in ('A02.1.06.009','A02.1.06.013'):
            kind='facial' if r['code'].endswith('009') else 'carotid'
            geom=next(g for g in channel['geometry']['structures'] if g['id'].startswith(kind))
            row.update(extent_status='source-wall-segments-traced',
                       observed=f'Проверены {geom["reviewed_interval_planes"]} последовательных косых сечений; сохранены {geom["triangles"]} треугольников реальной костной стенки. Протяжённость навигационного пути {geom["approximate_guide_span_mm"]:.3f} мм; она не является измерением всей длины анатомического канала.',
                       limit=(channel['facial_terminal_review']['export_limit']+' Полный периметр конечных апертур и непрерывная тонкая стенка не подтверждены.' if kind=='facial' else 'Часть границ не замыкается в исходной маске; внутреннее устье ещё не отделено уверенно от края подготовленного образца. Наличие открытых сечений само по себе не считается анатомическим отсутствием стенки.'),
                       source_report='research/temporal-channel-review.json',
                       source_mesh='skull-temporal-channels.glb',object=geom['id'],refs=channel['anatomical_sources'][geom['id']])
        rows.append(row)
    report={'scope':'13 подтерминов слуховых косточек и 43 ранее не подтверждённых мелких образования височной кости. Это не аудит всех 325 surface основного черепа.',
            'geometry_sha256':native['geometry_sha256'],
            'counts':{'ossicle_terms':13,'ossicle_whole_visible_parts_at_source_scale':11,'ossicle_partial_microdetails':2,'temporal_codes':43},
            'source_scale_not_absolute_accuracy':True,'external_anatomist_signoff':False,
            'no_primary_marker_flags_changed':True,'complete_temporal_geometry_claim':False,'features':rows}
    (ROOT/'research/temporal-extent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('56 finite extent entries; 11 whole visible ossicle parts, 2 partial microdetails; no global completeness claim')

if __name__=='__main__':main()
