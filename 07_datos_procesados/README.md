# Datos procesados y comparaciones

Este directorio contiene resultados agregados y datos de control del procesamiento. No contiene los Excel originales, respuestas individuales, identificadores de encuestas ni coordenadas individuales.

## Comparaciones de demanda

- `comparacion_entre_zonificaciones_anual.xlsx`: lectura de la demanda con zonas anteriores y por localidades, con diferencias calculadas como localidades menos zonas anteriores. Incluye una vista central y todas las combinaciones disponibles en las demás hojas.
- `comparacion_anual_*.csv.gz` y `comparacion_estacional_*.csv.gz`: versiones anuales y estacionales, por fuente y total de fuentes, para procesamiento automatizado. Las distintas vistas no se suman entre sí.
- `comparacion_metodologia_original_agregada.csv.gz`: detalle procesado por OD, fuente, segmento, estación, año y escenario. Conserva las cantidades de referencia, SBO, transferencia, inducción y demanda con proyecto, agregando los componentes que pertenecen al mismo grupo.

El último archivo es la versión pública agregada del detalle privado `comparacion_metodologia_original.csv.gz`. No conserva sus identificadores ni sus vínculos con registros individuales. Los costos y probabilidades se presentan como promedios descriptivos ponderados por la referencia positiva conocida; cada promedio incluye su denominador. No corresponde aplicar nuevamente las curvas de captación a esos costos medios para intentar reproducir la suma del cálculo por componente.

## Aforos, factores y datos observados procesados

`aforos_factores_y_datos_observados_procesados.xlsx` reúne los estratos de CITRA y ARISTO, la matriz CITRA por localidad de 12 horas y el diccionario de campos de la comparación procesada. Los CSV asociados contienen las mismas tablas.

Los factores se presentan con sus estados, motivos y exclusiones. Que un estrato aparezca en la tabla no significa que se haya utilizado en la demanda final. Los denominadores se definieron antes de filtrar el área de influencia; no se suman todos los aforos como si fueran un mercado único. Las filas de aforos representan grupos de fecha, control, sentido y clase, no vehículos ni personas encuestadas individualmente.

`atributos_viales_procesados_entre_zonas.csv.gz` contiene distancias, tiempos viales y COV de referencia entre unidades usadas. No incluye geometrías, coordenadas ni itinerarios GPS. Sus alternativas son rutas del modelo y sus segmentos corresponden al perfil de costos aplicado.

## Unidades, faltantes y escenarios

Mantener separados segmentos y unidades. Los escenarios de PIB, captación, inducción, años y alternativas son excluyentes. Los componentes pendientes se conservan y las celdas sin estimación no se convierten en cero. Los conteos de componentes del modelo no son cantidades de entrevistas ni demanda adicional.

Los CSV son UTF-8, separador coma y decimal punto. Los archivos `.csv.gz` deben descomprimirse o abrirse con una aplicación compatible. Las tablas Excel existentes en los directorios de resultados conservan la presentación legible de los escenarios y sus desagregaciones.

## Temporalización y antecedentes

`temporalizacion_mensual_aristo_procesada.csv.gz` conserva los aportes mensuales por perfil OD y clase, sin identificadores ni referencias a filas individuales. `factores_temporales_aristo.csv` y los dos archivos PNC contienen los coeficientes y antecedentes estacionales procesados. Son insumos de referencia congelados: no sustituyen los parámetros operativos vigentes de SBO ni implican que todas las sensibilidades temporales se hayan recalculado en las alternativas. Mantener separadas las vistas, versiones y escenarios.

`perfiles_od_aristo_procesados_a_y_b.csv.gz` reúne los perfiles OD agregados originales de A/B sin enlaces a filas ni textos originales individuales. `estadisticas_agregadas_longitud_cam.csv` contiene estadísticas de la flota declarada por estación y sentido, no longitudes por vehículo. `controles_y_movimientos_procesados.csv` identifica controles y movimientos interpretados sin coordenadas.
