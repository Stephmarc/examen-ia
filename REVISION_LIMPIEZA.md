> Actualización: ver CIERRE_DE_ENTREGA.md. En esta entrega los notebooks 01 y 03 ya conservan salidas ejecutadas y los cuatro ZIP ENAHO están incluidos.

# Revisión de limpieza

Se repitió la construcción desde los cuatro ZIP originales ENAHO y el padrón MINEDU. El resultado coincide, fila por fila y columna por columna, con la base utilizada en los modelos (tolerancia numérica 1e-12).

La base conserva **19 286 personas y 34 columnas**. Las **65 pruebas automáticas pasaron**, sin fallos. Se revisaron llaves, duplicados, tipos, rangos, categorías, fórmulas, equivalencia CSV/Parquet, cobertura del diccionario, cruces contextuales, particiones y separación de conglomerados en los cinco folds. También se comprobó que las variables del objetivo, llaves y pesos no formen parte de los predictores de clasificación.

## Faltantes que se conservan

369 personas (1,91 %) no encuentran contexto MINEDU por distrito y área. Cada una tiene cinco variables contextuales faltantes. No se inventaron valores ni se borraron estas personas. La imputación por mediana se ajusta dentro de cada entrenamiento, sin utilizar test. Las otras 29 columnas no tienen faltantes. Una base limpia puede contener nulos documentados.

## Valores extremos

La regla exploratoria de tres rangos intercuartílicos señala 340 registros de gasto, 349 de ingreso y 34 de miembros del hogar; las categorías pueden solaparse. Son alertas estadísticas, no errores confirmados. Se conservan para no excluir hogares válidos solo por ser distintos. Ingresos y gastos se transforman con log1p para el análisis.

## Qué cambió

Se añadieron pruebas reproducibles, un notebook de auditoría y tablas de distribución, faltantes y extremos. No se encontraron defectos que justificaran cambiar los valores de la base o volver a entrenar los modelos. No se modificaron sus resultados.

## Límites de esta revisión

Las pruebas verifican integridad y coherencia con los archivos recibidos, no la veracidad de cada respuesta del cuestionario. Siguen vigentes el uso del panel ENAHO, el rezago aproximado por edad declarada y grado, los archivos de matrícula/docentes dañados y los registros imputados del padrón. Limpieza correcta no implica capacidad predictiva: el modelo mantiene ROC-AUC 0,521 y no debe presentarse como herramienta lista para decisiones individuales.

## Repetir las pruebas

Abrir notebooks/03_AUDITORIA_LIMPIEZA.ipynb o ejecutar `python src/auditar_limpieza.py` desde la raíz. Las pruebas detalladas se guardan en resultados/auditoria_limpieza/pruebas.csv. La segunda reconstrucción desde originales se registra por separado en reconstruccion_originales.json.
