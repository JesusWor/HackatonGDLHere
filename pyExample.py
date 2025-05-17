import json

# Paso 1: Leer el archivo GeoJSON
#archivo = input("Nombre del archivo GeoJSON (incluye .geojson): ")

archivo= "data/STREETS_NAMING_ADDRESSING/SREETS_NAMING_ADDRESSING_4815075.geojson"
archivo= "SREETS_NAMING_ADDRESSING_4815075.geojson"

try:
    with open(archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)

        # Paso 2: Verificar que tenga una colección de 'features'
        if data["type"] != "FeatureCollection":
            raise ValueError("El archivo no contiene una colección de features válida.")

        features = data["features"]

        # Paso 3: Mostrar todas las llaves posibles dentro de 'properties'
        if not features:
            raise ValueError("No hay features en el archivo.")

        ejemplo_props = features[0]["properties"]
        print("\nPropiedades disponibles:")
        keys = list(ejemplo_props.keys())
        for i, key in enumerate(keys):
            print(f"{i}: {key}")

        # Paso 4: Elegir una propiedad
        idx = int(input("\nIngresa el número de la propiedad que quieres imprimir: "))
        clave = keys[idx]

        # Paso 5: Imprimir esa propiedad para cada feature
        print(f"\nValores de la propiedad '{clave}':")
        for f in features:
            print(f["properties"].get(clave, "No disponible"))

    def agrupar(street):
        #Pienso que, primero hay que agrupar todas las calles que se repitan (quiza mediante su nombre y otros datos que nos muestren que son la misma [tal vez como la direccion]). Estas calles tenerlas guardadas en una lista que se acceda mediante el nombre y, luego de tener agrupadas todas las calles iguales, obtenet un promedio de sus coordenadas.

        return street


except FileNotFoundError:
    print("Archivo no encontrado.")
except (ValueError, IndexError) as e:
    print(f"Error en selección o formato: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
