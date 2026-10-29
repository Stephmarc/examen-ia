"""Pruebas reproducibles de integridad; no rellena ni elimina observaciones válidas."""
from pathlib import Path
import json, hashlib, sys
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'data/processed'
O = ROOT / 'resultados/auditoria_limpieza'

def auditar():
    O.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(D / 'dataset_enaho_escale_2025.parquet')
    checks = []
    def test(nombre, ok, detalle=''):
        checks.append(dict(prueba=nombre, pasa=bool(ok), detalle=str(detalle)))
    key = ['CONGLOME', 'VIVIENDA', 'HOGAR', 'CODPERSO']
    test('Llaves completas', not df[key].isna().any(axis=None))
    test('Persona única', not df.duplicated(key).any())
    test('Sin filas idénticas', not df.duplicated().any())
    test('UBIGEO de seis dígitos', df.UBIGEO.astype('string').str.fullmatch(r'\d{6}').all())
    test('Sin infinitos', not np.isinf(df.select_dtypes('number').to_numpy()).any())
    for c, lo, hi in [('edad',6,17),('grado_acumulado',1,11),('edad_normativa',6,16),
                      ('altitud',-100,6000),('latitud_media',-19,1),('longitud_media',-82,-68),
                      ('proporcion_publica',0,1),('indice_brecha',0,1),('frecuencia_tic',0,3)]:
        s = df[c].dropna()
        test('Rango: '+c, s.between(lo,hi).all(), f'{s.min()} a {s.max()}')
    for c in ['edad','grado_acumulado','miembros_hogar','n_escuelas','frecuencia_tic']:
        s=df[c].dropna()
        test('Enteros: '+c, np.allclose(s, np.floor(s)))
    for c in ['rural','electricidad','internet_hogar','no_uso_internet','contexto_encontrado','rezago_escolar','rezago_dos_mas']:
        test('Binaria: '+c, df[c].dropna().isin([0,1]).all())
    for c in ['peso_poblacional','peso_hogar_referencia','miembros_hogar','n_escuelas']:
        test('Positiva: '+c, df[c].dropna().gt(0).all())
    for c in ['gasto_pc_mensual','ingreso_pc_mensual','ratio_alumno_docente','anios_rezago']:
        test('No negativa: '+c, df[c].dropna().ge(0).all())
    for c, allowed in [('sexo',['hombre','mujer']),('pobreza',['extrema','no_extrema','no_pobre']),
                       ('lengua_materna',['quechua','aimara','castellano','otra_originaria','otra_o_no_declarada'])]:
        test('Categorías: '+c, df[c].dropna().isin(allowed).all())
    for c in ['gasto_pc_mensual','ingreso_pc_mensual']:
        test('Fórmula log: '+c, np.allclose(df['log_'+c], np.log1p(df[c]),equal_nan=True))
    test('Fórmula edad normativa', np.allclose(df.edad_normativa,df.grado_acumulado+5))
    lag=(df.edad-df.grado_acumulado-5).clip(lower=0)
    test('Fórmula años de rezago', np.allclose(df.anios_rezago,lag))
    test('Objetivo principal', df.rezago_escolar.eq((lag>0).astype(int)).all())
    test('Umbral alternativo', df.rezago_dos_mas.eq((lag>=2).astype(int)).all())
    test('Fórmula índice', np.allclose(df.indice_brecha,.5*df.no_uso_internet+.5*(1-df.internet_hogar),equal_nan=True))
    test('Frecuencia cero si no usa', df.loc[df.no_uso_internet.eq(1),'frecuencia_tic'].eq(0).all())
    test('Frecuencia de usuarios', df.loc[df.no_uso_internet.eq(0),'frecuencia_tic'].dropna().isin([1,2,3]).all())
    csv=pd.read_csv(D/'dataset_enaho_escale_2025.csv',dtype={c:'string' for c in key+['UBIGEO']})
    try:
        pd.testing.assert_frame_equal(df,csv,check_dtype=False,check_exact=False,rtol=1e-12,atol=1e-12)
        equal=True
    except AssertionError: equal=False
    test('CSV y Parquet equivalentes',equal)
    dic=pd.read_csv(D/'diccionario_variables.csv')
    test('Diccionario completo sin duplicados',set(dic.variable)==set(df.columns) and not dic.variable.duplicated().any())
    context=pd.read_csv(D/'contexto_escolar_distrito_area.csv',dtype={'UBIGEO':'string','area_minedu':'string'})
    test('Contexto único por distrito y área',not context.duplicated(['UBIGEO','area_minedu']).any())
    q=df.assign(area_minedu=np.where(df.rural.eq(1),'2','1')).merge(context,on=['UBIGEO','area_minedu'],how='left',suffixes=('','_fuente'),validate='many_to_one',indicator=True)
    test('Indicador de cruce correcto',q.contexto_encontrado.eq(q._merge.eq('both').astype(int)).all())
    for c in ['n_escuelas','ratio_alumno_docente','proporcion_publica','latitud_media','longitud_media']:
        test('Cruce contextual: '+c,np.allclose(q[c],q[c+'_fuente'],equal_nan=True))
    part=pd.read_csv(ROOT/'resultados/particiones.csv',dtype={'CONGLOME':'string'})
    test('Particiones cubren cada fila una vez',len(part)==len(df) and not part.fila.duplicated().any() and set(part.fila)==set(range(len(df))))
    part=part.sort_values('fila')
    test('Particiones alineadas con personas',np.array_equal(part.CONGLOME.astype(str),df.CONGLOME.astype(str)))
    test('Particiones válidas',set(part.particion)=={'train','test'})
    train=part.particion.eq('train').to_numpy(); groups=df.CONGLOME.to_numpy()
    test('Sin conglomerados compartidos train/test',not set(groups[train])&set(groups[~train]))
    for fold,(a,b) in enumerate(GroupKFold(5).split(df.loc[train],groups=groups[train]),1):
        test(f'Sin conglomerados compartidos fold {fold}',not set(groups[train][a])&set(groups[train][b]))
    import pipeline
    forbidden=set(key+['UBIGEO','edad','grado_acumulado','edad_normativa','anios_rezago','rezago_escolar','rezago_dos_mas','peso_poblacional','peso_hogar_referencia'])
    test('Predictores sin llaves, pesos ni componentes del objetivo',not forbidden&set(pipeline.NUM+pipeline.CAT))
    missing=df.isna().sum().rename('n_faltantes').to_frame()
    missing['porcentaje']=100*missing.n_faltantes/len(df)
    missing.to_csv(O/'faltantes_por_variable.csv',encoding='utf-8-sig')
    desc=df.select_dtypes('number').describe(percentiles=[.01,.25,.5,.75,.99]).T
    desc.to_csv(O/'distribuciones.csv',encoding='utf-8-sig')
    alerts=[]
    for c in ['gasto_pc_mensual','ingreso_pc_mensual','miembros_hogar','ratio_alumno_docente']:
        s=df[c]; q1,q3=s.quantile([.25,.75]); mask=(s<q1-3*(q3-q1))|(s>q3+3*(q3-q1))
        alerts.append({'variable':c,'registros_fuera_3IQR':int(mask.sum()),'accion':'Conservar: extremo estadístico no demuestra error; revisar en fuente si se excluye.'})
    pd.DataFrame(alerts).to_csv(O/'extremos_para_revision.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(checks).to_csv(O/'pruebas.csv',index=False,encoding='utf-8-sig')
    summary={'filas':len(df),'columnas':len(df.columns),'pruebas':len(checks),'aprobadas':sum(c['pasa'] for c in checks),
             'fallos':[c for c in checks if not c['pasa']], 'sin_contexto_minedu':int(df.contexto_encontrado.eq(0).sum()),
             'sha256_parquet':hashlib.sha256((D/'dataset_enaho_escale_2025.parquet').read_bytes()).hexdigest(),
             'nota':'Los faltantes se conservan; el pipeline los imputa dentro de cada entrenamiento. Las pruebas no certifican la exactitud de las respuestas originales ni resuelven limitaciones del panel o edad normativa.'}
    (O/'resumen.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return summary

if __name__=='__main__':
    result=auditar()
    sys.exit(bool(result['fallos']))
