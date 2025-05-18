import os
import json
import pandas as pd
import requests
import math
from shapely.geometry import Point as ShapelyPoint
from pathlib import Path
from ultralytics import YOLO
from geojson import Feature, FeatureCollection, Point

# === Importar clave API desde archivo externo ===
root_path = Path(__file__).resolve().parent.parent.parent.parent
import sys
sys.path.append(str(root_path))
from clave import API_KEY

# === Configuración ===
ZOOM_LEVEL = 18
TILE_FORMAT = "png"
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === Funciones ===

def lat_lon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    n = 2.0 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return (x, y)

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
        print(f'❌ Error al descargar imagen para POI {poi_id} | Status: {response.status_code}')
        return False

def generar_overlays_json(pois, carpeta="output", tam_m=128):
    metros_por_grado = 111320
    delta = tam_m / metros_por_grado / 2
    overlays = []
    for d in pois:
        if d["Sin_detecciones"]:
            continue
        lat = float(d["lat"])
        lon = float(d["lon"])
        img_path = f"{carpeta}/poi_{d['POI_ID']}.png"
        bounds = [[lat - delta, lon - delta], [lat + delta, lon + delta]]
        overlays.append({
            "img": img_path.replace("\\", "/"),
            "bounds": bounds
        })
    with open("overlays.json", "w", encoding="utf-8") as f:
        json.dump(overlays, f, indent=2)
    print("✅ Archivo overlays.json generado.")

# === Cargar CSV plano personalizado ===
custom_csv_path = root_path / "data" / "calles_agrupadas_consentido_filtradasMulti.csv.xls"
df = pd.read_csv(custom_csv_path)
print(f"📦 POIs cargados: {len(df)}")

# === Cargar modelo YOLO ===
model = YOLO("yolov8x.pt")

# === Procesamiento ===
detecciones = []

for index, row in df.iterrows():
    poi_id = row["POI_ID"]
    lat = row["POI_LAT"]
    lon = row["POI_LON"]
    print(f"\n📍 Procesando POI {poi_id} | Coordenadas: lat={lat}, lon={lon}")

    if get_satellite_tile(lat, lon, ZOOM_LEVEL, TILE_FORMAT, API_KEY, poi_id):
        img_path = os.path.join(OUTPUT_FOLDER, f'poi_{poi_id}.{TILE_FORMAT}')
        results = model(img_path, imgsz=1536, conf=0.1, verbose=False)[0]

        cls_ids = results.boxes.cls.tolist() if results.boxes is not None else []
        labels = [model.names[int(cls)] for cls in cls_ids]
        print(f"🔍 Detecciones: {labels}")

        contiene_arbol = any(label in ["tree", "plant", "vegetation"] for label in labels)
        contiene_estructura = any(label in ["building", "house", "car", "truck"] for label in labels)
        contiene_tren = any(label == "train" for label in labels)
        contiene_agua = any(label in ["boat", "ship"] for label in labels)

        sin_deteccion = not any([contiene_arbol, contiene_estructura, contiene_tren, contiene_agua])

        if not sin_deteccion:
            results.save(filename=f"output/boxes_{poi_id}.jpg")

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

# === Guardar resultados
df_det = pd.DataFrame(detecciones)
df_det.to_csv("deteccion_pois.csv", index=False)
print("✅ Archivo deteccion_pois.csv generado.")

# === Guardar pois.geojson
features = []
for d in detecciones:
    if not d["Sin_detecciones"]:
        point = Point((d["lon"], d["lat"]))
        props = {
            "POI_ID": d["POI_ID"],
            "Objetos_detectados": d["Objetos_detectados"]
        }
        features.append(Feature(geometry=point, properties=props))

with open("pois.geojson", "w", encoding="utf-8") as f:
    json.dump(FeatureCollection(features), f, indent=2)
print("✅ Archivo pois.geojson generado.")

# === overlays.json
generar_overlays_json(detecciones)

# === Resumen
print("\n📊 Resumen:")
print("🌳 Árboles:", sum(d["Contiene_árbol"] for d in detecciones))
print("🏢 Estructuras:", sum(d["Contiene_estructura"] for d in detecciones))
print("🚆 Trenes:", sum(d["Contiene_tren"] for d in detecciones))
print("💧 Agua:", sum(d["Contiene_agua"] for d in detecciones))
print("❌ Sin detección:", sum(d["Sin_detecciones"] for d in detecciones))
