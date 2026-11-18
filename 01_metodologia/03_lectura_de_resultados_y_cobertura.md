# Lectura de resultados, unidades y cobertura

## Organización de los resultados

Las carpetas `03_resultados_zonificacion_anterior` y `04_resultados_zonificacion_localidades` presentan los mismos tipos de tablas, bajo sus respectivos códigos geográficos. La separación permite comparar una representación espacial con la otra sin sumar sus resultados.

| Archivo por zonificación | Consulta |
|---|---|
| `00_resumen_central_sbo_y_alternativas.xlsx` | Entrada de lectura: SBO y A1–A3, perfil B, PIB 2%, anual y estacional |
| `01_resumen_anual_sbo_y_alternativas.xlsx` | SBO y A1–A3 por año, segmento, sentido y fuente, con vistas de total de fuentes separadas |
| `02_resumen_estacional_sbo_y_alternativas.xlsx` | La misma desagregación para verano, otoño, invierno y primavera |
| `03_matrices_od_anuales.xlsx` | Origen y destino, segmento, sentido y escenarios para el aporte anual representado |
| `04_matrices_od_estacionales.xlsx` | Desagregación OD por estación y demás dimensiones del cálculo |
| `05_demanda_por_modo.xlsx` | Distribución entre ruta terrestre, barcaza actual y cruce del proyecto, con residual identificado |

Los CSV asociados conservan las dimensiones agregadas necesarias para filtrar o reconstruir tablas. No contienen identificadores de encuesta ni coordenadas individuales. Las hojas `Guía de lectura` describen el contenido de cada libro. Las vistas por fuente y las de total de fuentes son presentaciones alternativas del mismo cálculo: no se suman entre sí.

## Selección de una comparación

El libro `00_resumen_central_sbo_y_alternativas.xlsx` reúne la lectura principal sin filtros adicionales. En los libros completos, seleccionar el mismo año, perfil ARISTO, PIB, segmento y sentido. Para conservar la SBO junto a un caso de proyecto, mantener «No aplica a SBO» además del caso elegido en los filtros de captación e inducción. La SBO es común y no tiene una curva propia de captación hacia un proyecto inexistente.

## Demanda de referencia, SBO y demanda con proyecto

- **Demanda de referencia:** aporte existente estimado y temporalizado a partir de las encuestas y aforos compatibles.
- **SBO:** distribución de la referencia entre la ruta terrestre y el cruce actual, bajo los atributos de la situación base optimizada.
- **A1, A2 y A3:** alternativas excluyentes de proyecto. Cada una conserva la base y estima cuánto permanece en tierra y en la barcaza actual, cuánto utiliza el cruce del proyecto y qué parte permanece sin asignación calculable.
- **Viajes transferidos:** demanda que ya existía y cambia de alternativa.
- **Viajes inducidos:** incremento adicional calculable frente a los mínimos de costo de la SBO.
- **Demanda total del proyecto:** viajes transferidos más inducción asignada al cruce.
- **Residual:** referencia conservada sin distribución calculable entre alternativas. No es un modo físico ni demanda desaparecida.

La SBO es común a las alternativas. Si una comparación repite la SBO junto a A1, A2 y A3, esas repeticiones no son flujos adicionales. Los totales de A1, A2 y A3 tampoco se suman.

## Modo, segmento y unidad

En esta entrega, el modo o ruta distingue **tierra**, **barcaza actual** y **cruce del proyecto**. La clasificación del usuario o vehículo se mantiene en el segmento.

| Segmento | Unidad e interpretación |
|---|---|
| VL | Vehículos livianos de la clasificación original |
| CAM | Vehículos de carga; no toneladas transportadas |
| VP | Unidades privadas heterogéneas agrupadas por ARISTO; no se recodifican como VL |
| PEATON | Personas a pie registradas en esa categoría; no todos los pasajeros del transbordador |
| MOTO | Motocicletas |
| BICI | Bicicletas |
| BUS_TP | Buses de transporte público |
| OTRO_PASAJERO | Registros sin una base de conteo compatible para estimar demanda total |

No se suman personas con vehículos, bicicletas o unidades heterogéneas. Las vistas agregadas mantienen el segmento y su unidad. La utilización de un perfil de costos VL para VP es una aproximación de costos y no una homologación de sus conteos.

## Año y estaciones

| Estación del modelo | Meses |
|---|---|
| Verano | Diciembre, enero y febrero |
| Otoño | Marzo, abril y mayo |
| Invierno | Junio, julio y agosto |
| Primavera | Septiembre, octubre y noviembre |

Las estaciones pertenecen a un calendario anual normalizado. Los resultados de invierno y otras estaciones no medidas incluyen proxies e imputaciones documentadas. Un valor anual corresponde a la suma de aportes temporales representados por la fuente y la clase.

| Fuente y clase | Meses representados | Lectura |
|---|---|---|
| ARISTO VL | Enero, febrero, septiembre, octubre, noviembre y diciembre | Seis meses; no es un anual completo independiente |
| ARISTO VP | Marzo a agosto | Seis meses complementarios, con una clasificación diferente |
| ARISTO CAM | Enero a diciembre | Doce meses modelados, con temporalización heredada |
| ARISTO PEATON | Enero a diciembre | Doce meses modelados, con temporalización heredada |
| CITRA | Períodos temporalizados desde las campañas y componentes disponibles | Cobertura parcial del corredor y del OD; incluye hipótesis 12→24 e imputaciones estacionales |

La suma de VL y VP no se presenta automáticamente como un anual completo de vehículos livianos. Para hacerlo se necesitaría una homologación explícita y defendible de las categorías. Un total que combina CITRA VL con ARISTO VL reúne componentes de cobertura temporal distinta; no acredita por sí solo el tránsito anual completo de livianos.

## Origen y destino

Las matrices anteriores agregan por el código zonal original. Las matrices por localidades emplean la geoasignación disponible y conservan la pertenencia a la zona anterior. Puerto Guadal, Mallín Grande y Chile Chico se identifican separadamente.

Las referencias de localidades y sectores rurales no son límites urbanos certificados. La asignación por coordenadas o cercanía a una referencia es una inferencia geográfica; no acredita una dirección precisa. Si un componente carece de localización suficiente, se conserva como `Sin desagregar` asociado a su OD anterior, sin mezclar todos los desconocidos en un único OD ficticio.

Una combinación OD ausente no equivale a demanda cero. La entrega comprende las combinaciones presentes en el soporte del modelo, sus agregaciones válidas y los escenarios calculados. No crea viajes para completar el producto de todos los orígenes posibles con todos los destinos posibles.

## Reglas de comparación

1. Seleccionar una zonificación, situación, año, PIB, perfil ARISTO y caso de captación/inducción.
2. Mantener el mismo segmento y unidad al comparar la SBO con una alternativa.
3. Seleccionar el período anual o una estación; no sumar ambas vistas.
4. Utilizar la vista por fuente o la vista de total de fuentes, sin añadirlas entre sí.
5. Sumar ambos sentidos mediante la vista preparada, o los sentidos separados cuando su soporte sea compatible; no volver a sumar el total a sus componentes.
6. Conservar la demanda sin asignación al revisar balances. Un cero calculado y una celda sin estimación tienen significados distintos.

Los decimales son consecuencia de ponderadores y temporalización. No representan fracciones de una encuesta ni una precisión observada equivalente a esos decimales. Los valores vacíos se mantienen como falta de estimación; no se rellenan con cero para facilitar una suma.
