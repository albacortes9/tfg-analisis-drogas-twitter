import pandas as pd
import os
from sqlalchemy import create_engine, text
import numpy as np

# Crear la conexión a la base de datos (reemplaza con tu URI de conexión)
engine = create_engine("mysql+mysqlconnector://root:2003@localhost/twitter_analysis")
connection = engine.connect()

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Sube de src/modelo/ a TFG/
excel_path = os.path.join(base_dir, 'data', 'raw', 'Drugs.xlsx')

# Cargar las hojas "metamap" y "slang" en dataframes
df_metamap = pd.read_excel(excel_path, sheet_name="metamap")
df_slang = pd.read_excel(excel_path, sheet_name="slang")

# Crear dataframes para aplicar fleiss kappa
df_metamap_fk = pd.DataFrame(columns=['term', 'positivo', 'negativo', 'contexto'])
df_slang_fk = pd.DataFrame(columns=['slang', 'positivo', 'negativo', 'contexto'])
df_metamap_fk['term'] = df_metamap['term']
df_slang_fk['concept'] = df_slang['concept']

# Contar las ocurrencias de cada categoría en las columnas correspondientes
df_metamap_fk['positivo'] = (df_metamap.drop(columns=['term']) == 'positivo').sum(axis=1)
df_metamap_fk['negativo'] = (df_metamap.drop(columns=['term']) == 'negativo').sum(axis=1)
df_metamap_fk['contexto'] = (df_metamap.drop(columns=['term']) == 'contexto').sum(axis=1)

df_slang_fk['positivo'] = (df_slang.drop(columns=['concept']) == 'positivo').sum(axis=1)
df_slang_fk['negativo'] = (df_slang.drop(columns=['concept']) == 'negativo').sum(axis=1)
df_slang_fk['contexto'] = (df_slang.drop(columns=['concept']) == 'contexto').sum(axis=1)

final_annotation_slang = []
final_annotation_metamap = []

# Calcular el porcentaje de acuerdo por término para slang
for i, row in df_slang_fk.iterrows():
    total_anotaciones = row[['positivo', 'negativo', 'contexto']].sum()  # Total de anotaciones
    max_acuerdo = row[['positivo', 'negativo', 'contexto']].max()  # Máximo acuerdo en una categoría
    porcentaje_acuerdo = max_acuerdo / total_anotaciones if total_anotaciones > 0 else 0

    if porcentaje_acuerdo > 0.6:  # Si el porcentaje de acuerdo es mayor al 60%
        # Devolver la categoría con más apariciones
        categoria = row[['positivo', 'negativo', 'contexto']].idxmax()
        if categoria == 'positivo':
            final_annotation_slang.append(1)
        elif categoria == 'negativo':
            final_annotation_slang.append(-1)
        else:
            final_annotation_slang.append(0)
    else:
        final_annotation_slang.append(None)  # Añadir un valor nulo si no hay consenso

df_slang['final_annotation'] = final_annotation_slang

# Calcular el porcentaje de acuerdo por término para metamap
for i, row in df_metamap_fk.iterrows():
    total_anotaciones = row[['positivo', 'negativo', 'contexto']].sum()  # Total de anotaciones
    max_acuerdo = row[['positivo', 'negativo', 'contexto']].max()  # Máximo acuerdo en una categoría
    porcentaje_acuerdo = max_acuerdo / total_anotaciones if total_anotaciones > 0 else 0

    if porcentaje_acuerdo > 0.6:  # Si el porcentaje de acuerdo es mayor al 60%
        # Devolver la categoría con más apariciones
        categoria = row[['positivo', 'negativo', 'contexto']].idxmax()
        if categoria == 'positivo':
            final_annotation_metamap.append(1)
        elif categoria == 'negativo':
            final_annotation_metamap.append(-1)
        else:
            final_annotation_metamap.append(0)
    else:
        final_annotation_metamap.append(None)

df_metamap['final_annotation'] = final_annotation_metamap

# Crear la nueva columna 'final_annotation' en la tabla 'slang' si no existe
connection.execute(text('ALTER TABLE slang ADD COLUMN final_annotation INTEGER;'))

# Reemplazar valores NaN en la columna 'final_annotation' con None (que se traduce a NULL en SQL)
df_slang['final_annotation'] = df_slang['final_annotation'].replace({np.nan: None})

# Actualizar la tabla slang en la base de datos
for i, row in df_slang.iterrows():
    slang_value = row['concept']
    final_annotation_value = row['final_annotation']

    # Crear la consulta de inserción o actualización
    query = text("""
    UPDATE slang
    SET final_annotation = :final_annotation
    WHERE concept = :concept;
   """)
    connection.execute(query, {"concept": slang_value, "final_annotation": final_annotation_value})

# Crear la nueva columna 'final_annotation' en la tabla 'metamap' si no existe
connection.execute(text('ALTER TABLE metamap ADD COLUMN final_annotation INTEGER;'))

# Reemplazar valores NaN en la columna 'final_annotation' de df_metamap con None
df_metamap['final_annotation'] = df_metamap['final_annotation'].replace({np.nan: None})

# Actualizar la tabla metamap en la base de datos
for i, row in df_metamap.iterrows():
    term_value = row['term']
    final_annotation_value = row['final_annotation']

    # Crear vista de la tabla metamap
    connection.execute(text("""CREATE OR REPLACE VIEW metamap_view
    AS SELECT term, annotation1, annotation2, annotation3, final_annotation FROM metamap;"""))

    # Crear la consulta de inserción o actualización
    query = text("""
    UPDATE metamap_view
    SET final_annotation = :final_annotation
    WHERE term = :term;
    """)
    connection.execute(query, {"term": term_value, "final_annotation": final_annotation_value})

# Cerrar la conexión
connection.close()
