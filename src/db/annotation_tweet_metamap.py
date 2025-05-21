import pymysql

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2003',
    'db': 'twitter_analysis',
    'port': 3306,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

BATCH_SIZE = 200000

try:
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    # Crear columna si no existe
    try:
        cursor.execute("""
        ALTER TABLE tweet_metamap
        ADD COLUMN tweet_metamap_annotation INTEGER;
        """)
        connection.commit()
    except:
        pass  # Columna ya existe

    # Crear tabla temporal
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tmp_sumas (
        tweet_id BIGINT NOT NULL,
        suma INTEGER,
        PRIMARY KEY (tweet_id)
    );
    """)
    connection.commit()

    # 1. Obtener cuántos tweet_id únicos hay
    cursor.execute("SELECT COUNT(DISTINCT tweet_id) AS total FROM tweet_metamap;")
    total_ids = cursor.fetchone()['total']
    print(f"Total tweet_id únicos: {total_ids}")

    offset = 0
    while offset < total_ids:
        # 2. Obtener lote de tweet_ids únicos
        cursor.execute(f"""
        SELECT DISTINCT tweet_id
        FROM tweet_metamap
        ORDER BY tweet_id
        LIMIT {BATCH_SIZE} OFFSET {offset};
        """)
        ids = [str(row['tweet_id']) for row in cursor.fetchall()]
        if not ids:
            break

        ids_str = ",".join(ids)

        # 3. Ejecutar la agregación para este lote de tweet_ids
        insert_query = f"""
        INSERT IGNORE INTO tmp_sumas (tweet_id, suma)
        SELECT tm.tweet_id, SUM(m.final_annotation) AS suma
        FROM tweet_metamap tm
        JOIN metamap m ON tm.cui = m.cui
        WHERE tm.tweet_id IN ({ids_str})
        GROUP BY tm.tweet_id;
        """
        cursor.execute(insert_query)
        connection.commit()
        print(f"Insertado lote OFFSET {offset} con {len(ids)} tweet_ids")

        offset += BATCH_SIZE

    # Crear índice para acelerar el update
    cursor.execute("CREATE INDEX idx_tmp_tweet_id ON tmp_sumas(tweet_id);")
    connection.commit()

    # 4. Actualizar por lotes desde tmp_sumas
    offset = 0
    while offset < total_ids:
        cursor.execute(f"""
        SELECT tweet_id
        FROM tmp_sumas
        ORDER BY tweet_id
        LIMIT {BATCH_SIZE} OFFSET {offset};
        """)
        ids = [str(row['tweet_id']) for row in cursor.fetchall()]
        if not ids:
            break

        ids_str = ",".join(ids)

        update_query = f"""
        UPDATE tweet_metamap tm
        JOIN (
            SELECT tweet_id, suma FROM tmp_sumas
            WHERE tweet_id IN ({ids_str})
        ) AS t ON tm.tweet_id = t.tweet_id
        SET tm.tweet_metamap_annotation = t.suma;
        """
        cursor.execute(update_query)
        connection.commit()
        print(f"Actualizado lote OFFSET {offset} con {len(ids)} tweet_ids")

        offset += BATCH_SIZE

    # Eliminar tabla temporal
    cursor.execute("DROP TABLE tmp_sumas;")
    connection.commit()

except Exception as e:
    print("Error:", e)
finally:
    if cursor: cursor.close()
    if connection: connection.close()
