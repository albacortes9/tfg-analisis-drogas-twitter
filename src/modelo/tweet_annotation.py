import pymysql
import pandas as pd

# Conexión a la base de datos MySQL
connection = pymysql.connect(
    host='localhost',       # Cambia por la dirección de tu servidor MySQL
    user='root',            # Cambia por tu usuario de MySQL
    password='2003',        # Cambia por tu contraseña de MySQL
    database='twitter_analysis',  # Cambia por el nombre de tu base de datos
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Crear la tabla para almacenar los datos clasificados (si no existe)
create_table_query = """
CREATE TABLE IF NOT EXISTS classified_tweets (
    tweet_id BIGINT PRIMARY KEY,
    classification INTEGER
);
"""

with connection.cursor() as cursor:
    cursor.execute(create_table_query)
    connection.commit()

# Tamaño del bloque
batch_size = 50000
offset = 0

try:
    while True:
        # Consulta SQL con LIMIT y OFFSET
        query = f"""
        SELECT DISTINCT
            ts.tweet_id,
            ts.tweet_slang_annotation,
            tm.tweet_metamap_annotation
        FROM 
            tweet_slang ts
        JOIN 
            tweet_metamap tm
        ON 
            ts.tweet_id = tm.tweet_id
        WHERE 
            (ts.tweet_slang_annotation > 0 AND tm.tweet_metamap_annotation > 0) OR
            (ts.tweet_slang_annotation < 0 AND tm.tweet_metamap_annotation < 0) 
        LIMIT {batch_size} OFFSET {offset}
        """

        # Ejecutar la consulta
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        # Si no hay más resultados, salir del bucle
        if not result:
            break

        # Convertir los resultados a un DataFrame
        df = pd.DataFrame(result)

        # Clasificar los tweets directamente en el DataFrame
        df['classification'] = df.apply(
            lambda row: (
                1 if row['tweet_slang_annotation'] > 0 and row['tweet_metamap_annotation'] > 0 else
                0 if row['tweet_slang_annotation'] < 0 and row['tweet_metamap_annotation'] < 0 else
                None
            ),
            axis=1
        )

        # Insertar los datos clasificados en la tabla
        insert_query = """
        INSERT INTO classified_tweets (tweet_id, classification)
        VALUES (%s, %s)
        """
        data_to_insert = df[['tweet_id', 'classification']].values.tolist()

        with connection.cursor() as cursor:
            cursor.executemany(insert_query, data_to_insert)
            connection.commit()

        print(f"Insertados {len(data_to_insert)} registros en la tabla classified_tweets.")

        # Incrementar el offset para el siguiente bloque
        offset += batch_size

    print("Todos los datos han sido clasificados e insertados en la tabla classified_tweets.")

finally:
    # Cerrar la conexión a la base de datos
    connection.close()