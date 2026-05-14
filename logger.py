import logging
import sys

# Configurazione del formato del log
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_logger(name: str):
    logger = logging.getLogger(name)
    
    # Se il logger ha già degli handler, non aggiungerne altri (evita duplicati)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Handler per stampare sulla console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console_handler)
        
    return logger