# Análisis de los Efectos del Consumo Recreativo de Drogas en Publicaciones de Twitter

Este proyecto forma parte de mi Trabajo de Fin de Grado y tiene como objetivo analizar el uso y mención de drogas en publicaciones de Twitter a lo largo de varios años.

## Estructura del Proyecto

```
TFG/
├── data/
│   └── raw/                                          # Archivos JSON con tweets (no incluidos en el repo por tamaño)
│        └── Drugs.xlsx                               # Excel con información de drogas, palabras clave, slang, metamap y anotaciones
│   └── processed/                                    # Archivos procesados
│        ├── dataset_final.xlsx                       # Dataset final
│        ├── dataset_final_vectorizado.xlsx           # Dataset final vectorizado y normalizado
│        └── matriz_correlacion.xlsx                  # Matriz de correlación
├── notebook/                                         # Notebooks de Jupyter para análisis y experimentación
│   ├── analisis_descriptivo.ipynb                 # Análisis descriptivo de los datos
│   ├── analisis_metamap_slang.ipynb               # Análisis de MetaMap y Slang
│   └── analisis_modelo.ipynb                      # Entrenamiento y evaluación de modelos
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
│       └── utils.py                      # Lee los datos de los archivos .json
│   └── modelo/
│       ├── crear_dataset.py                 # Crear el dataset final
│       ├── preprocesado.py                  # Preprocesar el dataset final
│       ├── correlation.py                   # Calcula la matriz de correlacion del dataset
│       ├── cost-sensitive.py                # Entrenamiento con enfoque cost-sensitive
│       ├── oversampling_in.py               # Oversampling antes de la validación cruzada
│       ├── oversampling_out.py              # Oversampling durante la validación cruzada
│       └── sin_oversampling.py              # Entrenamiento sin oversampling
├── results/                                 # Carpeta donde se guardan todas las gráficas generadas
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
   - `src/db/final_annotation.py`: Evalúa el acuerdo final de cada término de MetaMap y Slang.
   - `src/db/annotation_tweet_metamap.py`: Evalúa el acuerdo final de MetaMap por tweet.
   - `src/db/annotation_tweet_slang.py`: Evalúa el acuerdo final de slang por tweet.
   - `src/db/tweet_annotation.py`: Evalúa el acuerdo entre slang y MetaMap por tweet.
6. Para entrenar el modelo:
   - `src/modelo/crear_dataset.py`: Genera el dataset final a partir de los datos procesados.
   - `src/modelo/preprocesado.py`: Realiza el preprocesamiento del dataset.
   - `src/modelo/correlation.py`: Analiza la correlación entre variables del dataset.
   - Ejecuta uno de los siguientes scripts según el enfoque de entrenamiento que desees utilizar:
     - `src/modelo/cost-sensitive.py`: Entrena el modelo usando un enfoque cost-sensitive.
     - `src/modelo/oversampling_in.py`: Entrena el modelo aplicando oversampling en la fase previa a cross-validation.
     - `src/modelo/oversampling_out.py`: Entrena el modelo aplicando oversampling en la fase de cross-validation.
     - `src/modelo/sin_oversampling.py`: Entrena el modelo sin aplicar oversampling.
   - Revisa los resultados y métricas generados tras el entrenamiento en la carpeta `results/`.

Consulta los comentarios en cada script para más detalles sobre su uso.

## Notas

- Los archivos `.json` con los tweets no están en el repositorio debido a su tamaño.

## Licencia

Este proyecto es de uso académico.
