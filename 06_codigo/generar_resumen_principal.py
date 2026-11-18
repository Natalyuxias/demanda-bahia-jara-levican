"""Crear una entrada de lectura del escenario central a partir de tablas agregadas."""
from pathlib import Path
import argparse
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter
p=argparse.ArgumentParser();p.add_argument('--salida',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();B=a.salida
names={'situacion':'Situación de evaluación','anio':'Año','temporada':'Estación','segmento':'Segmento','unidad':'Unidad','fuente':'Fuente','Q_referencia':'Demanda existente de referencia','D_tierra_CP_total':'Demanda calculable por tierra','D_actual_CP_total':'Demanda calculable en barcaza actual','D_nuevo_CP_total':'Demanda calculable en cruce del proyecto','D_residual_existente':'Demanda existente sin asignación calculable','D_inducida_incremental':'Demanda inducida incremental total','componentes_referencia_pendiente':'Componentes sin referencia calculable','componentes_asignacion_pendiente':'Componentes con asignación pendiente','componentes_induccion_pendiente':'Componentes con inducción pendiente','cobertura_temporal':'Cobertura temporal del aporte conocido'}
for folder,title in [('03_resultados_zonificacion_anterior','Zonificación anterior'),('04_resultados_zonificacion_localidades','Zonificación por localidades y sectores')]:
 D=B/folder;books=[]
 for tag,filename in [('Anual total fuentes','resumen_anual_total_fuentes_ambos_sentidos'),('Anual por fuente','resumen_anual_por_fuente_ambos_sentidos'),('Estacional total fuentes','resumen_estacional_total_fuentes_ambos_sentidos'),('Estacional por fuente','resumen_estacional_por_fuente_ambos_sentidos')]:
  f=pd.read_csv(D/'tablas_csv'/(filename+'.csv.gz'))
  f=f[f.perfil_ARISTO.eq('B')&f.escenario_PIB.eq('central')&f.escenario_captacion.isin(['central','no_aplica'])&f.escenario_induccion_costo.isin(['central','no_aplica'])]
  keep=[c for c in ['anio','temporada','situacion','fuente','segmento','unidad','Q_referencia','D_tierra_CP_total','D_actual_CP_total','D_nuevo_CP_total','D_inducida_incremental','D_residual_existente','componentes_referencia_pendiente','componentes_asignacion_pendiente','componentes_induccion_pendiente','cobertura_temporal'] if c in f]
  f=f[keep].sort_values([c for c in ['anio','temporada','segmento','fuente','situacion'] if c in keep]).rename(columns=names);books.append((tag,f))
 guide=pd.DataFrame([{'Tema':'Zonificación','Descripción':title},{'Tema':'Escenario','Descripción':'Perfil ARISTO B, PIB 2%, captación e inducción centrales, ambos sentidos. Las demás combinaciones están en los libros 01 a 05.'},{'Tema':'Comparación','Descripción':'La SBO y cada alternativa se muestran en filas separadas para cada año y clase. Las columnas muestran los modos de conexión y el residual. No sumar situaciones alternativas.'},{'Tema':'Unidades','Descripción':'No sumar personas, vehículos y unidades privadas heterogéneas. VP se mantiene separado de VL.'},{'Tema':'Cobertura','Descripción':'Anual significa aporte temporal representado. ARISTO VL y VP tienen seis meses cada uno; CAM y peatones doce meses modelados. El campo de cobertura identifica el aporte por fuente.'},{'Tema':'Pendientes','Descripción':'Los componentes sin referencia y sin asignación se conservan explícitos. Una celda vacía no es cero; el total calculable no completa la demanda faltante.'},{'Tema':'Fuentes','Descripción':'Las hojas de total de fuentes y por fuente son vistas alternativas. La misma regla aplica a tablas anuales y estacionales.'}])
 w=Workbook();w.remove(w.active)
 for sheet,frame in [('Guía de lectura',guide),*books]:
  ws=w.create_sheet(sheet);ws.append(list(frame.columns))
  for row in frame.astype(object).where(frame.notna(),None).itertuples(index=False,name=None):ws.append(list(row))
  ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
  for i,col in enumerate(frame.columns,1):ws.column_dimensions[get_column_letter(i)].width=min(58,max(18,len(str(col))*.8))
  ws.row_dimensions[1].height=45
  for c in ws[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='245B49');c.alignment=Alignment(wrap_text=True)
  for row in ws.iter_rows(min_row=2):
   for c in row:
    if isinstance(c.value,str):c.data_type='s'
    if isinstance(c.value,float):c.number_format='#,##0.00'
 w.save(D/'00_resumen_central_sbo_y_alternativas.xlsx')
 p=D/'README.md';text=p.read_text();text=text.replace('# Resultados por zonificación','# Resultados · '+title)
 if '00_resumen_central_sbo_y_alternativas.xlsx' not in text:text=text.replace('\n\n1.', '\n\nComenzar en `00_resumen_central_sbo_y_alternativas.xlsx`: escenario central, perfil B y PIB 2%, con vistas anuales y estacionales.\n\n1.',1)
 p.write_text(text)
 print(title,[(s,len(f)) for s,f in books])
