import os
import logging
from logging.handlers import RotatingFileHandler

#RotatingFileHandler Usage: https://medium.com/@dipan.saha/python-understanding-advanced-concepts-with-ease-day-10-logging-4ee875c5caaa

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

file_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,
    backupCount=5,
)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
