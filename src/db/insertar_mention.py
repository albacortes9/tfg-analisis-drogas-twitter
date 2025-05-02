from utils import conectar_bd

def insertar_mention(data):
    conn = conectar_bd()
    cursor = conn.cursor()
        
    for tweet in data:

        batch = []
        batch_size = 1000

        # tweet_id
        tweet_id = tweet.get("id")
        if isinstance(tweet_id, str):
            tweet_id = int(tweet_id)
        else:
            tweet_id = int(tweet_id.get("id"))
        
        # username, start_pos, end_pos
        entities = tweet.get("entities")
        if entities:
            mentions = entities.get("mentions", [])

            for mention in mentions:
                username = mention.get("username", None)
                start_pos = mention.get("start", None)
                end_pos = mention.get("end", None)                                                                                                      

                batch.append((tweet_id, username, start_pos, end_pos))
                
                if len(batch) >= batch_size:
                    cursor.executemany("""
                                    INSERT IGNORE INTO mention (tweet_id, username, start_pos, end_pos) VALUES (%s, %s, %s, %s)""", 
                                    batch)
                    conn.commit()
                    batch = []

    if batch:
        cursor.executemany(""" INSERT IGNORE INTO mention (tweet_id, username, start_pos, end_pos) VALUES (%s, %s, %s, %s)""", 
                            batch)
        conn.commit()
        
        
    cursor.close()
    conn.close()