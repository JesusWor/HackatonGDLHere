import pandas as pd
import os
import ast
from shapely.geometry import LineString, Point
from geopy.distance import geodesic

# === Rutas ===
pois_folder = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\datafinal\POIs\pois_filtrados'
tramos_path = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\calles_agrupadas_consentido_filtradasMulti.csv'
grupos_path = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\grupos_link_id_por_nombre.csv'
output_path = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\SOSPECHOSOS.csv'

# === Cargar tramos ===
df_tramos = pd.read_csv(tramos_path)
df_tramos['all_coordinates'] = df_tramos['all_coordinates'].apply(lambda x: ast.literal_eval(x))
link_geom = {row['link_id']: LineString(row['all_coordinates']) for _, row in df_tramos.iterrows()}

# === Cargar grupos ===
df_grupos = pd.read_csv(grupos_path)
link_to_grupo = {}
for _, row in df_grupos.iterrows():
    grupo_id = row['Grupo']
    for lid in row['Link_IDs'].split(','):
        link_to_grupo[int(lid.strip())] = grupo_id

# === Analizar POIs ===
sospechosos = []

for archivo in os.listdir(pois_folder):
    if not archivo.endswith('.csv'):
        continue

    pois_path = os.path.join(pois_folder, archivo)
    df_pois = pd.read_csv(pois_path)

    for _, poi in df_pois.iterrows():
        try:
            link_id = int(poi['LINK_ID'])
            perc = float(poi['PERCFRREF'])
            poi_id = poi['POI_ID']
            lado_poi = str(poi['POI_ST_SD']).strip().upper()
        except:
            continue

        if link_id not in link_geom:
            continue

        linea = link_geom[link_id]
        if linea.length == 0:
            continue

        # Coordenada del POI en su propio tramo
        poi_coord = linea.interpolate(perc * linea.length)
        grupo_id = link_to_grupo.get(link_id)
        if not grupo_id:
            continue

        # Tramos del mismo grupo
        link_ids_grupo = df_grupos[df_grupos['Grupo'] == grupo_id]['Link_IDs'].values[0]
        link_ids_grupo = [int(x.strip()) for x in link_ids_grupo.split(',') if int(x.strip()) != link_id]

        tramo_mas_cercano = None
        distancia_original = float('inf')

        for lid in link_ids_grupo:
            if lid not in link_geom:
                continue
            other_line = link_geom[lid]
            closest_point = other_line.interpolate(other_line.project(poi_coord))
            dist = geodesic((poi_coord.y, poi_coord.x), (closest_point.y, closest_point.x)).meters
            if dist < distancia_original:
                distancia_original = dist
                tramo_mas_cercano = other_line

        if not (3 <= distancia_original <= 80):
            continue  # No se considera sospechoso

        # === Dirección lateral del POI ===
        d = 0.00005  # desplazamiento ~5m lateral
        pos = perc * linea.length
        delta = 0.01 * linea.length
        before = linea.interpolate(max(pos - delta, 0))
        after = linea.interpolate(min(pos + delta, linea.length))

        dx = after.x - before.x
        dy = after.y - before.y
        norm = (dx**2 + dy**2)**0.5
        if norm == 0:
            continue

        # Movimiento a la derecha del camino
        px = poi_coord.x + d * (-dy / norm)
        py = poi_coord.y + d * (dx / norm)
        derecha_coord = Point(px, py)

        # Distancia desde punto derecho al tramo más cercano
        closest_derecha = tramo_mas_cercano.interpolate(tramo_mas_cercano.project(derecha_coord))
        distancia_derecha = geodesic((derecha_coord.y, derecha_coord.x), (closest_derecha.y, closest_derecha.x)).meters

        # Clasificación direccional
        if abs(distancia_derecha - distancia_original) < 0.5:
            direccion = 'NEUTRO'
        elif distancia_derecha > distancia_original:
            direccion = 'IZQUIERDO'
        else:
            direccion = 'DERECHO'

        # Revisión contra POI_ST_SD
        valido = False
        if direccion == 'NEUTRO':
            continue
        elif direccion == 'DERECHO' and lado_poi == 'R':
            valido = True
        elif direccion == 'IZQUIERDO' and lado_poi == 'L':
            valido = True

        if valido:
            sospechosos.append({
                'POI_ID': poi_id,
                'LINK_ID': link_id,
                'Grupo': grupo_id,
                'Distancia_m': round(distancia_original, 2),
                'POI_ST_SD': lado_poi,
                'Direccion': direccion,
                'POI_LAT': round(poi_coord.y, 6),
                'POI_LON': round(poi_coord.x, 6)
            })

# === Guardar CSV ===
df_out = pd.DataFrame(sospechosos)
df_out.to_csv(output_path, index=False, encoding='utf-8')
print(f"{len(df_out)} POIs sospechosos guardados en: {output_path}")