import os
import json

# Ruta de la carpeta y archivo de salida
naming_folder = "data/STREETS_NAMING_ADDRESSING"
output_file = "data/STREETS_NAMING_ADDRESSING.geojson"

# Acumulador de features
features = []

# Leer todos los archivos .geojson de naming
for filename in os.listdir(naming_folder):
    if filename.endswith(".geojson"):
        with open(os.path.join(naming_folder, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
            if data["type"] == "FeatureCollection":
                features.extend(data["features"])
            elif data["type"] == "Feature":
                features.append(data)

# Guardar archivo unificado
with open(output_file, "w", encoding="utf-8") as f:
    json.dump({
        "type": "FeatureCollection",
        "features": features
    }, f, indent=2)

print(f"✅ Naming unificado guardado en: {output_file}")
print(f"📄 Total de segmentos: {len(features)}")
