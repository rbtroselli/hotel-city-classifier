from pathlib import Path

# other files
from _keys import MAPQUEST_API_KEY
from _geocoder_exceptions import GEOCODER_EXCEPTION_DICT

# paths
current_dir = Path(__file__).resolve().parent
DB_FOLDER_PATH = current_dir.parent / 'database' 
DDL_FOLDER_PATH = current_dir.parent / 'database' / 'ddl'
LOG_FOLDER_PATH = current_dir.parent / 'logs'
API_KEYS_FILE_PATH = current_dir / 'keys.py'

# flags
DEBUG_MODE = False

# print(DATABASE_PATH / 'test.db')
