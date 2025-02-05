import logging
import os

from logging_config import formatter

# Create a logger for the api package
api_logger = logging.getLogger('api')
api_logger.setLevel(logging.DEBUG)  # Set the logging level for the api package

# Create a file handler for the api log
api_log_file_path = os.path.join(os.path.dirname(__file__), 'api.log')
api_file_handler = logging.FileHandler(api_log_file_path)
api_file_handler.setLevel(logging.DEBUG)

# Use the same formatter as the global logger
api_file_handler.setFormatter(formatter)

# Add the handler to the api logger
api_logger.addHandler(api_file_handler)