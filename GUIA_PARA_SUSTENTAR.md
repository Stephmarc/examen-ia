# Sustentación de la revisión final

## Problema
Elegimos la Opción A: clasificar un indicador operativo de rezago por edad superior a la normativa aproximada del grado. Analizamos cómo se relaciona con recursos del hogar y contexto escolar. No modelamos notas ni efectos causales.

## Explicación en un minuto
Extraemos 2025 de los archivos panel, unimos Educación y Personas por llave individual y Vivienda/Sumaria por hogar. ESCALE se agrega por distrito y área. Conservamos códigos, revisamos duplicados y nulos, y definimos rezago con edad y grado. Retiramos esos componentes de los predictores. Comparamos logística, Random Forest, XGBoost, LightGBM y MLP con cinco folds por conglomerado y una prueba separada. Formamos perfiles con K-Means/GMM y explicamos el ganador con SHAP.

## Preguntas clave
**¿Cómo defines grado?** P308C para primaria; P308B+6 para secundaria. Normativa aproximada=grado+5.

**¿Es la tasa oficial?** No exactamente. No hay nacimiento usable para edad al 31 de marzo. La definición >0 sigue el criterio operativo de la guía; también guardamos >=2 años y documentamos el límite.

**¿Por qué retirar edad y grado?** Construyen la respuesta. Incluirlos permitiría reconstruirla directamente en lugar de aprender asociaciones de recursos y contexto.

**¿Por qué no dividir personas al azar?** Hermanos y vecinos comparten recursos; podrían quedar en train y test. Usamos GroupShuffleSplit y GroupKFold por conglomerado.

**¿El MLP separa al azar una validación interna?** No: early_stopping=False. Sus hiperparámetros se comparan con los mismos folds agrupados.

**¿Por qué PR-AUC y F1 macro?** PR se centra en recuperar la clase positiva; AP se compara con prevalencia. F1 macro considera ambas clases. AP y área trapezoidal PR no son idénticas.

**¿Qué es un falso negativo?** Una persona con el indicador de rezago que el modelo no detecta. Puede perder una revisión de necesidad. Un falso positivo añade verificaciones. Ninguno autoriza excluir de apoyos.

**¿Qué significa la calibración?** Que una probabilidad predicha coincida con frecuencias observadas. Balancear clases puede desplazar probabilidades; por eso entregamos Brier y curva, sin afirmar calibración poblacional.

**¿Qué incluye el clustering?** Ingresos/gastos, ratio alumno/docente, frecuencia TIC, años de rezago y servicios. Al incluir rezago, las diferencias de rezago entre grupos no validan una predicción independiente. Las etiquetas de cluster no entran a clasificación.

**¿SHAP es causal?** No. Distribuye una predicción respecto a un fondo de train. Geografía, pobreza y lengua pueden compartir información. Las dependencias coloreadas no son una prueba causal.

**¿Qué faltó en los archivos originales?** Dos ZIP de MINEDU son HTML. Usamos TALUM y TDOC del padrón; no inventamos computadoras o conexión escolar. El origen ENAHO es panel y no certificamos equivalencia con toda la anual.

## Caso comparable y tres prácticas
Aprendo en casa utiliza TV, radio e internet. Como propuestas: separar acceso de uso; ofrecer alternativas fuera de línea; y verificar alertas con docentes antes de intervenir. No se comparan métricas con ese servicio ni se atribuyen efectos no medidos.

Fuente: https://www.gob.pe/8858-acceder-a-educacion-a-distancia-aprendo-en-casa

## Antes de entregar
Leer el informe actualizado, revisar la matriz de 34 puntos y enviar el ZIP completo con notebook, datas, diccionario, fuentes y resultados. No enviar solamente el PDF ni usar el ZIP de la versión anterior.
