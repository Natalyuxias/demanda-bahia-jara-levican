"""Exportar tablas agregadas de demanda; no ejecuta estimación ni expone microdatos.
python exportar_entrega_formal.py --entrada detalle_privado.csv.gz --salida carpeta_entrega
"""
from pathlib import Path
import argparse,json,gzip,hashlib,time
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter

AP=argparse.ArgumentParser(description=__doc__)
AP.add_argument('--entrada',type=Path,default=Path(__file__).resolve().parents[1]/'privado/comparacion_metodologia_original.csv.gz')
AP.add_argument('--salida',type=Path,default=Path(__file__).resolve().parents[1])
AP.add_argument('--referencias',type=Path,help='Carpeta privada con zonas_55.csv y geografia.json.gz opcional; si se omite usa catálogos públicos de la entrega.')
AP.add_argument('--solo-tablas',action='store_true',help='Actualizar CSV y controles sin reescribir los libros Excel.')
A=AP.parse_args();OUT=A.salida.resolve();OUT.mkdir(parents=True,exist_ok=True)
start=time.time();counts={};checks={}
metrics=['Q_referencia','D_tierra_SBO','D_actual_SBO','D_existente_nuevo','D_tierra_CP_existente','D_actual_CP_existente','D_inducida_incremental','D_inducida_tierra','D_inducida_actual','D_inducida_nuevo','D_tierra_CP_total','D_actual_CP_total','D_nuevo_CP_total','D_residual_existente']
extra=['zonificacion','alternativa_proyecto','version_referencia','escenario_PIB','tasa_PIB_anual','escenario_captacion','escenario_elasticidad','anio','temporada','direccion_cruce','fuente','segmento','unidad','origen','destino','zona_origen_anterior','zona_destino_anterior','zona_origen_localidad','zona_destino_localidad','id_base']
d=pd.read_csv(A.entrada,usecols=metrics+extra)
d['unidad']=d.unidad.fillna('Sin unidad compatible')
# Catálogo de códigos, sin coordenadas ni identificadores de encuestas.
cat={}
if A.referencias and (A.referencias/'zonas_55.csv').exists():
 z=pd.read_csv(A.referencias/'zonas_55.csv');cat={str(int(float(r.ID_Nodo))):r.Zona for r in z.itertuples(index=False)}
else:
 for p in (OUT/'02_zonificaciones').glob('*anteriores*.csv'):
  z=pd.read_csv(p)
  if {'codigo_zona_anterior','nombre_zona_anterior'}.issubset(z):z=z.rename(columns={'codigo_zona_anterior':'codigo_zona','nombre_zona_anterior':'nombre_zona'})
  if {'codigo_zona','nombre_zona'}.issubset(z):cat=dict(zip(z.codigo_zona.astype(str).str.replace('Z','').str.lstrip('0'),z.nombre_zona));break

def code(v):
 try:return 'Z'+str(int(float(v))).zfill(3)
 except (ValueError,TypeError):return 'SIN_ZONA_ANTERIOR'
def oldname(v):return cat.get(str(int(float(v))),str(v)) if pd.notna(v) else 'Sin zona anterior identificada'
for side in ['origen','destino']:
 d['codigo_'+side+'_anterior']=d['zona_'+side+'_anterior'].map(code)
 mask=d.zonificacion.eq('original')
 d.loc[mask,'codigo_'+side]=d.loc[mask,'codigo_'+side+'_anterior']
 d.loc[mask,'nombre_'+side]=d.loc[mask,'zona_'+side+'_anterior'].map(oldname)
 f=~mask;raw=d.loc[f,'zona_'+side+'_localidad'].fillna('SIN_DESAGREGAR').astype(str)
 unresolved=raw.eq('SIN_DESAGREGAR')
 raw.loc[unresolved]=raw.loc[unresolved]+'_'+d.loc[raw.index[unresolved],'codigo_'+side+'_anterior']
 d.loc[f,'codigo_'+side]=raw
 d.loc[f,'nombre_'+side]=d.loc[f,side]
 d.loc[raw.index[unresolved],'nombre_'+side]='Sin desagregar · '+d.loc[raw.index[unresolved],'zona_'+side+'_anterior'].map(oldname)
# SBO: una sola copia de cada componente por PIB/perfil/año, antes de agregar.
base=d[d.alternativa_proyecto.eq('A1')&d.escenario_captacion.eq('central')&d.escenario_elasticidad.eq('central')].copy()
# La referencia debe ser idéntica entre proyectos para cada caso central.
key=['zonificacion','version_referencia','escenario_PIB','anio','id_base','codigo_origen','codigo_destino']
for alt in ['A2','A3']:
 z=d[d.alternativa_proyecto.eq(alt)&d.escenario_captacion.eq('central')&d.escenario_elasticidad.eq('central')].groupby(key,dropna=False).Q_referencia.sum(min_count=1)
 q=base.groupby(key,dropna=False).Q_referencia.sum(min_count=1)
 checks['SBO_referencia_identica_'+alt]=bool(np.allclose(q.sort_index(),z.sort_index(),equal_nan=True))
base['situacion']='SBO';base['escenario_captacion']='no_aplica';base['escenario_elasticidad']='no_aplica'
base['D_tierra_CP_existente']=base.D_tierra_SBO;base['D_actual_CP_existente']=base.D_actual_SBO
for c in ['D_existente_nuevo','D_inducida_incremental','D_inducida_tierra','D_inducida_actual','D_inducida_nuevo','D_nuevo_CP_total','D_residual_existente']:base[c]=np.where(base.Q_referencia.notna(),0.,np.nan)
base['D_tierra_CP_total']=base.D_tierra_SBO;base['D_actual_CP_total']=base.D_actual_SBO
cp=d.copy();cp['situacion']=cp.alternativa_proyecto
x=pd.concat([base,cp],ignore_index=True)
x=x.drop(columns=['id_base','origen','destino','zona_origen_anterior','zona_destino_anterior','zona_origen_localidad','zona_destino_localidad','alternativa_proyecto'])
x=x.rename(columns={'version_referencia':'perfil_ARISTO','escenario_elasticidad':'escenario_induccion_costo','direccion_cruce':'sentido'})
x['componentes_referencia_pendiente']=x.Q_referencia.isna().astype(int)
x['componentes_induccion_pendiente']=(x.Q_referencia.notna()&x.D_inducida_incremental.isna()).astype(int)
x['componentes_asignacion_pendiente']=(x.Q_referencia.notna()&x.D_existente_nuevo.isna()).astype(int)
flags=[];seasons=['Verano','Otoño','Invierno','Primavera'];season_months={'Verano':[12,1,2],'Otoño':[3,4,5],'Invierno':[6,7,8],'Primavera':[9,10,11]}
for source in ['ARISTO','CITRA']:
 for i,season in enumerate(seasons):
  c='cobertura_'+source+'_'+str(i);x[c]=(x.fuente.eq(source)&x.temporada.eq(season)&x.Q_referencia.notna()).astype(int);flags.append(c)
stat=['componentes_referencia_pendiente','componentes_induccion_pendiente','componentes_asignacion_pendiente']
common=['situacion','perfil_ARISTO','escenario_PIB','tasa_PIB_anual','escenario_captacion','escenario_induccion_costo','anio','segmento','unidad']
od=['codigo_origen','nombre_origen','codigo_destino','nombre_destino']
labels={'situacion':'Situación de evaluación','perfil_ARISTO':'Perfil ARISTO','escenario_PIB':'Escenario de crecimiento del PIB','tasa_PIB_anual':'Crecimiento anual del PIB','escenario_captacion':'Escenario de captación','escenario_induccion_costo':'Escenario de inducción por costo','anio':'Año','segmento':'Segmento','unidad':'Unidad','temporada':'Estación','sentido':'Sentido del cruce','fuente':'Fuente de información','codigo_origen':'Código de origen','nombre_origen':'Origen','codigo_destino':'Código de destino','nombre_destino':'Destino','Q_referencia':'Demanda existente de referencia','D_tierra_SBO':'Demanda terrestre sin proyecto','D_actual_SBO':'Demanda lacustre actual sin proyecto','D_existente_nuevo':'Demanda existente transferida al proyecto','D_tierra_CP_existente':'Demanda existente que permanece por tierra','D_actual_CP_existente':'Demanda existente que permanece en barcaza actual','D_inducida_incremental':'Demanda inducida incremental total','D_inducida_tierra':'Demanda inducida asignada a tierra','D_inducida_actual':'Demanda inducida asignada a barcaza actual','D_inducida_nuevo':'Demanda inducida asignada al proyecto','D_tierra_CP_total':'Demanda calculable por tierra, incluida inducción','D_actual_CP_total':'Demanda calculable en barcaza actual, incluida inducción','D_nuevo_CP_total':'Demanda calculable en el cruce del proyecto','D_residual_existente':'Demanda existente sin asignación calculable','componentes_referencia_pendiente':'Componentes del modelo sin referencia calculable','componentes_induccion_pendiente':'Componentes con inducción pendiente','componentes_asignacion_pendiente':'Componentes con asignación pendiente','cobertura_temporal':'Cobertura temporal del aporte conocido','modo':'Modo o estado de asignación','naturaleza':'Naturaleza de la fila','demanda_existente':'Demanda existente','demanda_inducida':'Demanda inducida estimable','demanda_calculable':'Demanda calculable por modo o estado'}
style_font=Font(bold=True,color='FFFFFF');style_fill=PatternFill('solid',fgColor='245B49')
guide=[{'Tema':'Objeto','Descripción':'Resultados agregados del modelo de demanda: SBO y alternativas A1/A2/A3. No se incorporan nuevos aforos, rutas ni encuestas.'},{'Tema':'Períodos','Descripción':'Anual significa suma del aporte temporal modelado. ARISTO VL cubre seis meses (enero, febrero y septiembre a diciembre); VP seis meses (marzo a agosto). CAM y peatones tienen doce meses modelados, con proxies heredados. El soporte no representa todo el mercado.'},{'Tema':'Escenarios','Descripción':'PIB 1%, 2% y 3% con elasticidad fija 1,2 vehículos y 0,6 peatones. Los cinco casos de captación/inducción y perfiles A/B son alternativos. No se suman escenarios, años, alternativas ni perfiles.'},{'Tema':'SBO','Descripción':'La demanda sin proyecto se exporta una vez por PIB, perfil y año. Captación e inducción por proyecto no aplican. La misma SBO es referencia de A1/A2/A3; no se suma tres veces.'},{'Tema':'Fuentes y sentidos','Descripción':'Las hojas de fuentes y las hojas de total de fuentes son vistas alternativas. Las hojas de ambos sentidos y por sentido también lo son: no se suman entre sí.'},{'Tema':'Segmentos y unidades','Descripción':'Se mantienen separados VL, VP, CAM, MOTO, BICI, BUS_TP, PEATON y OTRO_PASAJERO. VP es una categoría heterogénea y no se homologa automáticamente a VL. No sumar personas y vehículos.'},{'Tema':'Faltantes','Descripción':'Una celda vacía significa sin estimación; no equivale a cero. Las sumas de aportes conocidos se acompañan de componentes pendientes. Estos son componentes del modelo, no números de encuestas ni de vehículos.'},{'Tema':'Modos','Descripción':'Tierra, barcaza actual y cruce del proyecto son conexiones físicas. Sin asignación de ruta es un estado pendiente, no un cuarto modo.'},{'Tema':'OD','Descripción':'La zonificación anterior se agrega por códigos de sus zonas; la nueva distingue localidades y sectores. Sin desagregar conserva la zona anterior y no agrupa territorios distintos como un mismo lugar.'},{'Tema':'Demanda calculable','Descripción':'La demanda por modo suma existente e inducción estimable. Cuando la inducción falta, el total conserva el aporte existente conocido y se marca el componente pendiente. No se presume inducción cero.'}]

def agg(frame,keys):
 g=frame.groupby(keys,dropna=False,sort=True)
 quant=g[metrics].sum(min_count=1)
 ss=g[stat].sum();ff=g[flags].max()
 out=quant.join(ss).join(ff).reset_index()
 codes={src:sum(out['cobertura_'+src+'_'+str(i)].to_numpy(dtype=int)*(1<<i) for i in range(4)) for src in ['ARISTO','CITRA']}
 cov={}
 for src in ['ARISTO','CITRA']:
  table={}
  for mask in range(16):
   months=sorted({m for i,s in enumerate(seasons) if mask&(1<<i) for m in season_months[s]})
   table[mask]=(src+': '+str(len(months))+' meses ('+','.join(map(str,months))+')') if months else ''
  cov[src]=pd.Series(codes[src]).map(table)
 out['cobertura_temporal']=(cov['ARISTO']+'; '+cov['CITRA']).str.strip('; ').replace('', 'Sin referencia temporal estimable')
 return out.drop(columns=flags)

def readable(frame):
 f=frame.rename(columns=labels).copy()
 if 'Escenario de crecimiento del PIB' in f:f['Escenario de crecimiento del PIB']=f['Escenario de crecimiento del PIB'].replace({'conservador':'Bajo: PIB 1%','central':'Central: PIB 2%','alto':'Alto: PIB 3%'})
 if 'Crecimiento anual del PIB' in f:f['Crecimiento anual del PIB']=f['Crecimiento anual del PIB'].map(lambda v:f'{v:.0%}')
 if 'Escenario de captación' in f:f['Escenario de captación']=f['Escenario de captación'].replace({'no_aplica':'No aplica a SBO','conservador':'Conservador','central':'Central','alto':'Alto'})
 if 'Escenario de inducción por costo' in f:f['Escenario de inducción por costo']=f['Escenario de inducción por costo'].replace({'no_aplica':'No aplica a SBO','central':'Central','menor_induccion':'Menor inducción','mayor_induccion':'Mayor inducción'})
 return f

def excel(path,sheets):
 if A.solo_tablas:
  counts[str(path.relative_to(OUT))]={'hojas':{name:len(df) for name,df in sheets},'bytes':path.stat().st_size if path.exists() else 0};return
 w=Workbook(write_only=True)
 for name,frame in [('Guía de lectura',pd.DataFrame(guide)),*sheets]:
  f=readable(frame);ws=w.create_sheet(name[:31]);ws.freeze_panes='A2'
  cells=[]
  for v in f.columns:
   c=WriteOnlyCell(ws,value=str(v));c.font=style_font;c.fill=style_fill;c.alignment=Alignment(wrap_text=True,vertical='center');cells.append(c)
  for i,col in enumerate(f.columns,1):ws.column_dimensions[get_column_letter(i)].width=min(55,max(17,len(str(col))*.85))
  ws.row_dimensions[1].height=45
  ws.append(cells)
  for row in f.astype(object).where(pd.notna(f),None).itertuples(index=False,name=None):
   cells=[]
   for v in row:
    if isinstance(v,str):c=WriteOnlyCell(ws,value=v);c.data_type='s';cells.append(c)
    elif isinstance(v,(float,np.floating)):
     c=WriteOnlyCell(ws,value=float(v));c.number_format='#,##0.00';cells.append(c)
    elif isinstance(v,np.integer):cells.append(int(v))
    else:cells.append(v)
   ws.append(cells)
  ws.auto_filter.ref=f'A1:{get_column_letter(len(f.columns))}{len(f)+1}'
 w.save(path);counts[str(path.relative_to(OUT))]={'hojas':{name:len(df) for name,df in sheets},'bytes':path.stat().st_size};print(path.name,'guardado',flush=True)

def csvwrite(path,frame):
 frame.to_csv(path,index=False,encoding='utf-8-sig',float_format='%.10g',compression='gzip' if str(path).endswith('.gz') else None)
 counts[str(path.relative_to(OUT))]={'filas':len(frame),'bytes':path.stat().st_size}

def modes(frame):
 parts=[]
 spec=[('Ruta terrestre','Conexión física','D_tierra_CP_existente','D_inducida_tierra','D_tierra_CP_total'),('Barcaza actual','Conexión física','D_actual_CP_existente','D_inducida_actual','D_actual_CP_total'),('Cruce del proyecto','Conexión física','D_existente_nuevo','D_inducida_nuevo','D_nuevo_CP_total'),('Sin asignación de ruta','Estado pendiente','D_residual_existente',None,'D_residual_existente')]
 keep=[c for c in frame.columns if c not in metrics]
 for mode,kind,ex,ind,total in spec:
  z=frame[keep].copy();z['modo']=mode;z['naturaleza']=kind;z['demanda_existente']=frame[ex];z['demanda_inducida']=frame[ind] if ind else np.nan;z['demanda_calculable']=frame[total];parts.append(z)
 return pd.concat(parts,ignore_index=True)

for zone,folder in [('original','03_resultados_zonificacion_anterior'),('localidades','04_resultados_zonificacion_localidades')]:
 guide[0]['Descripción']=('Zonificación anterior. ' if zone=='original' else 'Zonificación por localidades y sectores. ')+'Resultados agregados del modelo: SBO y alternativas A1/A2/A3. No se incorporan nuevos aforos, rutas ni encuestas.'
 target=OUT/folder;target.mkdir(parents=True,exist_ok=True);tab=target/'tablas_csv';tab.mkdir(exist_ok=True)
 f=x[x.zonificacion.eq(zone)].drop(columns='zonificacion')
 annual_source_both=agg(f,common+['fuente']);annual_source_direction=agg(f,common+['fuente','sentido'])
 annual_total_both=agg(f,common);annual_total_direction=agg(f,common+['sentido'])
 seasonal_source_both=agg(f,common+['temporada','fuente']);seasonal_source_direction=agg(f,common+['temporada','fuente','sentido'])
 seasonal_total_both=agg(f,common+['temporada']);seasonal_total_direction=agg(f,common+['temporada','sentido'])
 annual_od_source=agg(f,common+od+['fuente','sentido']);annual_od_total=agg(f,common+od+['sentido'])
 seasonal_od_source=agg(f,common+od+['temporada','fuente','sentido']);seasonal_od_total=agg(f,common+od+['temporada','sentido'])
 # Completeness and conservation after aggregation, not after formatted rounding.
 a=annual_source_both.groupby(common,dropna=False)[metrics].sum(min_count=1).sort_index();b=annual_total_both.set_index(common)[metrics].sort_index()
 checks[zone+'_fuentes_reconcilian']=bool(np.allclose(a,b,equal_nan=True))
 reference=annual_source_both.Q_referencia
 existing=annual_source_both[['D_tierra_CP_existente','D_actual_CP_existente','D_existente_nuevo','D_residual_existente']].fillna(0).sum(axis=1).where(reference.notna())
 checks[zone+'_conservacion_demanda_existente']=bool(np.allclose(reference,existing,equal_nan=True))
 route_total=annual_source_both[['D_tierra_CP_total','D_actual_CP_total','D_nuevo_CP_total','D_residual_existente']].fillna(0).sum(axis=1).where(reference.notna())
 checks[zone+'_conservacion_con_induccion_estimable']=bool(np.allclose(reference+annual_source_both.D_inducida_incremental.fillna(0),route_total,equal_nan=True))
 a=annual_od_source.groupby(common+['fuente'],dropna=False)[metrics].sum(min_count=1).sort_index();b=annual_source_both.set_index(common+['fuente'])[metrics].sort_index()
 checks[zone+'_OD_reconcilia_anual']=bool(np.allclose(a,b,equal_nan=True))
 a=seasonal_source_both.groupby(common+['fuente'],dropna=False)[metrics].sum(min_count=1).sort_index()
 checks[zone+'_estaciones_reconcilian_anual']=bool(np.allclose(a,b,equal_nan=True))
 for name,frame in [('resumen_anual_por_fuente_ambos_sentidos',annual_source_both),('resumen_anual_por_fuente_y_sentido',annual_source_direction),('resumen_anual_total_fuentes_ambos_sentidos',annual_total_both),('resumen_anual_total_fuentes_por_sentido',annual_total_direction),('resumen_estacional_por_fuente_ambos_sentidos',seasonal_source_both),('resumen_estacional_por_fuente_y_sentido',seasonal_source_direction),('resumen_estacional_total_fuentes_ambos_sentidos',seasonal_total_both),('resumen_estacional_total_fuentes_por_sentido',seasonal_total_direction),('matrices_od_anuales_por_fuente_y_sentido',annual_od_source),('matrices_od_anuales_total_fuentes_por_sentido',annual_od_total),('matrices_od_estacionales_por_fuente_y_sentido',seasonal_od_source),('matrices_od_estacionales_total_fuentes_por_sentido',seasonal_od_total)]:csvwrite(tab/(name+'.csv.gz'),frame)
 print(zone,'filas OD estacional:',len(seasonal_od_source),'totalfuentes:',len(seasonal_od_total),flush=True)
 excel(target/'01_resumen_anual_sbo_y_alternativas.xlsx',[('Ambos sentidos por fuente',annual_source_both),('Por sentido y fuente',annual_source_direction),('Ambos sentidos total fuentes',annual_total_both),('Por sentido total fuentes',annual_total_direction)])
 excel(target/'02_resumen_estacional_sbo_y_alternativas.xlsx',[('Ambos sentidos por fuente',seasonal_source_both),('Por sentido y fuente',seasonal_source_direction),('Ambos sentidos total fuentes',seasonal_total_both),('Por sentido total fuentes',seasonal_total_direction)])
 excel(target/'03_matrices_od_anuales.xlsx',[('Por fuente',annual_od_source),('Total fuentes',annual_od_total)])
 excel(target/'04_matrices_od_estacionales.xlsx',[('Por fuente',seasonal_od_source),('Total fuentes',seasonal_od_total)])
 modeannualsource=modes(annual_source_direction);modeannualtotal=modes(annual_total_direction)
 # Full detail by mode/OD/season is canonical and remains aggregated, never individual.
 csvwrite(tab/'demanda_por_modo_od_estacion_fuente_y_sentido.csv.gz',modes(seasonal_od_source))
 csvwrite(tab/'demanda_por_modo_od_estacion_total_fuentes_y_sentido.csv.gz',modes(seasonal_od_total))
 csvwrite(tab/'demanda_por_modo_anual_por_fuente_y_sentido.csv.gz',modeannualsource)
 csvwrite(tab/'demanda_por_modo_anual_total_fuentes_y_sentido.csv.gz',modeannualtotal)
 mode_season_source=modes(seasonal_source_direction);mode_season_total=modes(seasonal_total_direction)
 central=lambda t:t[t.perfil_ARISTO.eq('B')&t.escenario_PIB.eq('central')&(t.escenario_captacion.isin(['central','no_aplica']))&t.escenario_induccion_costo.isin(['central','no_aplica'])]
 excel(target/'05_demanda_por_modo.xlsx',[('Anual por fuente',modeannualsource),('Anual total fuentes',modeannualtotal),('Estacional central por fuente',central(mode_season_source)),('Estacional central total fuentes',central(mode_season_total))])
 (target/'README.md').write_text('''# Resultados por zonificación\n\n1. `01_resumen_anual_sbo_y_alternativas.xlsx`: aportes anuales modelados; hojas por fuente y total de fuentes, para ambos sentidos y por sentido.\n2. `02_resumen_estacional_sbo_y_alternativas.xlsx`: los mismos resultados separados en verano, otoño, invierno y primavera.\n3. `03_matrices_od_anuales.xlsx`: matrices OD anuales, conservando escenario, año, segmento y sentido.\n4. `04_matrices_od_estacionales.xlsx`: matrices OD por estación, con las mismas dimensiones.\n5. `05_demanda_por_modo.xlsx`: presentación por tierra, barcaza actual, cruce del proyecto y estado sin asignación. La vista anual incluye todos los casos; la estacional del libro muestra el caso central B y PIB 2%. Las matrices OD de los libros 03 y 04 contienen todos los escenarios y modos en columnas. El CSV por modo, OD, estación, fuente y sentido contiene esos mismos resultados en formato largo, para transformación y filtrado.\n\nCada libro comienza con una guía. Las hojas de total y detalle son vistas alternativas: no sumarlas entre sí. La SBO no se triplica por aparecer en tres comparaciones. No sumar escenarios, alternativas, perfiles o unidades diferentes.\n\n`tablas_csv/` contiene tablas agregadas completas en CSV UTF-8 comprimido. Se pueden descomprimir con cualquier gestor de archivos y leer con software de datos. No contiene registros individuales ni coordenadas. Los Excel ofrecen las tablas de consulta; los CSV permiten filtrar y transformar el detalle completo.\n\nUna celda vacía no es cero. Los aportes conocidos se acompañan de componentes pendientes y cobertura temporal por fuente. Los campos de componentes se refieren al modelo y no al número de encuestas.\n''')
# No protected fields can cross the public boundary.
forbidden={'id_base','id_flujo','id_registro_2026','ids_encuestas','origen_lat','origen_lon','destino_lat','destino_lon','lat','lon','hash_registro_original'}
checks['sin_campos_individuales_en_tablas']=not bool(forbidden.intersection(seasonal_od_source.columns))
checks['SBO_no_repite_casos_captacion_induccion']=set(x.loc[x.situacion.eq('SBO'),'escenario_captacion'])=={'no_aplica'}
checks['SBO_no_repite_componentes']=not bool(base.duplicated(key).any())
control={'estado':'correcto' if all(checks.values()) else 'revisar','verificaciones':checks,'alcance':'Exportación agregada de los resultados ya calculados. No genera nuevas sensibilidades, aforos ni demanda. Los residuales no se consideran modo físico.','archivos':counts,'segundos':round(time.time()-start,2)}
(OUT/'05_verificacion').mkdir(exist_ok=True)
(OUT/'05_verificacion/control_exportacion.json').write_text(json.dumps(control,ensure_ascii=False,indent=2));assert all(checks.values()),checks
print('Exportación terminada:',len(counts),'tablas/libros;',round(time.time()-start,1),'segundos',flush=True)
