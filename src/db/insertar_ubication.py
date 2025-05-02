import json
from utils import conectar_bd

def insertar_ubication(data):
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

        geo = tweet.get("geo")
        if geo:
            place = geo.get("place_id", {})

            # en el caso de que place_id sea un dict seguir buscando los demas atributos
            if isinstance(place, dict):

                # place_id 
                place_id = place.get("id")

                # country_code
                country_code = place.get("country_code", None)

                # country
                country = place.get("country", None)

                # name
                name = place.get("name", None)

                # place_typr
                place_type = place.get("place_type", None)

                # full_name
                full_name = place.get("full_name", None)

                # bbox
                bbox = place.get("geo", {}).get("bbox", [])

            # si place_id es un string el resto de atributos a null
            elif isinstance(place, str):

                # place_id 
                place_id = place

                country_code = None
                country = None
                name = None
                place_type = None
                full_name = None
                bbox = None

            bbox_str = json.dumps(bbox)   

            batch.append((tweet_id, place_id, name, full_name, country_code, country, place_type, bbox_str))

            if len(batch) >= batch_size:
                cursor.executemany("""
                                INSERT IGNORE INTO ubication (tweet_id, id, name, full_name, country_code, country, place_type, bbox)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", batch)
                conn.commit()
                batch = []
    
    if batch:
        cursor.executemany("""
                                INSERT IGNORE INTO ubication (tweet_id, id, name, full_name, country_code, country, place_type, bbox)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", batch)
        conn.commit()
    
    cursor.close()
    conn.close()