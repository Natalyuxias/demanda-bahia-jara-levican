"""Validar integridad, límites de publicación y estructura de una entrega agregada."""
from pathlib import Path
import json,csv,gzip,hashlib,ast,re,tempfile,subprocess
from concurrent.futures import ThreadPoolExecutor
from zipfile import ZipFile
from openpyxl import load_workbook
B=Path(__file__).resolve().parents[1];V=B/'05_verificacion';checks={};files=[p for p in B.rglob('*') if p.is_file() and '.git' not in p.parts]
for name in ['control_exportacion.json','control_zonas.json']:
 d=json.loads((V/name).read_text());checks[name+'_controles']=all(d['verificaciones'].values())
checks['dos_zonificaciones_separadas']=all((B/f).is_dir() for f in ['03_resultados_zonificacion_anterior','04_resultados_zonificacion_localidades'])
checks['sin_originales_ni_capas_individuales']=not any(p.suffix.lower() in ['.shp','.gpkg','.kmz','.kml','.pdf','.xlsb'] for p in files)
checks['sin_detalle_individual']=not any(p.name=='comparacion_metodologia_original.csv.gz' for p in files)
checks['archivos_menores_100MB']=all(p.stat().st_size<100_000_000 for p in files)
checks['scripts_compilan']=all(ast.parse(p.read_text()) is not None for p in (B/'06_codigo').glob('*.py'))
forbidden={'id_base','id_flujo','id_encuesta','id_registro_2026','ids_encuestas','lat','lon','latitud','longitud','origen_lat','origen_lon','destino_lat','destino_lon','hash_registro_original','patente','direccion_domicilio'}
def bad_header(header):return sorted(forbidden.intersection(str(v or '').strip().lower() for v in header))
bad=[];csv_count=0
for p in files:
 if p.name.endswith('.csv') or p.name.endswith('.csv.gz'):
  op=gzip.open if p.suffix=='.gz' else open
  with op(p,'rt',encoding='utf-8-sig',newline='') as f:
   header=next(csv.reader(f));found=bad_header(header)
  csv_count+=1
  if found:bad.append((str(p.relative_to(B)),found))
checks['CSV_sin_identificadores_ni_coordenadas']=not bad
books=[p for p in files if p.suffix=='.xlsx']
def bookcheck(p):
 with ZipFile(p) as z:
  broken=z.testzip()
 if broken:return str(p.relative_to(B)),False,[]
 w=load_workbook(p,read_only=True,data_only=True);found=[]
 for s in w:
  row=next(s.values,[]);found+=bad_header(row)
 w.close();return str(p.relative_to(B)),not found,found
with ThreadPoolExecutor(max_workers=2) as ex:results=list(ex.map(bookcheck,books))
checks['Excel_integros_y_sin_campos_individuales']=all(ok for _,ok,_ in results)
for folder in ['03_resultados_zonificacion_anterior','04_resultados_zonificacion_localidades']:
 checks[folder+'_resumen_principal']=(B/folder/'00_resumen_central_sbo_y_alternativas.xlsx').exists()
 checks[folder+'_cinco_libros_completos']=all((B/folder/n).exists() for n in ['01_resumen_anual_sbo_y_alternativas.xlsx','02_resumen_estacional_sbo_y_alternativas.xlsx','03_matrices_od_anuales.xlsx','04_matrices_od_estacionales.xlsx','05_demanda_por_modo.xlsx'])
with tempfile.TemporaryDirectory(prefix='validar_git_demanda_') as td:
 subprocess.run(['git','init','-q',td],check=True)
 args=['git','--git-dir='+str(Path(td)/'.git'),'--work-tree='+str(B.resolve()),'check-ignore','--stdin']
 probes=['privado/detalle.csv.gz','02_procesamiento/geografia.json.gz','00_fuentes/referencia/citra_individual.csv','.env']
 r=subprocess.run(args,input='\n'.join(probes)+'\n',text=True,capture_output=True,cwd=B)
 checks['Git_excluye_datos_privados']=set(r.stdout.splitlines())==set(probes)
report={'estado':'correcto' if all(checks.values()) else 'revisar','perfil_distribucion':'entrega completa para repositorio privado; no publicación remota','verificaciones':checks,'libros_verificados':len(books),'CSV_verificados':csv_count,'maximo_archivo_bytes':max(p.stat().st_size for p in files),'campos_prohibidos_detectados':bad,'alcance':'Comprueba integridad de libros, columnas, estructura, exclusión de insumos y controles de agregación. Las matrices OD pueden contener desagregaciones de baja frecuencia: esta validación no autoriza difusión pública de esas celdas ni completa sensibilidades pendientes.'}
(V/'verificacion_de_entrega.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));assert all(checks.values()),checks
manifest=[]
for p in sorted(B.rglob('*')):
 if p.is_file() and p.name!='inventario_de_archivos.csv' and '.git' not in p.parts:manifest.append({'archivo':str(p.relative_to(B)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
with (V/'inventario_de_archivos.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['archivo','bytes','sha256']);w.writeheader();w.writerows(manifest)
