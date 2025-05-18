import pandas as pd
import os

# Ruta a la carpeta que contiene los CSVs
carpeta_csv = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\datafinal\POIs'

columnas_necesarias = [
    "LINK_ID", "link_id", "POI_ID", "FAC_TYPE", "POI_NAME",
    "POI_ST_NUM", "ST_NAME", "POI_ST_SD", "IN_VICIN",
    "PERCFRREF", "ACT_ADDR", "ACT_ST_NAM", "ACT_ST_NUM", "ACT_POSTAL"
]

# Crear carpeta de salida si no existe
carpeta_salida = os.path.join(carpeta_csv, "filtrados")
os.makedirs(carpeta_salida, exist_ok=True)

# Iterar sobre los archivos CSV
for archivo in os.listdir(carpeta_csv):
    if archivo.endswith('.csv'):
        ruta_entrada = os.path.join(carpeta_csv, archivo)
        df = pd.read_csv(ruta_entrada)

        # Identificar primera columna
        primera_columna = df.columns[0]

        # Filtrar columnas necesarias (solo las que existan)
        columnas_presentes = [col for col in columnas_necesarias if col in df.columns]

        # Incluir primera columna al inicio si no está ya incluida
        if primera_columna not in columnas_presentes:
            columnas_finales = [primera_columna] + columnas_presentes
        else:
            columnas_finales = columnas_presentes

        df_filtrado = df[columnas_finales]

        # Guardar resultado con el nuevo nombre
        nombre_base = os.path.splitext(archivo)[0]
        archivo_salida = f"{nombre_base}_filtered.csv"
        ruta_salida = os.path.join(carpeta_salida, archivo_salida)
        df_filtrado.to_csv(ruta_salida, index=False)

print("Procesamiento completo. Archivos filtrados guardados en:", carpeta_salida)