import sqlite3
from datetime import datetime
from sys import exc_info

from .models import FileRecord
from src.logging.logger import get_logger

logger = get_logger(__name__)

class DBManager:
    def __init__(self, db_path: str = "file_copier.db"):
        self.conn = sqlite3.connect(db_path)
        try:
            self._init_db()
        except (sqlite3.Error, OperationalError) as e:
            logger.error(f"Error initializing database: {str(e)}")

    def _init_db(self):
        """Создаёт таблицы при первом запуске."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY,
                    file_name_src TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    copied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}", exc_info=True)

    def is_file_duplicate(self, file_hash: str, file_size: int) -> bool:
        """Проверяет, есть ли файл в БД."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT 1 FROM files WHERE file_hash=? AND file_size=? LIMIT 1",
            (file_hash, file_size)
        )
        return cursor.fetchone() is not None

    def add_file_record(self, fileinfo: FileRecord):
        """Добавляет запись о скопированном файле."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO files (file_name_src, file_name, file_hash, file_size, copied_at) VALUES (?, ?, ?, ?, ?)",
                    (fileinfo.file_name_src, fileinfo.file_name, fileinfo.file_hash, fileinfo.file_size, datetime.now())
                )
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error adding file record: {str(e)}", exc_info=True)