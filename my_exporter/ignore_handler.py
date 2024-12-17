# my_exporter/ignore_handler.py

from pathspec import PathSpec


def load_ignore_patterns(ignore_file: str = '.gitignore') -> PathSpec:
    """Load ignore patterns from the specified ignore file.

    This function reads the ignore patterns (e.g., from a `.gitignore` file) and compiles them
    into a `PathSpec` object using the 'gitwildmatch' syntax. The resulting `PathSpec` can be
    used to match file paths against the ignore patterns.

    Args:
        ignore_file (str, optional): Path to the ignore file. Defaults to '.gitignore'.

    Returns:
        PathSpec: Compiled path specification for ignore patterns.

    Raises:
        FileNotFoundError: If the specified ignore file does not exist.
        IOError: If an I/O error occurs while reading the ignore file.

    Example:
        ignore_spec = load_ignore_patterns('.gitignore')
    """
    with open(ignore_file, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    spec = PathSpec.from_lines('gitwildmatch', lines)
    return spec


def load_include_patterns(include_file: str) -> PathSpec:
    """Load include patterns from the specified include file.

    This function reads the include patterns and compiles them into a `PathSpec` object
    using the 'gitwildmatch' syntax. The resulting `PathSpec` can be used to match file
    paths against the include patterns.

    Args:
        include_file (str): Path to the include file.

    Returns:
        PathSpec: Compiled path specification for include patterns.

    Raises:
        FileNotFoundError: If the specified include file does not exist.
        IOError: If an I/O error occurs while reading the include file.

    Example:
        include_spec = load_include_patterns('include_patterns.txt')
    """
    with open(include_file, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    spec = PathSpec.from_lines('gitwildmatch', lines)
    return spec
