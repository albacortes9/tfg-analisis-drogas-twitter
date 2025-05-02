from utils import obtener_archivos_json, cargar_archivo_json
from insertar_user import insertar_user
from insertar_tweet import insertar_tweet
from insertar_metrics import insertar_metrics
from insertar_ubication import insertar_ubication
from insertar_mention import insertar_mention
from insertar_tweet_keyword import insertar_tweet_keywords
from insertar_references import insertar_references

def main():
    archivos = obtener_archivos_json()
    for archivo in archivos:
        print(f"Procesando archivo: {archivo}")
        data = cargar_archivo_json(archivo)
        insertar_user(data)
        insertar_tweet(data)
        insertar_metrics(data)
        insertar_ubication(data)
        insertar_mention(data)
        insertar_tweet_keywords(data)
        insertar_references(data)
        print(f"Archivo {archivo} procesado.\n")

if __name__ == '__main__':
    main()