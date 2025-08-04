import sqlite3
from contextlib import closing

def init_db(db_path="file_cache.db"):
    """Инициализирует БД и создаёт таблицы."""
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS copied_files
                        (original_name TEXT PRIMARY KEY,
                         new_name TEXT,
                         camera TEXT,
                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        conn.commit()