# my_exporter/exporter.py

import os
import json
from typing import Optional, Set, TextIO

from pathspec import PathSpec
from .ignore_handler import load_ignore_patterns, load_include_patterns
from .logger import logger  # <-- Import the logger


def strip_notebook_outputs(nb_content: str) -> str:
    """
    Remove all output cells from a Jupyter notebook's JSON content.

    Args:
        nb_content (str): JSON string content of the Jupyter notebook.

    Returns:
        str: JSON string of the notebook with output cells removed.

    Example:
        .. code-block:: python

            stripped_nb = strip_notebook_outputs(original_nb_json)
    """
    logger.debug("Stripping notebook outputs.")
    try:
        nb = json.loads(nb_content)
        for cell in nb.get('cells', []):
            if cell.get('cell_type') == 'code':
                cell['outputs'] = []
                cell['execution_count'] = None
        logger.debug("Successfully stripped notebook outputs.")
        return json.dumps(nb, indent=2, ensure_ascii=False)
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse notebook JSON. Returning original content.")
        logger.debug(f"JSONDecodeError: {e}")
        return nb_content


def convert_nb_to_py(nb_stripped_json: str) -> str:
    """
    Convert a stripped Jupyter notebook JSON into a Python (.py) file representation.

    - **Code cells**: Included as-is.
    - **Markdown cells**: Commented out.
    - **Other cell types**: Commented out with an indication of unsupported type.

    Args:
        nb_stripped_json (str): JSON string of the notebook with outputs stripped.

    Returns:
        str: Python-compatible text representation of the notebook.

    Example:
        .. code-block:: python

            py_content = convert_nb_to_py(stripped_nb_json)
    """
    logger.debug("Converting stripped notebook JSON to .py format.")
    try:
        nb = json.loads(nb_stripped_json)
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse stripped notebook JSON. Returning original content.")
        logger.debug(f"JSONDecodeError: {e}")
        return nb_stripped_json

    lines = []
    for cell in nb.get('cells', []):
        cell_type = cell.get('cell_type', '')
        source = cell.get('source', [])
        if cell_type == 'markdown':
            # Comment out markdown cells
            lines.append("# === Markdown Cell ===")
            for line in source:
                lines.append("# " + line.rstrip('\n'))
            lines.append("")  # Blank line after cell
        elif cell_type == 'code':
            # Code cells: include the source code
            lines.append("# === Code Cell ===")
            for line in source:
                lines.append(line.rstrip('\n'))
            lines.append("")  # Blank line after cell
        else:
            # Indicate unsupported cell types
            lines.append(f"# === {cell_type.capitalize()} Cell (Unsupported) ===")
            for line in source:
                lines.append("# " + line.rstrip('\n'))
            lines.append("")

    logger.debug("Successfully converted notebook to .py format.")
    return "\n".join(lines)


def should_include(
    path: str,
    ignore_spec: Optional[PathSpec],
    include_spec: Optional[PathSpec]
) -> bool:
    """
    Determine whether a file or directory should be included based on ignore and include specifications.

    Args:
        path (str): The file or directory path.
        ignore_spec (Optional[PathSpec]): Spec for ignored patterns.
        include_spec (Optional[PathSpec]): Spec for included patterns.

    Returns:
        bool: True if the path should be included, False otherwise.

    Example:
        .. code-block:: python

            include = should_include(file_path, ignore_spec, include_spec)
    """
    logger.debug(f"Checking inclusion for path: {path}")

    # Normalize path to use forward slashes for consistent matching across OSes
    normalized_path = path.replace("\\", "/")
    logger.debug(f"Normalized path for matching: {normalized_path}")

    if include_spec and not ignore_spec:
        result = include_spec.match_file(normalized_path)
    elif ignore_spec and not include_spec:
        result = not ignore_spec.match_file(normalized_path)
    elif include_spec and ignore_spec:
        # Included if it matches the include pattern OR it doesn't match the ignore pattern
        result = include_spec.match_file(normalized_path) or not ignore_spec.match_file(normalized_path)
    else:
        result = True  # No specifications provided; include everything

    logger.debug(f"Path '{path}' inclusion result: {result}")
    return result


def has_included_content(
    dir_path: str,
    ignore_spec: Optional[PathSpec],
    include_spec: Optional[PathSpec],
    exclude_files: Optional[Set[str]]
) -> bool:
    """
    Recursively check if 'dir_path' contains at least one file (or subdirectory)
    that should be included. If it contains none, return False.

    Args:
        dir_path (str): The directory path to check.
        ignore_spec (Optional[PathSpec]): Spec for ignored patterns.
        include_spec (Optional[PathSpec]): Spec for included patterns.
        exclude_files (Optional[Set[str]]): Set of absolute file paths to exclude.

    Returns:
        bool: True if the directory contains included content, False otherwise.
    """
    # If the directory itself is explicitly ignored, no included content
    if ignore_spec and ignore_spec.match_file(dir_path):
        logger.debug(f"Directory '{dir_path}' is explicitly ignored.")
        return False

    try:
        entries = os.listdir(dir_path)
    except PermissionError:
        logger.warning(f"Permission denied accessing directory: {dir_path}")
        return False

    for entry in entries:
        path = os.path.join(dir_path, entry)
        abs_path = os.path.abspath(path)

        if os.path.isdir(path):
            # Recurse into subdirectories
            if has_included_content(path, ignore_spec, include_spec, exclude_files):
                return True
        else:
            # Skip excluded files
            if exclude_files and abs_path in exclude_files:
                continue

            # Check if the file is included
            if should_include(path, ignore_spec, include_spec):
                return True

    # No included content found in this directory
    logger.debug(f"No included content found in directory: {dir_path}")
    return False


def print_structure(
    root_dir: str = '.',
    out: Optional[TextIO] = None,
    prefix: str = '',
    ignore_spec: Optional[PathSpec] = None,
    include_spec: Optional[PathSpec] = None,
    exclude_files: Optional[Set[str]] = None
) -> None:
    """
    Recursively print a "tree" structure of directories and files.

    This function will:
      - Skip directories only if they're explicitly matched by ignore_spec.
      - Only include directories that contain at least one included file or subdirectory.
      - For files, apply the full should_include (ignore + include) logic.
      - Also exclude any files in `exclude_files`.

    Args:
        root_dir (str, optional): The directory to print the structure of. Defaults to '.'.
        out (Optional[TextIO], optional): The file object to write the output to. Defaults to sys.stdout.
        prefix (str, optional): The prefix string for the current level (used for formatting). Defaults to ''.
        ignore_spec (Optional[PathSpec], optional): Spec for ignored patterns. Defaults to None.
        include_spec (Optional[PathSpec], optional): Spec for included patterns. Defaults to None.
        exclude_files (Optional[Set[str]], optional): Set of absolute file paths to exclude. Defaults to None.

    Example:
        .. code-block:: python

            print_structure('/path/to/project', out=output_file, ignore_spec=ignore_spec, include_spec=include_spec)
    """
    if out is None:
        import sys
        out = sys.stdout

    logger.debug(f"Listing directory: {root_dir}")
    try:
        all_entries = sorted(os.listdir(root_dir))
    except PermissionError:
        logger.warning(f"Permission denied accessing directory: {root_dir}")
        out.write(prefix + "└── [Permission Denied]\n")
        return

    # Separate directories from files to handle them differently
    dirs = []
    files = []
    for entry in all_entries:
        path = os.path.join(root_dir, entry)
        abs_path = os.path.abspath(path)

        # Handle directories
        if os.path.isdir(path):
            # Only include the directory if it has included content
            if has_included_content(path, ignore_spec, include_spec, exclude_files):
                dirs.append(entry)
        else:
            # Handle files
            if exclude_files and abs_path in exclude_files:
                logger.debug(f"Excluding file from structure: {abs_path}")
                continue
            if should_include(path, ignore_spec, include_spec):
                files.append(entry)

    # Combine directories and files, sorted alphabetically
    combined = sorted(dirs) + sorted(files)

    for i, entry in enumerate(combined):
        path = os.path.join(root_dir, entry)
        is_last = (i == len(combined) - 1)
        connector = '└── ' if is_last else '├── '

        out.write(prefix + connector + entry)
        logger.debug(f"Added to structure: {path}")

        if entry in dirs:
            out.write("/\n")
            # Update the prefix for child entries
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_structure(
                path,
                out=out,
                prefix=new_prefix,
                ignore_spec=ignore_spec,
                include_spec=include_spec,
                exclude_files=exclude_files
            )
        else:
            # It's a file, just finish the line
            out.write("\n")


def export_folder_contents(
    root_dir: str = '.',
    output_file: str = 'output.txt',
    ignore_file: Optional[str] = '.gitignore',
    include_file: Optional[str] = None,
    exclude_notebook_outputs: bool = True,
    convert_notebook_to_py: bool = False
) -> None:
    """
    Export the contents of a folder into a single text file while respecting
    ignore patterns and optionally excluding or converting Jupyter notebook outputs.

    Args:
        root_dir (str, optional): Root directory to start exporting from. Defaults to '.'.
        output_file (str, optional): Name of the output text file. Defaults to 'output.txt'.
        ignore_file (Optional[str], optional): Path to the ignore file (e.g., .gitignore). Defaults to '.gitignore'.
        include_file (Optional[str], optional): Path to the include file. Defaults to None.
        exclude_notebook_outputs (bool, optional): If True, excludes output cells from .ipynb files. Defaults to True.
        convert_notebook_to_py (bool, optional): If True, converts .ipynb files to .py format. Defaults to False.

    Raises:
        IOError: If an I/O error occurs during file operations.

    Example:
        .. code-block:: python

            export_folder_contents(
                root_dir='path/to/project',
                output_file='exported_contents.txt',
                ignore_file='.gitignore',
                include_file='include_patterns.txt',
                exclude_notebook_outputs=False,
                convert_notebook_to_py=True
            )
    """
    logger.info(f"Exporting folder contents from '{root_dir}' to '{output_file}'.")
    logger.debug(
        f"Ignore file: {ignore_file}, Include file: {include_file}, "
        f"Exclude NB outputs: {exclude_notebook_outputs}, Convert NB: {convert_notebook_to_py}"
    )

    # Check if the ignore_file exists; if not, assign None and issue a warning
    if ignore_file is not None and not os.path.isfile(ignore_file):
        logger.warning(f"Ignore file '{ignore_file}' does not exist. Proceeding without ignore file.")
        ignore_file = None

    # Now safely attempt to load patterns, ignoring the file if it's None or doesn't exist
    try:
        # Load specs (may be None if file not found or not given)
        ignore_spec = load_ignore_patterns(ignore_file) if ignore_file else None
        include_spec = load_include_patterns(include_file) if include_file else None
        logger.debug("Loaded ignore and include patterns successfully.")

        # Log the compiled ignore patterns
        if ignore_spec:
            logger.info("Compiled Ignore Patterns:")
            for pat in ignore_spec.patterns:
                logger.info(f"Ignore pattern -> text: '{pat.pattern}', regex: '{pat.regex}'")

        # Log the compiled include patterns
        if include_spec:
            logger.info("Compiled Include Patterns:")
            for pat in include_spec.patterns:
                logger.info(f"Include pattern -> text: '{pat.pattern}', regex: '{pat.regex}'")

    except Exception as e:
        logger.exception(f"Failed to load ignore/include patterns: {e}")
        raise

    # Prepare a set of absolute paths to exclude from the directory structure and from file contents
    exclude_files: Set[str] = set()
    if ignore_file:
        exclude_files.add(os.path.abspath(ignore_file))
        logger.debug(f"Excluding ignore file from structure: {os.path.abspath(ignore_file)}")
    if include_file:
        exclude_files.add(os.path.abspath(include_file))
        logger.debug(f"Excluding include file from structure: {os.path.abspath(include_file)}")

    try:
        with open(output_file, 'w', encoding='utf-8', errors='replace') as out:
            logger.debug(f"Opened output file '{output_file}' for writing.")

            # 1) Print the directory structure
            out.write("================\n")
            out.write("DIRECTORY STRUCTURE\n")
            out.write("================\n\n")
            logger.debug("Writing directory structure header.")

            print_structure(
                root_dir,
                out=out,
                ignore_spec=ignore_spec,
                include_spec=include_spec,
                exclude_files=exclude_files
            )
            logger.debug("Directory structure printed successfully.")

            out.write("\n")
            # 2) Print the file contents
            out.write("================\n")
            out.write("FILE CONTENTS\n")
            out.write("================\n\n")
            logger.debug("Writing file contents header.")

            # Walk the directory tree, but only prune directories explicitly ignored
            for root, dirs, files in os.walk(root_dir):
                # 1) Prune directories that are explicitly matched by the ignore spec
                if ignore_spec:
                    dirs[:] = [
                        d for d in dirs
                        if not ignore_spec.match_file(os.path.join(root, d))
                    ]

                logger.debug(f"Walking through directory: {root}")

                # 2) Handle each file, applying full should_include
                for filename in files:
                    filepath = os.path.join(root, filename)
                    abs_filepath = os.path.abspath(filepath)

                    # Skip if it's the ignore or include file
                    if abs_filepath in exclude_files:
                        logger.debug(f"Skipping special file: {abs_filepath}")
                        continue

                    # Now do a normal should_include check for files
                    if not should_include(filepath, ignore_spec, include_spec):
                        logger.debug(f"Excluding file based on patterns: {filepath}")
                        continue

                    relpath = os.path.relpath(filepath, start=root_dir)
                    logger.debug(f"Processing file: {filepath} (Relative path: {relpath})")

                    # Print a header for this file's contents
                    out.write(f"==={relpath}===\n")

                    # Write the file content
                    try:
                        if filename.endswith('.ipynb'):
                            logger.debug(f"Handling Jupyter notebook: {filepath}")
                            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                                nb_content = f.read()
                            if convert_notebook_to_py:
                                logger.debug("Converting notebook to .py format.")
                                # When converting to .py, always strip outputs
                                stripped_content = strip_notebook_outputs(nb_content)
                                py_content = convert_nb_to_py(stripped_content)
                                out.write(py_content)
                            else:
                                if exclude_notebook_outputs:
                                    logger.debug("Stripping notebook outputs.")
                                    # Exclude outputs by stripping them
                                    stripped_content = strip_notebook_outputs(nb_content)
                                    out.write(stripped_content)
                                else:
                                    logger.debug("Including notebook outputs.")
                                    # Include original notebook content with outputs
                                    out.write(nb_content)
                        else:
                            # Regular file
                            logger.debug(f"Reading regular file: {filepath}")
                            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                                out.write(f.read())
                    except Exception as e:
                        logger.error(f"Failed to read file '{filepath}': {e}")
                        out.write(f"[Non-text or unreadable content: {e}]")

                    # Blank line after each file
                    out.write("\n\n")
    except IOError as e:
        logger.exception(f"Failed to write to output file '{output_file}': {e}")
        raise
    else:
        logger.info(f"Folder contents successfully exported to '{output_file}'.")
