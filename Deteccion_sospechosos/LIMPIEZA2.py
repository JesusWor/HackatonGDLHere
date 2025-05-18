import geopandas as gpd
import os

# Ruta a la carpeta que contiene los GeoJSONs
carpeta_geojson = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\datafinal\STREETS_NAMING_ADDRESSING'

columnas_necesarias = [
    "LINK_ID", "link_id", "ST_NAME", "FEAT_ID", "NUM_STNMES",
    "N_SHAPEPNT", "DIR_TRAVEL", "L_AREA_ID", "R_AREA ID",
    "L_POSTCODE", "R_POSTCODE", "RAMP", "POIACCESS", "MULTIDIGIT",
    "MANOEUVRE", "FULL_GEOM", "ROUTE_TYPE", "PERCFRREF",
    "ACT_ADDR", "ACT_ST_NAM", "ACT_ST_NUM", "ACT_POSTAL",
    "POI_ID", "FAC_TYPE", "POI_NAME", "POI_ST_NUM",
    "POI_ST_SD", "IN_VICIN", "geometry"
]

# Crear carpeta de salida
carpeta_salida = os.path.join(carpeta_geojson, "filtrados")
os.makedirs(carpeta_salida, exist_ok=True)

# Iterar sobre los archivos GeoJSON
for archivo in os.listdir(carpeta_geojson):
    if archivo.endswith('.geojson'):
        ruta_entrada = os.path.join(carpeta_geojson, archivo)
        try:
            gdf = gpd.read_file(ruta_entrada)

            # Identificar primera columna
            primera_columna = gdf.columns[0]

            # Filtrar columnas necesarias (solo las que existan)
            columnas_presentes = [col for col in columnas_necesarias if col in gdf.columns]

            # Incluir primera columna si no está en la lista ya
            if primera_columna not in columnas_presentes:
                columnas_finales = [primera_columna] + columnas_presentes
            else:
                columnas_finales = columnas_presentes

            # Añadir geometría si no está incluida
            if 'geometry' not in columnas_finales:
                columnas_finales.append('geometry')

            gdf_filtrado = gdf[columnas_finales]

            # Guardar resultado con nuevo nombre
            nombre_base = os.path.splitext(archivo)[0]
            archivo_salida = f"{nombre_base}_filtrado.geojson"
            ruta_salida = os.path.join(carpeta_salida, archivo_salida)
            gdf_filtrado.to_file(ruta_salida, driver="GeoJSON")

        except Exception as e:
            print(f"Error procesando {archivo}: {e}")

print("Procesamiento completo. Archivos filtrados guardados en:", carpeta_salida)
