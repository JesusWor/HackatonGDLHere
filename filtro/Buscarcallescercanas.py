import geopandas as gpd
import json

# === Archivos ===
calles_file = "data/calles_multidigit.geojson"
pois_file = "data/pois.geojson"
calles_out = "data/calles_multidigit_cercanas.geojson"
pois_out = "data/pois_cercanos.geojson"
max_dist_m = 80  # metros

# === 1. Cargar calles MULTIDIGIT
gdf = gpd.read_file(calles_file)
gdf = gdf.to_crs(epsg=6372)

# === 2. Buscar calles cercanas con mismo nombre y diferente link_id
tramos_cercanos = []
link_ids_result = set()
sindex = gdf.sindex  # índice espacial global

for i, row in gdf.iterrows():
    name = row.get("street_name")
    link_id = row.get("link_id")
    geom = row.geometry

    if not name or link_id is None:
        continue

    # Buscar índices espaciales en todo el GeoDataFrame
    posibles_idx = list(sindex.intersection(geom.buffer(max_dist_m).bounds))
    posibles_calles = gdf.iloc[posibles_idx]

    # Filtrar por nombre e ID diferente
    candidatos = posibles_calles[
        (posibles_calles["street_name"] == name) &
        (posibles_calles["link_id"] != link_id)
    ]

    for _, other in candidatos.iterrows():
        if geom.distance(other.geometry) <= max_dist_m:
            tramos_cercanos.append(row)
            link_ids_result.add(link_id)
            break


# === 3. Crear GeoDataFrame de calles resultantes
gdf_cercanos = gpd.GeoDataFrame(tramos_cercanos, geometry="geometry").drop_duplicates(subset=["link_id"])
gdf_cercanos = gdf_cercanos.set_crs(epsg=6372).to_crs(epsg=4326)
gdf_cercanos.to_file(calles_out, driver="GeoJSON")

print(f"✅ Calles cercanas guardadas: {calles_out} ({len(gdf_cercanos)} tramos)")

# === 4. Cargar y filtrar POIs
with open(pois_file, "r", encoding="utf-8") as f:
    pois_data = json.load(f)

# Crear diccionario link_id -> street_name
link_to_name = dict(zip(gdf["link_id"], gdf["street_name"]))

pois_filtrados = []
for feat in pois_data["features"]:
    poi_link = feat["properties"].get("link_id")
    if poi_link in link_ids_result:
        # Asignar nombre si existe
        feat["properties"]["street_name"] = link_to_name.get(poi_link)
        pois_filtrados.append(feat)

# === 5. Guardar POIs actualizados
with open(pois_out, "w", encoding="utf-8") as f:
    json.dump({
        "type": "FeatureCollection",
        "features": pois_filtrados
    }, f, indent=2)

print(f"✅ POIs filtrados y actualizados guardados: {pois_out} ({len(pois_filtrados)} puntos)")
