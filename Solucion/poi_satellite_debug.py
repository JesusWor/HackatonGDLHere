
import os
import json
import pandas as pd
import requests
import math
from shapely.geometry import shape, LineString
import sys
from pathlib import Path

# === Importar clave API desde archivo externo ===
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))
from clave import API_KEY

# === Configuración general ===
ZOOM_LEVEL = 18
TILE_FORMAT = "png"
OFFSET_METERS = 5

# === Funciones de geometría ===

def lat_lon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    n = 2.0 ** zoom
    x = int((lon_rad - (-math.pi)) / (2 * math.pi) * n)
    y = int((1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n)
    return (x, y)

def calculate_poi_coordinates(link_geom: LineString, perc: float, side: str, offset_meters=5):
    poi_point = link_geom.interpolate(perc * link_geom.length)
    if side == 'R':
        poi_point = poi_point.buffer(offset_meters).centroid
    elif side == 'L':
        poi_point = poi_point.buffer(-offset_meters).centroid
    return poi_point.y, poi_point.x

def get_satellite_tile(lat, lon, zoom, tile_format, api_key, poi_id):
    x, y = lat_lon_to_tile(lat, lon, zoom)
    url = f'https://maps.hereapi.com/v3/base/mc/{zoom}/{x}/{y}/{tile_format}&style=satellite.day&size=512?apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs("output", exist_ok=True)
        with open(f'output/poi_{poi_id}.{tile_format}', 'wb') as file:
            file.write(response.content)
        print(f'✅ POI {poi_id} tile saved.')
        return True
    else:
        print(f'❌ Failed to retrieve tile for POI {poi_id} | Status: {response.status_code}')
        return False

# === Función para cargar GeoJSON sin geopandas ===

def load_geojson_files(folder_path):
    data_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.geojson'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
                for feature in geojson_data['features']:
                    props = feature['properties']
                    geom = shape(feature['geometry'])
                    props['geometry'] = geom
                    data_list.append(props)
    return pd.DataFrame(data_list)

# === Función para cargar CSVs de POIs ===
def load_csv_files(folder_path):
    csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
    dataframes = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            dataframes.append(df)
        except Exception as e:
            print(f"⚠️ Error leyendo archivo {file}: {e}")
    return pd.concat(dataframes, ignore_index=True)


# === Cargar datos ===

pois_folder = "../data/filtrados_POIs"
streets_folder = "../data/nav_filtrados"

poi_df = load_csv_files(pois_folder)
streets_df = load_geojson_files(streets_folder)

# Verifica que los archivos se hayan cargado
print(f"Total POIs cargados: {len(poi_df)}")
print(f"Total calles cargadas: {len(streets_df)}")

# Normalizar columnas si es necesario
if "LINK_ID" in poi_df.columns and "LINK_ID" not in streets_df.columns and "link_id" in streets_df.columns:
    streets_df.rename(columns={"LINK_ID": "LINK_ID"}, inplace=True)

# === Generar imágenes satelitales ===

for index, poi in poi_df.iterrows():
    print(f"Procesando POI {poi.get('POI_ID')} con LINK_ID {poi.get('LINK_ID')}")

    link_matches = streets_df[streets_df["link_id"] == poi["LINK_ID"]]
    if link_matches.empty:
        print(f"LINK_ID {poi['LINK_ID']} no encontrado en dataset de calles.")
        continue

    link_geom = link_matches.iloc[0]["geometry"]
    perc = poi.get("PERCFRREF", 0.5)
    side = poi.get("POI_ST_SD", "R")

    try:
        lat, lon = calculate_poi_coordinates(link_geom, perc, side)
        print(f"Coordenadas para POI {poi['POI_ID']}: lat={lat}, lon={lon}")
        print(f"Descargando imagen para POI {poi['POI_ID']}...")
        get_satellite_tile(lat, lon, ZOOM_LEVEL, TILE_FORMAT, API_KEY, poi["POI_ID"])
    except Exception as e:
        print(f"❗ Error processing POI {poi['POI_ID']}: {e}")
