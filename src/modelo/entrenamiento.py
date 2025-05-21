import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, train_test_split, RandomizedSearchCV
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, make_scorer, f1_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from imblearn.combine import SMOTEENN
from imblearn.pipeline import Pipeline as ImbPipeline
from scipy.stats import randint, uniform

# Cargar datos
df = pd.read_excel("data/processed/dataset_final_vectorizado.xlsx")

# Eliminar columnas redundantes
columns_to_drop = ['retweet_count', 'reply_count', 'quote_count', 'user_listed_count']
df = df.drop(columns=columns_to_drop)

# Features y target
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

# Dividir el dataset en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Aplicar SMOTE-ENN solo al conjunto de entrenamiento
smote_enn = SMOTEENN(random_state=42)
X_train_resampled, y_train_resampled = smote_enn.fit_resample(X_train, y_train)

# Modelos para prueba
models = {
    "DT": DecisionTreeClassifier(),
    "RF" : RandomForestClassifier(n_estimators=50), 
    "XGBoost" : XGBClassifier(random_state=42, verbosity = 0),
    "AdaBoost" : AdaBoostClassifier(), 
}

# Espacio reducido de hiperparámetros
hyperparameters = {
    "DT": {
        'm__splitter': ['best','random'],
        'm__max_features': ['sqrt', 'log2'],
        'm__criterion' :['gini', 'entropy','log_loss']
    },
    "RF": {
        'm__n_estimators': randint(100,250),
        'm__max_features': ['sqrt', 'log2'],
        'm__criterion' :['gini', 'entropy']
    },
    "XGBoost": {
        'm__max_depth':[2, 3, 5, 7, 10],
        'm__n_estimators':[10, 100, 500]
    },
    "AdaBoost" :{
        'm__n_estimators': randint(50,150),
        'm__learning_rate': uniform(0.8,1.2)
    } 
}

# Métricas
scoring = {
    'accuracy': make_scorer(accuracy_score),
    'f1': make_scorer(f1_score),
    'roc_auc': make_scorer(roc_auc_score)
}

# Entrenar y evaluar modelos
for name, model in models.items():
    print(f"\nEntrenando modelo: {name}")

    # Crear pipeline con escalado, balanceo y modelo
    pipe = ImbPipeline([
        ('scaler', StandardScaler()),
        ('resampler', SMOTEENN(random_state=42)),
        ('m', model)
    ])

    # Búsqueda de hiperparámetros
    search = RandomizedSearchCV(
        pipe,
        param_distributions=hyperparameters[name],
        n_iter=4,
        scoring='f1',
        cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
        random_state=42,
        n_jobs=-1
    )

    # Entrenar el modelo con validación cruzada
    search.fit(X_train, y_train)

    # Evaluar en el conjunto de prueba
    y_pred = search.best_estimator_.predict(X_test)
    y_prob = search.best_estimator_.predict_proba(X_test)[:, 1]

    print("\n--- Evaluación en el conjunto de prueba ---")
    print("\n--- Reporte de Clasificación ---")
    print(classification_report(y_test, y_pred, digits=4))

    print("\n--- Matriz de Confusión ---")
    print(confusion_matrix(y_test, y_pred))

    print("\n--- AUC-ROC ---")
    print(f"AUC: {roc_auc_score(y_test, y_prob):.4f}")

    print(f"\nMejores hiperparámetros para {name}: {search.best_params_}")