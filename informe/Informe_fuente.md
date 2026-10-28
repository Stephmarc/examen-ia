Brecha digital y rezago escolar en el Perú con ENAHO y ESCALE

Jannys Graciela Navarro · Ingeniería de Sistemas · Universidad Peruana Unión<br/>Inteligencia Artificial · Producto de la Unidad 2 · Datos 2025

Resumen

Se integró el corte 2025 de ENAHO panel con el padrón ESCALE actualizado el 29/10/2025 para perfilar contextos socioeducativos y clasificar rezago escolar operativo. La base final contiene 19,286 residentes habituales de 6 a 17 años matriculados en primaria/secundaria, con grado válido, de 4,701 conglomerados y 1,186 distritos. La cobertura escolar contextual fue 98.1%. Se comparó regresión logística con Random Forest, XGBoost, LightGBM y un MLP de dos capas mediante cinco folds agrupados y prueba aislada por conglomerado. El ganador de validación, MLP, obtuvo en test ROC-AUC 0.521, average precision 0.409 y F1 macro 0.518. Se añadieron K-Means/GMM, PCA y SHAP global/local. Las fechas de nacimiento no permiten reconstruir edad al 31 de marzo: el rezago es una aproximación por edad declarada y grado, no la tasa oficial de atraso escolar. No se estima impacto causal de conectividad ni totales nacionales del panel.

Abstract

A reproducible workflow links the 2025 cross-section of ENAHO panel files with school registry context. It compares a logistic baseline with Random Forest, XGBoost, LightGBM and a two-layer MLP using grouped cross-validation and a held-out cluster split. The selected model achieves ROC-AUC 0.521 and average precision 0.409. Clustering and SHAP complement the analysis. School-age delay is operationalized from reported age and current grade; it is not an official population estimate or evidence of causal educational effects.

<b>Palabras clave:</b> brecha digital; rezago escolar; ENAHO; ESCALE; GroupKFold; SHAP.

1 Introducción y problema elegido

Acceso doméstico, uso personal y competencias digitales son conceptos distintos. El INEI reporta indicadores separados de acceso y uso [1]. Por ello, no se equipara una respuesta de no uso con la exclusión digital efectiva completa. Se elige explícitamente la Opción A de la guía: clasificar rezago por edad superior a la normativa aproximada para el grado, con variables del hogar y contexto escolar. El no uso de internet se conserva como descriptivo y para un ejercicio complementario del sílabo.

El criterio operativo es edad declarada &gt; grado acumulado + 5. Primaria utiliza P308C (1–6); secundaria utiliza P308B (1–5), más seis. Se guarda además el umbral de dos o más años de diferencia. MINEDU define la edad normativa al 31 de marzo y publica un indicador de atraso de dos o más años [2,3]; sin nacimiento usable, no se afirma reproducir exactamente esos indicadores. La finalidad es explorar patrones y orientar verificación educativa, no diagnosticar ni excluir a estudiantes de beneficios.


---


2 Ingeniería de datos y prevención de fuga

Los archivos del Drive son paneles 2021–2025 con columnas por año. Se seleccionó sufijo _25 y AÑO=2025 mediante lectura por bloques; el BOM real es UTF-8, por lo que no se forzó latin1. Se conservaron llaves como texto y los espacios vacíos como nulos. No se imputaron respuestas objetivo ni se reemplazaron saltos por cero. Las cuatro tablas extraídas no tenían llaves duplicadas ni vacías; la equivalencia con toda la muestra anual no se da por demostrada.

Fuente | Nivel y llave de unión | Filas corte 2025
Personas 200 | Conglomerado, vivienda, hogar, persona | 115 145
Educación 300 | Misma llave de persona | 106 958
Vivienda 100 | Conglomerado, vivienda, hogar | 44 599
Sumaria | Misma llave de hogar | 33 702

Figura 1. Integración 1:1 por persona y N:1 por hogar y contexto distrital/área. AÑO se fija antes del cruce.

De 24 195 personas de 6–17 años, 527 no encontraron Educación; no se inventaron respuestas. Se filtraron residentes habituales, matrícula primaria/secundaria y grado válido. El flujo completo y los porcentajes de ausencia se entregan en CSV. Se agregaron servicios activos del padrón por UBIGEO y área: suma TALUM/suma TDOC, proporción pública y coordenadas medias válidas. Se homologaron estratos ENAHO 1–5 urbanos y 6–8 rurales. Los nombres reales TALUM/TDOC y la ubicación de coordenadas en Padron difieren de los ejemplos de la guía; altitud procede de ENAHO.

El cruce contextual cubrió 98.1%; las ausencias permanecen nulas hasta imputación dentro de train. Los ZIP de Matrícula y Docentes contienen HTML inválido y no aportan detalles de equipos/conexión escolar. El padrón completo incluye 3 407 registros totalmente imputados y 175 parcialmente imputados: fecha de actualización no equivale a observación nueva de cada total. No se asigna a cada alumno un colegio individual.

Se retiraron de X edad, grado, edad normativa, años de rezago y sus indicadores derivados. Los clusters no se usan como predictores. Imputación mediana/moda, StandardScaler y one-hot se ajustan dentro de cada fold. Los identificadores y ponderadores tampoco entran en X. FACPOB07 individual se conserva para sensibilidad de métricas; FACTOR07 de hogar se conserva como referencia, sin tratarlo como peso individual ni habilitar inferencia nacional del panel.


---


3 Clasificación agrupada comparación y errores

Train contiene 15,498 observaciones de 3,760 conglomerados y test 3,788 de 941; no hay conglomerados compartidos. GroupKFold de cinco folds usa las mismas filas y variables para todos los modelos. Se evalúan C=0.1/1 en logística; hojas mínimas 5/15 en Random Forest; profundidad 3/5 en XGBoost; 7/15 hojas en LightGBM; capas (32,16)/(64,32) en MLP. El MLP no usa early stopping aleatorio. Pesos de balance se estiman por fold; semilla 42. La selección usa AP media de validación antes de evaluar test; umbral fijo 0.5.

Modelo | AP CV | ROC test | AP test | F1 macro | Brier
MLP | 0.409 | 0.521 | 0.409 | 0.518 | 0.248
Logistica | 0.404 | 0.539 | 0.421 | 0.527 | 0.249
XGBoost | 0.402 | 0.529 | 0.409 | 0.517 | 0.249
LightGBM | 0.401 | 0.528 | 0.408 | 0.517 | 0.249
RandomForest | 0.398 | 0.524 | 0.397 | 0.521 | 0.249

El ganador de CV fue MLP, pero ROC-AUC 0.521 está cerca de 0.5 y su IC95 % [0.498, 0.542] incluye ese valor: no hay evidencia de discriminación útil en esta prueba. AP 0.409 está cerca de la prevalencia positiva 38.6%. Se distingue AP de área PR trapezoidal. El IC95 % de AP, por 200 remuestras de conglomerados, fue [0.377, 0.435]. Los intervalos no prueban superioridad entre modelos ni representan el diseño completo de encuesta.

Figura 2. ROC y precisión/recall sobre test. No se utilizó test para elegir hiperparámetros o ganador.

La matriz, filas reales [sin rezago, con rezago] y columnas predichas en igual orden, fue [[1480, 846], [878, 584]]. Hubo 878 falsos negativos y 846 falsos positivos. Los primeros pueden omitir revisión de una necesidad; los segundos incrementan verificaciones. Recall=0.399 y precisión=0.408. La curva de calibración y Brier se entregan sin afirmar calibración poblacional: el balance de clases puede desplazar probabilidades.

En una sensibilidad con distritos completos separados, el mismo algoritmo obtuvo ROC-AUC 0.528 y AP 0.397. Es un diagnóstico adicional y no una nueva selección. Se adjuntan métricas ponderadas con FACPOB07, tablas por lengua/ruralidad y predicciones con tipo de error; los grupos pequeños requieren cautela.


---


4 Clustering con frecuencia TIC y años de rezago

Se utilizaron once variables: ingresos/gastos logarítmicos per cápita, ratio alumno/docente, frecuencia TIC, años de rezago, ruralidad, electricidad, internet doméstico, miembros, altitud y proporción pública. P314D se recodificó ordinalmente: 3 diaria, 2 semanal, 1 mensual/menos, y 0 si P314A declara no uso. Los faltantes de usuarios no se confundieron con no uso. K-Means y GMM diagonal se compararon para k=2…6 sobre la misma representación y submuestra fija de hasta 1 800 registros de train.

La selección por silueta eligió KMeans con k=4: silueta 0.294, Davies–Bouldin 1.293 y Calinski–Harabasz 422.3. Se maximiza silueta y se contrasta con los demás índices, no con el resultado de test. Imputación, escalado y PCA se ajustaron solo en train; a test se aplicó predict/transform.

Figura 3. Silueta por observación de la muestra de train y proyección PCA. La curva de selección k y las diez corridas están en resultados/.

Grupo | n | Rural | Internet | TIC 0–3 | Rezago años | No uso
0 | 1053 | 87% | 100% | 1.20 | 0.53 | 53%
1 | 11547 | 1% | 100% | 2.36 | 0.42 | 17%
2 | 830 | 66% | 0% | 1.03 | 0.54 | 61%
3 | 5856 | 91% | 100% | 1.74 | 0.43 | 35%

Los nombres descriptivos, medias de todas las variables y acciones propuestas se entregan por grupo. Se recomienda revisar barreras de acceso para perfiles sin conexión y barreras de uso/acompañamiento cuando existe conexión pero el uso es bajo. Las acciones requieren verificación local; pertenecer a un cluster no prueba una necesidad individual ni autoriza exclusión de apoyos.

La guía pide incluir años de retraso en el perfil: por ello las diferencias de rezago entre clusters son parcialmente definitorias y no validan una predicción independiente. Los clusters no se introducen en el clasificador. La escala ordinal TIC resume frecuencia, no horas de uso; no mide aprendizaje o competencias. Los perfiles se describen en esta muestra sin afirmar proporciones poblacionales.


---


5 Explicabilidad del modelo ganador

Se explicó MLP en 402 casos de test, con fondo exclusivo de train. Las primeras características fueron proporcion_publica, altitud, latitud_media, sexo_mujer, log_ingreso_pc_mensual. El beeswarm muestra diez características transformadas; cada categoría one-hot se trata separadamente. Las contribuciones están en probabilidad, no en puntos porcentuales salvo salida en probabilidad.

Figura 4. Diez características con mayor contribución absoluta media. No equivale a causalidad ni a importancia agregada de categorías.

Figura 5. Conexión doméstica coloreada por lengua quechua, y ratio alumno/docente coloreado por ruralidad. Las variables numéricas se restituyen a unidades originales.

Las dependencias permiten observar contribuciones distintas según contexto y no linealidad. El color no calcula valores formales de interacción SHAP ni identifica efectos causales: lengua, geografía y recursos están correlacionados. Hay pocos casos de algunas lenguas en la muestra explicada y la ausencia visual de contraste no demuestra ausencia de efecto.

Figura 6. Casos extremos correctamente clasificados: alto rezago a la izquierda y bajo a la derecha. Las cifras junto a las variables son sus valores originales o logaritmos documentados.

Las probabilidades de los casos fueron 0.763 y 0.280, con clases reales 1 y 0. El error máximo de reconstrucción base+suma SHAP fue 0.000000. Los waterfall muestran qué contribuciones elevan o reducen la salida respecto al fondo; son ilustraciones seleccionadas por extremos, no casos representativos. Las probabilidades de un ajuste balanceado requieren validación/calibración antes de decisiones individuales.


---


6 Discusión recomendaciones y conclusiones

Como complemento del sílabo se compararon Ridge y Random Forest Regressor para el índice 0.5×no uso + 0.5×ausencia de conexión doméstica, con los mismos grupos y cinco folds. Se excluyeron ambos componentes de X. Esta escala tiene tres valores (0, 0.5, 1), no se presenta como índice continuo oficial ni como cumplimiento de la Opción B; la clasificación de rezago satisface la opción predictiva elegida.

Modelo | MAE | RMSE | R²
Ridge | 0.185 | 0.232 | 0.216
RandomForestRegressor | 0.183 | 0.232 | 0.217

<b>Referencia de aplicación.</b> Aprendo en casa ofrece televisión, radio e internet [4]. El contraste inspira tres prácticas: distinguir acceso de uso; ofrecer alternativas fuera de línea; y verificar alertas con docentes antes de asignar intervenciones. No se comparan métricas con ese servicio ni se atribuyen impactos que este análisis no midió. Los perfiles y errores sirven para planear verificaciones y priorizar revisión, no decisiones automáticas de exclusión.

<b>Limitaciones.</b> Se utiliza el corte 2025 de archivos panel sin certificar equivalencia con toda la anual. Los factores anuales no validan por sí solos inferencia del panel. Edad declarada y grado aproximan rezago, con sesgo posible por cumpleaños; no hay nacimiento usable para la referencia al 31 de marzo. Los módulos MINEDU dañados impiden detalles de equipos/conexión escolar. El padrón tiene imputaciones y el contexto distrital no identifica la escuela individual. Separar conglomerados no elimina toda similitud territorial, por lo que se añadió sensibilidad por distrito. Los grupos lingüísticos pequeños, calibración y definición del umbral requieren evaluación externa.

<b>Conclusiones.</b> La base es trazable y la comparación agrupada eligió MLP por AP de validación, pero su desempeño no justifica uso predictivo operativo. No debe emplearse para priorizar personas. La contribución es metodológica y descriptiva: documentar datos, perfiles y límites, y mostrar que los predictores disponibles no resuelven este objetivo aproximado. Antes de otro ensayo se requiere una definición temporal de rezago más precisa y datos educativos validados; no añadir edad/grado para inflar métricas. No se infieren efectos causales ni notas inexistentes.

Referencias y reproducción

[1] INEI. Estadísticas TIC, segundo trimestre 2025. https://www.gob.pe/institucion/inei/noticias/1254582-el-60-1-de-los-hogares-tiene-conexion-a-internet<br/>[2] MINEDU. Edades normativas, referencia al 31 de marzo. https://www.gob.pe/institucion/minedu/informes-publicaciones/2742610-edades-normativas<br/>[3] MINEDU ESCALE. Alumnos con atraso escolar, metadatos. https://escale.minedu.gob.pe/tendencias-portlet/servlet/tendencias/archivo?idCuadro=143&amp;tipo=meta<br/>[4] MINEDU. Aprendo en casa. https://www.gob.pe/8858-acceder-a-educacion-a-distancia-aprendo-en-casa<br/>[5] INEI. ENAHO panel 2021–2025 y diccionario, archivos del proyecto; MINEDU, padrón actualizado 29/10/2025 y diccionarios del Censo 2025.<br/>[6] Lundberg y Lee. A Unified Approach to Interpreting Model Predictions. NeurIPS, 2017. https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html<br/>Reproducción: notebooks/01_datos_y_auditoria.ipynb y 02_PROYECTO_COMPLETO.ipynb; src/pipeline.py; requirements.txt; semilla 42. Dataset CSV/Parquet, diccionario, fuentes y experimentos incluidos. Auditoría completa de 34 puntos en AUDITORIA_GUIA_PUNTO_POR_PUNTO.md.