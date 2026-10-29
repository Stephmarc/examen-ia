# Examen de Inteligencia Artificial

**Jannys Graciela Navarro · Ingeniería de Sistemas · Universidad Peruana Unión**

Análisis de brecha digital y rezago escolar con el corte 2025 de ENAHO y el padrón ESCALE. La base final contiene 19 286 escolares de 6 a 17 años y 34 columnas.

## Contenido

- `notebooks/01_datos_y_auditoria.ipynb`: construcción desde los originales.
- `notebooks/02_PROYECTO_COMPLETO.ipynb`: análisis ejecutado, modelos, clustering y SHAP.
- `src/`: código de construcción, entrenamiento e informe.
- `data/processed/`: base limpia, diccionario y tablas seleccionadas de 2025.
- `data/raw/`: padrón MINEDU, diccionarios y procedencia de los archivos ENAHO.
- `resultados/`: métricas, corridas, particiones, figuras y modelo guardado.
- `informe/Informe_Brecha_Digital_U2.pdf`: artículo de seis páginas.

## Ejecución

Se utilizó Python 3.12. Instalar las dependencias con `pip install -r requirements.txt`, abrir Jupyter y ejecutar `notebooks/02_PROYECTO_COMPLETO.ipynb`. Las tablas y el padrón que utiliza ese notebook están incluidos en el repositorio. Se puede leer el notebook con sus resultados sin repetir el entrenamiento.

Para reconstruir desde los ZIP originales, seguir `data/raw/INEI/README.md` y ejecutar el notebook 01 o `python src/construir_datos.py`. Las tablas seleccionadas se mantienen como texto durante los cruces. La reconstrucción se contrastó con la base usada en los modelos; el registro está en `VALIDACION_CREACION_DATOS.json`.

## Método y resultados

Se compararon regresión logística, Random Forest, XGBoost, LightGBM y MLP con cinco folds por conglomerado. Se reservó un conjunto de prueba separado y se ajustaron las transformaciones dentro de cada fold. Para clustering se compararon K-Means y GMM, con PCA y evaluación de silueta, Davies–Bouldin y Calinski–Harabasz. El ganador de clasificación se explicó con SHAP.

El MLP fue seleccionado por AP de validación. En prueba obtuvo ROC-AUC 0.521, AP 0.409 y F1 macro 0.518. Su desempeño es cercano al azar; el análisis no respalda decisiones individuales. Los perfiles y las limitaciones se explican en el informe.

## Fuentes y alcance

Se seleccionó 2025 de archivos ENAHO panel 2021–2025. El padrón MINEDU tiene fecha de actualización 29/10/2025. El indicador de rezago usa edad declarada y grado, por lo que aproxima la referencia normativa. Dos archivos del Drive tenían HTML en lugar de datos; se utilizaron los totales disponibles del padrón. Detalles en `LIMITACIONES_DE_LAS_FUENTES.md`.

La revisión de la guía está en `AUDITORIA_GUIA_PUNTO_POR_PUNTO.md`. Las instrucciones para la exposición se encuentran en `GUIA_PARA_SUSTENTAR.md`.


## Entrega completa revisada

Esta carpeta incluye los cuatro ZIP ENAHO utilizados y el padrón MINEDU. Los tres notebooks conservan salidas ejecutadas: construcción desde originales, análisis principal y auditoría. Las pruebas no eliminan las limitaciones del panel, la definición aproximada del rezago o el desempeño predictivo. Consultar CIERRE_DE_ENTREGA.md.
