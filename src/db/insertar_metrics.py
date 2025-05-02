from utils import conectar_bd

def insertar_metrics(data):
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

        # retweet_count, reply_count, like_count, quote_count
        metrics = tweet.get("public_metrics", {})

        retweet = metrics.get("retweet_count", 0)
        reply = metrics.get("reply_count", 0)
        like = metrics.get("like_count", 0)
        quote = metrics.get("quote_count", 0)

        batch.append((tweet_id, retweet, reply, like, quote)) 

        if len(batch) >= batch_size:                                                                                                       
            cursor.executemany("""
                            INSERT IGNORE INTO tweet_metrics (tweet_id, retweet_count, reply_count, like_count, quote_count)
                            VALUES (%s, %s, %s, %s, %s)""", batch)
            conn.commit()
            batch = []

    if batch:
        cursor.executemany("""
                            INSERT IGNORE INTO tweet_metrics (tweet_id, retweet_count, reply_count, like_count, quote_count)
                            VALUES (%s, %s, %s, %s, %s)""", batch)
        conn.commit()
    
    cursor.close()
    conn.close()