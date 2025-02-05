import logging
import os

# Create a global logger
global_logger = logging.getLogger('global')
global_logger.setLevel(logging.DEBUG)

# Create a file handler for the global log
global_log_file_path = os.path.join(os.path.dirname(__file__), 'global.log')
global_file_handler = logging.FileHandler(global_log_file_path)
global_file_handler.setLevel(logging.DEBUG)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
global_file_handler.setFormatter(formatter)

# Add the handler to the global logger
global_logger.addHandler(global_file_handler)