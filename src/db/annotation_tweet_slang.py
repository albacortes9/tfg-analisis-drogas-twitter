import pymysql

# Parámetros de conexión a la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2003',
    'db': 'twitter_analysis',
    'port': 3306,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

BATCH_SIZE = 200000  # tamaño del lote a procesar

try:
    # Conexión a la base de datos
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    # # 1. Añadir columna tweet_slang_annotation a la tabla slang
    # Crear columna si no existe
    try:
        cursor.execute("""
        ALTER TABLE tweet_slang
        ADD COLUMN tweet_slang_annotation INTEGER;
        """)
        connection.commit()
    except:
        pass  # Columna ya existe

    # 1. Crear la tabla temporal (si no existe)
    create_table_query = """
    CREATE TABLE IF NOT EXISTS tmp_sumas (
    tweet_id BIGINT NOT NULL,
    suma INTEGER,
    PRIMARY KEY (tweet_id)
    );
    """
    cursor.execute(create_table_query)
    connection.commit()

    # 2. Inserción de datos en lotes
    offset = 0
    while True:
        insert_query = f"""
        INSERT INTO tmp_sumas (tweet_id, suma)
        SELECT ts.tweet_id, SUM(s.final_annotation) AS suma
        FROM tweet_slang ts
        JOIN slang s ON ts.slang_id = s.id
        GROUP BY ts.tweet_id
        LIMIT {BATCH_SIZE} OFFSET {offset};
        """
        cursor.execute(insert_query)
        connection.commit()

        filas_afectadas = cursor.rowcount
        if filas_afectadas == 0:
            print("No se insertaron más filas. Fin de la inserción en lotes.")
            break

        print(f"Insertado lote: OFFSET {offset} con {filas_afectadas} filas.")
        offset += BATCH_SIZE

    # 3. Crear el índice sobre tmp_sumas
    create_index_query = """
    CREATE INDEX  idx_tmp_tweet_id 
    ON tmp_sumas(tweet_id);
    """
    cursor.execute(create_index_query)
    connection.commit()
    print("Índice idx_tmp_tweet_id creado.")

    # 4. Actualización de la tabla tweet_slang en lotes
    offset = 0
    while True:
        update_query = f"""
        UPDATE tweet_slang ts
        JOIN (
            SELECT tweet_id, suma
            FROM tmp_sumas
            ORDER BY tweet_id
            LIMIT {BATCH_SIZE} OFFSET {offset}
        ) AS t ON ts.tweet_id = t.tweet_id
        SET ts.tweet_slang_annotation = t.suma;
        """
        cursor.execute(update_query)
        connection.commit()

        filas_afectadas = cursor.rowcount
        if filas_afectadas == 0:
            print("No se actualizaron más filas. Fin de la actualización en lotes.")
            break

        print(f"Actualizado lote: OFFSET {offset} con {filas_afectadas} filas.")
        offset += BATCH_SIZE

    # 5. Eliminar la tabla temporal
    drop_table_query = "DROP TABLE tmp_sumas;"
    cursor.execute(drop_table_query)
    connection.commit()
    print("Tabla tmp_sumas eliminada.")

except Exception as e:
    print("Error durante la ejecución:", e)
finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
