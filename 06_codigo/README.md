# Código de cálculo y exportación

Los resultados incluidos pueden consultarse sin ejecutar código. Los scripts requieren Python y las dependencias de `requirements.txt`.

## Reexportación de tablas

```bash
python 06_codigo/exportar_resultados.py --entrada /ruta/privada/comparacion_metodologia_original.csv.gz --salida .
python 06_codigo/generar_resumen_principal.py --salida .
```

El archivo de entrada contiene el detalle privado del modelo. La exportación elimina identificadores y coordenadas y agrupa los resultados por las dimensiones documentadas. No vuelve a expandir encuestas ni estima nuevas rutas.

## Reproducción del modelo

`calcular_demanda_por_zonificacion.py` aplica las configuraciones congeladas a los insumos privados. Conserva la cohorte, selección de pantallas, expansión y temporalización; actualiza los atributos dependientes de la zonificación y proyecta desde 2026 con PIB de 1%, 2% o 3% y elasticidades fijas.

Para reproducir esta etapa deben restaurarse los archivos de referencia privados y la caché geográfica en la estructura inventariada. El repositorio no distribuye esos datos individuales. Las instrucciones metodológicas y las tablas permiten revisar resultados y balances sin acceder a ellos.

## Comprobación de la entrega

```bash
python 06_codigo/verificar_entrega.py
```

El verificador revisa la integridad de los libros, las columnas, las exclusiones de datos privados y los controles de agregación; actualiza el inventario de archivos. La validación se refiere a la distribución pública de resultados agregados. No certifica representatividad estadística, precisión de celdas con base reducida ni cobertura completa del mercado.

## Comparaciones y datos procesados publicables

```bash
python 06_codigo/exportar_comparaciones.py --salida .
python 06_codigo/exportar_datos_procesados.py --entrada /ruta/privada/comparacion_metodologia_original.csv.gz --referencias /ruta/privada/referencia --salida .
```

La primera orden compara tablas públicas existentes. La segunda publica agregaciones y antecedentes de procesamiento, conservando fuera del repositorio los registros individuales y las fuentes originales.
