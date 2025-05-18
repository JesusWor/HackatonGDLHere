import json

# Cargar naming
with open("data/STREETS_NAMING_ADDRESSING.geojson", "r", encoding="utf-8") as f:
    naming_data = json.load(f)

# Diccionario link_id -> nombre
link_id_to_name = {}
for feat in naming_data["features"]:
    props = feat["properties"]
    link_id = props.get("link_id")
    name = props.get("ST_NAME") or props.get("ST_NM_BASE")
    if link_id and name:
        link_id_to_name[int(link_id)] = name.strip().upper()

# Cargar calles
with open("data/calles.geojson", "r", encoding="utf-8") as f:
    calles_data = json.load(f)

# Agregar nombre a cada calle
for feat in calles_data["features"]:
    lid = feat["properties"].get("link_id")
    if lid in link_id_to_name:
        feat["properties"]["street_name"] = link_id_to_name[lid]

# Guardar archivo actualizado
with open("data/calles.geojson", "w", encoding="utf-8") as f:
    json.dump(calles_data, f, indent=2)

print("✅ Nombres de calle añadidos a 'calles.geojson'")
