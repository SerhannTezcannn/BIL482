import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_db_path = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "fantasy.db"))

if os.path.exists(data_db_path):
    DB_NAME = data_db_path
else:
    DB_NAME = os.path.join(BASE_DIR, "fantasy.db")

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
