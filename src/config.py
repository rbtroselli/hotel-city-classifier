# config.py

from pathlib import Path

current_dir = Path(__file__).resolve().parent

# paths
DATABASE_FOLDER_PATH = current_dir.parent / 'database' 
DDL_FOLDER_PATH = current_dir.parent / 'database' / 'ddl'
LOG_FOLDER_PATH = current_dir.parent / 'logs'
API_KEYS_FILE_PATH = current_dir / 'keys.py'

DEBUG_MODE = False

# print(DATABASE_PATH / 'test.db')
