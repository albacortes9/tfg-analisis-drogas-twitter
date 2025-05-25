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

# Semilla
R = 42

# 1. Cargar el dataset
try:
    df = pd.read_excel('data/processed/dataset_final_vectorizado.xlsx')
except FileNotFoundError:
    print("Error: El archivo 'dataset_final_vectorizado.xlsx' no se encuentra en 'data/processed/'.")
    exit()

X = df.iloc[:, :-1]
y = df.iloc[:, -1]

# 2. División train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=R, stratify=y)

# 3. Calcular class weight manual (opcional)
from sklearn.utils.class_weight import compute_class_weight
classes = np.unique(y_train)
weights = compute_class_weight(class_weight='balanced', classes=classes, y=y_train)
class_weight_dict = {cls: w for cls, w in zip(classes, weights)}

# 4. Modelos cost-sensitive (cuando es posible)
models = {
    "DT": DecisionTreeClassifier(class_weight='balanced'),
    "RF": RandomForestClassifier(n_estimators=50, class_weight='balanced'),
    "LR": LogisticRegression(max_iter=1000, class_weight='balanced'),
    "XGBoost": XGBClassifier(random_state=R, scale_pos_weight=weights[1]/weights[0], verbosity=0),

    # Modelos no compatibles directamente
    "AdaBoost": AdaBoostClassifier(),
    "Bagging": BaggingClassifier(),
    "MLP": MLPClassifier(max_iter=500)
}

# 5. Hiperparámetros
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

    "LR": {'m__penalty': ['l1', 'l2', 'elasticnet', None],
           'm__solver': ['lbfgs', 'sag', 'saga', 'newton-cholesky']},

    "XGBoost": {'m__max_depth': [2, 3, 5, 7, 10],
                'm__n_estimators': [10, 100, 500]},

    "MLP": {'m__activation': ['identity', 'logistic', 'tanh', 'relu'],
            'm__hidden_layer_sizes': randint(50, 150),
            'm__learning_rate': ['constant', 'invscaling', 'adaptive']}
}

# 6. Configuración de validación cruzada
inner_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=R)
scorer = make_scorer(f1_score)

# 7. Entrenamiento y evaluación
results = []

for name, model in models.items():
    print(f"\n🔍 Evaluando modelo: {name}")

    pipeline = Pipeline([
        ("m", model)
    ])

    search = RandomizedSearchCV(
        pipeline,
        param_distributions=hyperparameters[name],
        n_iter=10,
        scoring=scorer,
        cv=inner_cv,
        random_state=R,
        n_jobs=-1,
        verbose=0
    )

    # Entrenamiento + búsqueda de hiperparámetros (sin SMOTE)
    search.fit(X_train, y_train)

    # 7.1 Evaluación en test
    y_pred = search.predict(X_test)
    y_proba = search.predict_proba(X_test)[:, 1] if hasattr(search, "predict_proba") else None

    f1 = f1_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    auroc = roc_auc_score(y_test, y_proba) if y_proba is not None else None
    auprc = average_precision_score(y_test, y_proba) if y_proba is not None else None

    # 7.2 Validación cruzada con mejores hiperparámetros
    best_model = search.best_estimator_
    metrics_cv = {
        "f1": cross_val_score(best_model, X_train, y_train, cv=inner_cv, scoring='f1'),
        "accuracy": cross_val_score(best_model, X_train, y_train, cv=inner_cv, scoring='accuracy'),
        "recall": cross_val_score(best_model, X_train, y_train, cv=inner_cv, scoring='recall'),
        "precision": cross_val_score(best_model, X_train, y_train, cv=inner_cv, scoring='precision')
    }

    results.append({
        "name": name,
        "f1_test": f1,
        "rec_test": rec,
        "prec_test": prec,
        "acc_test": acc,
        "tn": tn,
        "fn": fn,
        "fp": fp,
        "tp": tp,
        "auroc_test": auroc,
        "auprc_test": auprc,
        "f1_cv": f"{metrics_cv['f1'].mean():.3f} ± {metrics_cv['f1'].std():.3f}",
        "acc_cv": f"{metrics_cv['accuracy'].mean():.3f} ± {metrics_cv['accuracy'].std():.3f}",
        "prec_cv": f"{metrics_cv['precision'].mean():.3f} ± {metrics_cv['precision'].std():.3f}",
        "rec_cv": f"{metrics_cv['recall'].mean():.3f} ± {metrics_cv['recall'].std():.3f}"
    })

# Mostrar resultados
results_df = pd.DataFrame(results)
print("\n📊 Resultados finales:")
print(results_df)
