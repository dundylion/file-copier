from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileRecord:
    file_name_src: str
    file_name: str
    file_hash: str
    file_size: int
    copied_at: datetime = None