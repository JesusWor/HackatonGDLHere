import os
import json
import pandas as pd
import requests
import math
from shapely.geometry import shape, LineString
import sys
from pathlib import Path
from ultralytics import YOLO

# === Importar clave API desde archivo externo ===
root_path = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(root_path))
from clave import API_KEY

ZOOM_LEVEL = 18
TILE_FORMAT = "png"
OFFSET_METERS = 5
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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
        return True
    return False

def load_geojson_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.geojson'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
                data = []
                for feat in geojson_data['features']:
                    props = feat['properties']
                    props['geometry'] = shape(feat['geometry'])
                    data.append(props)
                return pd.DataFrame(data)
    raise FileNotFoundError("No se encontró ningún .geojson.")

def load_csv_files(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            return pd.read_csv(os.path.join(folder_path, file))
    raise FileNotFoundError("No se encontró ningún .csv.")

# === Directorios de entrada ===
script_dir = Path(__file__).resolve().parent.parent.parent.parent
pois_folder = script_dir/"data"/"filtrados_POIs"
streets_folder = script_dir/"data"/"nav_filtrados"

poi_df = load_csv_files(pois_folder).head(500)
streets_df = load_geojson_files(streets_folder)

if "LINK_ID" in poi_df.columns and "LINK_ID" not in streets_df.columns and "link_id" in streets_df.columns:
    streets_df.rename(columns={"link_id": "LINK_ID"}, inplace=True)

model = YOLO("yolov8n.pt")

detecciones = []
for _, poi in poi_df.iterrows():
    poi_id = poi.get('POI_ID')
    link_id = poi.get('LINK_ID')
    link_geom = streets_df[streets_df["LINK_ID"] == link_id]
    if link_geom.empty: continue
    geom = link_geom.iloc[0]["geometry"]
    perc = float(poi.get("PERCFRREF", 0.5) or 0.5)
    side = poi.get("POI_ST_SD", "R") or "R"
    try:
        lat, lon = calculate_poi_coordinates(geom, perc, side)
        if get_satellite_tile(lat, lon, ZOOM_LEVEL, TILE_FORMAT, API_KEY, poi_id):
            img_path = f"{OUTPUT_FOLDER}/poi_{poi_id}.{TILE_FORMAT}"
            results = model(img_path, verbose=False)[0]
            labels = [r.name for r in results.boxes]

            contiene_arbol = any(l in ["tree", "plant"] for l in labels)
            contiene_estructura = any(l in ["building", "house", "skyscraper"] for l in labels)
            contiene_tren = any(l == "train" for l in labels)
            contiene_agua = any(l in ["boat", "ship"] for l in labels)
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

# Guardar resultados
resultados_df = pd.DataFrame(detecciones)
resultados_df.to_csv("deteccion_pois.csv", index=False)

# Generar overlays.json
def generar_overlays_json(data):
    overlays = []
    meters_per_deg = 111320
    deg_offset = 256 / meters_per_deg / 2
    for d in data:
        lat, lon = float(d["lat"]), float(d["lon"])
        overlays.append({
            "img": f"output/poi_{d['POI_ID']}.png",
            "bounds": [[lat - deg_offset, lon - deg_offset], [lat + deg_offset, lon + deg_offset]]
        })
    with open("overlays.json", "w", encoding="utf-8") as f:
        json.dump(overlays, f, indent=2)

generar_overlays_json(detecciones)
print("✅ Todo completado.")
