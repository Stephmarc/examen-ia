"""Construcción de las tablas de trabajo desde los ZIP originales."""
from pathlib import Path
import argparse,json,zipfile
import pandas as pd

RAIZ=Path(__file__).resolve().parents[1]
LLAVE_HOGAR=['CONGLOME','VIVIENDA','HOGAR']
LLAVE_PERSONA=LLAVE_HOGAR+['CODPERSO']
ARCHIVOS={
    'vivienda':('1041-Modulo1474.zip','100-panel.csv',LLAVE_HOGAR+['AÑO','UBIGEO','ESTRATO','P1121','P1144','ALTITUD','FACTOR07']),
    'personas':('1041-Modulo1479.zip','200-panel.csv',LLAVE_PERSONA+['AÑO','UBIGEO','ESTRATO','P208A','P204','P205','P206','P207','FACPOB07']),
    'educacion':('1041-Modulo1475.zip','300-panel.csv',LLAVE_PERSONA+['AÑO','UBIGEO','ESTRATO','P300A','P306','P307','P308A','P308B','P308C','P314A','P314D','FACPOB07','FACTOR07']),
    'sumaria':('1041-Modulo1478.zip','sumaria-2021-2025-panel.csv',LLAVE_HOGAR+['AÑO','POBREZA','MIEPERHO','GASHOG2D','INGHOG2D','FACTOR07'])}

def leer_corte_2025(ruta,sufijo,columnas):
    with zipfile.ZipFile(ruta) as archivo:
        nombre=next(n for n in archivo.namelist() if n.lower().endswith(sufijo))
        with archivo.open(nombre) as f:
            encoding='utf-8-sig' if f.read(3)==b'\xef\xbb\xbf' else 'latin1'
        with archivo.open(nombre) as f:
            encabezado=pd.read_csv(f,encoding=encoding,nrows=0).columns
        seleccion={c:c[:-3].upper().strip() for c in encabezado if c.lower().endswith('_25') and c[:-3].upper().strip() in columnas}
        faltan=set(columnas)-set(seleccion.values())
        if faltan: raise ValueError(f'{ruta.name}: faltan columnas {sorted(faltan)}')
        bloques=[]
        with archivo.open(nombre) as f:
            for bloque in pd.read_csv(f,encoding=encoding,usecols=list(seleccion),dtype='string',chunksize=10000):
                bloque= bloques_normalizados(bloque,seleccion)
                bloques.append(bloque.loc[bloque['AÑO'].eq('2025')])
        return pd.concat(bloques,ignore_index=True)

def bloques_normalizados(bloque,nombres):
    bloque=bloque.rename(columns=nombres)
    for c in bloque: bloque[c]=bloque[c].str.strip().replace('',pd.NA)
    return bloque

def reconstruir(salida=None):
    salida=Path(salida) if salida is not None else RAIZ/'data/processed/reconstruccion'
    salida.mkdir(parents=True,exist_ok=True)
    tablas={}; auditoria=[]
    for nombre,(zip_nombre,sufijo,columnas) in ARCHIVOS.items():
        tabla=leer_corte_2025(RAIZ/'data/raw/INEI'/zip_nombre,sufijo,columnas)
        llave=LLAVE_PERSONA if nombre in ['personas','educacion'] else LLAVE_HOGAR
        if tabla[llave].isna().any(axis=None) or tabla.duplicated(llave).any():
            raise ValueError(f'Llaves incompletas o duplicadas en {nombre}')
        tablas[nombre]=tabla
        tabla.to_csv(salida/f'{nombre}_2025.csv',index=False,encoding='utf-8-sig')
        auditoria.append({'tabla':nombre,'filas':len(tabla),'columnas_usadas':len(tabla.columns),'duplicados':0,'llaves_vacias':0})
        print(f'{nombre}: {len(tabla):,} registros de 2025',flush=True)
    p=tablas['personas']
    p=p.loc[pd.to_numeric(p.P208A,errors='coerce').between(6,17)].copy()
    base=p.merge(tablas['educacion'],on=LLAVE_PERSONA,how='left',validate='one_to_one',suffixes=('','_EDU'),indicator='cruce_educacion')
    base=base.merge(tablas['vivienda'],on=LLAVE_HOGAR,how='left',validate='many_to_one',suffixes=('','_VIV'),indicator='cruce_vivienda')
    base=base.merge(tablas['sumaria'],on=LLAVE_HOGAR,how='left',validate='many_to_one',suffixes=('','_SUM'),indicator='cruce_sumaria')
    base.to_csv(salida/'base_escolar_ENAHO_2025_PRELIMINAR.csv',index=False,encoding='utf-8-sig')
    import pipeline
    anteriores=pipeline.D,pipeline.O,pipeline.F
    try:
        pipeline.D=salida; pipeline.O=salida/'auditoria'; pipeline.F=pipeline.O/'figuras'
        pipeline.F.mkdir(parents=True,exist_ok=True)
        final=pipeline.preparar()
    finally:
        pipeline.D,pipeline.O,pipeline.F=anteriores
    informe={'tablas':auditoria,'filas_antes_limpieza_final':len(base),'filas_finales':len(final),'columnas_finales':len(final.columns),'fuentes':'ZIP originales de data/raw; selección de columnas utilizadas, corte 2025, limpieza y cruces reproducibles.'}
    (salida/'construccion_desde_originales.json').write_text(json.dumps(informe,ensure_ascii=False,indent=2),encoding='utf-8')
    return final,informe

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--salida',type=Path)
    args=parser.parse_args();reconstruir(args.salida)
