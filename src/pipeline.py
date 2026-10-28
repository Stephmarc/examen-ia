"""Proyecto reproducible. Ejecutar desde la raíz: python src/pipeline.py."""
from pathlib import Path
import json, os, time, warnings, zipfile, struct
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, ParameterGrid
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, RandomForestRegressor
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.metrics import (roc_auc_score, average_precision_score, f1_score,
 accuracy_score, precision_score, recall_score, confusion_matrix,
 ConfusionMatrixDisplay, RocCurveDisplay, PrecisionRecallDisplay,
 silhouette_score, silhouette_samples, davies_bouldin_score,
 calinski_harabasz_score, mean_absolute_error, mean_squared_error, r2_score,
 brier_score_loss, precision_recall_curve, auc)
from sklearn.calibration import calibration_curve
from sklearn.utils.class_weight import compute_sample_weight
import joblib

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data/processed'; O=ROOT/'resultados'; F=O/'figuras'
for p in [D,O,F]: p.mkdir(parents=True,exist_ok=True)
SEED=42
plt.rcParams.update({'figure.dpi':120,'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
def savefig(name):
    plt.tight_layout(); plt.savefig(F/f'{name}.png',dpi=180,bbox_inches='tight'); plt.close()
def dump(name,obj):
    (O/f'{name}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)),encoding='utf-8')
def read(name):
    return pd.read_csv(D/name,dtype='string',encoding='utf-8-sig')

def leer_dbf_zip(path,member,keep):
    # Leer los campos utilizados en el análisis.
    with zipfile.ZipFile(path) as z, z.open(member) as f:
        h=f.read(32); n,hl,rl=struct.unpack('<IHH',h[4:12]); fields=[]; off=1
        for _ in range((hl-33)//32):
            x=f.read(32); key=x[:11].split(b'\0')[0].decode(); ln=x[16]
            if key in keep: fields.append((key,off,ln))
            off+=ln
        f.read(hl-32-32*((hl-33)//32)); rows=[]
        for _ in range(n):
            r=f.read(rl)
            if r[:1]!=b'*': rows.append({k:r[o:o+l].decode('cp1252',errors='replace').strip() for k,o,l in fields})
    return pd.DataFrame(rows)

def preparar():
    print('ETAPA 1 Limpieza e integración',flush=True)
    b=read('base_escolar_ENAHO_2025_PRELIMINAR.csv')
    steps=[{'filtro':'Base 6 a 17 años','n':len(b)}]
    # Residente habitual: miembro no ausente >=30 días, o no miembro presente >=30 días.
    resident=((b.P204=='1')&(b.P205=='2'))|((b.P204=='2')&(b.P206=='1'))
    b=b.loc[resident.fillna(False)].copy(); steps.append({'filtro':'Residentes habituales','n':len(b)})
    b=b.loc[(b.P306=='1') & b.P308A.isin(['2','3'])].copy()
    steps.append({'filtro':'Matriculados primaria o secundaria','n':len(b)})
    b=b.loc[b.P314A.isin(['1','2'])].copy()
    steps.append({'filtro':'Respuesta válida sobre uso de internet','n':len(b)})
    source=ROOT/'data/raw/MINEDU'
    keep={'COD_MOD','ANEXO','CODLOCAL','D_NIV_MOD','GESTION','AREA_CENSO','CODGEO','NLAT_IE','NLONG_IE','ESTADO','TALUM','TDOC','FECHA_ACT','IMPUTADO'}
    pad=leer_dbf_zip(source/'00_Padron.zip','Padron.dbf',keep)
    dates=pad.FECHA_ACT.value_counts().to_dict()
    dump('metadatos_padron',{'fechas_actualizacion':dates,'filas':len(pad),'gestion':pad.GESTION.value_counts().to_dict(),'area':pad.AREA_CENSO.value_counts().to_dict(),'imputado':pad.IMPUTADO.value_counts().to_dict()})
    # Seleccionar primaria y secundaria regular.
    pad=pad.loc[(pad.ESTADO=='1') & pad.D_NIV_MOD.isin(['Primaria','Secundaria']) & pad.CODGEO.str.fullmatch(r'\d{6}')].copy()
    if pad.duplicated(['COD_MOD','ANEXO']).any(): raise ValueError('Servicios educativos duplicados')
    for c in ['TALUM','TDOC','NLAT_IE','NLONG_IE']: pad[c]=pd.to_numeric(pad[c],errors='coerce')
    for c in ['TALUM','TDOC']: pad.loc[pad[c]<0,c]=np.nan
    pad.loc[~pad.NLAT_IE.between(-19,1),'NLAT_IE']=np.nan
    pad.loc[~pad.NLONG_IE.between(-82,-68),'NLONG_IE']=np.nan
    pad['publica']=pad.GESTION.map({'1':1.,'2':1.,'3':0.})
    context=pad.groupby(['CODGEO','AREA_CENSO']).agg(
        n_escuelas=('COD_MOD','size'),alumnos=('TALUM',lambda x:x.sum(min_count=1)),
        docentes=('TDOC',lambda x:x.sum(min_count=1)),proporcion_publica=('publica','mean'),
        latitud_media=('NLAT_IE','mean'),longitud_media=('NLONG_IE','mean')).reset_index()
    context['ratio_alumno_docente']=context.alumnos/context.docentes.where(context.docentes>0)
    context.rename(columns={'CODGEO':'UBIGEO','AREA_CENSO':'area_minedu'},inplace=True)
    b['area_minedu']=np.where(pd.to_numeric(b.ESTRATO,errors='coerce')>=6,'2','1')
    b=b.merge(context,on=['UBIGEO','area_minedu'],how='left',validate='many_to_one',indicator='cruce_minedu')
    context.to_csv(D/'contexto_escolar_distrito_area.csv',index=False,encoding='utf-8-sig')
    # Coordenadas medias del contexto escolar.
    def num(c): return pd.to_numeric(b[c],errors='coerce').astype(float)
    out=b[['CONGLOME','VIVIENDA','HOGAR','CODPERSO','UBIGEO']].copy()
    out['edad']=num('P208A'); out['sexo']=b.P207.map({'1':'hombre','2':'mujer'})
    lang=num('P300A')
    out['lengua_materna']=np.select([lang.eq(1),lang.eq(2),lang.eq(4),lang.isin([3,10,11,12,13,14,15,16,17])],['quechua','aimara','castellano','otra_originaria'],default='otra_o_no_declarada')
    out['rural']=(num('ESTRATO')>=6).astype(float)
    out['electricidad']=num('P1121').where(num('P1121').isin([0,1]))
    out['internet_hogar']=num('P1144').where(num('P1144').isin([0,1]))
    out['pobreza']=b.POBREZA.map({'1':'extrema','2':'no_extrema','3':'no_pobre'})
    out['miembros_hogar']=num('MIEPERHO').where(num('MIEPERHO')>0)
    for col,orig in [('gasto_pc_mensual','GASHOG2D'),('ingreso_pc_mensual','INGHOG2D')]:
        vals=num(orig)/out.miembros_hogar/12
        out[col]=vals.where(vals>=0)
        out['log_'+col]=np.log1p(out[col])
    out['altitud']=num('ALTITUD').where(num('ALTITUD').between(-100,6000))
    for c in ['n_escuelas','ratio_alumno_docente','proporcion_publica','latitud_media','longitud_media']:
        out[c]=pd.to_numeric(b[c],errors='coerce')
    out['peso_poblacional']=num('FACPOB07').where(num('FACPOB07')>0)
    out['peso_hogar_referencia']=num('FACTOR07_SUM').where(num('FACTOR07_SUM')>0)
    out['no_uso_internet']=(b.P314A=='2').astype(int)
    # Primaria: P308C grado 1..6. Secundaria: P308B año 1..5.
    nivel=num('P308A'); grado_prim=num('P308C'); anio_sec=num('P308B')
    grado=np.where((nivel==2)&grado_prim.between(1,6),grado_prim,
                   np.where((nivel==3)&anio_sec.between(1,5),anio_sec+6,np.nan))
    out['grado_acumulado']=grado
    out['edad_normativa']=out.grado_acumulado+5
    out['anios_rezago']=(out.edad-out.edad_normativa).clip(lower=0)
    out['rezago_escolar']=(out.anios_rezago>0).astype(int)
    out['rezago_dos_mas']=(out.anios_rezago>=2).astype(int)
    # Frecuencia ordinal: 0 no usa, 1 mensual/menos, 2 semanal, 3 diaria.
    frecuencia=num('P314D').map({1:3.,2:2.,3:1.,4:1.})
    out['frecuencia_tic']=frecuencia.where(b.P314A.eq('1'),0.)
    out['indice_brecha']=0.5*out.no_uso_internet+0.5*(1-out.internet_hogar)
    # Conservar base amplia para auditoría antes de exigir grado válido.
    out.to_csv(D/'base_escolares_antes_validar_grado.csv',index=False,encoding='utf-8-sig')
    valido=out.grado_acumulado.notna()
    steps.append({'filtro':'Grado actual válido para definir rezago','n':int(valido.sum())})
    out=out.loc[valido].copy()
    out['contexto_encontrado']=(b.cruce_minedu=='both').astype(int)
    out=out.reset_index(drop=True)
    assert not out.duplicated(['CONGLOME','VIVIENDA','HOGAR','CODPERSO']).any()
    assert out.UBIGEO.str.len().eq(6).all()
    out.to_csv(D/'dataset_enaho_escale_2025.csv',index=False,encoding='utf-8-sig')
    out.to_parquet(D/'dataset_enaho_escale_2025.parquet',index=False)
    pd.DataFrame(steps).to_csv(O/'flujo_limpieza.csv',index=False)
    out.isna().mean().rename('fraccion_faltante').to_csv(O/'faltantes.csv')
    report={'filas':len(out),'conglomerados':out.CONGLOME.nunique(),'distritos':out.UBIGEO.nunique(),
      'no_uso':int(out.no_uso_internet.sum()),'prevalencia':out.rezago_escolar.mean(),'con_rezago':int(out.rezago_escolar.sum()),'criterio_rezago':'Edad declarada > grado acumulado + 5; aproximación sin fecha de nacimiento al 31 de marzo; sensibilidad >=2 años disponible.',
      'cobertura_minedu':out.contexto_encontrado.mean(),'pesos_validos':int(out.peso_poblacional.notna().sum()),
      'fechas_padron':dates,'flujo':steps}
    dump('auditoria_final',report); print(report,flush=True)
    return out

NUM=['rural','electricidad','internet_hogar','miembros_hogar','log_gasto_pc_mensual','log_ingreso_pc_mensual','altitud','ratio_alumno_docente','proporcion_publica','latitud_media','longitud_media','n_escuelas']
CAT=['sexo','lengua_materna','pobreza']
def preprocessor(num=NUM,cat=CAT):
    return ColumnTransformer([
        ('numericas',Pipeline([('imputar',SimpleImputer(strategy='median',keep_empty_features=True)),('escalar',StandardScaler())]),num),
        ('categoricas',Pipeline([('imputar',SimpleImputer(strategy='most_frequent')),('codificar',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cat)],verbose_feature_names_out=False)
def metricas(y,p,w=None):
    pred=(p>=0.5).astype(int); pr,re,_=precision_recall_curve(y,p,sample_weight=w)
    return {'ROC_AUC':roc_auc_score(y,p,sample_weight=w),'PR_AUC_AP':average_precision_score(y,p,sample_weight=w),
     'PR_AUC_trapecios':auc(re,pr),'F1_macro':f1_score(y,pred,average='macro',sample_weight=w),
     'accuracy':accuracy_score(y,pred,sample_weight=w),'precision':precision_score(y,pred,sample_weight=w,zero_division=0),
     'recall':recall_score(y,pred,sample_weight=w),'Brier':brier_score_loss(y,p,sample_weight=w)}

def clasificar(df):
    print('ETAPA 2 Clasificación y validación agrupada',flush=True)
    assert not set(NUM+CAT)&{'edad','grado_acumulado','edad_normativa','anios_rezago','rezago_escolar','rezago_dos_mas'}
    X=df[NUM+CAT].copy(); y=df.rezago_escolar.to_numpy(); groups=df.CONGLOME.to_numpy()
    tr,te=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=SEED).split(X,y,groups))
    assert not set(groups[tr])&set(groups[te])
    pd.DataFrame({'fila':np.arange(len(df)),'particion':np.where(np.isin(np.arange(len(df)),te),'test','train'),'CONGLOME':groups}).to_csv(O/'particiones.csv',index=False)
    cv=list(GroupKFold(n_splits=5).split(X.iloc[tr],y[tr],groups[tr]))
    for a,b in cv: assert not set(groups[tr][a])&set(groups[tr][b])
    configs={
      'Logistica':(LogisticRegression(max_iter=1500,random_state=SEED),{'C':[.1,1.]}),
      'RandomForest':(RandomForestClassifier(n_estimators=120,n_jobs=2,random_state=SEED,max_features='sqrt'),{'min_samples_leaf':[5,15],'max_depth':[12]}),
      'LightGBM':(LGBMClassifier(n_estimators=160,learning_rate=.05,n_jobs=2,random_state=SEED,verbosity=-1),{'num_leaves':[7,15]}),
      'MLP':(MLPClassifier(max_iter=180,early_stopping=False,batch_size=256,tol=1e-3,random_state=SEED),{'hidden_layer_sizes':[(32,16),(64,32)],'alpha':[.01]}),
      'XGBoost':(XGBClassifier(n_estimators=160,max_depth=3,learning_rate=.05,subsample=.9,colsample_bytree=.9,n_jobs=2,random_state=SEED,eval_metric='logloss'),{'max_depth':[3,5]})}
    rows=[]; chosen={}; fitted={}; summaries=[]
    for name,(base,grid) in configs.items():
        best=-np.inf; params_best=None
        for params in ParameterGrid(grid):
            foldrows=[]
            for fold,(a,b) in enumerate(cv,1):
                ia=tr[a]; ib=tr[b]
                pipe=Pipeline([('preparar',preprocessor()),('modelo',clone(base).set_params(**params))])
                # Equilibrio de clases se estima exclusivamente en el fold de entrenamiento.
                weights=compute_sample_weight('balanced',y[ia])
                pipe.fit(X.iloc[ia],y[ia],modelo__sample_weight=weights)
                met=metricas(y[ib],pipe.predict_proba(X.iloc[ib])[:,1])
                record={'modelo':name,'parametros':json.dumps(params),'fold':fold,**met}
                rows.append(record); foldrows.append(record)
            score=np.mean([r['PR_AUC_AP'] for r in foldrows])
            if score>best: best=score; params_best=params
        chosen[name]=params_best
        part=pd.DataFrame(rows); part=part.loc[(part.modelo==name)&(part.parametros==json.dumps(params_best))]
        summaries.append({'modelo':name,'parametros':json.dumps(params_best),**{f'CV_{c}':part[c].mean() for c in ['ROC_AUC','PR_AUC_AP','F1_macro','Brier']},'CV_AP_std':part.PR_AUC_AP.std()})
        fitted[name]=Pipeline([('preparar',preprocessor()),('modelo',clone(base).set_params(**params_best))])
        fitted[name].fit(X.iloc[tr],y[tr],modelo__sample_weight=compute_sample_weight('balanced',y[tr]))
        print(name,'AP CV',round(best,4),params_best,flush=True)
    cvsummary=pd.DataFrame(summaries).sort_values('CV_PR_AUC_AP',ascending=False)
    winner=str(cvsummary.iloc[0].modelo)
    # Ganador fijado por CV; test queda reservado para evaluación final de todos los modelos.
    tests=[]; weighted=[]
    for name,pipe in fitted.items():
        prob=pipe.predict_proba(X.iloc[te])[:,1]
        tests.append({'modelo':name,**metricas(y[te],prob)})
        w=df.peso_poblacional.iloc[te].to_numpy(float); ok=np.isfinite(w)&(w>0)
        weighted.append({'modelo':name,**metricas(y[te][ok],prob[ok],w[ok])})
    pd.DataFrame(rows).to_csv(O/'clasificacion_corridas_cv.csv',index=False)
    cvsummary.to_csv(O/'clasificacion_seleccion_cv.csv',index=False)
    pd.DataFrame(tests).to_csv(O/'clasificacion_test.csv',index=False)
    pd.DataFrame(weighted).to_csv(O/'clasificacion_test_ponderado_sensibilidad.csv',index=False)
    bestpipe=fitted[winner]; prob=bestpipe.predict_proba(X.iloc[te])[:,1]; pred=(prob>=.5).astype(int)
    cm=confusion_matrix(y[te],pred)
    ConfusionMatrixDisplay(cm,display_labels=['Sin rezago','Con rezago']).plot(cmap='Blues',colorbar=False)
    plt.title(f'Matriz de confusión - {winner}'); savefig('matriz_confusion')
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for name,pipe in fitted.items():
        p=pipe.predict_proba(X.iloc[te])[:,1]
        RocCurveDisplay.from_predictions(y[te],p,name=name,ax=axes[0])
        PrecisionRecallDisplay.from_predictions(y[te],p,name=name,ax=axes[1])
    axes[0].set_title('ROC - prueba aislada'); axes[1].set_title('Precisión y recall - prueba aislada'); savefig('curvas_roc_pr')
    plt.figure(figsize=(6,4)); plt.plot([0,1],[0,1],'--',color='gray')
    for name,pipe in fitted.items():
        p=pipe.predict_proba(X.iloc[te])[:,1]; a,b=calibration_curve(y[te],p,n_bins=8,strategy='quantile'); plt.plot(b,a,'o-',label=name)
    plt.xlabel('Probabilidad media predicha'); plt.ylabel('Frecuencia observada'); plt.legend(fontsize=8); savefig('calibracion')
    # Sensibilidad: mismo ganador, mismos hiperparámetros, separación por distrito.
    dt,dv=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=SEED).split(X,y,df.UBIGEO))
    geo=clone(bestpipe).fit(X.iloc[dt],y[dt],modelo__sample_weight=compute_sample_weight('balanced',y[dt]))
    geomet=metricas(y[dv],geo.predict_proba(X.iloc[dv])[:,1])
    errors=df.iloc[te][['CONGLOME','UBIGEO','edad','rural','lengua_materna','rezago_escolar']].copy()
    errors['probabilidad']=prob; errors['prediccion']=pred
    errors['tipo_error']=np.select([(y[te]==0)&(pred==1),(y[te]==1)&(pred==0)],['falso_positivo','falso_negativo'],default='correcto')
    errors.to_csv(O/'predicciones_y_errores.csv',index=False,encoding='utf-8-sig')
    subgroup=[]
    for c in ['rural','lengua_materna']:
        for val,sub in errors.groupby(c):
            subgroup.append({'variable':c,'grupo':val,'n':len(sub),'tasa_rezago':sub.rezago_escolar.mean(),'recall':recall_score(sub.rezago_escolar,sub.prediccion,zero_division=0),'F1_macro':f1_score(sub.rezago_escolar,sub.prediccion,average='macro',zero_division=0)})
    pd.DataFrame(subgroup).to_csv(O/'auditoria_subgrupos.csv',index=False,encoding='utf-8-sig')
    joblib.dump(bestpipe,O/'modelo_ganador.joblib')
    # Bootstrap por conglomerado, conservando juntos a sus miembros.
    rng=np.random.default_rng(SEED); ids=np.unique(groups[te]); boots=[]
    for _ in range(200):
        sample=np.concatenate([np.flatnonzero(groups[te]==g) for g in rng.choice(ids,len(ids),replace=True)])
        if len(np.unique(y[te][sample]))==2:
            met=metricas(y[te][sample],prob[sample]); boots.append([met['ROC_AUC'],met['PR_AUC_AP'],met['F1_macro']])
    intervals={c:np.quantile(np.array(boots)[:,j],[.025,.975]).tolist() for j,c in enumerate(['ROC_AUC','PR_AUC_AP','F1_macro'])}
    summary={'ganador_cv':winner,'n_train':len(tr),'n_test':len(te),'grupos_train':len(set(groups[tr])),'grupos_test':len(set(groups[te])),
      'interseccion_grupos':0,'prevalencia_test':float(y[te].mean()),'matriz_confusion':cm.tolist(),
      'test_ganador':next(t for t in tests if t['modelo']==winner),'IC95_bootstrap_grupos':intervals,'sensibilidad_separacion_distrito':geomet,
      'umbral':.5,'ponderacion':'Entrenamiento: balance de clases del fold; sensibilidad de evaluación con FACPOB07. FACTOR07 de hogar se conserva, no se usa como predictor. No se afirman totales nacionales del panel.'}
    summary['objetivo']='rezago_escolar: edad declarada superior a normativa aproximada de grado'
    summary['variables_excluidas_por_fuga']=['edad','grado_acumulado','edad_normativa','anios_rezago','rezago_dos_mas']
    dump('resumen_clasificacion',summary)
    return X,y,tr,te,bestpipe,winner

def clustering(df,tr,te):
    print('ETAPA 3 Clustering',flush=True)
    cols=['frecuencia_tic','anios_rezago','rural','electricidad','internet_hogar','log_gasto_pc_mensual','log_ingreso_pc_mensual','miembros_hogar','altitud','ratio_alumno_docente','proporcion_publica']
    prep=Pipeline([('imputar',SimpleImputer(strategy='median',keep_empty_features=True)),('escalar',StandardScaler())])
    A=prep.fit_transform(df.iloc[tr][cols]); B=prep.transform(df.iloc[te][cols])
    rng=np.random.default_rng(SEED); ids=rng.choice(len(A),min(1800,len(A)),replace=False); rows=[]; models={}
    for algo in ['KMeans','GMM']:
        for k in [2,3,4,5,6]:
            model=(KMeans(n_clusters=k,n_init=10,random_state=SEED) if algo=='KMeans' else GaussianMixture(n_components=k,covariance_type='diag',n_init=2,random_state=SEED,reg_covar=1e-4))
            labels=model.fit_predict(A); sub=labels[ids]
            met={'algoritmo':algo,'k':k,'silhouette':silhouette_score(A[ids],sub),'Davies_Bouldin':davies_bouldin_score(A[ids],sub),'Calinski_Harabasz':calinski_harabasz_score(A[ids],sub)}
            rows.append(met); models[(algo,k)]=model
    scores=pd.DataFrame(rows).sort_values(['silhouette','Davies_Bouldin'],ascending=[False,True]); scores.to_csv(O/'clustering_comparacion.csv',index=False)
    row=scores.iloc[0]; key=(row.algoritmo,int(row.k)); model=models[key]
    labels=np.empty(len(df),dtype=int); labels[tr]=model.predict(A); labels[te]=model.predict(B)
    profiles=df[cols+['no_uso_internet','rezago_escolar']].copy(); profiles['cluster']=labels
    profile=profiles.groupby('cluster').mean(); profile['n']=profiles.groupby('cluster').size()
    names=[]
    for i,r in profile.iterrows():
        area='Rural' if r.rural>=.5 else 'Urbano'
        connect='conectividad doméstica alta' if r.internet_hogar>=.75 else 'conectividad doméstica limitada'
        names.append(f'{area}, {connect}, log del gasto medio {r.log_gasto_pc_mensual:.2f}')
    profile['perfil_descriptivo']=names
    profile['accion_propuesta']=np.where(profile.internet_hogar<.5,'Verificar acceso y ofrecer alternativas fuera de línea',np.where(profile.frecuencia_tic<2,'Revisar barreras de uso efectivo y acompañamiento','Revisar necesidades pedagógicas y casos de rezago'))
    profile.to_csv(O/'perfiles_clusters.csv',encoding='utf-8-sig')
    pd.DataFrame({'fila':np.arange(len(df)),'cluster':labels}).to_csv(O/'asignacion_clusters.csv',index=False)
    fig,ax=plt.subplots(figsize=(7,4))
    for algo,sub in pd.DataFrame(rows).groupby('algoritmo'): ax.plot(sub.k,sub.silhouette,'o-',label=algo)
    ax.set_xlabel('Número de grupos'); ax.set_ylabel('Silueta (misma submuestra de train)'); ax.legend(); savefig('seleccion_clusters')
    pca=PCA(n_components=2,random_state=SEED).fit(A)
    proj=pca.transform(np.vstack([A,B])); all_labels=np.r_[labels[tr],labels[te]]
    plt.figure(figsize=(7,4)); plt.scatter(proj[:,0],proj[:,1],c=all_labels,s=5,cmap='tab10',alpha=.35)
    plt.xlabel('Componente principal 1'); plt.ylabel('Componente principal 2'); plt.title(f'{key[0]} k={key[1]} - PCA'); savefig('clusters_pca')
    samplelabels=model.predict(A[ids]); sil=silhouette_samples(A[ids],samplelabels)
    fig,ax=plt.subplots(figsize=(7,4)); low=10
    for cl in sorted(np.unique(samplelabels)):
        vals=np.sort(sil[samplelabels==cl]); upper=low+len(vals); ax.fill_betweenx(np.arange(low,upper),0,vals,alpha=.7); ax.text(-.08,(low+upper)/2,str(cl)); low=upper+10
    ax.axvline(sil.mean(),color='red',linestyle='--'); ax.set_xlabel('Coeficiente de silueta'); ax.set_yticks([]); savefig('siluetas')
    dump('resumen_clustering',{'ganador':key,'metricas_train':row.to_dict(),'PCA_varianza':pca.explained_variance_ratio_.tolist(),'seleccion':'Silueta máxima sobre train; muestra fija 1800. Test solo se asigna con predict, no selecciona k.','nota':'El rezago se incluye como variable de perfil según la guía; sus diferencias entre clusters son parcialmente definitorias, no una validación predictiva. Los clusters no son predictores de clasificación.'})

def regresion(df,tr,te):
    print('ETAPA 4 Regresión complementaria del índice',flush=True)
    # El objetivo incluye uso personal y acceso doméstico: excluir ambos componentes y todos sus derivados.
    nums=[c for c in NUM if c!='internet_hogar']; cols=nums+CAT
    valid=df.indice_brecha.notna().to_numpy(); a=tr[valid[tr]]; b=te[valid[te]]
    y=df.indice_brecha.to_numpy(float); X=df[cols]
    rows=[]; fitted={}; grids={'Ridge':(Ridge(),{'alpha':[1.,10.]}),'RandomForestRegressor':(RandomForestRegressor(n_estimators=120,n_jobs=2,random_state=SEED,max_depth=12),{'min_samples_leaf':[5,15]})}
    cv=list(GroupKFold(n_splits=5).split(X.iloc[a],y[a],df.CONGLOME.iloc[a]))
    for name,(model,grid) in grids.items():
        best=np.inf; chosen=None
        for par in ParameterGrid(grid):
            scores=[]
            for fold,(i,j) in enumerate(cv,1):
                pipe=Pipeline([('preparar',preprocessor(nums)),('modelo',clone(model).set_params(**par))])
                pipe.fit(X.iloc[a[i]],y[a[i]]); p=pipe.predict(X.iloc[a[j]])
                rmse=float(np.sqrt(mean_squared_error(y[a[j]],p))); scores.append(rmse)
                rows.append({'modelo':name,'parametros':json.dumps(par),'fold':fold,'MAE':mean_absolute_error(y[a[j]],p),'RMSE':rmse,'R2':r2_score(y[a[j]],p)})
            if np.mean(scores)<best: best=np.mean(scores); chosen=par
        pipe=Pipeline([('preparar',preprocessor(nums)),('modelo',clone(model).set_params(**chosen))]).fit(X.iloc[a],y[a])
        fitted[name]=pipe
    tests=[]
    for name,pipe in fitted.items():
        p=pipe.predict(X.iloc[b]); tests.append({'modelo':name,'MAE':mean_absolute_error(y[b],p),'RMSE':float(np.sqrt(mean_squared_error(y[b],p))),'R2':r2_score(y[b],p)})
    pd.DataFrame(rows).to_csv(O/'regresion_corridas_cv.csv',index=False); pd.DataFrame(tests).to_csv(O/'regresion_test.csv',index=False)
    # Revisar residuos del modelo de regresión.
    p=fitted['RandomForestRegressor'].predict(X.iloc[b]); plt.figure(figsize=(6,4)); plt.scatter(p,y[b]-p,s=6,alpha=.2); plt.axhline(0,color='red'); plt.xlabel('Índice predicho'); plt.ylabel('Residuo observado menos predicho'); savefig('residuos_regresion')
    dump('resumen_regresion',{'objetivo':'Índice operativo 0.5*(no uso internet)+0.5*(sin internet doméstico). Valores 0, 0.5 y 1; escala acotada, no índice oficial ni capacidad digital observada.','predictores_excluidos':['internet_hogar','P314A y derivados','indice_brecha','no_uso_internet'],'n_test':len(b),'nota':'Se añade para cubrir regresión del sílabo; clasificación es el problema principal de la guía. El diseño transversal estima asociación, no pronóstico temporal.'})

def explicar(df,X,y,tr,te,pipe,winner):
    print('ETAPA 5 SHAP',flush=True)
    import shap
    prep=pipe.named_steps['preparar']; model=pipe.named_steps['modelo']
    A=prep.transform(X.iloc[tr]); B=prep.transform(X.iloc[te]); names=list(prep.get_feature_names_out())
    rng=np.random.default_rng(SEED)
    sample=rng.choice(len(B),min(400,len(B)),replace=False)
    prob=pipe.predict_proba(X.iloc[te])[:,1]
    high=np.flatnonzero((y[te]==1)&(prob>=.5)); low=np.flatnonzero((y[te]==0)&(prob<.5))
    if not len(high) or not len(low): raise ValueError('No hay ejemplos correctamente clasificados de ambas clases')
    hi=high[np.argmax(prob[high])]; lo=low[np.argmin(prob[low])]
    sample=np.unique(np.r_[sample,hi,lo]); background=A[rng.choice(len(A),min(100,len(A)),replace=False)]
    if winner=='Logistica':
        explainer=shap.LinearExplainer(model,background); ex=explainer(B[sample])
    elif winner=='MLP':
        explainer=shap.Explainer(lambda v:model.predict_proba(v)[:,1],background[:40],algorithm='permutation',seed=SEED)
        ex=explainer(B[sample],max_evals=2*B.shape[1]+1)
    else:
        explainer=shap.TreeExplainer(model,data=background,feature_perturbation='interventional',model_output='raw')
        ex=explainer(B[sample],check_additivity=False)
    vals=ex.values; bases=ex.base_values
    if vals.ndim==3: vals=vals[:,:,1]; bases=bases[:,1]
    exp=shap.Explanation(values=vals,base_values=bases,data=B[sample],feature_names=names)
    plt.figure(); shap.plots.beeswarm(exp,max_display=10,show=False,group_remaining_features=False); savefig('shap_beeswarm')
    importance=pd.DataFrame({'variable':names,'SHAP_abs_medio':np.abs(vals).mean(axis=0)}).sort_values('SHAP_abs_medio',ascending=False)
    importance.to_csv(O/'shap_importancia.csv',index=False)
    # Datos transformados: recuperar unidades originales de numéricas para leer los ejes.
    displaydata=B[sample].copy(); scaler=prep.named_transformers_['numericas'].named_steps['escalar']
    displaydata[:,:len(NUM)]=scaler.inverse_transform(displaydata[:,:len(NUM)])
    pairs=[('internet_hogar',next((n for n in names if 'lengua_materna_quechua'==n),'rural')),('ratio_alumno_docente','rural')]
    for j,(feature,color) in enumerate(pairs,1):
        shap.dependence_plot(feature,vals,displaydata,feature_names=names,interaction_index=color,show=False)
        savefig(f'shap_dependencia_{j}')
    exp.data=displaydata
    for key,idx in [('alto',hi),('bajo',lo)]:
        where=int(np.flatnonzero(sample==idx)[0]); shap.plots.waterfall(exp[where],max_display=10,show=False); savefig(f'shap_caso_{key}')
    np.savez_compressed(O/'shap_valores.npz',valores=vals,bases=bases,filas_test=sample,variables=np.array(names))
    units='log odds' if winner in ['Logistica','XGBoost','LightGBM'] else 'probabilidad'
    reconstructed=np.asarray(bases).reshape(-1)+vals.sum(axis=1)
    expected=np.log(prob[sample]/(1-prob[sample])) if units=='log odds' else prob[sample]
    error=float(np.max(np.abs(reconstructed-expected)))
    dump('resumen_shap',{'modelo':winner,'n_explicados':len(sample),'unidad':units,'error_max_aditividad':error,'alto':{'probabilidad':float(prob[hi]),'clase_real':int(y[te][hi])},'bajo':{'probabilidad':float(prob[lo]),'clase_real':int(y[te][lo])},'advertencia':'Dependence muestra asociación entre característica y contribución; colorear por otra variable no equivale a calcular SHAP interaction values. No hay inferencia causal.'})
    assert error<.02, f'Error de aditividad SHAP: {error}'

def main():
    start=time.time(); df=preparar(); X,y,tr,te,pipe,winner=clasificar(df)
    clustering(df,tr,te); regresion(df,tr,te); explicar(df,X,y,tr,te,pipe,winner)
    dump('ejecucion',{'semilla':SEED,'segundos':round(time.time()-start,2),'estado':'completo'})
    print('TERMINADO',winner,round(time.time()-start,1),'segundos',flush=True)
if __name__=='__main__': main()
