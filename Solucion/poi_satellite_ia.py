import os
import json
import pandas as pd
import requests
import math
from shapely.geometry import shape, LineString
import sys
from pathlib import Path
from ultralytics import YOLO
from geojson import Feature, FeatureCollection, Point

# === Importar clave API desde archivo externo ===
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))
from clave import API_KEY

# === Configuración general ===
ZOOM_LEVEL = 18
TILE_FORMAT = "png"
OFFSET_METERS = 5
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Funciones de geometría ===

def lat_lon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    n = 2.0 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
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
        file_path = os.path.join(OUTPUT_FOLDER, f'poi_{poi_id}.{tile_format}')
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f'✅ Imagen guardada: POI {poi_id}')
        return True
    else:
        print(f'❌ Error descargando tile para POI {poi_id} | Status: {response.status_code}')
        return False

# === Cargar archivos ===

def load_geojson_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.geojson'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
                data_list = []
                for feature in geojson_data['features']:
                    props = feature['properties']
                    geom = shape(feature['geometry'])
                    props['geometry'] = geom
                    data_list.append(props)
                print(f"✅ Usando archivo GeoJSON: {filename}")
                return pd.DataFrame(data_list)
    raise FileNotFoundError("❌ No se encontró ningún archivo .geojson en la carpeta.")

def load_csv_files(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            try:
                path = os.path.join(folder_path, file)
                print(f"✅ Usando archivo CSV: {file}")
                return pd.read_csv(path)
            except Exception as e:
                print(f"⚠️ Error leyendo archivo {file}: {e}")
    raise FileNotFoundError("❌ No se encontró ningún archivo .csv en la carpeta.")

# === Directorios de entrada ===

pois_folder = "../data/filtrados_POIs"
streets_folder = "../data/nav_filtrados"

poi_df = load_csv_files(pois_folder).head(500)
streets_df = load_geojson_files(streets_folder)

print(f"Total POIs cargados: {len(poi_df)}")
print(f"Total calles cargadas: {len(streets_df)}")

# Normalizar columnas
if "LINK_ID" in poi_df.columns and "LINK_ID" not in streets_df.columns and "link_id" in streets_df.columns:
    streets_df.rename(columns={"link_id": "LINK_ID"}, inplace=True)

# === Cargar modelo YOLOv8 ===
model = YOLO("yolov8n.pt")  # Usa yolov8s.pt para más precisión si deseas

# === Procesamiento POIs + Detección ===

detecciones = []

for index, poi in poi_df.iterrows():
    poi_id = poi.get('POI_ID')
    link_id = poi.get('LINK_ID')
    print(f"📍 Procesando POI {poi_id} con LINK_ID {link_id}")

    link_matches = streets_df[streets_df["LINK_ID"] == link_id]
    if link_matches.empty:
        print(f"⚠️ LINK_ID {link_id} no encontrado.")
        continue

    link_geom = link_matches.iloc[0]["geometry"]
    perc = float(poi.get("PERCFRREF", 0.5) or 0.5)
    side = poi.get("POI_ST_SD", "R") or "R"

    try:
        lat, lon = calculate_poi_coordinates(link_geom, perc, side)
        print(f"🧭 Coordenadas: lat={lat}, lon={lon}")

        if get_satellite_tile(lat, lon, ZOOM_LEVEL, TILE_FORMAT, API_KEY, poi_id):
            img_path = os.path.join(OUTPUT_FOLDER, f'poi_{poi_id}.{TILE_FORMAT}')
            results = model(img_path, verbose=False)[0]
            labels = [r.name for r in results.boxes]

            contiene_arbol = any(label in ["tree", "plant"] for label in labels)
            contiene_estructura = any(label in ["building", "house", "skyscraper"] for label in labels)
            contiene_tren = any(label in ["train"] for label in labels)
            contiene_agua = any(label in ["boat", "ship"] for label in labels)

            sin_deteccion = not any([contiene_arbol, contiene_estructura, contiene_tren, contiene_agua])

            detecciones.append({
                "POI_ID": poi_id,
                "Contiene_árbol": contiene_arbol,
                "Contiene_estructura": contiene_estructura,
                "Contiene_tren": contiene_tren,
                "Contiene_agua": contiene_agua,
                "Sin_detecciones": sin_deteccion,
                "Objetos_detectados": ", ".join(set(labels)) if labels else "Ninguno",
                "lat": lat,
                "lon": lon
            })

    except Exception as e:
        print(f"❗ Error con POI {poi_id}: {e}")

# === Guardar resultados ===

resultados_df = pd.DataFrame(detecciones)
resultados_df.to_csv("deteccion_pois.csv", index=False)
print("✅ Archivo de resultados 'deteccion_pois.csv' generado.")


# Crear lista de features donde sí hay detección
features = []
for d in detecciones:
    if not d["Sin_detecciones"]:
        point = Point((d["lon"], d["lat"]))
        props = {
            "POI_ID": d["POI_ID"],
            "Objetos_detectados": d["Objetos_detectados"]
        }
        features.append(Feature(geometry=point, properties=props))

# Guardar como GeoJSON
geojson_pois = FeatureCollection(features)
with open("pois.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson_pois, f, indent=2)
print("✅ Archivo pois.geojson generado.")

