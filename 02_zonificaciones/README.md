# Zonificaciones y correspondencias

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

Las 55 zonas corresponden al catálogo original completo; las 39 etiquetas corresponden al soporte efectivamente utilizado. Sus cantidades no miden por sí solas el grado de desagregación: varias zonas originales no tienen viajes en la cohorte analizada.

## Alcance del catálogo

La preparación cartográfica exploratoria contenía 61 unidades. Ese inventario no es el catálogo final del modelo: este directorio conserva solamente las 39 etiquetas presentes en sus resultados. La correspondencia puede ser de uno a varios y se presenta sin ponderadores ni frecuencias de entrevistas.

Los catálogos no incluyen coordenadas, identificadores individuales ni microdatos. Sus denominaciones proceden del catálogo zonal original y de las referencias normalizadas utilizadas en el cálculo.
