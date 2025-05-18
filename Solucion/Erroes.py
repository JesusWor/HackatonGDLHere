import os
import json
import pandas as pd
from shapely.geometry import shape

# Función para cargar archivos GeoJSON sin geopandas
def load_geojson_files(folder_path):
    data_list = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.geojson'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
                for feature in geojson_data['features']:
                    props = feature['properties']
                    geom = shape(feature['geometry'])  # crea geometría Shapely
                    props['geometry'] = geom
                    data_list.append(props)

    return pd.DataFrame(data_list)

# Cargar POIs
pois_folder = "../data/POIs"
poi_df = load_geojson_files(pois_folder)

# Cargar calles
streets_folder = "../data/STREETS_NAV"
streets_df = load_geojson_files(streets_folder)

# Ejemplo de columnas disponibles
print("POIs: ",poi_df.columns)
print("Streets: ",streets_df.columns)
