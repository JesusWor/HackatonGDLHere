import os
import pandas as pd
import geopandas as gpd

# Ruta a los geojsons y CSV
carpeta_geojson = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\datafinal\STREETS_NAMING_ADDRESSING'
csv_path = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\sospechosos.csv'

# Cargar CSV y normalizar nombres de columnas
df_csv = pd.read_csv(csv_path)
df_csv.columns = df_csv.columns.str.lower()

# Cargar y combinar geojsons
geojson_files = [f for f in os.listdir(carpeta_geojson) if f.endswith('.geojson')]
gdf_geo = pd.concat([gpd.read_file(os.path.join(carpeta_geojson, f)) for f in geojson_files], ignore_index=True)
gdf_geo.columns = gdf_geo.columns.str.lower()  # Normalizar también columnas del geojson

# Columnas L_ y R_
l_cols = [col for col in gdf_geo.columns if col.startswith("l_")]
r_cols = [col for col in gdf_geo.columns if col.startswith("r_")]

# Lista de cambios
cambios = []

# Iterar por los registros del CSV
for idx, row in df_csv.iterrows():
    link_id = row["link_id"]
    poi_st_sd = str(row["poi_st_sd"]).upper()

    # Buscar feature con el mismo link_id
    feature = gdf_geo[gdf_geo["link_id"] == link_id]
    if feature.empty:
        continue

    feature = feature.iloc[0]

    # Contar nulos
    l_nulls = sum(pd.isnull(feature[col]) for col in l_cols)
    r_nulls = sum(pd.isnull(feature[col]) for col in r_cols)

    # Evaluar si se debe cambiar el valor
    nuevo_valor = poi_st_sd
    if l_nulls > r_nulls and poi_st_sd == "L":
        nuevo_valor = "R"
    elif r_nulls > l_nulls and poi_st_sd == "R":
        nuevo_valor = "L"

    # Aplicar cambio si es necesario
    if nuevo_valor != poi_st_sd:
        cambios.append({
            "link_id del registro cambiado": link_id,
            "cambiado a": nuevo_valor
        })
        df_csv.at[idx, "poi_st_sd"] = nuevo_valor  # Actualizar en DataFrame original

# Guardar archivo de cambios
df_cambios = pd.DataFrame(cambios)
df_cambios.to_csv("cambios_poi_st_sd.csv", index=False)

# Guardar CSV corregido
df_csv.to_csv("sospechosos_actualizado.csv", index=False)

print("Análisis completado.")
print("Archivo de cambios: cambios_poi_st_sd.csv")
print("Archivo CSV actualizado: sospechosos_actualizado.csv")