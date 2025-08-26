from __future__ import annotations
import hashlib
import os
from src.logging.logger import get_logger

logger = get_logger(__name__)

def get_quick_hash(file_path: str, chunk_size: int = 1024*1024) -> str | None:
    try:  
        with open(file_path, 'rb') as f:  
            file_size = os.path.getsize(file_path)
            hasher = hashlib.md5()  
            hasher.update(f.read(chunk_size))
            if file_size > chunk_size:  
                f.seek(-chunk_size, os.SEEK_END)  
                hasher.update(f.read())
            return hasher.hexdigest()  
    except (FileNotFoundError, PermissionError, OSError) as e:  
        logger.error(f'Read error {file_path}: {str(e)}', exc_info=True)
        raise FileNotFoundError('File Access Error. See logs') from e
        return None