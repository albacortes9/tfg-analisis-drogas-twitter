from utils import conectar_bd
import os
import pandas as pd

def insertar_tweet_slang(data):
    # Ruta al archivo Excel en data/raw/
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Sube de src/db/ a TFG/
    excel_path = os.path.join(base_dir, 'data', 'raw', 'Drugs.xlsx')

    # Leer las slang desde el archivo Excel
    df_slang = pd.read_excel(excel_path, sheet_name='match_slang')  # Asegúrate de que la hoja se llame 'slang'
    slangs = df_slang[['id', 'concept']].values.tolist()  # Convertir a lista de tuplas [(id, slang), ...]


    conn = conectar_bd()
    cursor = conn.cursor()

    batch = []
    batch_size = 1000

    for tweet in data:
        # tweet_id
        tweet_id = tweet.get("id")
        if isinstance(tweet_id, str):
            tweet_id = int(tweet_id)
        else:
            tweet_id = int(tweet_id.get("id"))

        # text del tweet
        text = tweet.get("text", "").lower()

        for slang_id, slang in slangs:
            if slang.lower() in text:     # si la slang esta en el text se inserta

                batch.append((tweet_id, slang_id))

                if len(batch) >= batch_size:
                    cursor.executemany("""
                        INSERT IGNORE INTO tweet_slang (tweet_id, slang_id) VALUES (%s, %s)""", 
                        batch)
                    conn.commit()
                    batch = []

    if batch:
        cursor.executemany("""
            INSERT IGNORE INTO tweet_slang (tweet_id, slang_id) VALUES (%s, %s)""", 
            batch)
        conn.commit()

    cursor.close()
    conn.close()
