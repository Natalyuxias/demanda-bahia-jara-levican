"""Comparar las tablas agregadas de ambas zonificaciones sin recalcular demanda."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();B=a.salida.resolve();O=B/'07_datos_procesados';O.mkdir(parents=True,exist_ok=True)
metrics=['Q_referencia','D_tierra_SBO','D_actual_SBO','D_existente_nuevo','D_tierra_CP_existente','D_actual_CP_existente','D_inducida_incremental','D_inducida_tierra','D_inducida_actual','D_inducida_nuevo','D_tierra_CP_total','D_actual_CP_total','D_nuevo_CP_total','D_residual_existente']
labels={'situacion':'Situación de evaluación','perfil_ARISTO':'Perfil ARISTO','escenario_PIB':'Escenario del PIB','tasa_PIB_anual':'Crecimiento anual del PIB','escenario_captacion':'Escenario de captación','escenario_induccion_costo':'Escenario de inducción por costo','anio':'Año','segmento':'Segmento','unidad':'Unidad','temporada':'Estación','fuente':'Fuente','Q_referencia':'Demanda existente de referencia','D_tierra_SBO':'Demanda terrestre sin proyecto','D_actual_SBO':'Demanda lacustre actual sin proyecto','D_existente_nuevo':'Demanda existente transferida al proyecto','D_tierra_CP_existente':'Demanda existente que permanece por tierra','D_actual_CP_existente':'Demanda existente que permanece en barcaza actual','D_inducida_incremental':'Inducción incremental total','D_inducida_tierra':'Inducción asignada a tierra','D_inducida_actual':'Inducción asignada a barcaza actual','D_inducida_nuevo':'Inducción asignada al proyecto','D_tierra_CP_total':'Demanda calculable por tierra','D_actual_CP_total':'Demanda calculable en barcaza actual','D_nuevo_CP_total':'Demanda calculable del cruce del proyecto','D_residual_existente':'Demanda existente sin asignación calculable'}
common=['situacion','perfil_ARISTO','escenario_PIB','tasa_PIB_anual','escenario_captacion','escenario_induccion_costo','anio','segmento','unidad']
frames={};checks={};counts={}
for period in ['anual','estacional']:
 for view in ['total_fuentes','por_fuente']:
  stem=f'resumen_{period}_{view}_ambos_sentidos';name=f'comparacion_{period}_{view}'
  old=pd.read_csv(B/'03_resultados_zonificacion_anterior/tablas_csv'/f'{stem}.csv.gz');fine=pd.read_csv(B/'04_resultados_zonificacion_localidades/tablas_csv'/f'{stem}.csv.gz')
  keys=common+(['temporada'] if period=='estacional' else [])+(['fuente'] if view=='por_fuente' else [])
  assert not old.duplicated(keys).any() and not fine.duplicated(keys).any(),name
  cols=keys+metrics+['cobertura_temporal']
  out=old[cols].merge(fine[cols],on=keys,suffixes=('_zonas_anteriores','_localidades'),how='outer',validate='one_to_one',indicator=True)
  checks[name+'_mismas_claves']=bool(out._merge.eq('both').all());assert checks[name+'_mismas_claves']
  out=out.drop(columns='_merge')
  for m in metrics:out['diferencia_'+m]=out[m+'_localidades']-out[m+'_zonas_anteriores']
  checks[name+'_misma_referencia']=bool(np.allclose(out.Q_referencia_zonas_anteriores,out.Q_referencia_localidades,equal_nan=True))
  checks[name+'_ND_preservados']=all(out['diferencia_'+m].isna().equals(out[m+'_zonas_anteriores'].isna()|out[m+'_localidades'].isna()) for m in metrics)
  ordered=keys+[c for m in metrics for c in [m+'_zonas_anteriores',m+'_localidades','diferencia_'+m]]+['cobertura_temporal_zonas_anteriores','cobertura_temporal_localidades']
  out=out[ordered].sort_values(keys);out.to_csv(O/f'{name}.csv.gz',index=False,encoding='utf-8-sig',compression='gzip',float_format='%.10g');frames[name]=out;counts[name]=len(out)
def central(f):return f[f.perfil_ARISTO.eq('B')&f.escenario_PIB.eq('central')&f.escenario_captacion.isin(['central','no_aplica'])&f.escenario_induccion_costo.isin(['central','no_aplica'])]
def readable(frame,short=False):
 keys=[c for c in common+['temporada','fuente'] if c in frame]
 ms=['Q_referencia','D_tierra_CP_total','D_actual_CP_total','D_nuevo_CP_total','D_inducida_incremental','D_residual_existente'] if short else metrics
 cols=keys+[c for m in ms for c in [m+'_zonas_anteriores',m+'_localidades','diferencia_'+m]]+['cobertura_temporal_zonas_anteriores','cobertura_temporal_localidades']
 f=frame[cols].copy();rename={**labels,'cobertura_temporal_zonas_anteriores':'Cobertura temporal · zonas anteriores','cobertura_temporal_localidades':'Cobertura temporal · localidades'}
 for m in ms:
  rename[m+'_zonas_anteriores']=labels[m]+' · zonas anteriores';rename[m+'_localidades']=labels[m]+' · localidades';rename['diferencia_'+m]='Diferencia · '+labels[m]
 f=f.rename(columns=rename)
 f['Escenario del PIB']=f['Escenario del PIB'].replace({'conservador':'PIB bajo: 1%','central':'PIB central: 2%','alto':'PIB alto: 3%'})
 f['Crecimiento anual del PIB']=f['Crecimiento anual del PIB'].map(lambda v:f'{v:.0%}')
 f['Escenario de captación']=f['Escenario de captación'].replace({'no_aplica':'No aplica a SBO','central':'Central','conservador':'Conservador','alto':'Alto'})
 f['Escenario de inducción por costo']=f['Escenario de inducción por costo'].replace({'no_aplica':'No aplica a SBO','central':'Central','menor_induccion':'Menor inducción','mayor_induccion':'Mayor inducción'})
 return f
guide=pd.DataFrame([{'Tema':'Objeto','Descripción':'Comparación directa de ambas zonificaciones a partir de las tablas agregadas publicadas. No se recalcula el modelo ni se añaden encuestas.'},{'Tema':'Diferencia','Descripción':'Diferencia = localidades menos zonas anteriores. Una celda sin estimación conserva esa condición; no se sustituye por cero.'},{'Tema':'Escenario central','Descripción':'Perfil ARISTO B, PIB 2%, captación e inducción centrales. Se incluye la SBO, cuyo caso de captación e inducción es No aplica.'},{'Tema':'Todos los casos','Descripción':'Las hojas anuales completas incluyen todos los escenarios calculados, ambas versiones ARISTO, años, segmentos y unidades. Los CSV incluyen también todo el detalle estacional agregado.'},{'Tema':'Unidades','Descripción':'No sumar alternativas, perfiles, años, personas con vehículos o VP con VL. La tabla de total de fuentes no se suma a su desagregación por fuente.'},{'Tema':'Temporalidad','Descripción':'Anual significa aporte temporal modelado. ARISTO VL y VP representan seis meses cada uno. El campo de cobertura conserva los meses por fuente.'},{'Tema':'VST carga','Descripción':'El parámetro CAM vigente es 12.954 CLP por hora de camión. Los demás segmentos conservan su valor anterior.'}])
sheets=[('Guía de lectura',guide),('Central anual total fuentes',readable(central(frames['comparacion_anual_total_fuentes']),True)),('Anual todos los casos',readable(frames['comparacion_anual_total_fuentes'])),('Anual por fuente',readable(frames['comparacion_anual_por_fuente'])),('Central estacional',readable(central(frames['comparacion_estacional_total_fuentes']),True))]
w=Workbook(write_only=True)
for name,f in sheets:
 ws=w.create_sheet(name);ws.freeze_panes='A2';ws.row_dimensions[1].height=55
 for i,c in enumerate(f.columns,1):ws.column_dimensions[get_column_letter(i)].width=min(58,max(18,len(str(c))*.8))
 cells=[]
 for v in f.columns:
  c=WriteOnlyCell(ws,value=str(v));c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='245B49');c.alignment=Alignment(wrap_text=True);cells.append(c)
 ws.append(cells)
 for row in f.astype(object).where(f.notna(),None).itertuples(index=False,name=None):
  cells=[]
  for v in row:
   c=WriteOnlyCell(ws,value=v)
   if isinstance(v,str):c.data_type='s'
   elif isinstance(v,(float,np.floating)):c.number_format='#,##0.00'
   cells.append(c)
  ws.append(cells)
 ws.auto_filter.ref=f'A1:{get_column_letter(len(f.columns))}{len(f)+1}'
w.save(O/'comparacion_entre_zonificaciones_anual.xlsx')
report={'estado':'correcto' if all(checks.values()) else 'revisar','verificaciones':checks,'filas_por_tabla':counts,'filas_hojas_Excel':{n:len(f) for n,f in sheets},'alcance':'Comparaciones agregadas de resultados ya publicados; diferencia localidades menos zonas anteriores, sin sustituir nulos por cero y sin identificadores individuales.'}
(B/'05_verificacion/control_comparaciones_publicadas.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert all(checks.values())
print(json.dumps(report,ensure_ascii=False,indent=2))
