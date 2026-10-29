# Originales ENAHO

Los ZIP originales utilizados se descargan de la carpeta compartida para el curso:

https://drive.google.com/drive/folders/1J2ExK_k8T9TAveZForau6i90lb8Ef7P2

Copiar desde INEI a esta carpeta:

- 1041-Modulo1474.zip — vivienda.
- 1041-Modulo1479.zip — personas.
- 1041-Modulo1475.zip — educación.
- 1041-Modulo1478.zip — Sumaria.

Conservar esos nombres y dejarlos comprimidos. `src/construir_datos.py` lee los CSV dentro de los ZIP, selecciona el corte 2025 y guarda las tablas de trabajo. Los hashes de procedencia se incluyen en `../manifiesto_fuentes.json`.

Los originales grandes se distribuyen por el enlace; la base final y las tablas seleccionadas ya están en `data/processed`.
