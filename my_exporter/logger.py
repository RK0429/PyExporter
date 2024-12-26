# my_exporter/logger.py
import logging

# Create a named logger to distinguish log messages (you can pick any name)
logger = logging.getLogger("my_exporter")
logger.setLevel(logging.INFO)  # Set the base logging level (DEBUG, INFO, WARNING, etc.)

# Create a console handler that outputs to stdout
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # This handler will log DEBUG and above

# Define a simple format
formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(formatter)

# Attach the handler to the logger
logger.addHandler(console_handler)
