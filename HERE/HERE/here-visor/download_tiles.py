import os, json, requests
from shapely.geometry import shape
from tile_utils import lat_lon_to_tile, tile_coords_to_bounds
import time

import geopandas as gpd

API_KEY = 'nkw9-t4-EKAVoWdhKrPxNMW_s-rr8sX9gi_kvmdAzWU'
TILE_SIZE = 512
ZOOM = 16
OUT_FOLDER = "tiles"
os.makedirs(OUT_FOLDER, exist_ok=True)

gdf = gpd.read_file("chunks.geojson")
downloaded = []
overlays = []

MAX_RETRIES = 3
MAX_TILES = 10
tile_count = 0

for feature in gdf["geometry"]:
    if tile_count >= MAX_TILES:
        break
    # ... el resto del ciclo
    tile_count += 1


    centroid = feature.centroid
    lat, lon = centroid.y, centroid.x
    x, y = lat_lon_to_tile(lat, lon, ZOOM)

    url = f"https://1.aerial.maps.ls.hereapi.com/maptile/2.1/maptile/newest/satellite.day/{ZOOM}/{x}/{y}/{TILE_SIZE}/png8?apikey={API_KEY}"
    filename = f"{ZOOM}_{x}_{y}.png"
    filepath = os.path.join(OUT_FOLDER, filename)

    attempts = 0
    while attempts < MAX_RETRIES:
        if not os.path.exists(filepath):
            r = requests.get(url)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(r.content)
                print(f"✅ Saved {filename}")
                break  # salir del ciclo si tuvo éxito
            elif r.status_code == 429:
                print(f"⏳ Rate limited on tile {x},{y}. Waiting...")
                time.sleep(2.5)  # espera más tiempo si te bloquearon
                attempts += 1
            else:
                print(f"❌ Failed {x},{y}: {r.status_code}")
                break
        else:
            break
    else:
        print(f"❌ Gave up on tile {x},{y} after {MAX_RETRIES} retries.")

    # Generar bounds aunque no se descargue
    bbox = list(feature.bounds)
    lon1, lat1, lon2, lat2 = bbox
    leaflet_bounds = [[lat1, lon1], [lat2, lon2]]
    overlays.append({
        "img": f"tiles/{filename}",
        "bounds": leaflet_bounds
    })
    time.sleep(0.3)  # pausa corta después de cada tile



# Sobrescribe el bounds por el del chunk real (no el del tile)
    bbox = list(feature.bounds)
    lon1, lat1, lon2, lat2 = bbox
    leaflet_bounds = [[lat1, lon1], [lat2, lon2]]
    overlays.append({
        "img": f"tiles/{filename}",
        "bounds": leaflet_bounds
    })


# Guardar bounds para Leaflet
with open("overlays.json", "w", encoding="utf-8") as f:
    json.dump(overlays, f, indent=2)
print("✔️ overlays.json guardado.")
