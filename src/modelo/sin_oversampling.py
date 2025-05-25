import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    f1_score, recall_score, precision_score, accuracy_score,
    confusion_matrix, roc_auc_score, average_precision_score, make_scorer
)

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, BaggingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier

from scipy.stats import randint, uniform

# Fijar semilla
R = 42

# 1. Cargar el dataset
try:
    df = pd.read_excel('data/processed/dataset_final_vectorizado.xlsx')
except FileNotFoundError:
    print("Error: El archivo 'dataset_final_vectorizado.xlsx' no se encuentra en 'data/processed/'.")
    exit()

# Suponiendo que la última columna es la variable objetivo
X = df.iloc[:, :-1]
y = df.iloc[:, -1]

# 2. División del dataset en train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=R, stratify=y)

# 3. Definir modelos
models = {
    "DT": DecisionTreeClassifier(),
    "RF": RandomForestClassifier(n_estimators=50),
    "AdaBoost": AdaBoostClassifier(),
    "Bagging": BaggingClassifier(),
    "LR": LogisticRegression(max_iter=1000),
    "XGBoost": XGBClassifier(random_state=R, verbosity=0),
    "MLP": MLPClassifier(max_iter=500)
}

# 4. Hiperparámetros
hyperparameters = {
    "DT": {'m__splitter': ['best', 'random'],
           'm__max_features': ['sqrt', 'log2'],
           'm__criterion': ['gini', 'entropy', 'log_loss']},

    "RF": {'m__n_estimators': randint(100, 250),
           'm__max_features': ['sqrt', 'log2'],
           'm__criterion': ['gini', 'entropy']},

    "Bagging": {'m__n_estimators': randint(10, 100),
                'm__max_samples': [0.8, 1.0],
                'm__max_features': [0.8, 1.0],
                'm__warm_start': [True, False]},

    "AdaBoost": {'m__n_estimators': randint(50, 150),
                 'm__learning_rate': uniform(0.8, 1.2)},

    "LR": {'m__penalty': ['l2', 'elasticnet', None],
           'm__solver': ['lbfgs', 'sag', 'saga', 'newton-cholesky']},

    "XGBoost": {'m__max_depth': [2, 3, 5, 7, 10],
                'm__n_estimators': [10, 100, 500]},

    "MLP": {'m__activation': ['identity', 'logistic', 'tanh', 'relu'],
            'm__hidden_layer_sizes': randint(50, 150),
            'm__learning_rate': ['constant', 'invscaling', 'adaptive']}
}

# 5. Configurar validación cruzada
inner_cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=R)
scorer = make_scorer(f1_score)

# 6. Entrenamiento y evaluación
results = []

for name, model in models.items():
    print(f"Entrenando modelo: {name}")
    pipeline = Pipeline([("m", model)])
    param_grid = hyperparameters[name]

    search = RandomizedSearchCV(pipeline, param_distributions=param_grid,
                                n_iter=10, scoring=scorer, cv=inner_cv,
                                random_state=R, n_jobs=-1)

    search.fit(X_train, y_train)
    best_model = search.best_estimator_

    # Predicción en test
    y_pred = best_model.predict(X_test)
    y_proba = best_model.predict_proba(X_test)[:, 1] if hasattr(best_model, "predict_proba") else None

    # Métricas en test
    f1 = f1_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    auroc = roc_auc_score(y_test, y_proba) if y_proba is not None else None
    auprc = average_precision_score(y_test, y_proba) if y_proba is not None else None

    # Métricas de validación cruzada
    metrics_cv = {
        "f1": cross_val_score(best_model, X_train, y_train, cv=inner_cv, scoring='f1'),
        "accuracy": cross_val_score(best_model, X_train, y_train, cv=inner_cv, scoring='accuracy'),
        "recall": cross_val_score(best_model, X_train, y_train, cv=inner_cv, scoring='recall'),
        "precision": cross_val_score(best_model, X_train, y_train, cv=inner_cv, scoring='precision')
    }

    results.append({
        "name": name,
        "f1": f1,
        "nrec": tp + fn,
        "rec": rec,
        "prec": prec,
        "acc": acc,
        "tn": tn,
        "fn": fn,
        "fp": fp,
        "tp": tp,
        "auroc": auroc,
        "auprc": auprc,
        "f1_cv": f"{metrics_cv['f1'].mean():.3f} ± {metrics_cv['f1'].std():.3f}",
        "acc_cv": f"{metrics_cv['accuracy'].mean():.3f} ± {metrics_cv['accuracy'].std():.3f}",
        "rec_cv": f"{metrics_cv['recall'].mean():.3f} ± {metrics_cv['recall'].std():.3f}",
        "prec_cv": f"{metrics_cv['precision'].mean():.3f} ± {metrics_cv['precision'].std():.3f}"
    })

# Convertir resultados a DataFrame y mostrar
results_df = pd.DataFrame(results)
print("\n📊 Resultados finales:")
print(results_df)
