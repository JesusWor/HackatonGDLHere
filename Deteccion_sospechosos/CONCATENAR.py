import os
import geopandas as gpd
from shapely.geometry import LineString
import pandas as pd

# Ruta de la carpeta con los archivos GeoJSON
carpeta_geojson = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\datafinal\STREETS_NAMING_ADDRESSING'

# Cargar todos los geojson en un único GeoDataFrame
def cargar_geojsons(carpeta):
    frames = []
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.geojson'):
            path = os.path.join(carpeta, archivo)
            try:
                gdf = gpd.read_file(path)
                frames.append(gdf)
            except Exception as e:
                print(f"⚠️ Error procesando {archivo}: {e}")
    return pd.concat(frames, ignore_index=True)

# Cargar datos
gdf = cargar_geojsons(carpeta_geojson)

# Asegurar que existan columnas necesarias
if 'link_id' not in gdf.columns or 'geometry' not in gdf.columns or 'ST_NAME' not in gdf.columns:
    raise ValueError("Faltan columnas necesarias: 'link_id', 'geometry' o 'ST_NAME'")

# Agrupar por link_id
agrupado = gdf.groupby('link_id').agg({
    'geometry': lambda geoms: [coord for geom in geoms if geom is not None and geom.geom_type == 'LineString'
                               for coord in geom.coords],
    'ST_NAME': lambda names: list(set(name for name in names if pd.notna(name)))
}).reset_index()

# Renombrar columnas para claridad
agrupado.rename(columns={'geometry': 'all_coordinates', 'ST_NAME': 'all_ST_NAMES'}, inplace=True)

# Exportar a CSV opcional
agrupado.to_csv("calles_agrupadas.csv", index=False)

# Mostrar algunos resultados
print(agrupado.head())