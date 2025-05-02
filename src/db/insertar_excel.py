import pandas as pd
from sqlalchemy import create_engine
import os

# Configuración de la conexión
usuario = 'root'
contraseña = '2003'
host = 'localhost'
puerto = '3306'
nombre_bd = 'twitter_analysis'

# Ruta al archivo Excel en data/raw/
base_dir = os.path.dirname(os.path.dirname(__file__))  # Sube de src/db/ a TFG/
excel_path = os.path.join(base_dir, 'data', 'raw', 'Drugs.xlsx')

# Lectura de las hojas del Excel
df_drug = pd.read_excel(excel_path, sheet_name='drug')
df_keywords = pd.read_excel(excel_path, sheet_name='drug_keyword')
df_slang = pd.read_excel(excel_path, sheet_name='slang')
df_metamap = pd.read_excel(excel_path, sheet_name='metamap')

# Conexión a la base de datos
engine = create_engine(f'mysql+mysqlconnector://{usuario}:{contraseña}@{host}:{puerto}/{nombre_bd}', echo=False)

# Inserción en las tablas correspondientes
df_drug.to_sql(name='drug', con=engine, if_exists='append', index=False)
df_keywords.to_sql(name='drug_keyword', con=engine, if_exists='append', index=False)
df_slang.to_sql(name='slang', con=engine, if_exists='append', index=False)
df_metamap.to_sql(name='metamap', con=engine, if_exists='append', index=False)

print("Datos insertados correctamente en las tablas 'drug', 'drug_keyword', 'slang' y 'metamap'")
