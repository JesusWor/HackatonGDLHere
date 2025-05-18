import pandas as pd
import json
import os
from shapely.geometry import LineString, Point
import geopandas as gpd

# === Configuración ===
pois_folder = "data/POIs"
calles_file = "data/calles.geojson"
output_file = "data/pois.geojson"
offset_m = 0.0001  # desplazamiento lateral aproximado

# === 1. Cargar calles ===
street_lines = {}
calles_gdf = gpd.read_file(calles_file)

for _, row in calles_gdf.iterrows():
    if row["geometry"].geom_type == "LineString":
        street_lines[row["link_id"]] = row["geometry"]

# === 2. Procesar POIs ===
features = []
for filename in os.listdir(pois_folder):
    if filename.endswith(".csv"):
        df = pd.read_csv(os.path.join(pois_folder, filename), low_memory=False)
        for _, row in df.iterrows():
            link_id = row.get("LINK_ID")
            perc = row.get("PERCFRREF", 50)
            side = str(row.get("POI_ST_SD", "")).strip().upper()
            name = row.get("POI_NAME")

            if pd.isna(link_id) or link_id not in street_lines:
                continue

            try:
                line = street_lines[link_id]
                point = line.interpolate(float(perc) / 100.0, normalized=True)

                # Desplazar lateralmente
                if side in ["L", "R"]:
                    coords = list(line.coords)
                    nearest_seg = min(
                        zip(coords[:-1], coords[1:]),
                        key=lambda seg: LineString(seg).distance(point)
                    )
                    dx = nearest_seg[1][0] - nearest_seg[0][0]
                    dy = nearest_seg[1][1] - nearest_seg[0][1]
                    length = (dx**2 + dy**2)**0.5
                    if length != 0:
                        offset_x = -dy / length * offset_m
                        offset_y = dx / length * offset_m
                        if side == "R":
                            offset_x *= -1
                            offset_y *= -1
                        point = Point(point.x + offset_x, point.y + offset_y)

                # Guardar punto como Feature
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [point.x, point.y]
                    },
                    "properties": {
                        "POI_ID": int(row["POI_ID"]),
                        "name": None if pd.isna(name) else name,
                        "link_id": int(link_id),
                        "side": side
                    }
                })
            except:
                continue

# === 3. Guardar GeoJSON final ===
geojson_obj = {
    "type": "FeatureCollection",
    "features": features
}

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(geojson_obj, f, indent=2, ensure_ascii=False)

print(f"✅ POIs generados: {len(features)}")
print(f"✅ Guardado en: {output_file}")
