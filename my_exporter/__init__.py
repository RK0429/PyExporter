# my_exporter/__init__.py

from .exporter import export_folder_contents
from .ignore_handler import load_ignore_patterns, load_include_patterns  # Updated

__all__ = [
    'export_folder_contents',
    'load_ignore_patterns',
    'load_include_patterns',  # Added to __all__
]
