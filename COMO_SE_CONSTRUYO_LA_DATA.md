# Construcción de la base

1. Se leyeron los ZIP originales de ENAHO y se seleccionó el corte 2025. Los códigos de persona, hogar y distrito se conservaron como texto.
2. Se limpiaron los espacios vacíos y se revisaron llaves incompletas y duplicadas.
3. Personas y Educación se unieron por conglomerado, vivienda, hogar y persona. Vivienda y Sumaria se incorporaron por la llave de hogar.
4. Se seleccionaron residentes de 6 a 17 años matriculados en primaria o secundaria, con grado válido.
5. Se calcularon los indicadores escolares por distrito y área usando el padrón: alumnos por docente, proporción pública y coordenadas medias.
6. Se crearon las variables de gasto e ingreso per cápita, frecuencia TIC y rezago. Las fórmulas están en el diccionario.
7. La base final se guardó en CSV y Parquet. La imputación, el escalado y la codificación para los modelos se ajustaron después, dentro de cada fold de entrenamiento.

La construcción se puede repetir con `src/construir_datos.py`. Los datos originales se conservan en `data/raw`, las tablas de trabajo en `data/processed` y la base final se llama `dataset_enaho_escale_2025`.
