"""Comparación espacial: mismas cohortes, expansión, tarifas y ecuaciones del modelo oficial.
Solo se desagrega ARISTO con la composición original de cada fecha y OD.
CITRA ya contenía localidades en el modelo oficial: conserva flujos y costos.
"""
from pathlib import Path
import json,gzip,hashlib,math,unicodedata
from collections import defaultdict,Counter
import numpy as np
import pandas as pd
B=Path(__file__).resolve().parents[1];R=B/'00_fuentes/referencia';P=B/'02_procesamiento';V=B/'05_verificacion'
def read(p):return pd.read_csv(p,keep_default_na=False)
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',str(s).upper()) if unicodedata.category(c)!='Mn').strip()
def zone(x):
 try:return str(int(float(x)))
 except (ValueError,TypeError):return ''
def finite(x):
 try:return math.isfinite(float(x))
 except (ValueError,TypeError):return False
def gz(p):
 with gzip.open(p,'rt') as f:return json.load(f)
# The historical workbook is the frozen, verified model, not the recent recalculation.
book=R/'modelo_anterior.xlsx';costs=pd.read_csv(R/'costos_originales.csv.gz',float_precision='round_trip');old=pd.read_csv(R/'demanda_original.csv.gz',float_precision='round_trip')
cfg=json.loads((R/'config_oficial.json').read_text());cc=json.loads((R/'config_transferencia.json').read_text());ec=json.loads((R/'config_induccion.json').read_text())
geo=gz(P/'geografia.json.gz');georecords={(r['source'],str(r['id'])):r for r in geo['records']};zones={z['id']:z for z in geo['zones']}
monthly=read(R/'aristo_mensual_original.csv');monthly=monthly[(monthly.escenario=='central')&(monthly.vista=='clases_originales')]
ind=read(R/'aristo_individual.csv');physical=read(R/'atributos_viales_localidades.csv')
phys={(r.zo,r.zd,r.segmento,r.alternativa):r._asdict() for r in physical.itertuples(index=False)}
# Original date profiles and original temporal coefficients establish the locality shares.
profiles=defaultdict(list)
for r in ind.to_dict('records'):
 k=(r['campana'],r['fecha'],r['sentido_cruce'],r['segmento'],zone(r['zona_origen']),zone(r['zona_destino']))
 profiles[k].append(str(r['id_encuesta']))
shares=defaultdict(lambda:defaultdict(float));shareids=defaultdict(lambda:defaultdict(set));unmapped=[]
for r in monthly.to_dict('records'):
 key=(r['version'],r['temporada_destino'],r['sentido_cruce'],r['segmento'],zone(r['zona_origen']),zone(r['zona_destino']),r['componente'],r['subtipo'])
 if not finite(r['aporte_mes']) or float(r['aporte_mes'])<=0:continue
 dates=str(r['fechas_perfil']).split('|');ids=[]
 for date in dates:ids+=profiles.get((r['campana'],date,r['sentido_cruce'],r['segmento'],zone(r['zona_origen']),zone(r['zona_destino'])),[])
 ids=sorted(set(ids));ids=[id for id in ids if ('ARISTO',id) in georecords]
 if not ids:
  shares[key][('SIN_DESAGREGAR','SIN_DESAGREGAR')]+=float(r['aporte_mes']);continue
 for id in ids:
  gr=georecords['ARISTO',id];pair=(gr['origin']['new_zone'],gr['destination']['new_zone']);shares[key][pair]+=float(r['aporte_mes'])/len(ids);shareids[key][pair].add(id)
# Anchors are the named original reference; common-tail costs retain the same core.
alias={'COIHAIQUE':'COYHAIQUE','RIO IBANEZ':'PUERTO IBANEZ','AYSEN':'PUERTO AYSEN','CISNES':'PUERTO CISNES'}
nameid={norm(z['name']):z['id'] for z in geo['zones'] if z['kind']=='localidad'}
def anchor(name):return nameid.get(alias.get(norm(name),norm(name)))
def oldanchors(r):
 if bool(r.costo_solo_nucleo):return ('LOC_CHILE_CHICO','LOC_COYHAIQUE') if norm(r.origen)=='CHILE CHICO' else ('LOC_COYHAIQUE','LOC_CHILE_CHICO')
 return anchor(r.origen),anchor(r.destino)
def delta(r,pair,alternative):
 a,b=oldanchors(r);x,y=pair
 if not a or not b or x=='SIN_DESAGREGAR':return 0.,'Costo heredado: sin anclaje físico comparable'
 if bool(r.costo_solo_nucleo):
  # Preserve the unpriced common northern tail; change only its southern local endpoint.
  if a=='LOC_COYHAIQUE':x=a
  if b=='LOC_COYHAIQUE':y=b
 if (a,b)==(x,y):return 0.,'Mismo referente físico: costo heredado sin cambio'
 segment='VL' if r.segmento=='VP' else r.segmento
 p0=phys.get((a,b,segment,alternative));p1=phys.get((x,y,segment,alternative))
 if p0 is None or p1 is None or not all(finite(p[k]) for p in [p0,p1] for k in ['h','km','cov']):return 0.,'Costo heredado: delta vial no respaldado para ambos referentes'
 dh=float(p1['h'])-float(p0['h']);dk=float(p1['km'])-float(p0['km'])
 if r.segmento=='PEATON':
  rate=9000/382.515 if alternative=='tierra' else 10000/121.956 if alternative=='actual' else cfg['tarifa_bus_km'];dc=dk*rate
 else:dc=float(p1['cov'])-float(p0['cov'])
 return dc+cfg['VST']*float(r.ocupacion)*dh,'Delta espacial de COV/tiempo vial; tarifas y operación heredadas'
# Split only after all historical expansion/temporal/projection operations: original Q is preserved.
cidx={(r.alternativa_proyecto,int(r.id_base)):r for r in costs.itertuples(index=False)}
metrics=['Q_referencia','D_tierra_SBO','D_actual_SBO','D_existente_nuevo','D_desviada_tierra','D_desviada_actual','D_tierra_CP_existente','D_actual_CP_existente','D_inducida_incremental','D_inducida_tierra','D_inducida_actual','D_inducida_nuevo','D_tierra_CP_total','D_actual_CP_total','D_nuevo_CP_total','D_residual_existente','D_base_fuera_soporte_induccion']
result=[];trace=[];nchanged=0
for row in old.to_dict('records'):
 r=cidx[row['alternativa_proyecto'],int(row['id_base'])];base={**row,'zonificacion':'original','zona_origen_anterior':r.zona_origen,'zona_destino_anterior':r.zona_destino,'criterio_espacial':'Modelo anterior reproducido sin cambios','participacion_localidad':1.,'ids_encuestas':''};result.append(base)
 if r.fuente=='CITRA':
  a,b=anchor(r.origen),anchor(r.destino);parts=[((a or 'SIN_DESAGREGAR',b or 'SIN_DESAGREGAR'),1.,set())];reason='CITRA ya estaba desagregada por localidad: se conserva cálculo completo'
 else:
  key=(r.version_referencia,r.temporada,r.sentido_cruce,r.segmento,zone(r.zona_origen),zone(r.zona_destino),r.componente,r.subtipo);raw=shares.get(key,{})
  total=sum(raw.values());parts=[(p,w/total,shareids[key][p]) for p,w in raw.items()] if total>0 else [(('SIN_DESAGREGAR','SIN_DESAGREGAR'),1.,set())];reason='Composición por localidad dentro del mismo perfil fecha/OD y temporalización original' if total else 'Sin perfil desagregable: se conserva componente zonal'
 for pair,weight,ids in parts:
  z={**base,'zonificacion':'localidades','participacion_localidad':weight,'ids_encuestas':'|'.join(sorted(ids)),'criterio_espacial':reason,'zona_origen_localidad':pair[0],'zona_destino_localidad':pair[1],'origen':zones[pair[0]]['name'] if pair[0] in zones else row['origen'],'destino':zones[pair[1]]['name'] if pair[1] in zones else row['destino']}
  for m in metrics:z[m]=row[m]*weight if finite(row[m]) else np.nan
  if r.fuente=='CITRA':z['delta_costo_tierra']=z['delta_costo_actual']=z['delta_costo_proyecto']=0.;result.append(z);continue
  dt,nt=delta(r,pair,'tierra');da,na=delta(r,pair,'actual');dn,nn=delta(r,pair,r.alternativa_proyecto)
  z.update(delta_costo_tierra=dt,delta_costo_actual=da,delta_costo_proyecto=dn,evidencia_delta_tierra=nt,evidencia_delta_actual=na,evidencia_delta_proyecto=nn)
  co=float(r.CG_origen_SBO)+da if finite(r.CG_origen_SBO) else np.nan;cn=float(r.CG_nuevo_CP)+dn if finite(r.CG_nuevo_CP) else np.nan;ct=float(r.CG_tierra_SBO)+dt if finite(r.CG_tierra_SBO) else np.nan;ca=float(r.CG_actual_SBO)+da if finite(r.CG_actual_SBO) else np.nan
  z.update(CG_origen_SBO=co,CG_nuevo_CP=cn,CG_tierra_SBO=ct,CG_actual_SBO=ca)
  # Original cost/modelability restrictions are inherited; no expansion of model scope.
  modelable=bool(r.modelable_captacion) and finite(co) and finite(cn) and co>0 and cn>0 and r.segmento in cc['familia'];p=np.nan;induced=np.nan
  if modelable:
   a=(co-cn)/co;case=row['escenario_captacion'];curve=cc['curvas'][cc['familia'][r.segmento]][case]
   if bool(r.costo_solo_nucleo):lam=cc['peso_cota_superior_cola_comun'][case];p=((1-lam)*np.interp(min(a,0),cc['nudos_ahorro_relativo'],curve)+lam*np.interp(max(a,0),cc['nudos_ahorro_relativo'],curve))*cc['factibilidad'][cc['familia'][r.segmento]]
   else:p=np.interp(a,cc['nudos_ahorro_relativo'],curve)*cc['factibilidad'][cc['familia'][r.segmento]]
  q=z['Q_referencia'];vals=[v for v in [ct,ca] if finite(v) and v>0];ms=min(vals) if vals else np.nan;mp=min(vals+[cn]) if vals and finite(cn) and cn>0 else np.nan
  if bool(r.modelable_induccion) and modelable and finite(q) and finite(ms) and finite(mp):
   eps=ec['elasticidades'][r.segmento][row['escenario_elasticidad']];induced=max(0,q*((mp/co)**eps-(ms/co)**eps)) if mp<ms-1e-9 else 0.
  captured=q*p if finite(q) and finite(p) else np.nan;remaining=q-captured if finite(captured) else np.nan;inew=induced*p if finite(induced) and finite(p) else np.nan
  z.update(p_nuevo=p,CG_min_SBO=ms,CG_min_CP=mp,D_existente_nuevo=captured,D_desviada_tierra=0. if finite(p) else np.nan,D_desviada_actual=captured,D_tierra_CP_existente=0. if finite(p) else np.nan,D_actual_CP_existente=remaining,D_inducida_incremental=induced,D_inducida_tierra=0. if finite(induced) else np.nan,D_inducida_actual=induced*(1-p) if finite(induced) and finite(p) else np.nan,D_inducida_nuevo=inew,D_residual_existente=q if not finite(p) else 0. if finite(q) else np.nan,D_base_fuera_soporte_induccion=q if not bool(r.modelable_induccion) else 0.,modelable_captacion=modelable,modelable_induccion=bool(r.modelable_induccion) and modelable)
  for route,existing in [('nuevo','D_existente_nuevo'),('tierra','D_tierra_CP_existente'),('actual','D_actual_CP_existente')]:
   x,y=z[existing],z['D_inducida_'+route];z['D_'+route+'_CP_total']=(x if finite(x) else 0)+(y if finite(y) else 0) if finite(x) or finite(y) else np.nan
  z['nuevo_diario_equiv']=z['D_nuevo_CP_total']/r.dias_equivalentes if finite(z['D_nuevo_CP_total']) else np.nan;z['nuevo_por_zarpe_equiv']=z['D_nuevo_CP_total']/r.zarpes_nuevo_sentido_temporada if finite(z['D_nuevo_CP_total']) else np.nan
  result.append(z)
out=pd.DataFrame(result)
# Validate inherited baseline and preserved demand on each original component, not only totals.
keys=['alternativa_proyecto','version_referencia','escenario_captacion','escenario_elasticidad','anio','id_base']
a=out[out.zonificacion.eq('original')].set_index(keys);b=out[out.zonificacion.eq('localidades')].groupby(keys,dropna=False).Q_referencia.sum(min_count=1)
checks={'misma_Q_por_componente_original':bool(np.allclose(a.Q_referencia.sort_index(),b.sort_index(),equal_nan=True)),'original_exacto':all(np.allclose(out[out.zonificacion.eq('original')][m],old[m],equal_nan=True) for m in metrics),'CITRA_costos_y_demanda_intactos':all(np.allclose(out[(out.zonificacion=='original')&(out.fuente=='CITRA')][m].reset_index(drop=True),out[(out.zonificacion=='localidades')&(out.fuente=='CITRA')][m].reset_index(drop=True),equal_nan=True) for m in metrics),'p_entre_cero_y_uno':out.p_nuevo.dropna().between(0,1).all()}
checks['conservacion_demanda_existente']=bool(np.allclose(out.Q_referencia,out[['D_existente_nuevo','D_tierra_CP_existente','D_actual_CP_existente','D_residual_existente']].fillna(0).sum(axis=1).where(out.Q_referencia.notna()),equal_nan=True))
z0=out[(out.zonificacion=='localidades')&(out.fuente=='ARISTO')].copy()
z0=z0[z0[['delta_costo_tierra','delta_costo_actual','delta_costo_proyecto']].fillna(0).abs().sum(axis=1)<1e-8]
z0=z0.merge(out[out.zonificacion=='original'],on=keys,suffixes=('','_original'),validate='many_to_one')
checks['sin_delta_fisico_mismo_resultado_ponderado']=all(np.allclose(z0[m],z0[m+'_original']*z0.participacion_localidad,equal_nan=True) for m in ['D_existente_nuevo','D_inducida_nuevo','D_nuevo_CP_total','D_residual_existente'])
validation={'estado':'correcto' if all(checks.values()) else 'revisar','verificaciones':{k:bool(v) for k,v in checks.items()},'filas':len(out),'metodo':'Modelo oficial congelado; misma muestra y selección de pantallas, pesos, temporalización, tarifas (incluida hipótesis CAM), conexiones, proyección, curvas e inducción. Solo se desagrega ARISTO por coordenadas y perfil original y se ajusta el delta espacial vial. CITRA ya contenía localidades y se conserva íntegra.','filas_con_delta_espacial':int(((out.get('delta_costo_tierra',0).fillna(0).abs()+out.get('delta_costo_actual',0).fillna(0).abs()+out.get('delta_costo_proyecto',0).fillna(0).abs())>1e-8).sum()),'limite':'Si no existe atributo vial comparable se conserva costo heredado y se marca; no se inventan costos ni se cambia el soporte. Los componentes sin perfil siguen zonales.'}
focus=out[(out.zonificacion=='localidades')&(out.version_referencia=='B')&(out.escenario_captacion=='central')&(out.escenario_elasticidad=='central')&(out.anio==2026)&(out.alternativa_proyecto=='A1')&(out.fuente=='ARISTO')].copy()
focus['con_perfil']=focus.ids_encuestas.fillna('').str.len().gt(0)
validation['cobertura_espacial_ARISTO_B_2026']={'filas':len(focus),'filas_con_perfil':int(focus.con_perfil.sum()),'flujo_con_perfil':float(focus.loc[focus.con_perfil,'Q_referencia'].sum()),'flujo_sin_perfil':float(focus.loc[~focus.con_perfil,'Q_referencia'].sum()),'flujo_con_algun_delta_no_respaldado':float(focus.loc[focus.evidencia_delta_actual.fillna('').str.contains('no respaldado|sin anclaje')|focus.evidencia_delta_proyecto.fillna('').str.contains('no respaldado|sin anclaje'),'Q_referencia'].sum()),'nota':'No sumar segmentos con unidades distintas: estas sumas solo permiten auditar componentes; ver desglose por segmento.'}
validation['cobertura_por_segmento']=focus.groupby('segmento',dropna=False).apply(lambda f:pd.Series({'flujo_referencia':f.Q_referencia.sum(min_count=1),'flujo_con_perfil':f.loc[f.con_perfil,'Q_referencia'].sum(min_count=1),'flujo_con_delta_vial_no_respaldado':f.loc[f.evidencia_delta_actual.fillna('').str.contains('no respaldado|sin anclaje')|f.evidencia_delta_proyecto.fillna('').str.contains('no respaldado|sin anclaje'),'Q_referencia'].sum(min_count=1)}),include_groups=False).reset_index().astype(object).where(lambda d:pd.notna(d),None).to_dict('records')
# Proyección vigente: sensibilidad del PIB y elasticidad demanda/PIB fija.
# El cálculo espacial y los coeficientes de captación/inducción se conservan.
growth=json.loads((R/'config_crecimiento.json').read_text())
base2026=out[out.anio.eq(2026)].copy().reset_index(drop=True)
base2026['id_registro_2026']=np.arange(len(base2026))
years=cfg['anios'];projected=[]
quantity_cols=metrics+[c for c in ['nuevo_diario_equiv','nuevo_por_zarpe_equiv','actual_SBO_por_zarpe_equiv','actual_CP_por_zarpe_equiv'] if c in base2026]
family=base2026.segmento.map(growth['familia_por_segmento'])
eta=family.map({name:values['central'] for name,values in growth['elasticidades'].items()})
assert not (eta.isna()&base2026.Q_referencia.fillna(0).gt(0)).any(), 'Clase positiva sin elasticidad PIB compatible'
for scenario,rate in growth['tasas_PIB_anuales'].items():
 for year in years:
  z=base2026.copy();factor=(1+rate)**((year-2026)*eta)
  # Solo clases con base cero o faltante pueden carecer de eta: se conservan tal cual.
  factor=factor.fillna(1.)
  for col in quantity_cols:z[col]=pd.to_numeric(z[col],errors='coerce')*factor
  z['anio']=year;z['escenario_PIB']=scenario;z['tasa_PIB_anual']=rate
  z['elasticidad_demanda_PIB']=eta;z['factor_proyeccion_PIB']=factor;z['anio_base_proyeccion']=2026
  projected.append(z)
out=pd.concat(projected,ignore_index=True)
pkeys=keys+['escenario_PIB']
qa=out[out.zonificacion.eq('original')].set_index(pkeys).Q_referencia.sort_index()
qb=out[out.zonificacion.eq('localidades')].groupby(pkeys,dropna=False).Q_referencia.sum(min_count=1).sort_index()
checks['PIB_misma_Q_ambas_zonas']=bool(np.allclose(qa,qb,equal_nan=True))
checks['elasticidad_PIB_fija_entre_escenarios']=bool(out.groupby('segmento').elasticidad_demanda_PIB.nunique(dropna=True).le(1).all())
checks['PIB_1_2_3_por_ciento']=set(out.tasa_PIB_anual.unique())=={.01,.02,.03}
checks['base_2026_factor_uno']=bool(np.allclose(out.loc[out.anio.eq(2026),'factor_proyeccion_PIB'],1))
checks['cantidades_2026_intactas']=all(np.allclose(out[(out.anio==2026)&(out.escenario_PIB=='central')][col],base2026[col],equal_nan=True) for col in quantity_cols)
checks['CG_y_probabilidades_sin_cambio_por_PIB']=bool(out.groupby('id_registro_2026')[['p_nuevo','CG_origen_SBO','CG_nuevo_CP','epsilon_CG']].nunique(dropna=False).le(1).all().all())
expected={(1.2,.01):1.331850766,(1.2,.02):1.768825322,(1.2,.03):2.342675154,(.6,.01):1.154058389,(.6,.02):1.329971925,(.6,.03):1.530580006}
checks['factores_2050_contraste_independiente']=all(abs((1+rate)**(24*eta_value)-value)<1e-8 for (eta_value,rate),value in expected.items())
checks['PIB_conservacion_existente']=bool(np.allclose(out.Q_referencia,out[['D_existente_nuevo','D_tierra_CP_existente','D_actual_CP_existente','D_residual_existente']].fillna(0).sum(axis=1).where(out.Q_referencia.notna()),equal_nan=True))
# La reproducción histórica anterior se verificó antes de actualizar la proyección vigente.
checks['reproduccion_historica_previa_a_actualizar_PIB']=checks.pop('original_exacto')
validation.update(estado='correcto' if all(checks.values()) else 'revisar',verificaciones={k:bool(v) for k,v in checks.items()},filas=len(out),proyeccion_PIB={'anio_base':2026,'tasas':growth['tasas_PIB_anuales'],'eta_fija':{k:v['central'] for k,v in growth['elasticidades'].items()},'formula':'Q(t)=Q(2026)*(1+PIB)^((t-2026)*eta)','escenario_elasticidad':'Se refiere a inducción por costo generalizado, no a elasticidad respecto al PIB.'})
validation['filas_con_delta_espacial']=int(out[['delta_costo_tierra','delta_costo_actual','delta_costo_proyecto']].fillna(0).abs().sum(axis=1).gt(1e-8).sum())
validation['metodo']+=' Proyección vigente actualizada para ambas zonificaciones: PIB 1/2/3% con eta fija 1,2 vehículos y 0,6 peatones. La reproducción histórica se preserva en fuentes y las cantidades de 2026 no cambian.'
assert all(checks.values()),checks
out.to_csv(P/'comparacion_metodologia_original.csv.gz',index=False,compression='gzip')

(V/'comparacion_solo_zonas.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2));assert all(checks.values()),checks
print(json.dumps(validation,ensure_ascii=False,indent=2));print(out[(out.version_referencia=='B')&(out.escenario_captacion=='central')&(out.escenario_elasticidad=='central')&(out.anio==2026)&(out.escenario_PIB=='central')].groupby(['zonificacion','alternativa_proyecto','segmento']).D_nuevo_CP_total.sum(min_count=1).to_string())
