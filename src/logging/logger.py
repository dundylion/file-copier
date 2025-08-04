import logging
import logging.handlers
import os
from pathlib import Path

def get_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """
    Создает и настраивает логгер с консольным и файловым выводом.
    
    Args:
        name: Имя логгера (обычно __name__ вызывающего модуля)
        log_dir: Директория для сохранения логов (относительно корня проекта)
    
    Returns:
        Настроенный экземпляр logging.Logger
    """
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Минимальный уровень для захвата сообщений

    # Формат сообщений
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Консольный вывод (только WARNING и выше)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. Файловый вывод (все сообщения DEBUG и выше)
    Path(log_dir).mkdir(exist_ok=True)  # Создаем директорию для логов
    log_file = os.path.join(log_dir, 'file_copier.log')
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger