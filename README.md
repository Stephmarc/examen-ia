# Brecha digital y rezago escolar — Inteligencia Artificial

**Jannys Graciela Navarro Acrota · VIII ciclo · Universidad Peruana Unión, Juliaca**  
Docente: Ángel Rosendo Coaquira · Datos: corte 2025

## Revisar la entrega

- [Informe con carátula](informe/Informe_Brecha_Digital_U2.pdf): artículo de seis páginas más portada.
- [Notebook principal ejecutado](notebooks/02_PROYECTO_COMPLETO.ipynb): modelos, clustering, métricas y SHAP.
- [Dataset limpio CSV](data/processed/dataset_enaho_escale_2025.csv) · [Parquet](data/processed/dataset_enaho_escale_2025.parquet) · [Diccionario](data/processed/diccionario_variables.csv).
- [Construcción desde fuentes](notebooks/01_datos_y_auditoria.ipynb) · [Pruebas de limpieza](notebooks/03_AUDITORIA_LIMPIEZA.ipynb).

La base final contiene **19 286 personas y 34 columnas**. Se comparan logística, Random Forest, XGBoost, LightGBM y MLP; K-Means y GMM para perfiles. El MLP fue elegido por AP de validación y obtuvo ROC-AUC 0,521, AP 0,409 y F1 macro 0,518 en test. El desempeño es cercano al azar; no se propone uso para decisiones individuales.

## Ejecutar

Python 3.12. Desde la raíz, instalar `pip install -r requirements.txt` y abrir `notebooks/02_PROYECTO_COMPLETO.ipynb` en Jupyter. Sus tablas de entrada y el padrón MINEDU están incluidos. Para revisar los resultados guardados no hace falta entrenar otra vez. Semilla: 42.

Para reconstruir desde originales, descargar los cuatro ZIP ENAHO siguiendo [estas instrucciones](data/raw/INEI/README.md) y ejecutar el notebook 01. **Esos ZIP grandes no están incluidos en GitHub**. El código genera las tablas intermedias y una nueva base en `data/processed/reconstruccion/`.

## Organización

| Carpeta | Contenido |
|---|---|
| `data/` | Fuentes, entradas, base final y diccionario |
| `notebooks/` | Tres notebooks con salidas ejecutadas |
| `src/` | Construcción, modelos, auditoría e informe |
| `resultados/` | Corridas, métricas, predicciones, modelo y figuras |
| `informe/` | PDF final |
| `docs/` | Metodología, limitaciones y contraste con la guía |

## Alcance de los datos

Se utiliza 2025 de ENAHO panel, no se certifica equivalencia con la anual completa. El rezago se aproxima con edad declarada y grado. Los datos escolares son contexto de distrito y área, no la escuela individual. Quedan 369 registros sin contexto MINEDU; sus faltantes se imputan solo durante entrenamiento. [Método y limitaciones](docs/METODOLOGIA.md) · [Requisitos de la guía](docs/AUDITORIA_GUIA_PUNTO_POR_PUNTO.md).
