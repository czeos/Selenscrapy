import logging
import os
from logging.handlers import RotatingFileHandler
from logging_config import formatter

# Create a logger for the api package
vk_logger = logging.getLogger('vk')
vk_logger.setLevel(logging.DEBUG)  # Set the logging level for the api package

# Create a file handler for the api log
vk_log_file_path = os.path.join(os.path.dirname(__file__), 'vk.log')
vk_file_handler = RotatingFileHandler(vk_log_file_path, mode='a', maxBytes=10000, backupCount=0, encoding=None, delay=0)

vk_file_handler.setLevel(logging.DEBUG)

# Use the same formatter as the global logger
vk_file_handler.setFormatter(formatter)

# Add the handler to the api logger
vk_logger.addHandler(vk_file_handler)


