# Análisis de los Efectos del Consumo Recreativo de Drogas en Publicaciones de Twitter

Este proyecto forma parte de mi Trabajo de Fin de Grado y tiene como objetivo analizar el uso y mención de drogas en publicaciones de Twitter a lo largo de varios años.

## Estructura del Proyecto

```
TFG/
├── data/
│   └── raw/                                          # Archivos JSON con tweets (no incluidos en el repo por tamaño)
│        └── Drugs.xlsx                               # Excel con información de drogas y palabras clave
│   └── processed/                                    # Archivos procesados
│        ├── dataset_final.xlsx                       # Excel con los datos a utilizar en el modelo
|        └── dataset_final_vectorizado.xlsx           # Excel con los datos vectorizados a utilizar en el modelo
├── src/
│   └── db/
│       ├── script_tablas.sql             # Script SQL para crear tablas
│       ├── insertar_excel.py             # Inserta datos del Excel en la base de datos
│       ├── insertar_mention.py           # Inserta datos en la tabla mention
│       ├── insertar_metrics.py           # Inserta datos en la tabla tweet_metrics
│       ├── insertar_metamap.py           # Inserta datos en la tabla metamap
│       ├── insertar_references.py        # Inserta datos en la tabla referenced_tweet
│       ├── insertar_tweet.py             # Inserta datos en la tabla tweet
│       ├── insertar_tweet_keyword.py     # Inserta datos en la tabla tweet_keyword
│       ├── insertar_tweet_metamap.py     # Inserta datos en la tabla tweet_metamap
│       ├── insertar_tweet_slang.py       # Inserta datos en la tabla tweet_slang
│       ├── insertar_ubication.py         # Inserta datos en la tabla ubication
│       ├── insertar_user.py              # Inserta datos en la tabla user
│       ├── tweet_annotation.py           # Agreement por tweet
│       ├── final_annotation.py           # Agreement de metamap y slang
│       ├── annotation_tweet_metamap.py   # Agreement de tweet metamap
│       ├── annotation_tweet_slang.py     # Agreement de tweet slang
│       ├── final_annotation.py           # Agreement de metamap y slang
│       ├── main.py                       # Inserta datos a partir de archivos .json
│       └── utils.py                      # Lee los datos de los archivos.json
│   └── modelo/
│       ├── crear_dataset.py                   # Crear el dataset final
│       ├── preprocesado.py                    # Preprocesar el dataset final
│       ├── correlation.py                    # Preprocesar el dataset final
│       └── entrenamiento.py
├── results/
├── requirements.txt
├── .gitignore
└── README.md
```

## Requisitos

Instala los requisitos con:

    pip install -r requirements.txt

## Uso

1. Asegúrate de tener una base de datos MySQL corriendo.
2. Ejecuta `src/db/script_tablas.sql` para crear las tablas necesarias.
3. Corre `src/db/insertar_excel.py` para insertar los datos del Excel.
4. Usa `src/db/main.py` para cargar el resto de los datos desde archivos JSON.
5. Para el procesamiento y análisis de datos:
   - `src/modelo/final_annotation.py`: Evalúa el acuerdo final de cada término de MetaMap y Slang.
   - `src/modelo/annotation_tweet_metamap.py`: Evalúa el acuerdo final de MetaMap por tweet.
   - `src/modelo/annotation_tweet_slang.py`: Evalúa el acuerdo final de slang por tweet.
   - `src/modelo/tweet_annotation.py`: Evalúa el acuerdo entre slang y MetaMap por tweet.
   - `src/modelo/crear_dataset.py`: Genera el dataset final a partir de los datos procesados.
   - `src/modelo/preprocesado.py`: Realiza el preprocesamiento del dataset.

Consulta los comentarios en cada script para más detalles sobre su uso.

## Notas

- Los archivos `.json` con los tweets no están en el repositorio debido a su tamaño.

## Licencia

Este proyecto es de uso académico.
