import logging
import sys

def setup_logging(level=logging.INFO):
    """Настройка логирования."""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    
    logging.getLogger("src.services").setLevel(level)
    logging.getLogger("src.repositories").setLevel(level)
    
    return root_logger
