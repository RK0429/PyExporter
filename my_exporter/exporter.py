# my_exporter/exporter.py

import os
import json
from .ignore_handler import load_ignore_patterns, load_include_patterns


def strip_notebook_outputs(nb_content):
    """
    Given the JSON string content of a Jupyter notebook, remove output cells
    and return the modified JSON string.
    """
    try:
        nb = json.loads(nb_content)
        # Jupyter notebooks typically have a 'cells' field that is a list of cells.
        for cell in nb.get('cells', []):
            if cell.get('cell_type') == 'code':
                cell['outputs'] = []  # Clear outputs
                cell['execution_count'] = None
        return json.dumps(nb, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        # If JSON is invalid, return the original content
        return nb_content


def should_include(path, ignore_spec, include_spec):
    """
    Determine whether a file or directory should be included based on ignore and include specs.

    Parameters:
    - path (str): The file or directory path.
    - ignore_spec (PathSpec or None): Spec for ignored patterns.
    - include_spec (PathSpec or None): Spec for included patterns.

    Returns:
    - bool: True if the path should be included, False otherwise.
    """
    if include_spec and not ignore_spec:
        return include_spec.match_file(path)
    elif ignore_spec and not include_spec:
        return not ignore_spec.match_file(path)
    elif include_spec and ignore_spec:
        return include_spec.match_file(path) or not ignore_spec.match_file(path)
    else:
        return True  # No specs provided; include everything


def print_structure(root_dir='.', out=None, prefix='', ignore_spec=None, include_spec=None, exclude_files=None):
    """
    Recursively print a "tree" structure of directories and files.
    This function filters out ignored files/directories using the specs
    and excludes specific files if provided.

    Parameters:
    - root_dir (str): The directory to print the structure of.
    - out (file object): The file object to write the output to.
    - prefix (str): The prefix string for the current level (used for formatting).
    - ignore_spec (PathSpec or None): Spec for ignored patterns.
    - include_spec (PathSpec or None): Spec for included patterns.
    - exclude_files (set or None): Set of absolute file paths to exclude from the structure.
    """
    try:
        entries = sorted(os.listdir(root_dir))
    except PermissionError:
        out.write(prefix + "└── [Permission Denied]\n")
        return

    # Filter entries based on include and ignore specs
    entries = [
        e for e in entries
        if should_include(os.path.join(root_dir, e), ignore_spec, include_spec)
    ]

    for i, entry in enumerate(entries):
        path = os.path.join(root_dir, entry)
        abs_path = os.path.abspath(path)

        # Exclude specific files from the directory structure
        if exclude_files and abs_path in exclude_files:
            continue

        # Choose the connector symbol based on position
        connector = '├── ' if i < len(entries) - 1 else '└── '

        # Write directory or file name
        out.write(prefix + connector + entry + "\n")

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
    root_dir='.',
    output_file='output.txt',
    ignore_file='.gitignore',
    include_file=None,  # New parameter
    exclude_notebook_outputs=True  # New parameter to control notebook output exclusion
):
    """
    Export the contents of a folder into a single text file while respecting
    .gitignore patterns and optionally excluding Jupyter notebook outputs.

    Parameters:
    - root_dir (str): Root directory to start exporting from.
    - output_file (str): Name of the output text file.
    - ignore_file (str): Path to the ignore file (e.g., .gitignore).
    - include_file (str or None): Path to the include file.
    - exclude_notebook_outputs (bool): If True, excludes output cells from .ipynb files.
    """
    ignore_spec = load_ignore_patterns(ignore_file) if ignore_file else None
    include_spec = load_include_patterns(include_file) if include_file else None

    # Prepare a set of absolute paths to exclude from the directory structure and file contents
    exclude_files = set()
    if ignore_file:
        exclude_files.add(os.path.abspath(ignore_file))
    if include_file:
        exclude_files.add(os.path.abspath(include_file))

    with open(output_file, 'w', encoding='utf-8', errors='replace') as out:
        # Print the directory structure header
        out.write("================\n")
        out.write("DIRECTORY STRUCTURE\n")
        out.write("================\n\n")

        # Print the directory structure, excluding ignore_file and include_file
        print_structure(
            root_dir,
            out=out,
            ignore_spec=ignore_spec,
            include_spec=include_spec,
            exclude_files=exclude_files  # Pass the set of files to exclude
        )

        out.write("\n")
        # Print the file contents header
        out.write("================\n")
        out.write("FILE CONTENTS\n")
        out.write("================\n\n")

        # Now, write the file contents
        for root, dirs, files in os.walk(root_dir):
            # Modify dirs in-place based on include and ignore specs
            dirs[:] = [
                d for d in dirs
                if should_include(os.path.join(root, d), ignore_spec, include_spec)
            ]

            for filename in files:
                filepath = os.path.join(root, filename)
                abs_filepath = os.path.abspath(filepath)

                # Skip the ignore and include files themselves so they don't appear in output
                if ignore_file and abs_filepath == os.path.abspath(ignore_file):
                    continue
                if include_file and abs_filepath == os.path.abspath(include_file):
                    continue

                if not should_include(filepath, ignore_spec, include_spec):
                    continue  # Skip files that should not be included

                relpath = os.path.relpath(filepath, start=root_dir)

                # Print the file path with '===' on both sides
                out.write(f"==={relpath}===\n")

                # Write the file content
                try:
                    if exclude_notebook_outputs and filename.endswith('.ipynb'):
                        # Handle notebook files specially
                        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                            nb_content = f.read()
                        stripped_content = strip_notebook_outputs(nb_content)
                        out.write(stripped_content)
                    else:
                        # Regular files
                        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                            out.write(f.read())
                except Exception as e:
                    out.write(f"[Non-text or unreadable content: {e}]")
                out.write("\n\n")
