import json
import os
import mysql.connector

# Conexión a la base de datos

def conectar_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2003",
        database="twitter_analysis"
    )

# Leer archivos JSON desde carpeta data

def cargar_archivo_json(ruta_archivo):
    with open(ruta_archivo, encoding='utf-8') as f:
        return json.load(f)
    

# Obtener lista de archivos .json en carpeta "data"

def obtener_archivos_json():
    base_dir = os.path.join(os.path.dirname(__file__))
    raw_data_path = os.path.join(base_dir, 'data', 'raw')
    return [os.path.join(raw_data_path, archivo) for archivo in os.listdir(raw_data_path) if archivo.endswith('.json')]
