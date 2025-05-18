# import os
# from pathlib import Path
# from dotenv import load_dotenv


# env_path = Path('.') / '../.env'
# load_dotenv(dotenv_path=env_path)

# API_KEY = os.getenv("API_KEY")
# print(API_KEY)
# # from decouple import config
# # print(config('API_KEY'))
import sys
from pathlib import Path

# Ruta al directorio raíz (uno arriba)
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from clave import API_KEY, API_URL
print(API_KEY)
print(API_URL)