import pandas as pd
from collections import defaultdict
import networkx as nx

# Ruta al CSV original
csv_path = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\calles_agrupadas_consentido_filtradasMulti.csv'

# Ruta de salida para el CSV de grupos
output_path = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\grupos_link_id_por_nombre.csv'

# Cargar archivo
df = pd.read_csv(csv_path)

# Procesar columna de nombres
df['all_ST_NAMES'] = df['all_ST_NAMES'].astype(str).apply(lambda x: [name.strip() for name in x.split(',') if name.strip()])

# Crear diccionario nombre → set de link_id
nombre_to_ids = defaultdict(set)
for _, row in df.iterrows():
    for name in row['all_ST_NAMES']:
        nombre_to_ids[name].add(row['link_id'])

# Crear grafo de link_ids conectados por nombres compartidos
G = nx.Graph()
for ids in nombre_to_ids.values():
    ids = list(ids)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            G.add_edge(ids[i], ids[j])

# Detectar componentes conexas
componentes = list(nx.connected_components(G))

# Crear DataFrame con los grupos
grupos_data = []
for idx, grupo in enumerate(componentes, 1):
    grupo_ordenado = sorted(grupo)
    grupos_data.append({
        'Grupo': idx,
        'Link_IDs': ', '.join(map(str, grupo_ordenado))
    })

df_grupos = pd.DataFrame(grupos_data)

# Guardar a CSV
df_grupos.to_csv(output_path, index=False, encoding='utf-8')
print(f"CSV generado en: {output_path}")