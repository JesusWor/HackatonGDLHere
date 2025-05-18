import geopandas as gpd
from shapely.geometry import LineString, Point
import pandas as pd

# === Archivos ===
calles_file = "data/calles_multidigit_cercanas.geojson"
pois_file = "data/pois_cercanos.geojson"
pois_out = "data/pois_enmedio_perpendicular.geojson"
calles_out = "data/calles_enmedio_perpendicular.geojson"
buffer_m = 80  # distancia lateral

# === 1. Cargar datos y reproyectar
gdf_calles = gpd.read_file(calles_file).to_crs(epsg=6372)
gdf_pois = gpd.read_file(pois_file).to_crs(epsg=6372)

# Índice espacial de calles
calles_sindex = gdf_calles.sindex

# Acumuladores
pois_enmedio_idx = []
calles_enmedio_ids = set()

# === 2. Recorrer POIs
for i, poi in gdf_pois.iterrows():
    poi_geom = poi.geometry
    side = poi.get("side")
    link_id = poi.get("link_id")
    name = poi.get("street_name")

    if side not in ["L", "R"] or name is None or link_id is None:
        continue

    # Obtener calle base del POI
    base = gdf_calles[gdf_calles["link_id"] == link_id]
    if base.empty:
        continue
    base_line = base.iloc[0].geometry

    # Proyectar punto sobre la línea base
    proj_dist = base_line.project(poi_geom)
    nearest_pt = base_line.interpolate(proj_dist)

    # Encontrar segmento más cercano
    seg = None
    coords = list(base_line.coords)
    for j in range(len(coords) - 1):
        seg_line = LineString([coords[j], coords[j + 1]])
        if seg_line.project(nearest_pt) < seg_line.length:
            seg = (coords[j], coords[j + 1])
            break
    if seg is None:
        continue

    # Calcular vector perpendicular
    x1, y1 = seg[0]
    x2, y2 = seg[1]
    dx = x2 - x1
    dy = y2 - y1
    length = (dx**2 + dy**2)**0.5
    if length == 0:
        continue
    perp_dx = -dy / length
    perp_dy = dx / length

    # Direccion lateral
    mult = 1 if side == "L" else -1
    end_x = poi_geom.x + mult * perp_dx * buffer_m
    end_y = poi_geom.y + mult * perp_dy * buffer_m
    ray = LineString([poi_geom, Point(end_x, end_y)])

    # Buscar calles cercanas con el mismo nombre y distinto link_id
    bbox = ray.bounds
    posibles = list(calles_sindex.intersection(bbox))
    candidatos = gdf_calles.iloc[posibles]
    candidatos = candidatos[
        (candidatos["street_name"] == name) &
        (candidatos["link_id"] != link_id)
    ]

    # Verificar si la línea intersecta alguna calle
    for _, calle in candidatos.iterrows():
        if ray.intersects(calle.geometry):
            pois_enmedio_idx.append(i)
            calles_enmedio_ids.add(link_id)
            calles_enmedio_ids.add(calle["link_id"])
            break

# === 3. Guardar resultados
gdf_pois_enmedio = gdf_pois.loc[pois_enmedio_idx].to_crs(epsg=4326)
gdf_pois_enmedio.to_file(pois_out, driver="GeoJSON")

gdf_calles_enmedio = gdf_calles[gdf_calles["link_id"].isin(calles_enmedio_ids)].to_crs(epsg=4326)
gdf_calles_enmedio.to_file(calles_out, driver="GeoJSON")

print(f"✅ POIs en medio detectados: {len(gdf_pois_enmedio)}")
print(f"✅ Calles relacionadas detectadas: {len(gdf_calles_enmedio)}")
