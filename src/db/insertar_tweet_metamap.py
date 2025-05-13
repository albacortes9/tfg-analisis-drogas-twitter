from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

def insertar_tweet_metamap():
    try:
        # Crear el motor de conexión con SQLAlchemy
        engine = create_engine("mysql+mysqlconnector://root:2003@localhost/twitter_analysis")

        print("Connected to the database")

        # Tamaño del batch
        batch_size = 500
        offset = 0

        while True:
            # Query para realizar el JOIN y la inserción en batches
            query = f"""
            INSERT IGNORE INTO twitter_analysis.tweet_metamap (tweet_id, cui, tui, matched_words, positional_info)
            SELECT 
                t.id AS tweet_id, 
                m.cui, 
                m.tui, 
                m.matched_words, 
                m.positional_info
            FROM 
                twitter_analysis.tweet t
            INNER JOIN 
                twitter_drugs.metamap m
            ON 
                t.id = m.tweet_id
            LIMIT {batch_size} OFFSET {offset};
            """

            # Ejecutar la consulta
            with engine.connect() as connection:
                result = connection.execute(query)
                print(f"Batch with OFFSET {offset} processed")

                # Si no se insertaron filas, salir del bucle
                if result.rowcount == 0:
                    break

            # Incrementar el offset para el siguiente batch
            offset += batch_size

    except SQLAlchemyError as e:
        print(f"Error: {e}")
