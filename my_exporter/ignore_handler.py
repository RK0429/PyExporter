# my_exporter/ignore_handler.py

from pathspec import PathSpec


def load_ignore_patterns(ignore_file: str = '.gitignore'):
    with open(ignore_file, 'r') as f:
        lines = f.read().splitlines()
    spec = PathSpec.from_lines('gitwildmatch', lines)
    return spec


def load_include_patterns(include_file: str):
    """
    Load include patterns from the specified file.

    Parameters:
    - include_file (str): Path to the include file.

    Returns:
    - PathSpec: Compiled path specification for include patterns.
    """
    with open(include_file, 'r') as f:
        lines = f.read().splitlines()
    spec = PathSpec.from_lines('gitwildmatch', lines)
    return spec
