# SBO, alternativas y proyección de demanda

## Situación base optimizada

La **situación base optimizada (SBO)** mantiene la ruta terrestre por Chile y el cruce Puerto Ibáñez–Chile Chico, con la configuración operacional adoptada para la base. La demanda terrestre procede de CITRA y la lacustre de ARISTO. La demanda de referencia es común a A1, A2 y A3: no se cuenta tres veces por aparecer como base de tres proyectos.

| Parámetro | SBO |
|---|---:|
| Nave de referencia | Capitán Wellmann |
| Navegación del cruce actual | 107 minutos |
| Frecuencia por sentido, diciembre–abril | 11 servicios por semana |
| Frecuencia por sentido, mayo–noviembre | 8 servicios por semana |
| Presentación de vehículos | 2 horas |
| Presentación de peatones | 1 hora |
| Desembarque | 0,5 horas |
| Coeficiente de penalización por horario | 0,25 |

Estas frecuencias son la configuración del modelo, no una verificación de servicios efectivamente operados en cada fecha. Los tiempos de presentación y desembarque son supuestos de la base y se transfieren al proyecto según su configuración.

## Alternativas del proyecto

| Código | Alternativa | Acceso norte | Longitud de acceso norte | Navegación | Infraestructura de terminal |
|---|---|---|---:|---:|---|
| A1 | Convencional | P-20a | 31,14 km | 43 minutos | Rampa fija |
| A2 | Rápida con linkspan | P-20d | 24,62 km | 39 minutos | Puente basculante |
| A3 | Rápida con rampa fija | P-20b | 22,60 km | 39 minutos | Muelles y rampa fija |

Las tres alternativas son excluyentes. Se adopta acceso de ripio a 50 km/h con el perfil HDM4 de referencia. La componente sur se conserva en la geometría de referencia, evitando añadir dos veces los mismos tramos. Los empalmes y atributos nuevos son hipótesis de proyecto; un enlace esquemático entre terminales no equivale a un trazado vial o náutico validado.

El nuevo servicio utiliza las mismas frecuencias estacionales de 11/8 servicios semanales por sentido y una distancia de navegación de referencia de 7,3 millas náuticas. La disponibilidad de servicio no constituye una comprobación de capacidad.

## Costos generalizados

Para cada OD, segmento y alternativa se conserva la estructura de costo monetario y costo del tiempo:

$$CG=COV+Tarifas+VST\,o\,T$$

$COV$ corresponde al costo de operación vehicular; las tarifas incluyen los componentes viales, lacustres o de bus que procedan. $VST$ es el valor del tiempo y $o$ la ocupación empleada para expresar su costo por vehículo o usuario. Se conserva $VST=10.047$ CLP por persona-hora; ocupación 1,98 para VL y el perfil de costos VP, y 1 para camiones y peatones. Los precios siguen la convención de enero de 2026 del modelo de referencia.

El tiempo lacustre incluye acceso vial, navegación, presentación, desembarque y penalización por horario. Esta última utiliza $0,25\times168/f$, con $f$ en servicios semanales por sentido.

Los peatones mantienen la hipótesis de buses coordinados en los accesos. Se conservan sus tarifas y tiempos de referencia; no se interpreta esa hipótesis como un servicio comprometido. En camiones se mantienen los supuestos tarifarios y de flota del modelo de referencia. Su transferencia a CITRA es una hipótesis heredada, no una longitud vehicular observada en esas encuestas.

Los antecedentes de costos conservan valores históricos de navegación o frecuencia en textos de configuraciones anteriores. **La configuración operacional vigente es la indicada en las tablas de este documento:** 107 minutos en la SBO, 43/39/39 minutos en A1/A2/A3 y frecuencias de 11/8 en ambos cruces. Esos valores prevalecen sobre las referencias históricas 120/80 minutos o 14/12 servicios.

## Comparación de zonificaciones

La zonificación anterior conserva los 55 códigos de referencia. La representación por localidades distingue los extremos identificables mediante coordenadas y referencias de la red; mantiene sectores rurales, zonas externas y componentes sin desagregar cuando no existe mayor respaldo.

**CITRA ya diferenciaba viajes y costos por localidad**, incluidos Puerto Guadal, Mallín Grande y Puerto Río Tranquilo, aunque compartieran códigos zonales. Cambiar ese código no justifica alterar nuevamente su cálculo. Se conservan íntegramente sus componentes de base.

ARISTO se desagrega dentro del mismo perfil original de fecha, OD y temporalización. La participación de cada localidad reparte el aporte original; no crea ni elimina demanda base. Los costos se ajustan mediante la diferencia de atributos físicos entre la localidad y el referente anterior:

$$CG_{localidad}=CG_{referencia}+\Delta COV+VST\,o\,\Delta T$$

Para peatones se sustituye $\Delta COV$ por la variación de tarifa de bus asociada al acceso. Las tarifas lacustres y los parámetros no espaciales se mantienen. Cuando no existen atributos comparables para ambos referentes, se conserva el costo anterior y se identifica la limitación.

Las coordenadas permiten una geoasignación, no una afirmación de domicilio exacto ni de recorrido GPS. Los viajes internacionales o genéricos sin soporte de modelación permanecen como referencia o residual; no se agregan itinerarios por Argentina al modelo de captación.

## Captación del proyecto

El ahorro relativo respecto de la alternativa de procedencia es:

$$A=\frac{CG_{origen,SBO}-CG_{proyecto}}{CG_{origen,SBO}}$$

La participación $p$ del proyecto se obtiene interpolando las curvas heredadas por familia de usuarios y escenario. Se conservan casos conservador, central y alto. Son hipótesis de respuesta transferidas, no una nueva calibración local de logit ni intervalos estadísticos.

Si solo se dispone del costo de un núcleo con una cola exterior común sin valorar, se mantienen las cotas de ahorro y su ponderación original. Ese costo de núcleo no se presenta como el costo completo del OD.

Los viajes existentes transferidos al proyecto son $Qp$. El resto conocido permanece en la alternativa de procedencia. Cuando no puede calcularse la participación, la demanda permanece como residual sin asignación.

## Inducción incremental

La inducción distingue el potencial que ya estaba disponible en la SBO del incremento atribuible a una reducción adicional de costo con proyecto:

$$I=Q\left[\left(\frac{CG_{min,CP}}{CG_{origen,SBO}}\right)^\epsilon-\left(\frac{CG_{min,SBO}}{CG_{origen,SBO}}\right)^\epsilon\right]$$

Se calcula solo si existen costos positivos comparables y el mínimo con proyecto mejora el mínimo sin proyecto; el incremento se acota inferiormente a cero. Se excluyen de esta operación los costos de núcleo con cola exterior no valorada. El incremento se reparte con $p$ hacia el nuevo cruce y $1-p$ hacia la alternativa de procedencia.

Las elasticidades centrales respecto del **costo generalizado** son −0,354 para VL, VP y peatones, y −0,106 para camiones. Los casos de menor/mayor inducción modifican esos parámetros. No son elasticidades respecto del PIB.

La conservación se comprueba separando demanda existente, inducción y residual:

$$Q=D_{tierra}^{existente}+D_{actual}^{existente}+D_{proyecto}^{existente}+R$$

En el soporte donde la inducción es calculable, la suma de demanda con proyecto en las tres rutas más el residual equivale a la referencia más la inducción incremental. No se completa una suma faltante inventando componentes.

## Proyección y sensibilidad del PIB

Se utiliza 2026 como base y se presentan 2030, 2040 y 2050. El crecimiento se aplica por igual a ambas zonificaciones:

$$Q_t=Q_{2026}(1+g)^{(t-2026)\eta}$$

| Escenario de PIB real | Tasa anual $g$ | Elasticidad vehículos $\eta$ | Elasticidad peatones $\eta$ |
|---|---:|---:|---:|
| Bajo | 1% | 1,2 | 0,6 |
| Central | 2% | 1,2 | 0,6 |
| Alto | 3% | 1,2 | 0,6 |

Se sensibiliza la tasa de crecimiento del PIB y se mantienen fijas las elasticidades demanda/PIB. Las tasas son supuestos del análisis, no pronósticos oficiales ni una calibración local. Las clases conservan el agrupamiento de familias del modelo; no se crea una base positiva para clases con cero o sin información compatible.

Con costos, frecuencias y participaciones fijos, la referencia, captación, inducción y residuales escalan con el mismo factor de crecimiento de su segmento. Los tres escenarios coinciden en 2026. Cambiar el PIB no exige recalcular rutas o expansión.
