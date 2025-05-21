import pandas as pd
import seaborn as sns

import matplotlib.pyplot as plt

# Carga tu dataset (ajusta la ruta si es necesario)
dataset_final_vectorizado = pd.read_excel('data/processed/dataset_final_vectorizado.xlsx')

# Calcula la matriz de correlación
correlation_matrix = dataset_final_vectorizado.corr()

# Guarda la matriz de correlación en un archivo Excel
correlation_matrix.to_excel('data/processed/matriz_correlacion.xlsx')

# Opcional: muestra pares de variables con alta correlación (>0.8 o <-0.8)
threshold = 0.8
high_corr = []
for i in correlation_matrix.columns:
    for j in correlation_matrix.columns:
        if i != j and abs(correlation_matrix.loc[i, j]) > threshold:
            pair = tuple(sorted([i, j]))
            if pair not in high_corr:
                high_corr.append(pair)
                print(f"Alta correlación entre {i} y {j}: {correlation_matrix.loc[i, j]:.2f}")
