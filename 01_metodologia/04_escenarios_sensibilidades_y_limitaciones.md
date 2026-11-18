# Escenarios, controles y límites de interpretación

## Conjunto de escenarios calculado

| Dimensión | Valores disponibles |
|---|---|
| Zonificación | Anterior y localidades/sectores |
| Situación | SBO y alternativas A1, A2 y A3 |
| Año | 2026, 2030, 2040 y 2050 |
| Crecimiento anual del PIB | 1%, 2% y 3% |
| Elasticidad demanda/PIB | Fija: 1,2 vehículos y 0,6 peatones |
| Perfil ARISTO | A y B |
| Captación e inducción | Cinco pares heredados, indicados debajo |
| Período | Anual representado y estaciones |
| Sentido | Norte–Sur, Sur–Norte y vistas agregadas compatibles |
| Desagregación | Fuente, segmento, ruta o modo y OD |

Los cinco pares de captación/inducción son:

| Captación | Inducción por costo |
|---|---|
| Conservadora | Central |
| Central | Menor inducción |
| Central | Central |
| Central | Mayor inducción |
| Alta | Central |

Estos son casos definidos, no el cruce completo de tres curvas por tres elasticidades de inducción. Se cruzan con los tres PIB y los demás ejes de la entrega. Para las alternativas resultan 720 combinaciones de zonificación, proyecto, año, perfil ARISTO, PIB y caso de captación/inducción. La SBO conserva una referencia común y no depende de la curva de captación ni de la alternativa futura.

El perfil B, PIB 2%, captación central e inducción central constituyen la lectura principal. Los otros perfiles y casos son contrastes metodológicos. Ningún escenario constituye un intervalo de confianza estadístico.

## Sensibilidades adicionales

La batería amplia de 35 elementos tiene cobertura parcial en esta versión:

| Estado | Elementos | Contenido |
|---|---:|---|
| Representados | 7 | Central, captación conservadora/alta, PIB 1%/3% y menor/mayor inducción por costo |
| Sin resultados vigentes | 23 | Variaciones de valor del tiempo, COV, velocidad, tarifas, factor 12→24, presentación, desembarque, navegación, frecuencia, buses y temporalización |
| Por reaplicar al soporte conservado | 5 | Mínimo de encuestas por OD, N mayor que F, calidad de coordenadas y exclusión de colas externas |

La disponibilidad de muchas combinaciones de los escenarios calculados no sustituye una prueba de una variable no sensibilizada. Estas pruebas pendientes no se presentan como resultados del modelo vigente.

## Controles

El proceso verifica:

- Conservación de la demanda de referencia al desagregar cada componente original.
- Mantenimiento de la cohorte CITRA, sus pantallas y componentes ya diferenciados por localidad.
- Reproducción del modelo histórico antes de actualizar la proyección vigente.
- Factores de proyección coherentes con PIB 1/2/3% y elasticidades fijas; cantidades de 2026 intactas.
- Costos y probabilidades invariantes ante un cambio exclusivo de PIB.
- Probabilidades entre cero y uno; conservación de referencia, transferencias, remanentes, inducción y residuales en el soporte calculable.
- Presencia de las combinaciones configuradas y mantenimiento del soporte temporal y direccional original.
- Igualdad de la SBO entre las alternativas y ausencia de suma de sus copias.

Los resultados de exportación y sus conteos de filas se documentan en `05_verificacion`. Estos controles certifican consistencia computacional y trazabilidad dentro del soporte utilizado; no certifican representatividad estadística ni cobertura territorial completa.

## Demanda pendiente y cobertura numérica

Las limitaciones sin resolver se conservan de la referencia. La desagregación espacial no crea ponderadores ni completa clases sin conteo compatible.

En la referencia existen encuestas CITRA sin expansión válida, conteos ARISTO sin perfil suficiente y OD sin asignación espacial o de costos completa. Motos y bicicletas conservan su referencia sin una asignación al proyecto en las curvas vigentes; buses conservan la base cero disponible y otros pasajeros mantienen la falta de base compatible. Las unidades de ocupantes o grupos no se utilizan para completar pasajeros totales.

Una participación calculable puede ser cero si la curva de captación no asigna demanda al proyecto. Ese cero es distinto de un resultado no estimable. La demanda que no puede repartirse entre rutas permanece en una columna residual; no se elimina para hacer coincidir los totales asignados.

En OD con cola exterior no valorada se mantienen las reglas de cota para captación y se excluye la inducción basada en cocientes de costos absolutos. Si falta un delta vial comparable para una localidad, se conserva el costo heredado; el nuevo nombre geográfico no convierte ese costo en una medición local.

## Alcance de uso

Las tablas describen aportes de demanda del soporte de referencia y sus proyecciones, no el total de tránsito de Aysén ni una medición anual continua. La anualización conserva hipótesis de exposición y proxies. Las rutas son referencias de red y no trayectorias observadas por GPS.

El modelo no verifica capacidad, factibilidad de horarios, flota comprometida, operación de buses, costos de inversión u operación del proyecto ni beneficios sociales completos. Los resultados de captación dependen de curvas transferidas y de los supuestos de servicio y tarifa heredados. La inducción es incremental y condicionada al soporte de costos, no una demanda adicional atribuida automáticamente a todo viaje de la muestra.

Las tablas agregadas no incluyen microdatos, direcciones, identificadores individuales ni coordenadas. La revisión de esos antecedentes permanece en el archivo privado de las fuentes y la auditoría.
