import pandas as pd
from sqlalchemy import create_engine
from mysql.connector import Error
from sqlalchemy.dialects.mysql import insert

def insert_ignore(table, conn, keys, data_iter):
    table = table.table
    stmt = insert(table).values(list(data_iter))
    stmt = stmt.on_duplicate_key_update({key: stmt.inserted[key] for key in keys})
    conn.execute(stmt)


def insertar_tweet_metamap():
    
    try:
        # Crear el motor de conexión con SQLAlchemy
        engine = create_engine("mysql+mysqlconnector://root:2003@localhost/twitter_analysis")

        # Cargar datos de las tablas en dataframes
        query_tweet = "SELECT id FROM twitter_analysis.tweet;"
        query_metamap = "SELECT * FROM twitter_drugs.metamap;"

        tweet_df = pd.read_sql(query_tweet, con=engine)
        metamap_df = pd.read_sql(query_metamap, con=engine)

        # Realizar el join entre los dataframes
        merged_df = pd.merge(tweet_df, metamap_df, left_on='id', right_on='tweet_id')

        # Seleccionar las columnas necesarias
        result_df = merged_df[['tweet_id', 'cui', 'tui', 'matched_words', 'positional_info']]

        # Insertar en lotes
        batch_size = 500
        for i in range(0, len(result_df), batch_size):
            batch = result_df.iloc[i:i + batch_size]
            batch.to_sql(
                name='tweet_metamap',
                con=engine,
                schema='twitter_analysis',
                if_exists='append',
                index=False,
                method=insert_ignore
            )
            print(f"Batch {i // batch_size + 1} inserted")

    except Exception as e:
        print(f"Error: {e}")