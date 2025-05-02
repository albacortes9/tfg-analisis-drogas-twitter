from utils import conectar_bd
import mysql.connector

def insertar_tweet(data):
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

        # text
        text = tweet.get("text", None)

        # created_at
        created_at = tweet.get("created_at", None)

        # media
        media = tweet.get("attachments") is not None  # True si viene 'attachments', False si no   

        # author_id  
        author = tweet.get("author_id")
        if isinstance(author, dict): 
            author_id = int(author.get("id"))
        else:
            author_id = int(author)

        batch.append((tweet_id, text, author_id, created_at, media))

        if len(batch) >= batch_size:
            cursor.executemany("""
                INSERT IGNORE INTO tweet (id, text, author_id, created_at, media)
                VALUES (%s, %s, %s, %s, %s) """, batch)
            conn.commit()
            batch = []
    
    if batch:
        cursor.executemany("""
            INSERT IGNORE INTO tweet (id, text, author_id, created_at, media)
            VALUES (%s, %s, %s, %s, %s) """, batch)
        conn.commit()
    
    cursor.close()
    conn.close()