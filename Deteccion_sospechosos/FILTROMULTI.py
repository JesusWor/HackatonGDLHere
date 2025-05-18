import pandas as pd

# Ruta al archivo enriquecido

csv_path = r'C:\Users\JoshC\OneDrive\Desktop\HACKATON-GUADALAHACKS 2025\calles_agrupadas_consentido.csv'

# Cargar datos
df = pd.read_csv(csv_path)

# Filtrar filas: conservar solo MULTIDIGIT ≠ "N" y DIR_TRAVEL == "B"
df_filtrado = df[(df['MULTIDIGIT'] != 'N')]

# Mostrar cuántas filas se eliminaron
filas_eliminadas = len(df) - len(df_filtrado)
print(f"Filtrado completo. Filas eliminadas: {filas_eliminadas}")
print(f"Filas finales: {len(df_filtrado)}")

# Guardar CSV filtrado
salida = csv_path.replace(".csv", "_filtradasMulti.csv")
df_filtrado.to_csv(salida, index=False)
print(f"Archivo filtrado guardado como: {salida}")