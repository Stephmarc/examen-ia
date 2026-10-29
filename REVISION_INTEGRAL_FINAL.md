> Actualización: ver CIERRE_DE_ENTREGA.md. En esta entrega los notebooks 01 y 03 ya conservan salidas ejecutadas y los cuatro ZIP ENAHO están incluidos.

# Revisión integral de la entrega

Se contrastaron las siete páginas de la guía, los 34 puntos de la matriz, el código, el dataset, las salidas guardadas del notebook y las seis páginas del informe. Se inspeccionó visualmente el PDF actual. Esta revisión no asigna una nota.

## Evidencia técnica

- Limpieza: 65/65 pruebas aprobadas; 19 286 personas, 34 columnas, sin personas duplicadas ni llaves incompletas. La nueva construcción desde ZIP originales coincide con la base entregada.
- Entrega y resultados: 66/66 comprobaciones aprobadas. Incluyen dependencias instaladas frente a requirements.txt, sintaxis, estructura, notebook principal, modelo recargado, métricas recalculadas, clustering, SHAP y figuras.
- El notebook principal contiene ocho celdas de código ejecutadas con salidas, sin errores. Conserva dos avisos ConvergenceWarning del MLP; no se ocultaron. Los notebooks 01 y 03 permiten repetir construcción y auditoría; no se presentan como ejecutados en esta revisión.
- El modelo guardado reproduce las probabilidades del CSV de errores. ROC-AUC, AP, PR trapezoidal, F1 macro, exactitud, precisión, recall y Brier coinciden al recalcularlos.
- Cinco modelos (logística y cuatro avanzados), 50 corridas de clasificación; diez corridas de K-Means/GMM y tres métricas de clustering; PCA y perfiles con nombres y acciones.
- SHAP corresponde al modelo guardado y reconstruye sus probabilidades. Incluye beeswarm de diez características, dos dependencias y dos waterfall de ejemplos correctamente clasificados.
- El informe tiene seis páginas, resumen/abstract, introducción, datos y diagrama, resultados, errores, discusión, conclusiones y referencias. Incluye nueve imágenes compuestas/individuales; las trece figuras completas están en resultados/figuras. Las páginas se revisaron sin detectar cortes de contenido. Tiene presentación de artículo; no se certifica adhesión exacta a una plantilla editorial oficial IEEE/MDPI.

Las comprobaciones detalladas están en resultados/PRUEBAS_REVISION_INTEGRAL.csv y resultados/auditoria_limpieza/pruebas.csv. No deben interpretarse como 131 requisitos independientes de la rúbrica.

## Requisitos y estado

| Bloque de la guía | Estado y evidencia |
|---|---|
| Ingesta, llaves como texto, espacios y codificación | Implementado en src/construir_datos.py; se usa la codificación real de los archivos. |
| Filtro 6–17 y cruce 100/200/300/Sumaria/ESCALE | Implementado; cardinalidades validadas y flujo documentado. |
| Variables creadas y dataset CSV/Parquet | Incluidos junto con diccionario de las 34 columnas. No son registros sintéticos. |
| Contexto por distrito/área: ratio, gestión y coordenadas | Implementado usando campos reales TALUM/TDOC y coordenadas del padrón. |
| Separación por conglomerado y transformaciones dentro de train | Implementado; sin conglomerados compartidos train/test ni entre folds. |
| Sin componentes del objetivo en predictores | Revisado en código y listas de variables; tampoco se usan llaves, pesos o clusters para clasificar. |
| Clustering: al menos dos métodos, selección k y perfiles | K-Means/GMM, k=2…6, silueta, Davies–Bouldin, Calinski–Harabasz, PCA y perfiles incluidos. |
| Problema supervisado A o B | Se eligió A, rezago escolar aproximado. La regresión adicional no se hace pasar por índice continuo oficial. |
| Baseline y al menos tres avanzados | Logística, Random Forest, XGBoost, LightGBM y MLP adicional; satisface el mínimo sin depender de que MLP use PyTorch. |
| Desbalance, ponderación y métricas | Pesos de balance por fold; sensibilidad con factor individual y conservación del factor de hogar. Métricas, matriz y calibración incluidas. |
| SHAP global, dependencias y casos individuales | Incluido y contrastado con el modelo guardado. No se afirma causalidad ni interacción formal. |
| Repositorio estructurado, código y semilla | Estructura incluida y semilla 42. Los ZIP ENAHO grandes se obtienen desde el enlace documentado. |
| Artículo de 4–6 páginas y discusión de errores | Seis páginas verificadas; tablas, gráficos, falsos positivos/negativos y límites explícitos. |
| Defensa oral | Hay guía de sustentación; el dominio del estudiante no puede certificarse revisando archivos. |

El desglose completo de los 34 puntos está en AUDITORIA_GUIA_PUNTO_POR_PUNTO.md. Donde ese documento dice «implementado» para defensa, se refiere a los materiales, no a una defensa oral ya evaluada.

## Reservas que permanecen

1. La guía menciona ENAHO anual. La fuente recibida es ENAHO panel 2021–2025, del que se extrae 2025. No se confirmó equivalencia con la muestra anual completa: la aceptación de esa adaptación corresponde al docente.
2. Los archivos MINEDU de matrícula/docentes recibidos estaban dañados. Se usaron los totales del padrón; no hay datos detallados de computadoras o conectividad escolar inventados para rellenar esa ausencia.
3. El objetivo usa edad declarada y grado; sin nacimiento usable no reproduce edad exacta al 31 de marzo. Además, 369 personas no tienen contexto MINEDU y conservan nulos imputados solo durante entrenamiento.
4. El MLP muestra dos avisos de convergencia y ROC-AUC 0,521, cercano al azar. No se certifica convergencia de todos los ajustes ni utilidad operativa. Corregir la limpieza no garantiza mejorar esa métrica.
5. El repositorio publicado quedó privado. El docente necesita acceso. Las auditorías nuevas y el ajuste documental de esta revisión están en el paquete local, todavía no publicados en GitHub. No se volvió a comprobar la renderización remota del notebook en esta sesión.

## Cambios de esta revisión

Se corrigió una referencia antigua del notebook principal a la carpeta hermana IA: ahora señala data/raw y el enlace de originales ENAHO. Solo cambió texto; las ocho celdas ejecutadas y sus resultados se conservaron. Se agregaron las comprobaciones integrales y este informe. No se alteraron datos ni métricas para elevar resultados.

## Conclusión de la revisión

Los componentes técnicos principales y los archivos de entrega están presentes y son consistentes con la opción elegida. No es correcto afirmar «100 % sin reservas»: quedan las adaptaciones de fuente/objetivo, la convergencia parcial, el formato editorial no certificado, la defensa oral y el acceso/publicación final en GitHub.
