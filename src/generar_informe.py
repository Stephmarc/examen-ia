from pathlib import Path
import json, html
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER,TA_JUSTIFY
from reportlab.lib.pagesizes import A4
R=Path(__file__).resolve().parents[1]; O=R/'resultados'; F=O/'figuras'
def load(n): return json.loads((O/f'{n}.json').read_text(encoding='utf-8'))
a=load('auditoria_final'); c=load('resumen_clasificacion'); cl=load('resumen_clustering'); sh=load('resumen_shap')
cv=pd.read_csv(O/'clasificacion_seleccion_cv.csv'); test=pd.read_csv(O/'clasificacion_test.csv'); reg=pd.read_csv(O/'regresion_test.csv'); prof=pd.read_csv(O/'perfiles_clusters.csv'); imp=pd.read_csv(O/'shap_importancia.csv'); sub=pd.read_csv(O/'auditoria_subgrupos.csv')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body',fontName='Times-Roman',fontSize=10,leading=12.5,spaceAfter=7,alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name='SmallBody',fontName='Times-Roman',fontSize=8.5,leading=10.3,spaceAfter=5))
styles.add(ParagraphStyle(name='PaperTitle',fontName='Times-Bold',fontSize=18,leading=21,alignment=TA_CENTER,spaceAfter=12))
styles.add(ParagraphStyle(name='PaperHead',fontName='Times-Bold',fontSize=12,leading=14,spaceBefore=8,spaceAfter=6))
styles.add(ParagraphStyle(name='CaptionPaper',fontName='Times-Italic',fontSize=8,leading=9.5,spaceAfter=6))
story=[]; source=[]
def p(s,sty='Body'):
    story.append(Paragraph(s,styles[sty])); source.append(s)
def head(s): p(s,'PaperHead')
def table(rows,widths=None):
    rows=[[Paragraph(str(v),styles['SmallBody']) for v in row] for row in rows]
    t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8edf2')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#c9cdd2')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(t); story.append(Spacer(1,7)); source.append('\n'.join(' | '.join(x.getPlainText() for x in row) for row in rows))
def fig(name,width=480,maxheight=230,caption=''):
    im=Image(str(F/f'{name}.png')); scale=min(width/im.imageWidth,maxheight/im.imageHeight); im.drawWidth=im.imageWidth*scale; im.drawHeight=im.imageHeight*scale
    story.append(im)
    if caption: p(caption,'CaptionPaper')
def pair(n1,n2,caption):
    ims=[]
    for n in [n1,n2]:
        im=Image(str(F/f'{n}.png')); s=min(238/im.imageWidth,180/im.imageHeight); im.drawWidth=im.imageWidth*s; im.drawHeight=im.imageHeight*s; ims.append(im)
    story.append(Table([ims],colWidths=[245,245])); p(caption,'CaptionPaper')
def page(): story.append(PageBreak()); source.append('\n---\n')

metric=c['test_ganador']; cm=c['matriz_confusion']; ci=c['IC95_bootstrap_grupos']; g=c['sensibilidad_separacion_distrito']
p('Brecha digital y rezago escolar en el Perú con ENAHO y ESCALE','PaperTitle')
p('Jannys Graciela Navarro · Ingeniería de Sistemas · Universidad Peruana Unión<br/>Inteligencia Artificial · Producto de la Unidad 2 · Datos 2025','SmallBody')
head('Resumen')
p(f'Se integró el corte 2025 de ENAHO panel con el padrón ESCALE actualizado el 29/10/2025 para perfilar contextos socioeducativos y clasificar rezago escolar operativo. La base final contiene {a["filas"]:,} residentes habituales de 6 a 17 años matriculados en primaria/secundaria, con grado válido, de {a["conglomerados"]:,} conglomerados y {a["distritos"]:,} distritos. La cobertura escolar contextual fue {a["cobertura_minedu"]:.1%}. Se comparó regresión logística con Random Forest, XGBoost, LightGBM y un MLP de dos capas mediante cinco folds agrupados y prueba aislada por conglomerado. El ganador de validación, {c["ganador_cv"]}, obtuvo en test ROC-AUC {metric["ROC_AUC"]:.3f}, average precision {metric["PR_AUC_AP"]:.3f} y F1 macro {metric["F1_macro"]:.3f}. Se añadieron K-Means/GMM, PCA y SHAP global/local. Las fechas de nacimiento no permiten reconstruir edad al 31 de marzo: el rezago es una aproximación por edad declarada y grado, no la tasa oficial de atraso escolar. No se estima impacto causal de conectividad ni totales nacionales del panel.')
head('Abstract')
p(f'A reproducible workflow links the 2025 cross-section of ENAHO panel files with school registry context. It compares a logistic baseline with Random Forest, XGBoost, LightGBM and a two-layer MLP using grouped cross-validation and a held-out cluster split. The selected model achieves ROC-AUC {metric["ROC_AUC"]:.3f} and average precision {metric["PR_AUC_AP"]:.3f}. Clustering and SHAP complement the analysis. School-age delay is operationalized from reported age and current grade; it is not an official population estimate or evidence of causal educational effects.','SmallBody')
p('<b>Palabras clave:</b> brecha digital; rezago escolar; ENAHO; ESCALE; GroupKFold; SHAP.','SmallBody')
head('1 Introducción y problema elegido')
p('Acceso doméstico, uso personal y competencias digitales son conceptos distintos. El INEI reporta indicadores separados de acceso y uso [1]. Por ello, no se equipara una respuesta de no uso con la exclusión digital efectiva completa. Se elige explícitamente la Opción A de la guía: clasificar rezago por edad superior a la normativa aproximada para el grado, con variables del hogar y contexto escolar. El no uso de internet se conserva como descriptivo y para un ejercicio complementario del sílabo.')
p('El criterio operativo es edad declarada &gt; grado acumulado + 5. Primaria utiliza P308C (1–6); secundaria utiliza P308B (1–5), más seis. Se guarda además el umbral de dos o más años de diferencia. MINEDU define la edad normativa al 31 de marzo y publica un indicador de atraso de dos o más años [2,3]; sin nacimiento usable, no se afirma reproducir exactamente esos indicadores. La finalidad es explorar patrones y orientar verificación educativa, no diagnosticar ni excluir a estudiantes de beneficios.')
page()
head('2 Ingeniería de datos y prevención de fuga')
p('Los archivos del Drive son paneles 2021–2025 con columnas por año. Se seleccionó sufijo _25 y AÑO=2025 mediante lectura por bloques; el BOM real es UTF-8, por lo que no se forzó latin1. Se conservaron llaves como texto y los espacios vacíos como nulos. No se imputaron respuestas objetivo ni se reemplazaron saltos por cero. Las cuatro tablas extraídas no tenían llaves duplicadas ni vacías; la equivalencia con toda la muestra anual no se da por demostrada.')
table([['Fuente','Nivel y llave de unión','Filas corte 2025'],['Personas 200','Conglomerado, vivienda, hogar, persona','115 145'],['Educación 300','Misma llave de persona','106 958'],['Vivienda 100','Conglomerado, vivienda, hogar','44 599'],['Sumaria','Misma llave de hogar','33 702']],widths=[100,290,100])
fig('diagrama_cruces',maxheight=105,caption='Figura 1. Integración 1:1 por persona y N:1 por hogar y contexto distrital/área. AÑO se fija antes del cruce.')
p('De 24 195 personas de 6–17 años, 527 no encontraron Educación; no se inventaron respuestas. Se filtraron residentes habituales, matrícula primaria/secundaria y grado válido. El flujo completo y los porcentajes de ausencia se entregan en CSV. Se agregaron servicios activos del padrón por UBIGEO y área: suma TALUM/suma TDOC, proporción pública y coordenadas medias válidas. Se homologaron estratos ENAHO 1–5 urbanos y 6–8 rurales. Los nombres reales TALUM/TDOC y la ubicación de coordenadas en Padron difieren de los ejemplos de la guía; altitud procede de ENAHO.')
p(f'El cruce contextual cubrió {a["cobertura_minedu"]:.1%}; las ausencias permanecen nulas hasta imputación dentro de train. Los ZIP de Matrícula y Docentes contienen HTML inválido y no aportan detalles de equipos/conexión escolar. El padrón completo incluye 3 407 registros totalmente imputados y 175 parcialmente imputados: fecha de actualización no equivale a observación nueva de cada total. No se asigna a cada alumno un colegio individual.')
p('Se retiraron de X edad, grado, edad normativa, años de rezago y sus indicadores derivados. Los clusters no se usan como predictores. Imputación mediana/moda, StandardScaler y one-hot se ajustan dentro de cada fold. Los identificadores y ponderadores tampoco entran en X. FACPOB07 individual se conserva para sensibilidad de métricas; FACTOR07 de hogar se conserva como referencia, sin tratarlo como peso individual ni habilitar inferencia nacional del panel.')
page()
head('3 Clasificación agrupada comparación y errores')
p(f'Train contiene {c["n_train"]:,} observaciones de {c["grupos_train"]:,} conglomerados y test {c["n_test"]:,} de {c["grupos_test"]:,}; no hay conglomerados compartidos. GroupKFold de cinco folds usa las mismas filas y variables para todos los modelos. Se evalúan C=0.1/1 en logística; hojas mínimas 5/15 en Random Forest; profundidad 3/5 en XGBoost; 7/15 hojas en LightGBM; capas (32,16)/(64,32) en MLP. El MLP no usa early stopping aleatorio. Pesos de balance se estiman por fold; semilla 42. La selección usa AP media de validación antes de evaluar test; umbral fijo 0.5.')
rows=[['Modelo','AP CV','ROC test','AP test','F1 macro','Brier']]
for _,r in cv.iterrows():
    t=test.loc[test.modelo==r.modelo].iloc[0]; rows.append([r.modelo,f'{r.CV_PR_AUC_AP:.3f}',f'{t.ROC_AUC:.3f}',f'{t.PR_AUC_AP:.3f}',f'{t.F1_macro:.3f}',f'{t.Brier:.3f}'])
table(rows,widths=[120,65,75,75,80,75])
p(f'El ganador de CV fue {c["ganador_cv"]}, pero ROC-AUC {metric["ROC_AUC"]:.3f} está cerca de 0.5 y su IC95 % [{ci["ROC_AUC"][0]:.3f}, {ci["ROC_AUC"][1]:.3f}] incluye ese valor: no hay evidencia de discriminación útil en esta prueba. AP {metric["PR_AUC_AP"]:.3f} está cerca de la prevalencia positiva {c["prevalencia_test"]:.1%}. Se distingue AP de área PR trapezoidal. El IC95 % de AP, por 200 remuestras de conglomerados, fue [{ci["PR_AUC_AP"][0]:.3f}, {ci["PR_AUC_AP"][1]:.3f}]. Los intervalos no prueban superioridad entre modelos ni representan el diseño completo de encuesta.')
fig('curvas_roc_pr',maxheight=200,caption='Figura 2. ROC y precisión/recall sobre test. No se utilizó test para elegir hiperparámetros o ganador.')
p(f'La matriz, filas reales [sin rezago, con rezago] y columnas predichas en igual orden, fue [[{cm[0][0]}, {cm[0][1]}], [{cm[1][0]}, {cm[1][1]}]]. Hubo {cm[1][0]} falsos negativos y {cm[0][1]} falsos positivos. Los primeros pueden omitir revisión de una necesidad; los segundos incrementan verificaciones. Recall={metric["recall"]:.3f} y precisión={metric["precision"]:.3f}. La curva de calibración y Brier se entregan sin afirmar calibración poblacional: el balance de clases puede desplazar probabilidades.')
p(f'En una sensibilidad con distritos completos separados, el mismo algoritmo obtuvo ROC-AUC {g["ROC_AUC"]:.3f} y AP {g["PR_AUC_AP"]:.3f}. Es un diagnóstico adicional y no una nueva selección. Se adjuntan métricas ponderadas con FACPOB07, tablas por lengua/ruralidad y predicciones con tipo de error; los grupos pequeños requieren cautela.')
page()
head('4 Clustering con frecuencia TIC y años de rezago')
p('Se utilizaron once variables: ingresos/gastos logarítmicos per cápita, ratio alumno/docente, frecuencia TIC, años de rezago, ruralidad, electricidad, internet doméstico, miembros, altitud y proporción pública. P314D se recodificó ordinalmente: 3 diaria, 2 semanal, 1 mensual/menos, y 0 si P314A declara no uso. Los faltantes de usuarios no se confundieron con no uso. K-Means y GMM diagonal se compararon para k=2…6 sobre la misma representación y submuestra fija de hasta 1 800 registros de train.')
best=cl['metricas_train']
p(f'La selección por silueta eligió {cl["ganador"][0]} con k={cl["ganador"][1]}: silueta {best["silhouette"]:.3f}, Davies–Bouldin {best["Davies_Bouldin"]:.3f} y Calinski–Harabasz {best["Calinski_Harabasz"]:.1f}. Se maximiza silueta y se contrasta con los demás índices, no con el resultado de test. Imputación, escalado y PCA se ajustaron solo en train; a test se aplicó predict/transform.')
pair('siluetas','clusters_pca','Figura 3. Silueta por observación de la muestra de train y proyección PCA. La curva de selección k y las diez corridas están en resultados/.')
rows=[['Grupo','n','Rural','Internet','TIC 0–3','Rezago años','No uso']]
for _,r in prof.iterrows():
    rows.append([int(r.cluster),int(r.n),f'{r.rural:.0%}',f'{r.internet_hogar:.0%}',f'{r.frecuencia_tic:.2f}',f'{r.anios_rezago:.2f}',f'{r.no_uso_internet:.0%}'])
table(rows,widths=[45,60,65,75,75,90,80])
p('Los nombres descriptivos, medias de todas las variables y acciones propuestas se entregan por grupo. Se recomienda revisar barreras de acceso para perfiles sin conexión y barreras de uso/acompañamiento cuando existe conexión pero el uso es bajo. Las acciones requieren verificación local; pertenecer a un cluster no prueba una necesidad individual ni autoriza exclusión de apoyos.')
p('La guía pide incluir años de retraso en el perfil: por ello las diferencias de rezago entre clusters son parcialmente definitorias y no validan una predicción independiente. Los clusters no se introducen en el clasificador. La escala ordinal TIC resume frecuencia, no horas de uso; no mide aprendizaje o competencias. Los perfiles se describen en esta muestra sin afirmar proporciones poblacionales.')
page()
head('5 Explicabilidad del modelo ganador')
top=', '.join(str(x) for x in imp.variable.head(5))
p(f'Se explicó {c["ganador_cv"]} en {sh["n_explicados"]} casos de test, con fondo exclusivo de train. Las primeras características fueron {html.escape(top)}. El beeswarm muestra diez características transformadas; cada categoría one-hot se trata separadamente. Las contribuciones están en {sh["unidad"]}, no en puntos porcentuales salvo salida en probabilidad.','SmallBody')
fig('shap_beeswarm',maxheight=175,caption='Figura 4. Diez características con mayor contribución absoluta media. No equivale a causalidad ni a importancia agregada de categorías.')
pair('shap_dependencia_1','shap_dependencia_2','Figura 5. Conexión doméstica coloreada por lengua quechua, y ratio alumno/docente coloreado por ruralidad. Las variables numéricas se restituyen a unidades originales.')
p('Las dependencias permiten observar contribuciones distintas según contexto y no linealidad. El color no calcula valores formales de interacción SHAP ni identifica efectos causales: lengua, geografía y recursos están correlacionados. Hay pocos casos de algunas lenguas en la muestra explicada y la ausencia visual de contraste no demuestra ausencia de efecto.','SmallBody')
pair('shap_caso_alto','shap_caso_bajo','Figura 6. Casos extremos correctamente clasificados: alto rezago a la izquierda y bajo a la derecha. Las cifras junto a las variables son sus valores originales o logaritmos documentados.')
p(f'Las probabilidades de los casos fueron {sh["alto"]["probabilidad"]:.3f} y {sh["bajo"]["probabilidad"]:.3f}, con clases reales 1 y 0. El error máximo de reconstrucción base+suma SHAP fue {sh["error_max_aditividad"]:.6f}. Los waterfall muestran qué contribuciones elevan o reducen la salida respecto al fondo; son ilustraciones seleccionadas por extremos, no casos representativos. Las probabilidades de un ajuste balanceado requieren validación/calibración antes de decisiones individuales.','SmallBody')
page()
head('6 Discusión recomendaciones y conclusiones')
p('Como complemento del sílabo se compararon Ridge y Random Forest Regressor para el índice 0.5×no uso + 0.5×ausencia de conexión doméstica, con los mismos grupos y cinco folds. Se excluyeron ambos componentes de X. Esta escala tiene tres valores (0, 0.5, 1), no se presenta como índice continuo oficial ni como cumplimiento de la Opción B; la clasificación de rezago satisface la opción predictiva elegida.')
table([['Modelo','MAE','RMSE','R²']]+[[r.modelo,f'{r.MAE:.3f}',f'{r.RMSE:.3f}',f'{r.R2:.3f}'] for _,r in reg.iterrows()],widths=[220,90,90,90])
p('<b>Referencia de aplicación.</b> Aprendo en casa ofrece televisión, radio e internet [4]. El contraste inspira tres prácticas: distinguir acceso de uso; ofrecer alternativas fuera de línea; y verificar alertas con docentes antes de asignar intervenciones. No se comparan métricas con ese servicio ni se atribuyen impactos que este análisis no midió. Los perfiles y errores sirven para planear verificaciones y priorizar revisión, no decisiones automáticas de exclusión.')
p('<b>Limitaciones.</b> Se utiliza el corte 2025 de archivos panel sin certificar equivalencia con toda la anual. Los factores anuales no validan por sí solos inferencia del panel. Edad declarada y grado aproximan rezago, con sesgo posible por cumpleaños; no hay nacimiento usable para la referencia al 31 de marzo. Los módulos MINEDU dañados impiden detalles de equipos/conexión escolar. El padrón tiene imputaciones y el contexto distrital no identifica la escuela individual. Separar conglomerados no elimina toda similitud territorial, por lo que se añadió sensibilidad por distrito. Los grupos lingüísticos pequeños, calibración y definición del umbral requieren evaluación externa.')
p(f'<b>Conclusiones.</b> La base es trazable y la comparación agrupada eligió {c["ganador_cv"]} por AP de validación, pero su desempeño no justifica uso predictivo operativo. No debe emplearse para priorizar personas. La contribución es metodológica y descriptiva: documentar datos, perfiles y límites, y mostrar que los predictores disponibles no resuelven este objetivo aproximado. Antes de otro ensayo se requiere una definición temporal de rezago más precisa y datos educativos validados; no añadir edad/grado para inflar métricas. No se infieren efectos causales ni notas inexistentes.')
head('Referencias y reproducción')
p('[1] INEI. Estadísticas TIC, segundo trimestre 2025. https://www.gob.pe/institucion/inei/noticias/1254582-el-60-1-de-los-hogares-tiene-conexion-a-internet<br/>[2] MINEDU. Edades normativas, referencia al 31 de marzo. https://www.gob.pe/institucion/minedu/informes-publicaciones/2742610-edades-normativas<br/>[3] MINEDU ESCALE. Alumnos con atraso escolar, metadatos. https://escale.minedu.gob.pe/tendencias-portlet/servlet/tendencias/archivo?idCuadro=143&amp;tipo=meta<br/>[4] MINEDU. Aprendo en casa. https://www.gob.pe/8858-acceder-a-educacion-a-distancia-aprendo-en-casa<br/>[5] INEI. ENAHO panel 2021–2025 y diccionario, archivos del proyecto; MINEDU, padrón actualizado 29/10/2025 y diccionarios del Censo 2025.<br/>[6] Lundberg y Lee. A Unified Approach to Interpreting Model Predictions. NeurIPS, 2017. https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html<br/>Reproducción: notebooks/01_datos_y_auditoria.ipynb y 02_PROYECTO_COMPLETO.ipynb; src/pipeline.py; requirements.txt; semilla 42. Dataset CSV/Parquet, diccionario, fuentes y experimentos incluidos. Auditoría completa de 34 puntos en AUDITORIA_GUIA_PUNTO_POR_PUNTO.md.','SmallBody')
def footer(canvas,doc):
    canvas.setFont('Times-Roman',8); canvas.drawString(45,25,'Inteligencia Artificial · Unidad 2 · Revisión completa de la guía'); canvas.drawRightString(A4[0]-45,25,str(doc.page))
doc=SimpleDocTemplate(str(R/'informe/Informe_Brecha_Digital_U2.pdf'),pagesize=A4,leftMargin=45,rightMargin=45,topMargin=37,bottomMargin=40,title='Brecha digital y rezago escolar en el Perú',author='Jannys Graciela Navarro')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(R/'informe/Informe_fuente.md').write_text('\n\n'.join(source),encoding='utf-8')
print('Informe revisado generado')
