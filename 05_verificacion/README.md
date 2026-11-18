# Verificación y trazabilidad

| Archivo | Alcance |
|---|---|
| `actualizacion_valor_tiempo_carga.json` | Cambio específico CAM 10.047→12.954, conservación de referencia y otros segmentos, comparación de resultados |
| `control_datos_procesados_publicados.json` | Conservación de cantidades al agregar el detalle y revisión de campos excluidos |
| `control_comparaciones_publicadas.json` | Uniones entre zonificaciones, diferencias y faltantes preservados |
| `control_exportacion.json` | Reconciliación entre fuentes, OD, estaciones y resúmenes; deduplicación de la SBO |
| `control_zonas.json` | Catálogos, correspondencias y coincidencia de códigos en las matrices |
| `informe_metodologico_fuentes.json` | Cifras y parámetros contrastados con los insumos auditados |
| `verificacion_de_entrega.json` | Integridad de los Excel, columnas, exclusión de datos privados y estructura de distribución |
| `inventario_de_archivos.csv` | Tamaño y SHA-256 de los archivos distribuidos |

Los informes `comparacion_solo_zonas.json`, `verificacion_PIB.json`, `control_escenarios_cubo.json` y `reproduccion_historica.json` documentan el cálculo de origen. Sus referencias a hojas o rutas de procesamiento corresponden a esa etapa; las tablas distribuidas se verifican mediante `control_exportacion.json`.

`control_sensibilidades_previstas.json` distingue sensibilidades calculadas de pruebas pendientes. Los estados no calculados no constituyen demanda cero. Los controles de consistencia no certifican representatividad estadística ni cobertura completa del mercado.

Las 720 combinaciones configuradas corresponden a las alternativas de proyecto. La SBO se agrega como referencia independiente, sin repetirla por los casos de captación e inducción. El perfil de distribución es público y contiene resultados agregados. Los registros individuales, coordenadas y originales permanecen fuera del repositorio. Las celdas con base reducida conservan la incertidumbre de las fuentes.
