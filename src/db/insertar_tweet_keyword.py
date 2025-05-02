from utils import conectar_bd

def insertar_tweet_keywords(data):
    conn = conectar_bd()
    cursor = conn.cursor()

    batch = []
    batch_size = 1000

    for tweet in data:

        # Cargar todas las keywords desde la base de datos
        cursor.execute("SELECT id, keyword FROM drug_keyword")
        keywords = cursor.fetchall()  # [(1, 'mdma'), (2, 'ecstasy'), ...]

        # tweet_id
        tweet_id = tweet.get("id")
        if isinstance(tweet_id, str):
            tweet_id = int(tweet_id)
        else:
            tweet_id = int(tweet_id.get("id"))

        # text del tweet
        text = tweet.get("text", "").lower()

        for keyword_id, keyword in keywords:
            if keyword.lower() in text:     # si la keyword esta en el text se inserta

                batch.append((tweet_id, keyword_id))

                if len(batch) >= batch_size:
                    cursor.executemany("""
                        INSERT IGNORE INTO tweet_keyword (tweet_id, keyword_id) VALUES (%s, %s)""", 
                        batch)
                    conn.commit()
                    batch = []

    if batch:
        cursor.executemany("""
            INSERT IGNORE INTO tweet_keyword (tweet_id, keyword_id) VALUES (%s, %s)""", 
            batch)
        conn.commit()

    cursor.close()
    conn.close()
