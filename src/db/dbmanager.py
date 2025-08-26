import sqlite3
from datetime import datetime
from .models import FileRecord
from src.logging.logger import get_logger

logger = get_logger(__name__)

class DBManager:
    def __init__(self, db_path: str = "file_copier.db"):
        try:
            self.conn = sqlite3.connect(db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
        except sqlite3.Error as e:
            logger.critical(f"Database connection failed: {e}")
            raise RuntimeError(f"Cannot connect to database: {e}") from e

        try:
            self._init_db()
        except Exception as e:
            self.conn.close()
            raise

    def _init_db(self):
        """Создаёт таблицы и индексы."""
        cursor = self.conn.cursor()
        try:
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY,
                    file_name_src TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    copied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_file_hash ON files (file_hash);
                CREATE INDEX IF NOT EXISTS idx_file_size ON files (file_size);
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise

    def is_file_duplicate(self, file_hash: str, file_size: int) -> bool:
        """Проверяет, есть ли файл в БД."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT 1 FROM files WHERE file_hash = ? AND file_size = ? LIMIT 1",
            (file_hash, file_size)
        )
        return cursor.fetchone() is not None

    def add_file_record(self, fileinfo: FileRecord) -> bool:
        """Добавляет запись о файле. Возвращает True если успешно."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO files 
                (file_name_src, file_name, file_hash, file_size, copied_at) 
                VALUES (?, ?, ?, ?, ?)""",
                (fileinfo.file_name_src, fileinfo.file_name,
                 fileinfo.file_hash, fileinfo.file_size, datetime.now())
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Дубликат (параллельная запись)
            self.conn.rollback()
            return False
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Database error: {e}")
            raise

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()