# Datos y decisiones del análisis

La base final contiene 19 286 residentes habituales de 6–17 años matriculados en primaria/secundaria. Se integraron Personas y Educación por persona, Vivienda y Sumaria por hogar, y MINEDU por distrito y área. El diccionario registra fuentes, fórmulas y usos de las 34 variables. Los códigos se leen como texto y los campos vacíos se conservan como nulos.

## Objetivo y alcance

Se eligió la Opción A: rezago operativo si edad declarada > grado acumulado + 5. P308C define el grado de primaria; en secundaria se utiliza P308B+6. Se retiran de los predictores edad, grado y sus derivados. No se mide la edad exacta al 31 de marzo ni se afirma reproducir la tasa oficial. Los datos ENAHO recibidos son panel 2021–2025; se selecciona 2025 sin certificar equivalencia con la muestra anual completa.

Los archivos detallados MINEDU de matrícula y docentes recibidos contenían HTML. Se utilizaron TALUM y TDOC del padrón, sin inventar datos de computadoras o conectividad escolar. Las coordenadas proceden del padrón y la altitud de ENAHO. Los 369 registros sin contexto MINEDU conservan nulos que se imputan dentro de cada entrenamiento.

## Validación

GroupShuffleSplit reserva test por CONGLOME; GroupKFold usa cinco folds en train. Imputación, escalado, codificación y balance se ajustan dentro del fold. El ganador se elige por AP de validación. FACPOB07 se usa en una sensibilidad; los factores no habilitan por sí solos estimaciones nacionales del panel.

La reconstrucción desde originales coincide con la base del análisis. El notebook 03 conserva las 65 pruebas de limpieza y sus resultados. Los extremos estadísticos no se eliminan sin evidencia de error. El MLP final terminó antes de max_iter; dos ajustes de validación conservaron avisos de convergencia. Su ROC-AUC 0,521 es cercano al azar; no se recomienda usarlo para decidir sobre estudiantes. SHAP explica predicciones, no causalidad.

## Fuentes y reproducción

Los cuatro ZIP ENAHO grandes se descargan siguiendo data/raw/INEI/README.md. Están incluidos en el paquete local completo, pero no en GitHub. La lectura de las fuentes se implementa en src/construir_datos.py; las tablas intermedias se pueden regenerar y no se duplican en el repositorio. data/processed/base_escolar_ENAHO_2025_PRELIMINAR.csv permite ejecutar el notebook principal sin descargar de nuevo ENAHO. El padrón MINEDU utilizado sí está incluido.

El PDF final tiene una carátula adicional y un artículo de seis páginas. El logo se obtuvo de https://upeu.edu.pe/wp-content/uploads/2026/05/logo-upeu-dark.svg. El generador de informe produce el artículo; la portada institucional se conserva dentro del PDF final. La matriz por requisito está en docs/AUDITORIA_GUIA_PUNTO_POR_PUNTO.md.
