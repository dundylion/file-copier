import hashlib
import os
import logging

logging.basicConfig(
    filename='file_hasher.log',  
    level=logging.ERROR,             
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_quick_hash(file_path: str, chunk_size: int = 1000000) -> Optional[str]:  
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
        logging.error(f'Ошибка чтения {file_path}: {str(e)}', exc_info=True)  
        return None