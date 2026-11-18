"""Actualizar CAM conservando componentes monetarios, cantidades de referencia y otros segmentos."""
from pathlib import Path
import json,math,unicodedata
import numpy as np
import pandas as pd
B=Path(__file__).resolve().parents[1];R=B/'00_fuentes/referencia';P=B/'02_procesamiento';V=B/'05_verificacion'
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',str(s).upper()) if unicodedata.category(c)!='Mn').strip()
def actualizar():
 settings=json.loads((R/'config_valor_tiempo_por_segmento.json').read_text());ref=settings['valor_referencia_CLP_persona_h'];target=settings['valores_por_segmento']['CAM'];dv=target-ref
 path=P/'comparacion_metodologia_original.csv.gz';d=pd.read_csv(path,float_precision='round_trip');before=d.copy();mask=d.segmento.eq('CAM');c=d.loc[mask].copy()
 costs=pd.read_csv(R/'costos_originales.csv.gz',float_precision='round_trip');costs=costs[costs.segmento.eq('CAM')&costs.anio.eq(2026)]
 ti=pd.read_csv(R/'tiempos_cam_modelo_referencia.csv',float_precision='round_trip');ix=costs.set_index(['alternativa_proyecto','id_base']);tx=ti.set_index(['alternativa_proyecto','id_base'])
 keys=pd.MultiIndex.from_frame(c[['alternativa_proyecto','id_base']]);r=ix.reindex(keys).reset_index(drop=True);t=tx.reindex(keys).reset_index(drop=True);c=c.reset_index(drop=True)
 geo=json.loads(__import__('gzip').open(P/'geografia.json.gz','rt').read());names={norm(z['name']):z['id'] for z in geo['zones'] if z['kind']=='localidad'}
 phys=pd.read_csv(R/'atributos_viales_localidades.csv');phys=phys[phys.segmento.eq('CAM')];physical={(x.zo,x.zd,x.alternativa):x.h for x in phys.itertuples()};aliases={'COIHAIQUE':'COYHAIQUE','RIO IBANEZ':'PUERTO IBANEZ','AYSEN':'PUERTO AYSEN','CISNES':'PUERTO CISNES'};cache={}
 def dh(i,alt):
  if c.at[i,'zonificacion']=='original' or c.at[i,'fuente']=='CITRA':return 0.
  rr=r.iloc[i];a=names.get(aliases.get(norm(rr.origen),norm(rr.origen)));b=names.get(aliases.get(norm(rr.destino),norm(rr.destino)))
  if bool(rr.costo_solo_nucleo):a,b=('LOC_CHILE_CHICO','LOC_COYHAIQUE') if norm(rr.origen)=='CHILE CHICO' else ('LOC_COYHAIQUE','LOC_CHILE_CHICO')
  x,y=c.at[i,'zona_origen_localidad'],c.at[i,'zona_destino_localidad']
  if not a or not b or x=='SIN_DESAGREGAR':return 0.
  if bool(rr.costo_solo_nucleo):
   if a=='LOC_COYHAIQUE':x=a
   if b=='LOC_COYHAIQUE':y=b
  k=(a,b,x,y,alt)
  if k not in cache:
   p0,p1=physical.get((a,b,alt)),physical.get((x,y,alt));cache[k]=float(p1-p0) if p0 is not None and p1 is not None and pd.notna(p0) and pd.notna(p1) else 0.
  return cache[k]
 for alt,tc,cg,delta in [('tierra','T_tierra','CG_tierra_SBO','delta_costo_tierra'),('actual','T_actual','CG_actual_SBO','delta_costo_actual'),('proyecto','T_proyecto','CG_nuevo_CP','delta_costo_proyecto')]:
  hs=np.array([dh(i,c.at[i,'alternativa_proyecto'] if alt=='proyecto' else alt) for i in range(len(c))]);times=t[tc].to_numpy()+hs
  c['tiempo_CAM_'+alt+'_h']=times
  olddelta=delta+'_VST_referencia'
  if olddelta not in c:c[olddelta]=c[delta].fillna(0)
  initial=r[cg].to_numpy()+c[olddelta].fillna(0).to_numpy()
  c[cg]=initial+dv*times;c[delta]=c[olddelta].fillna(0)+dv*hs
 c['CG_origen_SBO']=np.where(c.fuente.eq('CITRA'),c.CG_tierra_SBO,c.CG_actual_SBO)
 model=r.modelable_captacion.to_numpy(dtype=bool)&c.CG_origen_SBO.gt(0).to_numpy()&c.CG_nuevo_CP.gt(0).to_numpy();p=np.full(len(c),np.nan)
 cc=json.loads((R/'config_transferencia.json').read_text());ec=json.loads((R/'config_induccion.json').read_text());tail=r.costo_solo_nucleo.to_numpy(dtype=bool)
 saving=(c.CG_origen_SBO-c.CG_nuevo_CP)/c.CG_origen_SBO
 for case in c.escenario_captacion.unique():
  m=model&c.escenario_captacion.eq(case).to_numpy();curve=cc['curvas'][cc['familia']['CAM']][case];fact=cc['factibilidad'][cc['familia']['CAM']];v=saving.to_numpy();a=m&~tail;b=m&tail
  p[a]=np.interp(v[a],cc['nudos_ahorro_relativo'],curve)*fact;lam=cc['peso_cota_superior_cola_comun'][case];p[b]=((1-lam)*np.interp(np.minimum(v[b],0),cc['nudos_ahorro_relativo'],curve)+lam*np.interp(np.maximum(v[b],0),cc['nudos_ahorro_relativo'],curve))*fact
 c['p_nuevo']=p;co=c.CG_origen_SBO.to_numpy();cn=c.CG_nuevo_CP.to_numpy();q=c.Q_referencia.to_numpy();ms=c[['CG_tierra_SBO','CG_actual_SBO']].where(lambda z:z>0).min(axis=1).to_numpy();mp=c[['CG_tierra_SBO','CG_actual_SBO','CG_nuevo_CP']].where(lambda z:z>0).min(axis=1).to_numpy()
 valid=r.modelable_induccion.to_numpy(dtype=bool)&model&np.isfinite(q)&np.isfinite(ms)&np.isfinite(mp);ind=np.full(len(c),np.nan);ind[valid]=0.;im=valid&(mp<ms-1e-9);eps=c.escenario_elasticidad.map(ec['elasticidades']['CAM']).to_numpy();ind[im]=np.maximum(0,q[im]*((mp[im]/co[im])**eps[im]-(ms[im]/co[im])**eps[im]))
 cap=q*p;rem=q-cap;source=c.fuente.eq('CITRA').to_numpy();known=np.isfinite(p);ki=np.isfinite(ind)
 c['D_existente_nuevo']=cap;c['D_desviada_tierra']=np.where(known,np.where(source,cap,0),np.nan);c['D_desviada_actual']=np.where(known,np.where(~source,cap,0),np.nan)
 c['D_tierra_CP_existente']=np.where(known,np.where(source,rem,0),np.nan);c['D_actual_CP_existente']=np.where(known,np.where(~source,rem,0),np.nan)
 c['D_inducida_incremental']=ind;c['D_inducida_nuevo']=ind*p;c['D_inducida_tierra']=np.where(ki,np.where(source,ind*(1-p),0),np.nan);c['D_inducida_actual']=np.where(ki,np.where(~source,ind*(1-p),0),np.nan)
 c['D_residual_existente']=np.where(np.isfinite(q),np.where(known,0,q),np.nan);c['D_base_fuera_soporte_induccion']=np.where(valid,0,q)
 for route,ex in [('tierra','D_tierra_CP_existente'),('actual','D_actual_CP_existente'),('nuevo','D_existente_nuevo')]:c['D_'+route+'_CP_total']=c[[ex,'D_inducida_'+route]].sum(axis=1,min_count=1)
 c['CG_min_SBO']=ms;c['CG_min_CP']=mp;c['epsilon_CG']=eps;c['modelable_captacion']=model;c['modelable_induccion']=valid
 c['nuevo_diario_equiv']=c.D_nuevo_CP_total/r.dias_equivalentes.to_numpy();c['nuevo_por_zarpe_equiv']=c.D_nuevo_CP_total/r.zarpes_nuevo_sentido_temporada.to_numpy();c['actual_SBO_por_zarpe_equiv']=c.D_actual_SBO/r.zarpes_actual_sentido_temporada.to_numpy();c['actual_CP_por_zarpe_equiv']=c.D_actual_CP_total/r.zarpes_actual_sentido_temporada.to_numpy();c['valor_tiempo_CAM_CLP_h']=target
 for col in c:
  if col not in d:d[col]=np.nan
  d.loc[mask,col]=c[col].to_numpy()
 common=before.columns.intersection(d.columns);checks={'otros_segmentos_intactos':before.loc[~mask,common].equals(d.loc[~mask,common]),'referencia_y_SBO_intactas':all(np.allclose(before[z],d[z],equal_nan=True) for z in ['Q_referencia','D_tierra_SBO','D_actual_SBO']),'tiempos_recuperados_CAM_modelable':bool(c.loc[model,['tiempo_CAM_tierra_h','tiempo_CAM_actual_h','tiempo_CAM_proyecto_h']].notna().all().all()),'p_entre_cero_y_uno':bool(c.p_nuevo.dropna().between(0,1).all()),'conservacion_existente':bool(np.allclose(q,c[['D_existente_nuevo','D_tierra_CP_existente','D_actual_CP_existente','D_residual_existente']].sum(axis=1).where(c.Q_referencia.notna()),equal_nan=True)),'induccion_no_negativa':bool(c.D_inducida_incremental.dropna().ge(0).all())}
 assert all(checks.values()),checks
 d.to_csv(path,index=False,compression='gzip')
 filt=lambda z:z[(z.zonificacion=='localidades')&(z.anio==2026)&(z.version_referencia=='B')&(z.escenario_PIB=='central')&(z.escenario_captacion=='central')&(z.escenario_elasticidad=='central')&(z.segmento=='CAM')].groupby('alternativa_proyecto').D_nuevo_CP_total.sum(min_count=1)
 comparison=pd.concat([filt(before).rename('demanda_CAM_anterior'),filt(d).rename('demanda_CAM_actualizada')],axis=1).reset_index()
 result={'estado':'correcto','valor_anterior':ref,'valor_CAM_actualizado':target,'unidad':'CLP enero 2026 por hora de camión, ocupación 1','verificaciones':checks,'alcance':'Solo CAM; CG actualizado por diferencia de VST multiplicada por tiempo recuperado. COV, tarifas, referencia, expansión y demás segmentos intactos.','comparacion_central_2026_localidades':comparison.to_dict('records')}
 (V/'actualizacion_valor_tiempo_carga.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':actualizar()
