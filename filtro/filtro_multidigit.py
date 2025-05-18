import json

# === Archivos de entrada y salida
calles_file = "data/calles.geojson"
pois_file = "data/pois.geojson"
calles_out = "data/calles_multidigit.geojson"
pois_out = "data/pois_multidigit.geojson"

# === Cargar calles
with open(calles_file, "r", encoding="utf-8") as f:
    calles_data = json.load(f)

# === Filtrar calles MULTIDIGIT = "Y"
calles_multi = [feat for feat in calles_data["features"]
                if feat["properties"].get("MULTIDIGIT", "").strip().upper() == "Y"]

# === Guardar solo calles MULTIDIGIT
with open(calles_out, "w", encoding="utf-8") as f:
    json.dump({
        "type": "FeatureCollection",
        "features": calles_multi
    }, f, indent=2)

# === Obtener link_ids MULTIDIGIT
multidigit_links = set(feat["properties"]["link_id"] for feat in calles_multi)

# === Cargar POIs
with open(pois_file, "r", encoding="utf-8") as f:
    pois_data = json.load(f)

# === Filtrar POIs cuyo link_id esté en las calles MULTIDIGIT
pois_multi = [feat for feat in pois_data["features"]
              if feat["properties"].get("link_id") in multidigit_links]

# === Guardar POIs filtrados
with open(pois_out, "w", encoding="utf-8") as f:
    json.dump({
        "type": "FeatureCollection",
        "features": pois_multi
    }, f, indent=2)

print(f"✅ Calles MULTIDIGIT guardadas en: {calles_out} ({len(calles_multi)} tramos)")
print(f"✅ POIs sobre calles MULTIDIGIT guardados en: {pois_out} ({len(pois_multi)} puntos)")
