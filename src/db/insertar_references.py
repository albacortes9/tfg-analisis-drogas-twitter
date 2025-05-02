from utils import conectar_bd
from insertar_tweet import insertar_tweet
from insertar_mention import insertar_mention
from insertar_metrics import insertar_metrics
from insertar_ubication import insertar_ubication
from insertar_tweet_keyword import insertar_tweet_keywords

def insertar_references(data):
    conn = conectar_bd()
    cursor = conn.cursor()
    author_id = ""
    reply_user_id = ""

    batch_ref = []
    batch_user = []
    batch_tweet = []
    batch_padres = []
    batch_size = 1000


    # El hijo es el tweet más fuera y el padre el más dentro
    def recorrer_referencia(hijo_id, ref_data):
        padre_info = ref_data[0].get("id")
        tipo = ref_data[0].get("type")
        nonlocal author_id, reply_user_id, batch_ref, batch_tweet, batch_padres, batch_user

        if isinstance(padre_info, dict): # Si el id del padre es un dict es porque hay otro tweet padre
            padre_id = padre_info.get("id")

            # Se inserta todos los datos que hay en id en sus correspondientes tablas
            batch_padres.append(padre_info)

            author_id = int(padre_info.get("author_id"))
            if tipo == "quoted":
                batch_user.append((author_id, None, None, None, None, None, 0, 0, 0, 0))
                cursor.executemany("""
                    INSERT IGNORE INTO user (id, name, username, location, verified, profile_image_url, 
                                            followers_count, following_count, tweet_count, listed_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", batch_user)
                conn.commit()
                batch_user = []  

            if padre_info.get("referenced_tweets"):         # se guarda el author_id del tweet padre que aparece en in_reply_to_user_id porque en el padre no aparece
                reply_user_id = padre_info.get("in_reply_to_user_id", None)
                if reply_user_id:
                    reply_user_id = int(reply_user_id)

            batch_ref.append((hijo_id, padre_id, tipo))        
            
            if len(batch_ref) >= batch_size:
                cursor.executemany("""
                    INSERT IGNORE INTO referenced_tweet (tweet_id, referenced_tweet_id, reference_type)
                    VALUES (%s, %s, %s)""", batch_ref)
                conn.commit()
                batch_ref = []

            padre_ref = padre_info.get("referenced_tweets")  
            if padre_ref:
                recorrer_referencia(padre_id, padre_ref) # Se vuelve a llamar recursivamente

        elif isinstance(padre_info, str): # Si el id del padre es un str entonces ese es el padre maximo
            padre_id = int(padre_info)

            batch_tweet.append((padre_id, None, reply_user_id, None, None))
            batch_user.append((reply_user_id, None, None, None, None, None, 0, 0, 0, 0))

            # if len(batch_user) >= batch_size:
            cursor.executemany("""
                    INSERT IGNORE INTO user (id, name, username, location, verified, profile_image_url, 
                                            followers_count, following_count, tweet_count, listed_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", batch_user)
            conn.commit()
            batch_user = []   

            # Insertar el id del padre en tweet aunque solo tengamos ese dato y el author_id (hay veces que no esta)
            # if len(batch_tweet) >= batch_size:
            cursor.executemany("""
                INSERT IGNORE INTO tweet (id, text, author_id, created_at, media)
                VALUES (%s, %s, %s, %s, %s)""", batch_tweet)
            conn.commit()
            batch_tweet = []

            # Insertar en tweet_references
            batch_ref.append((hijo_id, padre_id, tipo))        
            
            if len(batch_ref) >= batch_size:
                cursor.executemany("""
                    INSERT IGNORE INTO referenced_tweet (tweet_id, referenced_tweet_id, reference_type)
                    VALUES (%s, %s, %s)""", batch_ref)
                conn.commit()
                batch_ref = []


    for tweet in data:
        if tweet.get("referenced_tweets"):

            # tweet_id
            tweet_id = tweet.get("id")
            if isinstance(tweet_id, str):
                tweet_id = int(tweet_id)
            else:
                tweet_id = int(tweet_id.get("id"))

            # informacion del user al que se hace referencia y se inserta en user
            reply_user = tweet.get("in_reply_to_user_id") 
            if isinstance(reply_user,dict):
                author_id = int(reply_user.get("id"))
                username = reply_user.get("username", None)
                name = reply_user.get("name", None)
                verified = reply_user.get("verified", None) # False = 0, True = 1
                profile_image_url = reply_user.get("profile_image_url", None)
                location = reply_user.get("location", None)
                metrics = reply_user.get("public_metrics", {})

                followers = metrics.get("followers_count", 0)
                following = metrics.get("following_count", 0)
                tweets = metrics.get("tweet_count", 0)
                listed = metrics.get("listed_count", 0)

                batch_user.append((author_id, name, username, location, verified, profile_image_url, followers, following, tweets, listed))

                if len(batch_user) >= batch_size:
                    cursor.executemany("""
                            INSERT IGNORE INTO user (id, name, username, location, verified, profile_image_url, 
                                                    followers_count, following_count, tweet_count, listed_count)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", batch_user)
                    conn.commit()
                    batch_user = []                  
                
            elif reply_user is not None: # si no es un dict y no es null entonces es el author_id solo
                author_id = int(reply_user)

            referenced = tweet.get("referenced_tweets")
            if referenced:
                recorrer_referencia(tweet_id, referenced) # Se llama a recorrer referencia con el id del hijo y la parte de referenced_tweet

    if batch_ref:
        cursor.executemany("""
            INSERT IGNORE INTO referenced_tweet (tweet_id, referenced_tweet_id, reference_type)
            VALUES (%s, %s, %s)""", batch_ref)
        conn.commit()

    if batch_tweet:
        cursor.executemany("""
            INSERT IGNORE INTO tweet (id, text, author_id, created_at, media)
            VALUES (%s, %s, %s, %s, %s)""", batch_tweet)
        conn.commit() 

    if batch_user:
        cursor.executemany("""
                INSERT IGNORE INTO user (id, name, username, location, verified, profile_image_url, 
                                        followers_count, following_count, tweet_count, listed_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", batch_user)
        conn.commit() 

    if batch_padres:
        insertar_tweet(batch_padres) 
        insertar_metrics(batch_padres)
        insertar_mention(batch_padres)
        insertar_ubication(batch_padres)
        insertar_tweet_keywords(batch_padres) 


    cursor.close()
    conn.close()
