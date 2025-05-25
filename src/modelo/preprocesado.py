import pandas as pd
import numpy as np
from gensim.models import Word2Vec
import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from sklearn.preprocessing import StandardScaler
nltk.download('punkt_tab')
nltk.download('stopwords')

# --- Parámetros ---
VECTOR_SIZE = 30
DATASET_PATH = "data/processed/dataset_final.xlsx"
OUTPUT_PATH = "data/processed/dataset_final_vectorizado.xlsx"

# --- Preprocesamiento de texto ---
def preprocess_text(text):
    # Convertir a minúsculas
    text = text.lower()
    
    # Eliminar URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Eliminar menciones de usuarios
    text = re.sub(r'@\w+', '', text)
    
    # Eliminar hashtags
    text = re.sub(r'#\w+', '', text)
    
    # Eliminar números
    text = re.sub(r'\d+', '', text)
    
    # Eliminar puntuación
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenización
    tokens = word_tokenize(text)
    
    # Eliminar stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    return tokens

# --- Cargar dataset ---
df = pd.read_excel(DATASET_PATH)
df.dropna(subset=["text"], inplace=True)

# --- Eliminar nulos ---
if df.isnull().values.any():
    df = df.dropna()
    print("\nSe han eliminado las filas con valores nulos.")
else:
    print("No hay valores nulos en el dataset.")

# --- Preprocesar textos ---
df["tokens"] = df["text"].apply(preprocess_text)

# --- Entrenar modelo Word2Vec ---
sentences = df["tokens"].tolist()
w2v_model = Word2Vec(sentences=sentences, vector_size=VECTOR_SIZE, window=5, min_count=2, workers=4)

# --- Obtener vector promedio por tweet ---
def get_vector(tokens):
    vectors = [w2v_model.wv[word] for word in tokens if word in w2v_model.wv]
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        return np.zeros(VECTOR_SIZE)

df["vector"] = df["tokens"].apply(get_vector)

# --- Asegurar que todo esté alineado ---
df.reset_index(drop=True, inplace=True) 

# --- Separar vectores y etiquetas ---
w2v_df = pd.DataFrame(df["vector"].tolist(), columns=[f"w2v_{i}" for i in range(VECTOR_SIZE)])
other_features = df.drop(columns=["text", "tokens", "vector", "classification"])
target = df["classification"]

# --- Unir todo en un solo dataframe final ---
final_df = pd.concat([w2v_df, other_features], axis=1)
final_df["classification"] = target

# --- Estandarizar los datos ---
scaler = StandardScaler()

# Separar las características y la columna de clasificación
features = final_df.iloc[:, :-1].astype('float64')
classification = final_df.iloc[:, -1]

# Aplicar la estandarización solo a las características
final_df.iloc[:, :-1] = scaler.fit_transform(features).astype('float64')

# Volver a unir la columna de clasificación (ya está en su sitio)-ñlk

print("\nLos datos han sido estandarizados.")

# --- Guardar el DataFrame limpio, vectorizado y estandarizado ---
final_df.to_excel(OUTPUT_PATH, index=False)

print("Original:", df.shape)
print("Word2Vec vectors:", w2v_df.shape)
print("Final DF:", final_df.shape)

print("✅ Dataset vectorizado guardado en:", OUTPUT_PATH)
