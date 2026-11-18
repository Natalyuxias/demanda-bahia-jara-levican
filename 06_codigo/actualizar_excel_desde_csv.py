"""Actualizar únicamente cantidades CAM con proyecto en los libros formales.

Lee las tablas CSV agregadas ya recalculadas. Conserva byte por byte las filas
SBO y de otros segmentos y todos los componentes de estilo y configuración.
La modificación de cada libro es atómica y su estructura se verifica antes.
"""
from pathlib import Path
import argparse,ast,json,math,re,os,time
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import numpy as np
import pandas as pd

BASE=Path(__file__).resolve().parents[1]
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
ROW=re.compile(rb'<row\b[^>]*>.*?</row>',re.S)
CELL=re.compile(rb'<c\b[^>]*\br="([A-Z]+)[0-9]+"[^>]*(?:/>|>.*?</c>)',re.S)
VALUE=re.compile(rb'<v(?:\s[^>]*)?>.*?</v>',re.S)

def export_functions():
 tree=ast.parse((BASE/'06_codigo/exportar_resultados.py').read_text())
 env={'pd':pd,'np':np}
 for n in tree.body:
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['labels','metrics'] for t in n.targets):exec(compile(ast.Module(body=[n],type_ignores=[]),'exportar_resultados.py','exec'),env)
  if isinstance(n,ast.FunctionDef) and n.name in ['readable','modes']:exec(compile(ast.Module(body=[n],type_ignores=[]),'exportar_resultados.py','exec'),env)
 return env

def contents(row):
 node=ET.fromstring(row);out={}
 for c in node:
  col=re.sub(r'[0-9]','',c.attrib['r']);text=''.join(c.itertext())
  out[col]=text
 return out

def numeric_equal(a,b):
 if pd.isna(b):return a in ['',None]
 try:return math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=1e-12)
 except (TypeError,ValueError):return str(a)==str(b)

def patch_sheet(src,dst,frame,labels):
 # The exporter writes rows in this deterministic group order.
 columns=list(frame.columns);expected={i+2:row for i,row in enumerate(frame.itertuples(index=False,name=None)) if row[columns.index('Segmento')]=='CAM' and row[columns.index('Situación de evaluación')] in ['A1','A2','A3']}
 quantity_names=set(labels[c] for c in ['D_existente_nuevo','D_tierra_CP_existente','D_actual_CP_existente','D_inducida_incremental','D_inducida_tierra','D_inducida_actual','D_inducida_nuevo','D_tierra_CP_total','D_actual_CP_total','D_nuevo_CP_total','D_residual_existente','demanda_existente','demanda_inducida','demanda_calculable'] if c in labels)
 metadata=[c for c in columns if c not in quantity_names and not c.startswith('Demanda') and not c.startswith('Componentes') and not c.startswith('Cobertura')]
 header={};targetcols={};changed_rows=0;changed_cells=0;seen=0;protected_rows=0;protected_before=__import__('hashlib').sha256();protected_after=__import__('hashlib').sha256()
 def process(raw):
  nonlocal header,targetcols,changed_rows,changed_cells,seen,protected_rows
  number=int(re.search(rb'\br="([0-9]+)"',raw).group(1));seen+=1
  if number==1:
   header=contents(raw);assert list(header.values())==columns, ('Encabezados no coinciden',list(header.values()),columns)
   targetcols={col:columns.index(name) for col,name in header.items() if name in quantity_names};return raw
  if number not in expected:
   protected_rows+=1;protected_before.update(raw);protected_after.update(raw);return raw
  values=contents(raw);want=expected[number]
  for col,name in header.items():
   if name in metadata:assert numeric_equal(values.get(col,''),want[columns.index(name)]),('Orden o clave distinta',number,name,values.get(col),want[columns.index(name)])
  local_changes=0
  def cellreplace(m):
   nonlocal local_changes,changed_cells
   col=m.group(1).decode();value=want[targetcols[col]] if col in targetcols else None
   if col not in targetcols:return m.group(0)
   original=values.get(col,'')
   if pd.isna(value):
    assert original=='',('Nulo nuevo sobre valor previo',number,col,original)
    return m.group(0)
   if original=='':raise AssertionError(('Celda antes nula con valor nuevo',number,col,value))
   if numeric_equal(original,value):return m.group(0)
   local_changes+=1;changed_cells+=1
   return VALUE.sub(('<v>'+format(float(value),'.17g')+'</v>').encode(),m.group(0),count=1)
  result=CELL.sub(cellreplace,raw)
  for col,index in targetcols.items():
   value=want[index]
   if not pd.isna(value):assert col in values,('Celda numérica ausente',number,col)
  if local_changes:changed_rows+=1
  return result
 buffer=b''
 while True:
  chunk=src.read(1024*1024)
  if not chunk:break
  buffer+=chunk
  last=0
  for m in ROW.finditer(buffer):
   dst.write(buffer[last:m.start()]);dst.write(process(m.group(0)));last=m.end()
  buffer=buffer[last:]
  if b'<row' not in buffer and len(buffer)>1024*1024:dst.write(buffer);buffer=b''
 dst.write(buffer)
 assert seen==len(frame)+1,('Número de filas distinto',seen,len(frame)+1)
 assert protected_before.digest()==protected_after.digest()
 return {'filas':len(frame),'filas_CAM_con_proyecto':len(expected),'filas_CAM_modificadas':changed_rows,'celdas_modificadas':changed_cells,'filas_protegidas':protected_rows,'filas_SBO_y_no_CAM_identicas':True}

def frames_for_book(folder,book,env):
 tab=folder/'tablas_csv';rd=lambda name:pd.read_csv(tab/(name+'.csv.gz'))
 if book.startswith('01_'):
  names=[('Ambos sentidos por fuente','resumen_anual_por_fuente_ambos_sentidos'),('Por sentido y fuente','resumen_anual_por_fuente_y_sentido'),('Ambos sentidos total fuentes','resumen_anual_total_fuentes_ambos_sentidos'),('Por sentido total fuentes','resumen_anual_total_fuentes_por_sentido')]
 elif book.startswith('02_'):
  names=[('Ambos sentidos por fuente','resumen_estacional_por_fuente_ambos_sentidos'),('Por sentido y fuente','resumen_estacional_por_fuente_y_sentido'),('Ambos sentidos total fuentes','resumen_estacional_total_fuentes_ambos_sentidos'),('Por sentido total fuentes','resumen_estacional_total_fuentes_por_sentido')]
 elif book.startswith('03_'):names=[('Por fuente','matrices_od_anuales_por_fuente_y_sentido'),('Total fuentes','matrices_od_anuales_total_fuentes_por_sentido')]
 elif book.startswith('04_'):names=[('Por fuente','matrices_od_estacionales_por_fuente_y_sentido'),('Total fuentes','matrices_od_estacionales_total_fuentes_por_sentido')]
 else:
  output={name:env['readable'](rd(csv)) for name,csv in [('Anual por fuente','demanda_por_modo_anual_por_fuente_y_sentido'),('Anual total fuentes','demanda_por_modo_anual_total_fuentes_y_sentido')]}
  for name,csv in [('Estacional central por fuente','resumen_estacional_por_fuente_y_sentido'),('Estacional central total fuentes','resumen_estacional_total_fuentes_por_sentido')]:
   f=env['modes'](rd(csv));f=f[f.perfil_ARISTO.eq('B')&f.escenario_PIB.eq('central')&f.escenario_captacion.isin(['central','no_aplica'])&f.escenario_induccion_costo.isin(['central','no_aplica'])];output[name[:31]]=env['readable'](f)
  return output
 return {name[:31]:env['readable'](rd(csv)) for name,csv in names}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,default=BASE);p.add_argument('--libro',help='Nombre de un libro para limitar la actualización');a=p.parse_args();env=export_functions();reports={};start=time.time()
 for foldername in ['03_resultados_zonificacion_anterior','04_resultados_zonificacion_localidades']:
  folder=a.salida/foldername
  for book in sorted(folder.glob('0[1-5]_*.xlsx')):
   if a.libro and book.name!=a.libro:continue
   frames=frames_for_book(folder,book.name,env);temp=book.with_suffix('.actualizando.tmp');report={}
   try:
    with ZipFile(book) as zin,ZipFile(temp,'w') as zout:
     root=ET.fromstring(zin.read('xl/workbook.xml'));rels=ET.fromstring(zin.read('xl/_rels/workbook.xml.rels'));relmap={r.attrib['Id']:r.attrib['Target'] for r in rels}
     sheets={}
     for sheet in root.find('{'+NS+'}sheets'):
      name=sheet.attrib['name'];rid=sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'];target=relmap[rid];path=target.lstrip('/') if target.startswith('/') else 'xl/'+target
      if name in frames:sheets[path]=(name,frames[name])
     assert len(sheets)==len(frames)
     assert 'xl/sharedStrings.xml' not in zin.namelist(),'Este actualizador exige cadenas inline, como las producidas por el exportador.'
     for item in zin.infolist():
      with zin.open(item) as src,zout.open(item,'w') as dst:
       if item.filename in sheets:
        name,frame=sheets[item.filename];report[name]=patch_sheet(src,dst,frame,env['labels'])
       else:
        while True:
         b=src.read(1024*1024)
         if not b:break
         dst.write(b)
    os.replace(temp,book)
   except BaseException:
    if temp.exists():temp.unlink()
    raise
   reports[str(book.relative_to(a.salida))]=report;print(book.name,sum(r['celdas_modificadas'] for r in report.values()),'celdas actualizadas',flush=True)
 result={'estado':'correcto','alcance':'Actualización de cantidades CAM en A1/A2/A3 desde CSV agregados. Filas SBO y otras clases conservadas byte por byte; estilos y demás miembros ZIP preservados.','libros':reports,'segundos':round(time.time()-start,2)}
 (a.salida/'05_verificacion/actualizacion_excel_CAM.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('Terminado',result['segundos'],'s',flush=True)
if __name__=='__main__':main()
