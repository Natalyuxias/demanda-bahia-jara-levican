"""Publicar procesados por OD/escenario sin registros ni vínculos individuales."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill
p=argparse.ArgumentParser();p.add_argument('--entrada',type=Path,required=True);p.add_argument('--referencias',type=Path,required=True);p.add_argument('--salida',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();B=a.salida;O=B/'07_datos_procesados';O.mkdir(exist_ok=True);R=a.referencias
d=pd.read_csv(a.entrada,float_precision='round_trip');cat=pd.read_csv(B/'02_zonificaciones/catalogo_zonas_anteriores.csv');cat=cat.set_index('codigo_zona_anterior').nombre_zona_anterior.to_dict()
def zcode(v):return 'SIN_ZONA_ANTERIOR' if pd.isna(v) else 'Z'+str(int(v)).zfill(3)
for e in ['origen','destino']:
 old=d['zona_'+e+'_anterior'].map(zcode);fine=d['zona_'+e+'_localidad'].fillna('SIN_DESAGREGAR').astype(str);fine=fine.where(fine.ne('SIN_DESAGREGAR'),fine+'_'+old)
 d['codigo_'+e]=np.where(d.zonificacion.eq('original'),old,fine)
 d['nombre_'+e]=np.where(d.zonificacion.eq('original'),old.map(cat).fillna('Sin zona identificada'),d[e])
d['unidad']=d.unidad.fillna('Sin unidad compatible')
keys=['zonificacion','alternativa_proyecto','version_referencia','fuente','codigo_origen','nombre_origen','codigo_destino','nombre_destino','segmento','unidad','temporada','direccion_cruce','anio','escenario_PIB','tasa_PIB_anual','elasticidad_demanda_PIB','escenario_captacion','escenario_elasticidad']
quant=['Q_referencia','D_tierra_SBO','D_actual_SBO','D_existente_nuevo','D_desviada_tierra','D_desviada_actual','D_tierra_CP_existente','D_actual_CP_existente','D_inducida_incremental','D_inducida_tierra','D_inducida_actual','D_inducida_nuevo','D_tierra_CP_total','D_actual_CP_total','D_nuevo_CP_total','D_residual_existente','D_base_fuera_soporte_induccion']
g=d.groupby(keys,dropna=False,sort=True);out=g[quant].sum(min_count=1)
out['componentes_del_modelo']=g.size();out['componentes_sin_referencia']=g.Q_referencia.apply(lambda s:s.isna().sum())
means=['CG_origen_SBO','CG_nuevo_CP','CG_min_SBO','CG_min_CP','p_nuevo','delta_costo_tierra','delta_costo_actual','delta_costo_proyecto','tiempo_CAM_tierra_h','tiempo_CAM_actual_h','tiempo_CAM_proyecto_h']
for col in means:
 valid=d[col].notna()&d.Q_referencia.gt(0);temp=d[keys].copy();temp['_den']=d.Q_referencia.where(valid,0);temp['_num']=(d[col]*d.Q_referencia).where(valid,0)
 v=temp.groupby(keys,dropna=False,sort=True)[['_den','_num']].sum();out['promedio_ponderado_'+col]=v._num/v._den.replace(0,np.nan);out['referencia_usada_para_promedio_'+col]=v._den
out=out.reset_index();rename={'alternativa_proyecto':'alternativa','version_referencia':'perfil_ARISTO','direccion_cruce':'sentido','escenario_elasticidad':'escenario_induccion_costo'};out=out.rename(columns=rename)
out.to_csv(O/'comparacion_metodologia_original_agregada.csv.gz',index=False,encoding='utf-8-sig',compression='gzip',float_format='%.12g')
# Reconciliación contra el detalle privado: ni pérdida de referencias ni suma de escenarios.
ck=['zonificacion','alternativa_proyecto','version_referencia','fuente','segmento','unidad','temporada','direccion_cruce','anio','escenario_PIB','escenario_captacion','escenario_elasticidad']
old=d.groupby(ck,dropna=False)[quant].sum(min_count=1).sort_index();new=out.rename(columns={v:k for k,v in rename.items()}).groupby(ck,dropna=False)[quant].sum(min_count=1).sort_index()
checks={'totales_de_todas_las_cantidades_conservados':bool(np.allclose(old,new,equal_nan=True)),'sin_identificadores_individuales':not bool({'id_base','id_flujo','id_registro_2026','ids_encuestas','id_encuesta'}.intersection(out.columns)),'sin_coordenadas':not any(c in ['lat','lon','latitud','longitud','origen_lat','destino_lat','origen_lon','destino_lon'] for c in out),'sin_infinito':not np.isinf(out.select_dtypes('number').to_numpy()).any()}
# Aforos y factores son estratos agregados, no encuestas individuales.
c=pd.read_csv(R/'citra_estratos.csv');c=c.drop(columns=['id_estrato','ubicacion'],errors='ignore');c.to_csv(O/'aforos_y_factores_por_estrato_citra.csv',index=False,encoding='utf-8-sig')
ar=pd.read_csv(R/'aristo_balance_fecha.csv').drop(columns=['filas_fuente'],errors='ignore');ar.to_csv(O/'aforos_y_factores_por_estrato_aristo.csv',index=False,encoding='utf-8-sig')
loc=pd.read_csv(R/'citra_localidades_original.csv').drop(columns=['id_OD_zonal'],errors='ignore');loc.to_csv(O/'demanda_observada_citra_por_localidad_12_horas.csv',index=False,encoding='utf-8-sig')
# Atributos de red entre referencias zonales usadas; no geometrías ni trayectorias individuales.
used=set(pd.read_csv(B/'02_zonificaciones/catalogo_zonificacion_por_localidades.csv').codigo_unidad_localidad)
phys=pd.read_csv(R/'atributos_viales_localidades.csv');phys=phys[phys.zo.isin(used)&phys.zd.isin(used)]
phys=phys.rename(columns={'zo':'codigo_origen','zd':'codigo_destino','segmento':'segmento_de_costos','alternativa':'ruta_modelada','km':'distancia_vial_referencia_km','h':'tiempo_vial_referencia_h','cov':'costo_operacion_vial_referencia_CLP'});phys.to_csv(O/'atributos_viales_procesados_entre_zonas.csv.gz',index=False,encoding='utf-8-sig',compression='gzip')
# Temporalización y antecedentes estacionales: insumos agregados, no respuestas individuales.
monthly=pd.read_csv(R/'aristo_mensual_original.csv')
monthly_fields=['campana','fecha','sentido_cruce','segmento','version','unidad','origen','destino','zona_origen','zona_destino','componente','subtipo','flujo','N_perfil','perfil_otro_dia','procedimiento','calidad_perfil','vista','anio','mes','escenario','coef_mes_final','temporada_destino','aporte_mes','invierno_es_proxy','naturaleza_anual','alcance']
monthly=monthly[[c for c in monthly_fields if c in monthly]]
monthly.to_csv(O/'temporalizacion_mensual_aristo_procesada.csv.gz',index=False,encoding='utf-8-sig',compression='gzip')
for source,target in [('aristo_factores_temporales.csv','factores_temporales_aristo.csv'),('PNC_ratios.csv','factores_estacionales_pnc_referencia.csv'),('PNC_VP.csv','factores_estacionales_pnc_categoria_vp.csv')]:
 table=pd.read_csv(R/source).drop(columns=['filas_fuente'],errors='ignore');table.to_csv(O/target,index=False,encoding='utf-8-sig')
pd.read_csv(R/'longitudes_CAM.csv').to_csv(O/'estadisticas_agregadas_longitud_cam.csv',index=False,encoding='utf-8-sig')
profiles=[]
for version in ['A','B']:
 table=pd.read_csv(R/('aristo_OD_'+version+'.csv')).drop(columns=['filas_fuente','origen_original','destino_original'],errors='ignore');profiles.append(table)
pd.concat(profiles,ignore_index=True).to_csv(O/'perfiles_od_aristo_procesados_a_y_b.csv.gz',index=False,encoding='utf-8-sig',compression='gzip')
controls=pd.read_csv(R/'controles.csv').drop(columns=['latitud','longitud'],errors='ignore');controls.to_csv(O/'controles_y_movimientos_procesados.csv',index=False,encoding='utf-8-sig')
dictionary=[]
for name in out:
 if name.startswith('promedio_ponderado_'):desc='Promedio descriptivo ponderado por la demanda de referencia positiva con valor conocido. No sustituye el cálculo de captación e inducción por componente.'
 elif name.startswith('referencia_usada_para_promedio_'):desc='Denominador de referencia conocido utilizado para el promedio correspondiente. No sumar entre variables.'
 elif name in quant:desc='Suma conservando faltantes: referencia, SBO, transferencia, inducción o demanda de la alternativa. Definición detallada en la metodología.'
 elif name.startswith('componentes_'):desc='Conteo de componentes del modelo tras agregación; no representa cantidad de encuestas ni vehículos.'
 else:desc='Dimensión de zonificación, OD, fuente, año, segmento o escenario. Las situaciones y escenarios son alternativos y no se suman.'
 dictionary.append({'campo':name,'definicion':desc})
pd.DataFrame(dictionary).to_csv(O/'diccionario_comparacion_procesada.csv',index=False,encoding='utf-8-sig')
w=Workbook();w.remove(w.active)
for name,frame in [('Aforos y factores CITRA',c),('Aforos y factores ARISTO',ar),('OD observado CITRA 12h',loc),('Diccionario de campos',pd.DataFrame(dictionary))]:
 s=w.create_sheet(name);s.append(list(frame.columns))
 for row in frame.astype(object).where(frame.notna(),None).itertuples(index=False,name=None):
  s.append(list(row))
  for cell in s[s.max_row]:
   if isinstance(cell.value,str):cell.data_type='s'
 s.freeze_panes='A2';s.auto_filter.ref=s.dimensions
 for cell in s[1]:cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='245B49')
 for col in s.columns:s.column_dimensions[col[0].column_letter].width=28
w.save(O/'aforos_factores_y_datos_observados_procesados.xlsx')
report={'estado':'correcto' if all(checks.values()) else 'revisar','verificaciones':checks,'filas_procesadas_agregadas':len(out),'filas_estratos_citra':len(c),'filas_estratos_aristo':len(ar),'filas_od_observado_citra':len(loc),'filas_atributos_viales':len(phys),'alcance':'Resultados por OD y escenario y aforos por estrato. No incluye encuestas individuales, identificadores, coordenadas ni originales. Los promedios de costos/probabilidad son descriptivos; no reemplazan el cálculo por componente.'}
(B/'05_verificacion/control_datos_procesados_publicados.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));assert all(checks.values()),checks
