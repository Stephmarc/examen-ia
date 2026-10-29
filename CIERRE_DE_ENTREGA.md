# Cierre de la entrega

Esta es la versión completa para entregar. Incluye los cuatro ZIP ENAHO utilizados, el padrón MINEDU, las tablas de trabajo, la base final CSV/Parquet, el diccionario, el código, los experimentos, las figuras y el artículo de seis páginas.

## Resultados visibles

Los tres notebooks conservan sus salidas:

1. 01_datos_y_auditoria.ipynb: construcción desde los ZIP originales y vista de la base resultante.
2. 02_PROYECTO_COMPLETO.ipynb: limpieza, comparación de modelos, clustering, métricas y SHAP.
3. 03_AUDITORIA_LIMPIEZA.ipynb: pruebas de calidad, faltantes y alertas de valores extremos.

Los notebooks 01 y 03 se ejecutaron con IPython en Python 3.12 y guardaron salidas en el formato Jupyter; el notebook principal conserva su ejecución anterior. No se rellenaron salidas con resultados simulados. Se verificó que la reconstrucción coincide con la base utilizada en los modelos.

## Validación

65 pruebas de limpieza aprobadas. Otras 66 comprobaciones de archivos, resultados, métricas y explicaciones aprobadas en la revisión integral. Estas cifras son pruebas técnicas, no un porcentaje ni una nota de la rúbrica.

El MLP final guardado terminó en 15 iteraciones, antes del máximo de 180. Los dos avisos visibles del notebook pertenecen a ajustes de validación; no al estimador final. Se mantienen visibles por transparencia. No se afirma que todos los folds hayan convergido.

Se releyeron las siete páginas de la guía. El desglose de requisitos está en AUDITORIA_GUIA_PUNTO_POR_PUNTO.md y REVISION_INTEGRAL_FINAL.md. Este cierre actualiza su referencia anterior a notebooks 01/03 sin ejecutar: en esta carpeta ambos ya tienen salidas.

## Límites pendientes

La fuente ENAHO recibida es panel y se selecciona 2025. El rezago es aproximado por edad declarada y grado. Los archivos detallados MINEDU dañados no se inventaron. El informe tiene formato de artículo, sin certificación de plantilla editorial oficial. El modelo tiene discriminación cercana al azar y no se presenta como apto para decidir sobre estudiantes. La aceptación de estas adaptaciones y la sustentación oral corresponden al docente y al estudiante.

## GitHub

Esta carpeta y su ZIP son locales. La versión publicada anteriormente permanece privada y todavía no incluye este cierre. Para actualizar GitHub, cargar notebooks 01/02/03, src/auditar_limpieza.py, los reportes y resultados de auditoría, y README/CIERRE_DE_ENTREGA.md. Conservar los resultados de las celdas al guardar los notebooks. Los ZIP ENAHO grandes pueden mantenerse por enlace debido al límite de carga web: el paquete local sí los incluye. Dar acceso al docente antes de enviarle el enlace.
