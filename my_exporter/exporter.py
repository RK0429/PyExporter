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
    if include_spec and not ignore_spec:
        result = include_spec.match_file(path)
    elif ignore_spec and not include_spec:
        result = not ignore_spec.match_file(path)
    elif include_spec and ignore_spec:
        result = include_spec.match_file(path) or not ignore_spec.match_file(path)
    else:
        result = True  # No specifications provided; include everything

    logger.debug(f"Path '{path}' inclusion result: {result}")
    return result


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

    This function filters out ignored files/directories using the provided specifications
    and excludes specific files if provided.

    Args:
        root_dir (str, optional): The directory to print the structure of. Defaults to '.'.
        out (Optional[TextIO], optional): The file object to write the output to. Defaults to standard output.
        prefix (str, optional): The prefix string for the current level (used for formatting). Defaults to ''.
        ignore_spec (Optional[PathSpec], optional): Spec for ignored patterns. Defaults to None.
        include_spec (Optional[PathSpec], optional): Spec for included patterns. Defaults to None.
        exclude_files (Optional[Set[str]], optional): Set of absolute file paths to exclude from the structure. Defaults to None.

    Raises:
        None

    Example:
        .. code-block:: python

            print_structure('/path/to/project', out=output_file, ignore_spec=ignore_spec, include_spec=include_spec)
    """
    if out is None:
        import sys
        out = sys.stdout

    logger.debug(f"Listing directory: {root_dir}")
    try:
        entries = sorted(os.listdir(root_dir))
    except PermissionError:
        logger.warning(f"Permission denied accessing directory: {root_dir}")
        out.write(prefix + "└── [Permission Denied]\n")
        return

    # Filter entries based on include and ignore specifications
    entries = [
        e for e in entries
        if should_include(os.path.join(root_dir, e), ignore_spec, include_spec)
    ]

    for i, entry in enumerate(entries):
        path = os.path.join(root_dir, entry)
        abs_path = os.path.abspath(path)

        # Exclude specific files from the directory structure
        if exclude_files and abs_path in exclude_files:
            logger.debug(f"Excluding file from structure: {abs_path}")
            continue

        # Choose the connector symbol based on position
        connector = '├── ' if i < len(entries) - 1 else '└── '

        # Write directory or file name
        out.write(prefix + connector + entry + "\n")
        logger.debug(f"Added to structure: {path}")

        if os.path.isdir(path):
            # Update prefix for child entries
            if i < len(entries) - 1:
                new_prefix = prefix + "│   "
            else:
                new_prefix = prefix + "    "
            print_structure(
                path,
                out=out,
                prefix=new_prefix,
                ignore_spec=ignore_spec,
                include_spec=include_spec,
                exclude_files=exclude_files
            )


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
    logger.debug(f"Ignore file: {ignore_file}, Include file: {include_file}, "
                 f"Exclude NB outputs: {exclude_notebook_outputs}, Convert NB: {convert_notebook_to_py}")

    # Check if the ignore_file exists; if not, assign None and issue a warning
    if ignore_file is not None and not os.path.isfile(ignore_file):
        logger.warning(f"Ignore file '{ignore_file}' does not exist. Proceeding without ignore file.")
        ignore_file = None

    # Now safely attempt to load patterns, ignoring the file if it's None or doesn't exist
    try:
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

    # Prepare a set of absolute paths to exclude from the directory structure and file contents
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

            # Print the directory structure header
            out.write("================\n")
            out.write("DIRECTORY STRUCTURE\n")
            out.write("================\n\n")
            logger.debug("Writing directory structure header.")

            # Print the directory structure, excluding ignore_file and include_file
            print_structure(
                root_dir,
                out=out,
                ignore_spec=ignore_spec,
                include_spec=include_spec,
                exclude_files=exclude_files  # Pass the set of files to exclude
            )
            logger.debug("Directory structure printed successfully.")

            out.write("\n")
            # Print the file contents header
            out.write("================\n")
            out.write("FILE CONTENTS\n")
            out.write("================\n\n")
            logger.debug("Writing file contents header.")

            # Now, write the file contents
            for root, dirs, files in os.walk(root_dir):
                # Modify dirs in-place based on include and ignore specifications
                dirs[:] = [
                    d for d in dirs
                    if should_include(os.path.join(root, d), ignore_spec, include_spec)
                ]
                logger.debug(f"Walking through directory: {root}")

                for filename in files:
                    filepath = os.path.join(root, filename)
                    abs_filepath = os.path.abspath(filepath)

                    # Skip the ignore and include files themselves so they don't appear in output
                    if ignore_file and abs_filepath == os.path.abspath(ignore_file):
                        logger.debug(f"Skipping ignore file: {abs_filepath}")
                        continue
                    if include_file and abs_filepath == os.path.abspath(include_file):
                        logger.debug(f"Skipping include file: {abs_filepath}")
                        continue

                    if not should_include(filepath, ignore_spec, include_spec):
                        logger.debug(f"Excluding file based on patterns: {filepath}")
                        continue  # Skip files that should not be included

                    relpath = os.path.relpath(filepath, start=root_dir)
                    logger.debug(f"Processing file: {filepath} (Relative path: {relpath})")

                    # Print the file path with '===' on both sides
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
                            # Regular files
                            logger.debug(f"Reading regular file: {filepath}")
                            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                                out.write(f.read())
                    except Exception as e:
                        logger.error(f"Failed to read file '{filepath}': {e}")
                        out.write(f"[Non-text or unreadable content: {e}]")
                    out.write("\n\n")
    except IOError as e:
        logger.exception(f"Failed to write to output file '{output_file}': {e}")
        raise
    else:
        logger.info(f"Folder contents successfully exported to '{output_file}'.")
