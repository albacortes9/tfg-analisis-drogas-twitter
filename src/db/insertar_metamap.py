import mysql.connector
from mysql.connector import Error
import pandas as pd
import os

def insertar_metamap():
    try:
        # Conexión a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            database='twitter_analysis',
            user='root',
            password='2003'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Parámetros para el procesamiento en lotes
            batch_size = 500
            offset = 0

            while True:
                # Consulta SQL para insertar en lotes
                query = f"""
                INSERT IGNORE INTO twitter_analysis.metamap (cui, term, tui, column4, column5, column6)
                SELECT DISTINCT(cui), term, tui, null, null, null
                FROM twitter_drugs.metamap
                LIMIT {batch_size} OFFSET {offset};
                """

                # Ejecutar la consulta
                cursor.execute(query)
                connection.commit()

                # Verificar si se insertaron filas
                if cursor.rowcount == 0:
                    print("No hay más filas para procesar. Finalizando.")
                    break

                print(f"Lote procesado con OFFSET {offset}")
                offset += batch_size

            # Leer el archivo Excel
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Sube de src/db/ a TFG/
            excel_path = os.path.join(base_dir, 'data', 'raw', 'Drugs.xlsx')
            df = pd.read_excel(excel_path, sheet_name="metamap")

            # Iterar sobre las filas del DataFrame
            for _, row in df.iterrows():
                term = row['term']
                annotation1 = row['annotation1']
                annotation2 = row['annotation2']
                annotation3 = row['annotation3']

                # Insertar los registros si el término coincide
                update_query = """
                UPDATE twitter_analysis.metamap
                SET annotation1 = %s, annotation2 = %s, annotation3 = %s
                WHERE term = %s;
                """
                cursor.execute(update_query, (annotation1, annotation2, annotation3, term))
                connection.commit()

            print("Actualización completada con las anotaciones")

    except Error as e:
        print(f"Error al conectar o ejecutar la consulta: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada")
