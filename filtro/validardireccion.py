import geopandas as gpd
import pandas as pd

# === Archivos ===
pois_file = "data/pois_enmedio_perpendicular.geojson"
naming_file = "data/STREETS_NAMING_ADDRESSING.geojson"
output_valid = "data/pois_validados_flexible.geojson"
output_invalid = "data/pois_lado_equivocado_flexible.geojson"

# === Cargar archivos
pois = gpd.read_file(pois_file)
naming = gpd.read_file(naming_file)

# === Extraer columnas necesarias del naming
naming_reduced = naming[["link_id", "L_REFADDR", "R_REFADDR"]]

# === Hacer merge por link_id
merged = pois.merge(naming_reduced, on="link_id", how="left")

# === Validar con lógica flexible
def validar_lado_flexible(row):
    if row["side"] == "L":
        return pd.notna(row["L_REFADDR"]) or pd.notna(row["R_REFADDR"])
    elif row["side"] == "R":
        return pd.notna(row["R_REFADDR"]) or pd.notna(row["L_REFADDR"])
    return False

# Aplicar
merged["valido"] = merged.apply(validar_lado_flexible, axis=1)

# === Separar válidos e inválidos
validos = merged[merged["valido"] == True].copy()
invalidos = merged[merged["valido"] == False].copy()

# === Convertir a GeoDataFrame y guardar
validos = gpd.GeoDataFrame(validos, geometry="geometry", crs=pois.crs)
invalidos = gpd.GeoDataFrame(invalidos, geometry="geometry", crs=pois.crs)

validos.to_file(output_valid, driver="GeoJSON")
invalidos.to_file(output_invalid, driver="GeoJSON")

print(f"✅ POIs válidos (con algún REFADDR): {len(validos)}")
print(f"❌ POIs eliminados (sin REFADDR): {len(invalidos)}")
