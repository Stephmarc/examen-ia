# Objetivo supervisado elegido según la guía

Se elige Opción A: rezago escolar operativo por edad superior a la normativa aproximada para el grado. No se llama exclusión digital efectiva a la sola falta de uso de internet.

Primaria P308A=2: grado de P308C, valores 1–6. Secundaria P308A=3: año de P308B, valores 1–5, más seis. No confundir P308B=0 en primaria con grado cero.

Edad normativa aproximada = grado acumulado + 5. Años de desfase = max(edad declarada - normativa, 0). Clase principal positiva si desfase >0. Umbral >=2 años conservado como sensibilidad descriptiva.

La edad normativa oficial se refiere al 31 de marzo. Las columnas adicionales de fecha de nacimiento no tienen información usable en esta extracción, por lo que este indicador aproximado no se presenta como la tasa oficial de atraso de dos o más años. Un cumpleaños durante el año puede cambiar la clasificación bajo el criterio >0. Hay que validar la definición con el docente si exige reproducir un indicador oficial, en vez del criterio operativo de su guía.

Para evitar una clasificación tautológica, edad, grado, normativa, años de desfase y sus indicadores se excluyen de los predictores. El clustering sí incluye años de rezago por requisito expreso, pero sus etiquetas no se pasan al modelo supervisado.

El índice de regresión complementaria toma tres valores y no es continuo ni oficial: no se usa para afirmar cumplimiento de la Opción B. La guía exige al menos una opción predictiva y aquí se elige A.
