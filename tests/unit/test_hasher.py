import unittest
import os
import hashlib
from pathlib import Path
from src.core.hasher import get_quick_hash

class TestFileHashing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        """Создаём тестовые файлы."""
        cls.test_dir = Path("tests/test_data")
        cls.test_dir.mkdir(exist_ok=True)

        # Пустой файл
        cls.empty_file = cls.test_dir / "empty.bin"
        cls.empty_file.write_bytes(b"")

        # Маленький файл (500 KB)
        cls.small_file = cls.test_dir / "small.bin"
        cls.small_file.write_bytes(os.urandom(500 * 1024))

        # Большой файл (2 MB)
        cls.large_file = cls.test_dir / "large.bin"
        cls.large_file.write_bytes(os.urandom(2 * 1024 * 1024))

    @classmethod
    def tearDownClass(cls):
        """Чистим тестовые файлы."""
        for file in [cls.empty_file, cls.small_file, cls.large_file]:
            file.unlink(missing_ok=True)

    def test_empty_file_hash(self):
        """Хеш пустого файла должен совпадать с MD5 от пустой строки."""
        self.assertEqual(
            get_quick_hash(self.empty_file),
            hashlib.md5(b"").hexdigest()
        )

    def test_small_file_hash(self):
        """Хеш маленького файла должен совпадать с полным MD5."""
        with open(self.small_file, "rb") as f:
            full_hash = hashlib.md5(f.read()).hexdigest()

        self.assertEqual(
            get_quick_hash(self.small_file),
            full_hash
        )

    def test_large_file_hash(self):
        """Хеш большого файла должен учитывать начало и конец."""
        chunk_size = 1024 * 1024  # 1 MB

        with open(self.large_file, "rb") as f:
            hasher = hashlib.md5()

            # Читаем первый мегабайт
            hasher.update(f.read(chunk_size))

            # Перемещаемся на конец файла и читаем последний мегабайт
            f.seek(-chunk_size, os.SEEK_END)
            hasher.update(f.read(chunk_size))

            manual_hash = hasher.hexdigest()

        self.assertEqual(
            get_quick_hash(self.large_file),
            manual_hash
        )


if __name__ == "__main__":
    unittest.main()