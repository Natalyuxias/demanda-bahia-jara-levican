# Demanda de referencia y alternativas de conectividad Bahía Jara–Levicán

Resultados del modelo de demanda para la situación base optimizada (SBO) y las alternativas A1, A2 y A3. Se presentan por año, estación, segmento, modo de conexión, sentido y par origen–destino, con escenarios de crecimiento del PIB, captación e inducción.

La comparación utiliza la misma base y metodología en dos representaciones espaciales: zonas anteriores y localidades/sectores. Los costos CITRA que ya estaban diferenciados por localidad se conservan; ARISTO se desagrega con su información geográfica y sus perfiles originales.

## Organización

| Carpeta | Contenido |
|---|---|
| `00_fuentes` | Procedencia, versiones y configuraciones |
| `01_metodologia` | Construcción de referencia, expansión, temporalización, costos y asignación |
| `02_zonificaciones` | Catálogos anterior y por localidades, correspondencias y terminales |
| `03_resultados_zonificacion_anterior` | Resultados con los códigos zonales anteriores |
| `04_resultados_zonificacion_localidades` | Resultados por localidades y sectores |
| `05_verificacion` | Balances, cobertura de escenarios, límites y controles de exportación |
| `06_codigo` | Cálculo, exportación e instrucciones de reproducción |
| `privado` | Instrucciones para los insumos excluidos de Git; no contiene microdatos |

## Lectura de resultados

Comenzar en **`00_resumen_central_sbo_y_alternativas.xlsx`** de la zonificación elegida. Presenta el perfil B, PIB 2% y captación e inducción centrales, con tablas anuales y estacionales. Los libros 01 a 05 contienen el conjunto completo de escenarios y las matrices OD. La SBO representa la demanda existente por tierra y por la barcaza actual. Cada alternativa presenta por separado la demanda terrestre remanente, la barcaza actual, el cruce del proyecto y la demanda sin asignación calculable.

Los resúmenes estacionales distinguen verano, otoño, invierno y primavera. Las matrices OD conservan el sentido de viaje. Las vistas por fuente permiten separar CITRA y ARISTO; las vistas de total de fuentes se publican en hojas distintas y no se suman nuevamente a sus componentes.

Las tablas de detalle contienen las combinaciones calculadas de años 2026, 2030, 2040 y 2050; perfiles ARISTO A/B; PIB de 1%, 2% y 3%; y cinco casos de captación/inducción. No se crean OD sin soporte ni combinaciones no previstas en el diseño del modelo. La SBO se deduplica antes de agregar: no se suman copias procedentes de las tres alternativas.

## Unidades y cobertura

El modo de conexión distingue tierra, cruce lacustre actual y cruce lacustre del proyecto. El segmento distingue vehículos o usuarios. La demanda sin asignación de ruta es un estado pendiente, no un modo físico.

Mantener separadas personas, vehículos y unidades privadas heterogéneas (VP). No sumar alternativas, años, escenarios ni vistas de agregado y detalle. Una celda sin estimación no equivale a cero.

Los valores anuales son sumas del aporte temporal modelado. ARISTO camiones y peatones representan doce meses; VL representa enero, febrero y septiembre a diciembre, y VP representa marzo a agosto. VL y VP conservan seis meses cada uno y no son anuales completos independientes. Las imputaciones estacionales y el factor CITRA 12→24 de 1,20 son supuestos heredados, no nuevas mediciones.

## Escenarios y sensibilidad

La comparación principal usa perfil ARISTO B, PIB de 2% y captación e inducción centrales. Las elasticidades respecto del PIB permanecen fijas: 1,2 para vehículos y 0,6 para peatones. La elasticidad de inducción por costo es un parámetro distinto.

Las alternativas de proyecto tienen resultados para sus 720 estados configurados. La SBO añade sus referencias independientes por zonificación, perfil, PIB y año, sin multiplicarse por los casos de captación e inducción. La batería amplia de sensibilidad previamente planteada es parcial: siete elementos representados, 23 variaciones sin resultados vigentes y cinco pruebas de robustez por reaplicar. Su estado se documenta en `05_verificacion`; no se presentan como calculadas las pruebas pendientes.

## Distribución y reproducción

Esta entrega contiene resultados OD agregados y no incorpora encuestas individuales, coordenadas ni originales de consultoras. La versión completa conserva desagregaciones de baja frecuencia y se prepara para distribución privada. Una publicación abierta requiere revisar el nivel de agregación de esas matrices.

Los insumos privados están inventariados mediante nombres y SHA-256. El código de exportación permite reconstruir las tablas a partir del detalle validado; la reproducción de la estimación requiere restituir las fuentes privadas. El visor geográfico no forma parte de esta versión.
