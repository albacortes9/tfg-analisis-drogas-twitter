Análisis de los Efectos del Consumo Recreativo de Drogas en Publicaciones de Twitter
=====================================================================

Este proyecto forma parte de mi Trabajo de Fin de Grado y tiene como objetivo analizar el uso y mención de drogas en publicaciones de Twitter a lo largo de varios años.

Estructura del Proyecto
------------------------
```
TFG/
├── data/
│   └── raw/                     # Archivos JSON con tweets (no incluidos en el repo por tamaño)
│        └── Drugs.xlsx          # Excel con información de drogas y palabras clave
├── src/
│   └── db/
│       ├── script_tablas.sql             # Script SQL para crear tablas
│       ├── insertar_excel.py             # Inserta datos del Excel en la base de datos
│       ├── insertar_mention.py           # Inserta datos en la tabla mention
│       ├── insertar_metrics.py           # Inserta datos en la tabla tweet_metrics
│       ├── insertar_references.py        # Inserta datos en la tabla referenced_tweet
│       ├── insertar_tweet.py             # Inserta datos en la tabla tweet
│       ├── insertar_tweet_keyword.py     # Inserta datos en la tabla tweet_keyword
│       ├── insertar_ubication.py         # Inserta datos en la tabla ubication
│       ├── insertar_user.py              # Inserta datos en la tabla user
│       ├── main.py                       # Inserta datos a partir de archivos .json
│       └── utils.py                      # Lee los datos de los archivos.json
├── requirements.txt
├── .gitignore
└── README.txt
```

Requisitos
----------

Instala los requisitos con:

    pip install -r requirements.txt

Uso
---

1. Asegúrate de tener una base de datos MySQL corriendo.
2. Ejecuta `src/db/script_tablas.sql` para crear las tablas necesarias.
3. Corre `src/db/insert_excel.py` para insertar los datos del Excel.
4. Usa `src/db/main.py` para cargar el resto de los datos desde archivos JSON.

Notas
-----

- Los archivos `.json` con los tweets no están en el repositorio debido a su tamaño.

Licencia
--------

Este proyecto es de uso académico.
