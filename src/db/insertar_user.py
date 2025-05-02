from utils import conectar_bd

def insertar_user(data):
    conn = conectar_bd()
    cursor = conn.cursor()

    batch = []
    batch_size = 1000

    for tweet in data:

        author = tweet.get("author_id")
        if author: 

            # author_id 
            author_id = int(author.get("id"))

            # username
            username = author.get("username", None)

            # name
            name = author.get("name", None)

            # verified
            verified = author.get("verified", None) # False = 0, True = 1

            # profile_image_url
            profile_image_url = author.get("profile_image_url", None)

            # location
            location = author.get("location", None)

            # metrics
            metrics = author.get("public_metrics", {})

            followers = metrics.get("followers_count", 0)
            following = metrics.get("following_count", 0)
            tweets = metrics.get("tweet_count", 0)
            listed = metrics.get("listed_count", 0)

            batch.append((author_id, name, username, location, verified, profile_image_url, followers, following, tweets, listed))

            if len(batch) >= batch_size:
                cursor.executemany("""
                            INSERT IGNORE INTO user (id, name, username, location, verified, profile_image_url, followers_count, following_count, 
                            tweet_count, listed_count)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", batch)
                batch = []
                conn.commit
    
    if batch:
        cursor.executemany("""
            INSERT IGNORE INTO user (id, name, username, location, verified, profile_image_url, followers_count, following_count, 
            tweet_count, listed_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", batch)
        conn.commit()

    cursor.close()
    conn.close()