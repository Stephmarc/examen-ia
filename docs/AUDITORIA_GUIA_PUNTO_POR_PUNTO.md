# Auditoría completa de la guía de evaluación

Se contrastaron las siete páginas y los cinco criterios de la rúbrica. Esta matriz no asigna ni garantiza una nota. Los estados con limitación no deben presentarse como cumplimiento sin reservas.

## 1. Integrar ENAHO y ESCALE 2025
**Estado: Adaptación documentada.** Corte 2025 de los archivos panel proporcionados; padrón actualizado 29/10/2025. No se confirma equivalencia con toda la muestra anual.

Evidencia: `data/raw; data/processed; auditoria_final.json`.

## 2. Llaves de hogar, persona y distrito
**Estado: Implementado.** Persona: CONGLOME/VIVIENDA/HOGAR/CODPERSO; hogar: primeras tres; distrito y área para ESCALE. AÑO fijo en 2025 antes del cruce.

Evidencia: `notebooks/01_datos_y_auditoria.ipynb; src/pipeline.py`.

## 3. Ceros iniciales, espacios y encoding
**Estado: Implementado con ajuste al archivo real.** dtype string, strip y vacío a nulo. Los CSV originales tienen BOM UTF-8; no se fuerza latin1 porque alteraría AÑO.

Evidencia: `Notebook 01; fuentes originales`.

## 4. Población de 6 a 17 años
**Estado: Implementado.** Filtro de edad y residencia habitual; matrícula primaria/secundaria y grado válido para rezago.

Evidencia: `flujo_limpieza.csv`.

## 5. Ratio alumno/docente distrital por área
**Estado: Implementado.** Suma TALUM / suma TDOC; denominador no positivo a nulo; nombres reales difieren del ejemplo TALUMNO/TDOCENTE.

Evidencia: `contexto_escolar_distrito_area.csv`.

## 6. Proporción pública/privada y coordenadas
**Estado: Implementado.** Gestión 1/2 pública, 3 privada; medias de coordenadas válidas del padrón; contexto, no colegio individual.

Evidencia: `src/pipeline.py; diccionario_variables.csv`.

## 7. Cruce de módulos 100,200,300,Sumaria y ESCALE
**Estado: Implementado.** Cardinalidad validada; filas sin educación no se inventan; ausencia de contexto se registra e imputa solo en train.

Evidencia: `dataset_enaho_escale_2025.csv y parquet`.

## 8. Separación por CONGLOME
**Estado: Implementado.** GroupShuffleSplit test 20%; GroupKFold de 5 folds en train; intersecciones verificadas.

Evidencia: `particiones.csv; notebook 02`.

## 9. Transformaciones dentro del fold
**Estado: Implementado.** Imputación, escalado, codificación y pesos de balance se ajustan exclusivamente en cada fold de entrenamiento.

Evidencia: `Pipeline y ColumnTransformer`.

## 10. Excluir respuesta y proxies directos
**Estado: Corregido.** Se retiran edad, grado, edad normativa y años de rezago del modelo supervisado; los clusters no se usan como predictor.

Evidencia: `resumen_clasificacion.json`.

## 11. Clustering con ingresos, ratio, TIC, rezago y servicios
**Estado: Corregido.** Se añadieron frecuencia TIC de P314D y años de rezago. P316 describe actividades, no la frecuencia en estos datos.

Evidencia: `src/pipeline.py función clustering`.

## 12. PCA o UMAP
**Estado: Implementado.** PCA 2D ajustado solo en train; test solo transformado.

Evidencia: `clusters_pca.png`.

## 13. Al menos dos métodos de clustering
**Estado: Implementado.** K-Means y Gaussian Mixture con covarianza diagonal, k de 2 a 6.

Evidencia: `clustering_comparacion.csv`.

## 14. Silueta, Davies Bouldin y Calinski Harabasz
**Estado: Implementado.** Misma submuestra fija de hasta 1800 observaciones de train para comparar.

Evidencia: `clustering_comparacion.csv; siluetas.png`.

## 15. Nombres e interpretación de perfiles
**Estado: Implementado.** Perfiles, medias, tamaños y acciones propuestas. Se advierte que incluir rezago hace sus diferencias entre grupos parcialmente definitorias.

Evidencia: `perfiles_clusters.csv; informe sección 4`.

## 16. Resolver Opción A o B
**Estado: Corregido.** Se elige Opción A: rezago por edad superior a normativa aproximada del grado. No uso no se equipara a exclusión efectiva ni el índice de tres valores a continuo.

Evidencia: `notebook 02; informe`.

## 17. Definición de rezago
**Estado: Implementado con limitación.** Primaria P308C=grado; secundaria P308B=año, más 6. Normativa aproximada=grado acumulado+5. Edad declarada > normativa. Se conserva >=2 años; no se reproduce la fecha oficial al 31 de marzo sin nacimiento usable.

Evidencia: `diccionario_variables.csv; docs/METODOLOGIA.md`.

## 18. Baseline y al menos tres modelos avanzados
**Estado: Corregido.** Logística frente a Random Forest, XGBoost y LightGBM; MLP scikit-learn de dos capas como comparación adicional.

Evidencia: `clasificacion_corridas_cv.csv`.

## 19. Hiperparámetros y comparación justa
**Estado: Implementado.** Dos configuraciones por algoritmo y mismos folds/variables. El ganador usa AP de CV, nunca métricas test.

Evidencia: `clasificacion_seleccion_cv.csv`.

## 20. Balance y factor de expansión
**Estado: Implementado con alcance.** Balance por fold. Se conserva FACTOR07 de hogar y se evalúa sensibilidad FACPOB07 individual; no se usa un peso de hogar como si fuera individual ni se afirman totales nacionales del panel.

Evidencia: `clasificacion_test_ponderado_sensibilidad.csv`.

## 21. ROC-AUC PR-AUC F1 matriz calibración
**Estado: Implementado.** AP y área trapezoidal PR diferenciadas; umbral 0.5; matriz, curva de calibración y Brier.

Evidencia: `clasificacion_test.csv; figuras`.

## 22. Beeswarm diez variables del ganador
**Estado: Implementado.** Diez características transformadas; one-hot no se confunde con importancia agregada de la variable original.

Evidencia: `shap_beeswarm.png; shap_importancia.csv`.

## 23. Dos dependencias SHAP
**Estado: Implementado.** Conexión/lengua y ratio/ruralidad; ejes numéricos en unidades originales. Color explora heterogeneidad, no demuestra causalidad.

Evidencia: `shap_dependencia_1.png y 2`.

## 24. Dos waterfall extremos correctos
**Estado: Implementado.** Casos alto y bajo correctamente clasificados; fondo de train y verificación de aditividad.

Evidencia: `shap_caso_alto.png y bajo; resumen_shap.json`.

## 25. Carpeta data/raw processed notebooks src
**Estado: Implementado.** Originales utilizados, tablas de 2025, dataset final, código y notebooks juntos, con rutas relativas.

Evidencia: `Proyecto_IA`.

## 26. Jupyter ejecutable y semilla 42
**Estado: Verificado.** Notebook principal se ejecuta de nuevo tras las correcciones; código inicial documenta reproducción desde originales.

Evidencia: `02_PROYECTO_COMPLETO.ipynb; requirements.txt`.

## 27. Dataset final y diccionario
**Estado: Implementado.** CSV y Parquet; columnas, fuentes, fórmulas y uso. Copias visibles en DATAS_PARA_ENTREGAR.

Evidencia: `data/processed`.

## 28. Artículo científico 4 a 6 páginas
**Estado: Revisión de contenido y formato.** Seis páginas con resumen/abstract, introducción, método, resultados, discusión, recomendaciones y referencias; figuras de silueta y PCA dentro del informe.

Evidencia: `informe/Informe_Brecha_Digital_U2.pdf`.

## 29. Diagrama, faltantes y evidencia anti fuga
**Estado: Implementado.** Diagrama de cardinalidades; tasas de ausencia; exclusiones de predictores y particiones auditables.

Evidencia: `informe sección 2; faltantes.csv; particiones.csv`.

## 30. Tabla de validación y curvas ROC/PR
**Estado: Implementado.** Tabla de modelos CV/test; errores falsos positivos/negativos con implicaciones.

Evidencia: `informe sección 3`.

## 31. Conclusiones y recomendaciones basadas en evidencia
**Estado: Corregido al nuevo objetivo.** Resultados nuevos de rezago, incertidumbre y límites; no se reutilizan métricas del objetivo anterior.

Evidencia: `informe secciones 5 y 6`.

## 32. Defensa y código limpio
**Estado: Materiales disponibles.** Método y definición del objetivo documentados; la sustentación oral depende del estudiante.

Evidencia: `informe; README.md; docs/METODOLOGIA.md`.

## 33. Censo detallado y conectividad escolar
**Estado: No disponible completamente.** Matrícula y Docentes del Drive son HTML inválido. El padrón permite totales y contexto, pero no inventa computadoras ni conexión escolar.

Evidencia: `docs/METODOLOGIA.md`.

## 34. Regresión y benchmark del sílabo
**Estado: Complemento.** Ridge y bosque para índice operativo de tres valores, sin presentarlo como Opción B continua; caso MINEDU y tres prácticas.

Evidencia: `regresion_test.csv; informe sección 6`.



## Resultado de la ejecución
Ocho celdas de código ejecutadas sin errores. Dataset final y diccionario coherentes, cero llaves duplicadas y cero conglomerados compartidos entre train/test. La comparación incluyó 50 corridas CV y diez corridas de clustering. El clasificador de rezago mostró desempeño cercano al azar; no se presenta como útil para decisiones individuales.
