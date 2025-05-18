import geopandas as gpd

# Cargar calles y POIs
calles = gpd.read_file("data/calles_multidigit_cercanas.geojson")
pois = gpd.read_file("data/pois_cercanos.geojson")

# Crear diccionario: link_id -> street_name
link_to_name = dict(zip(calles["link_id"], calles["street_name"]))

# Agregar nombre a los POIs según link_id
pois["street_name"] = pois["link_id"].map(link_to_name)

# Guardar POIs actualizados
pois.to_file("data/pois_cercanos.geojson", driver="GeoJSON")
print("✅ Campo 'street_name' agregado a pois_cercanos.geojson")
