# Demanda de referencia: fuentes, expansión y temporalización

## Fuentes y componentes

La demanda de referencia reúne dos componentes estimados por separado: el terrestre, procedente de CITRA, y el lacustre de la barcaza Puerto Ibáñez–Chile Chico, procedente de ARISTO. Su integración se realiza después de revisar clases, sentidos, períodos y unidades. Un total de una fuente no se interpreta como el mercado completo del territorio.

| Fuente | Antecedentes utilizados | Función |
|---|---|---|
| CITRA | `EOD Aysen Febrero 2026 vf.xlsx` y `EOD Aysen Abril 2026.xlsx`, hojas `EOD` y `Flujos`; libros de mediciones de flujo; KMZ de controles | Viajes interceptados en pantallas terrestres, aforos y localización de puntos |
| ARISTO | `Base de datos agregada.xlsx`, hojas `BBDD-1` y `BBDD-2 (solo válidas)` | Validación, clase, origen, destino, sentido y coordenadas disponibles |
| ARISTO | `Consolidado Flujos.xlsx`, registros de transbordadores | Conteos asociados a fechas, sentidos y clases de la componente lacustre |
| Zonificación de referencia | `BBDD_para_Pijas_actualizada_EOD_Final.xlsx`, hoja `Zonas` | Catálogo de 55 zonas y homologación de códigos |
| Red vial y costos | Red vial y nodos del estudio, zonificación SIG y `Costos_Red_Vial_Actual.xlsx` | Caminos factibles, accesos y atributos físicos de costos |

Los informes CITRA, ARISTO y EVALSO respaldan la procedencia y las decisiones de modelación. Los libros originales y los cortes auditados se conservan en el archivo privado del cálculo. Los nombres de archivo o campaña no reemplazan la fecha efectiva de cada registro.

## Componente terrestre CITRA

La cohorte de referencia contiene **112 encuestas auditadas**. De ellas, 109 son admisibles para la estimación condicionada al corredor y tres quedan excluidas, conservadas en auditoría. Entre las 109 admisibles, 93 tienen factor compatible y 16 no pueden expandirse: once están afectadas por filas EOD idénticas no resueltas y cinco por grillas de conteo incompletas o intervalos duplicados no reconciliados.

La selección final utiliza **64 encuestas en la pantalla elegida**. Otras 29 encuestas con factor pertenecen a pantallas alternativas y no se suman a la seleccionada. Las 112 entrevistas son un conjunto auditado, no 112 viajes expandidos ni una muestra íntegramente utilizable para todos los cálculos.

La correspondencia entre aforo y encuesta se conserva por campaña, fecha, sección de control, sentido, segmento y ventana horaria. Los denominadores se calculan antes de filtrar por el área de influencia. Los conteos urbanos o de otra sección no se utilizan como sustitutos de una pantalla compatible.

Para un estrato compatible $h$, el ponderador proporcional es:

$$w_h=\frac{F_h}{N_h}$$

$F_h$ es el aforo de la clase y ventana correspondientes. $N_h$ es el número de encuestas del mismo estrato antes del filtro territorial. La asignación OD de la ventana se obtiene sumando los ponderadores de las encuestas elegibles:

$$\widehat Q_{ij,h}=\sum_{n\in(i,j,h)}w_h$$

Se conserva **una pantalla por OD zonal, campaña y clase**, elegida con los criterios de compatibilidad y cobertura del modelo de referencia. Después se distribuye su aporte entre las localidades observadas. No se vuelve a seleccionar una pantalla por cada localidad ni se suman controles sucesivos que puedan interceptar los mismos viajes. La síntesis de jornadas válidas conserva el promedio de la ventana de 12 horas y las fechas representadas.

La evidencia de interceptación permite reconocer un corredor y comprobar compatibilidad topológica. No constituye un registro GPS ni una declaración de todos los tramos de un itinerario. La componente terrestre conserva esa condición inferida y su cobertura parcial.

## Componente lacustre ARISTO

La base original contiene **290 entrevistas**, de las cuales **264** están en la hoja de encuestas válidas: 103 de verano, 85 de otoño y 76 de primavera. Hay 258 entrevistas con coeficiente compatible; 252 tienen simultáneamente coeficiente y OD zonal completo. Los OD genéricos o incompletos permanecen sin ubicación inventada.

Se identifican **40 estratos principales de fecha, sentido y segmento**. En cada estrato se distribuye el conteo mediante la composición de encuestas compatibles. El cálculo proporcional mantiene el denominador de todas las entrevistas válidas del estrato, no solo las que tienen OD dentro del proyecto:

$$\widehat Q_{ij,h}=F_h\frac{n_{ij,h}}{N_h}$$

La suma asignada a OD más el residual debe conservar el conteo. Los casos con $N_h>F_h$ se identifican como una limitación de representatividad; el coeficiente es una transferencia de composición y no una probabilidad de inclusión certificada.

Se conservan dos perfiles:

- **A:** utiliza entrevistas de la misma fecha; los conteos sin perfil compatible quedan sin asignación OD.
- **B:** permite transferir un perfil de otra fecha compatible de la misma campaña, sentido y clase cuando el procedimiento original lo autoriza. La procedencia de ese perfil permanece registrada. Es la versión principal del informe.

El contexto de rampa o transbordador y los conteos compatibles sustentan la componente lacustre. La localización en un muelle, por sí sola, no acredita un embarque individual completado. Tampoco los ocupantes de vehículos se convierten en peatones: cada segmento conserva la unidad de su conteo.

La componente lacustre CITRA no se añade al flujo ARISTO del mismo cruce. Se evita así duplicar fuentes que pueden representar el mismo mercado.

## Temporalización y año base

Las mediciones se trasladan al calendario normalizado de **2026** con los coeficientes de exposición y factores temporales heredados. ARISTO conserva la lectura central de exposición y los perfiles de fechas utilizados. CITRA conserva las campañas de verano y otoño y las imputaciones o proxies estacionales documentados. El invierno modelado no se presenta como un invierno medido.

El modelo utiliza para CITRA un factor **1,20 de 12 a 24 horas**, exclusivamente como hipótesis heredada. No es una conversión observada ni un factor 2 automático. Las mediciones de 12 horas y la demanda temporalizada corresponden a productos distintos.

El resultado anual es la suma de los aportes mensuales que el modelo representa, no un censo de todos los viajes de Aysén. La cobertura debe revisarse por fuente y segmento: ARISTO VL y VP tienen períodos complementarios de seis meses; camiones y peatones tienen doce meses modelados. Las reglas de lectura se detallan en el documento 03.

## Trazabilidad y revisiones

La comparación conserva las bases congeladas de encuestas, pantallas y temporalización. Los cortes auditados permiten comprobar factores y reproducir el cálculo sin modificar los Excel originales. No se incorporan automáticamente decisiones que permanezcan únicamente en un visor ni revisiones sin un archivo de entrada validado. Los datos faltantes y los componentes sin expansión válida se conservan como tales; no se sustituyen por cero.
