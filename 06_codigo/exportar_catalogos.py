"""Catálogos de zonificación y correspondencias sin coordenadas ni microdatos."""
from pathlib import Path
import json,gzip,hashlib
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill
from openpyxl.utils import get_column_letter

B=Path(__file__).resolve().parents[1]
DEST=B
O=DEST/'02_zonificaciones';V=DEST/'05_verificacion'
O.mkdir(parents=True,exist_ok=True);V.mkdir(parents=True,exist_ok=True)
old=pd.read_csv(B/'00_fuentes/referencia/zonas_55.csv')
old['codigo_zona_anterior']=old.ID_Nodo.map(lambda v:f'Z{int(v):03d}')
old['nombre_zona_anterior']=old.Zona
old['codigo_region_fuente']=old['Región']
old=old[['codigo_zona_anterior','nombre_zona_anterior','codigo_region_fuente']]
oldnames=old.set_index('codigo_zona_anterior').nombre_zona_anterior.to_dict()
with gzip.open(B/'02_procesamiento/geografia.json.gz','rt',encoding='utf-8') as f:geo=json.load(f)
lookup={z['id']:z for z in geo['zones']}
cols=['zonificacion','zona_origen_localidad','zona_destino_localidad','zona_origen_anterior','zona_destino_anterior','fuente','modelable_captacion']
d=pd.read_csv(B/'02_procesamiento/comparacion_metodologia_original.csv.gz',usecols=cols)
d=d[d.zonificacion.eq('localidades')]
def oldcode(v):return 'SIN_ZONA_ANTERIOR' if pd.isna(v) else f'Z{int(v):03d}'
ends=[]
for end in ['origen','destino']:
 x=d[[f'zona_{end}_localidad',f'zona_{end}_anterior','fuente','modelable_captacion']].copy()
 x.columns=['codigo_unidad_localidad','codigo_zona_anterior','fuente','modelable_captacion']
 x['codigo_zona_anterior']=x.codigo_zona_anterior.map(oldcode)
 x['codigo_base_modelo']=x.codigo_unidad_localidad
 mask=x.codigo_unidad_localidad.eq('SIN_DESAGREGAR')
 x.loc[mask,'codigo_unidad_localidad']='SIN_DESAGREGAR_'+x.loc[mask,'codigo_zona_anterior']
 ends.append(x)
links=pd.concat(ends,ignore_index=True).drop_duplicates()
used=sorted(links.codigo_unidad_localidad.dropna().unique())
kindnames={'localidad':'Localidad','rural':'Sector rural vial','externa':'Referencia territorial conservada','externa_argentina':'Referencia internacional sin captación modelada','pendiente':'Ubicación no identificada','sin_desagregar':'Componente zonal no desagregado'}
criteria={
 'localidad':'Referencia de localidad dentro del radio de 2,5 km y conexión próxima a la red regional. La referencia no define un límite urbano oficial.',
 'rural':'Sector definido por ruta y celda UTM de 5 km. Es una unidad espacial de análisis, no una localidad urbana ni un itinerario observado.',
 'externa':'Ubicación conservada al nivel territorial declarado, sin asignación fiable a una referencia de localidad. Esta etiqueta no implica por sí sola exclusión del área de influencia.',
 'externa_argentina':'Referencia territorial internacional conservada para trazabilidad. Sus componentes no tienen captación calculable en el modelo vigente; no se elimina la referencia ni se interpreta como demanda cero.',
 'pendiente':'Información insuficiente para identificar una localidad. Se conserva como pendiente y no se sustituye por una localización supuesta.',
 'sin_desagregar':'Componente que permanece en el OD zonal anterior. Deben conservarse los códigos de origen y destino anteriores; esta etiqueta no es una zona espacial única.'}
rows=[]
for code in used:
 f=links[links.codigo_unidad_localidad.eq(code)];basecode=str(f.codigo_base_modelo.iloc[0]);z=lookup.get(basecode,{});kind=z.get('kind','sin_desagregar')
 name=z.get('name','Sin desagregar · Sin zona anterior identificada') if code=='SIN_DESAGREGAR_SIN_ZONA_ANTERIOR' else z.get('name','Sin desagregar · '+oldnames.get(str(f.codigo_zona_anterior.iloc[0]),str(f.codigo_zona_anterior.iloc[0])))
 rows.append({'codigo_unidad_localidad':code,'codigo_base_modelo':basecode,'nombre_unidad':name,'tipo_unidad':kindnames[kind],'codigos_zonas_anteriores_asociadas':' | '.join(sorted(f.codigo_zona_anterior.unique())),'fuentes_presentes':' | '.join(sorted(f.fuente.unique())),'captacion_calculable_en_algun_componente':'Sí' if f.modelable_captacion.eq(True).any() else 'No','criterio_y_alcance':criteria[kind]})
new=pd.DataFrame(rows)
correspondence=links.groupby(['codigo_zona_anterior','codigo_unidad_localidad'],dropna=False).fuente.agg(lambda s:' | '.join(sorted(set(s)))).reset_index(name='fuentes_presentes')
correspondence['nombre_zona_anterior']=correspondence.codigo_zona_anterior.map(oldnames).fillna('Sin zona anterior identificada')
correspondence=correspondence.merge(new[['codigo_unidad_localidad','codigo_base_modelo','nombre_unidad','tipo_unidad']],on='codigo_unidad_localidad',validate='many_to_one')
correspondence['regla_de_uso']='Correspondencia de catálogo; no implica flujo, captación ni inclusión automática.'
correspondence.loc[correspondence.codigo_base_modelo.eq('SIN_DESAGREGAR'),'regla_de_uso']='Mantener el par OD anterior completo. No fusionar distintos OD por compartir SIN_DESAGREGAR.'
correspondence=correspondence[['codigo_zona_anterior','nombre_zona_anterior','codigo_unidad_localidad','codigo_base_modelo','nombre_unidad','tipo_unidad','fuentes_presentes','regla_de_uso']]
terminals=pd.DataFrame([
 {'terminal':'Puerto Ibáñez','funcion':'Extremo norte del cruce actual','relacion_con_zonificacion':'También aparece como localidad OD en la muestra.'},
 {'terminal':'Chile Chico','funcion':'Extremo sur del cruce actual','relacion_con_zonificacion':'También aparece como localidad OD en la muestra.'},
 {'terminal':'Levicán','funcion':'Extremo norte del cruce del proyecto','relacion_con_zonificacion':'Terminal del proyecto; no es una zona OD independiente con flujo propio en la cohorte utilizada.'},
 {'terminal':'Bahía Jara','funcion':'Extremo sur del cruce del proyecto','relacion_con_zonificacion':'Terminal del proyecto; no es una zona OD independiente con flujo propio en la cohorte utilizada.'}
])
for name,frame in [('catalogo_zonas_anteriores.csv',old),('catalogo_zonificacion_por_localidades.csv',new),('correspondencia_entre_zonificaciones.csv',correspondence),('terminales_y_funciones.csv',terminals)]:frame.to_csv(O/name,index=False,encoding='utf-8-sig')
labels={'codigo_base_modelo':'Código base del modelo','codigo_zona_anterior':'Código de zona anterior','nombre_zona_anterior':'Nombre de zona anterior','codigo_region_fuente':'Código de región en la fuente','codigo_unidad_localidad':'Código de unidad por localidad','nombre_unidad':'Nombre de la unidad','tipo_unidad':'Tipo de unidad','codigos_zonas_anteriores_asociadas':'Zonas anteriores asociadas','fuentes_presentes':'Fuentes presentes','captacion_calculable_en_algun_componente':'Captación calculable en algún componente','criterio_y_alcance':'Criterio y alcance','regla_de_uso':'Regla de uso','terminal':'Terminal','funcion':'Función','relacion_con_zonificacion':'Relación con la zonificación'}
w=Workbook();w.remove(w.active)
for title,frame in [('Zonas anteriores',old),('Localidades y unidades',new),('Correspondencias',correspondence),('Terminales del proyecto',terminals)]:
 s=w.create_sheet(title);s.append([labels.get(c,c) for c in frame.columns])
 for row in frame.astype(object).where(frame.notna(),None).itertuples(index=False,name=None):s.append(list(row))
 s.freeze_panes='A2';s.auto_filter.ref=s.dimensions
 for c in s[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='245B49')
 for j,c in enumerate(frame.columns,1):s.column_dimensions[get_column_letter(j)].width=70 if c in ['criterio_y_alcance','regla_de_uso','relacion_con_zonificacion'] else 32
 for row in s.iter_rows(min_row=2):
  for c in row:
   if isinstance(c.value,str):c.data_type='s'
w.save(O/'catalogos_y_correspondencias_de_zonas.xlsx')
checks={'55_zonas_anteriores':len(old)==55,'39_etiquetas_usadas':len(new)==39,'18_localidades':new.tipo_unidad.eq('Localidad').sum()==18,'7_sectores_rurales':new.tipo_unidad.eq('Sector rural vial').sum()==7,'codigos_nuevos_unicos':new.codigo_unidad_localidad.is_unique,'todos_los_codigos_usados_tienen_catalogo':set(used)==set(new.codigo_unidad_localidad),'residual_contextual_alineado_con_exportacion':'SIN_DESAGREGAR_SIN_ZONA_ANTERIOR' in set(new.codigo_unidad_localidad) and 'SIN_DESAGREGAR' not in set(new.codigo_unidad_localidad),'correspondencias_sin_duplicados':not correspondence.duplicated(['codigo_zona_anterior','codigo_unidad_localidad']).any(),'sin_coordenadas_ni_identificadores_de_encuesta':all(not any(t in c.lower() for t in ['latitud','longitud','ids_encuestas','id_encuesta','id_flujo','id_base']) for f in [old,new,correspondence,terminals] for c in f.columns),'Argentina_sin_captacion_modelada':not links[links.codigo_unidad_localidad.astype(str).str.startswith('EXT_ARG_')].modelable_captacion.eq(True).any()}
exported=DEST/'04_resultados_zonificacion_localidades/tablas_csv/matrices_od_anuales_total_fuentes_por_sentido.csv.gz'
if exported.exists():
 exported_codes=pd.read_csv(exported,usecols=['codigo_origen','codigo_destino'])
 exported_used=set(exported_codes.codigo_origen.dropna())|set(exported_codes.codigo_destino.dropna())
 checks['coincidencia_39_codigos_con_matrices_exportadas']=exported_used==set(new.codigo_unidad_localidad)
result={'estado':'correcto' if all(checks.values()) else 'revisar','verificaciones':{k:bool(v) for k,v in checks.items()},'zonas_anteriores':len(old),'etiquetas_espaciales_modelo':len(new),'tipos':new.tipo_unidad.value_counts().to_dict(),'correspondencias':len(correspondence),'cartografia_exploratoria_no_equivalente_a_catalogo_final':len(geo['zones']),'nota':'SIN_DESAGREGAR conserva el OD anterior y no define una zona única. El catálogo no contiene coordenadas ni frecuencias de encuestas.'}
(V/'control_zonas.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));assert all(checks.values()),checks
(O/'README.md').write_text('''# Zonificaciones y correspondencias

`catalogos_y_correspondencias_de_zonas.xlsx` reúne los catálogos y su relación. Los CSV contienen las mismas tablas para lectura automatizada.

| Archivo | Contenido |
|---|---|
| `catalogo_zonas_anteriores.csv` | Las 55 zonas del catálogo original, con su código y denominación de fuente |
| `catalogo_zonificacion_por_localidades.csv` | Las 39 etiquetas espaciales utilizadas en el cálculo final |
| `correspondencia_entre_zonificaciones.csv` | Relación entre zona anterior y unidad por localidad o sector, con su regla de uso |
| `terminales_y_funciones.csv` | Función de los terminales actuales y del proyecto, diferenciada del rol de zona OD |

## Unidades de la zonificación por localidades

El catálogo final contiene 18 localidades, 7 sectores rurales viales, 9 referencias territoriales conservadas, 3 referencias internacionales sin captación modelada, una etiqueta de ubicación no identificada y una de componente no desagregado. Son 39 etiquetas de análisis; no son 39 localidades nuevas.

Chile Chico, Puerto Guadal y Mallín Grande se mantienen separados. También se distinguen, entre otras localidades, Coyhaique, Balmaceda, Valle Simpson, Puerto Ibáñez, Puerto Río Tranquilo y Villa Cerro Castillo. La pertenencia a una comuna no reemplaza la localización empleada para los accesos del modelo.

Las referencias de localidad se asignan con la información geográfica disponible y su relación con la red vial. No definen polígonos urbanos oficiales ni certifican domicilios exactos. Los sectores rurales corresponden a ruta y celda de análisis; sus códigos son etiquetas zonales, no identificadores de encuestas.

Las referencias territoriales conservadas pueden corresponder a ubicaciones declaradas con menor precisión. La etiqueta no implica automáticamente estar fuera del área de influencia. La existencia de una unidad en el catálogo tampoco garantiza que todos sus OD tengan costos y captación calculables.

## Componentes sin desagregación

El código base `SIN_DESAGREGAR` no representa una zona geográfica única. La exportación lo contextualiza con el código anterior. En la entrega vigente se identifica como `SIN_DESAGREGAR_SIN_ZONA_ANTERIOR`, denominado «Sin desagregar · Sin zona anterior identificada». El campo `codigo_base_modelo` conserva el código original. Cuando aparece un componente sin desagregar, deben conservarse los códigos del par origen–destino anterior. No deben fusionarse distintos pares zonales porque compartan esta etiqueta. Las ubicaciones no identificadas y los componentes sin soporte se conservan como tales; no se convierten en demanda cero.

Bahía Jara y Levicán son terminales del proyecto. No aparecen como zonas OD independientes con flujo propio en la cohorte utilizada. Chile Chico y Puerto Ibáñez cumplen ambos roles: localidad OD y terminal actual.

## Alcance del catálogo

La preparación cartográfica exploratoria contenía 61 unidades. Ese inventario no es el catálogo final del modelo: este directorio conserva solamente las 39 etiquetas presentes en sus resultados. La correspondencia puede ser de uno a varios y se presenta sin ponderadores ni frecuencias de entrevistas.

Los catálogos no incluyen coordenadas, identificadores individuales ni microdatos. Sus denominaciones proceden del catálogo zonal original y de las referencias normalizadas utilizadas en el cálculo.
''')
print(json.dumps(result,ensure_ascii=False,indent=2))
