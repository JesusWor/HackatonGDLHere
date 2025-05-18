import os
import json

# Ruta de entrada y salida
streets_folder = "data/STREETS_NAV"
output_file = "data/calles.geojson"

# Lista para recolectar features
features = []

# Leer todos los archivos .geojson de la carpeta
for filename in os.listdir(streets_folder):
    if filename.endswith(".geojson"):
        path = os.path.join(streets_folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data["type"] == "FeatureCollection":
                features.extend(data["features"])
            elif data["type"] == "Feature":
                features.append(data)

# Construir nuevo GeoJSON unificado
output = {
    "type": "FeatureCollection",
    "features": features
}

# Guardar archivo de salida
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"✅ Calles unificadas guardadas en: {output_file}")
print(f"🛣️ Total de tramos: {len(features)}")
