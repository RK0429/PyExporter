# my_exporter/exporter.py

import os
import json
from .ignore_handler import load_ignore_patterns


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


def print_structure(root_dir='.', out=None, prefix='', spec=None):
    """
    Recursively print a "tree" structure of directories and files.
    This function filters out ignored files/directories using the spec.
    """
    try:
        entries = sorted(os.listdir(root_dir))
    except PermissionError:
        out.write(prefix + "└── [Permission Denied]\n")
        return

    # Filter out ignored entries
    entries = [
        e for e in entries
        if not spec.match_file(os.path.join(root_dir, e))
    ]

    for i, entry in enumerate(entries):
        path = os.path.join(root_dir, entry)
        # Choose the connector symbol based on position
        connector = '├── ' if i < len(entries)-1 else '└── '

        # Write directory or file name
        out.write(prefix + connector + entry + "\n")

        if os.path.isdir(path):
            # Update prefix for child entries
            if i < len(entries)-1:
                new_prefix = prefix + "│   "
            else:
                new_prefix = prefix + "    "
            print_structure(path, out=out, prefix=new_prefix, spec=spec)


def export_folder_contents(
    root_dir='.',
    output_file='output.txt',
    ignore_file='.gitignore',
    exclude_notebook_outputs=True  # New parameter to control notebook output exclusion
):
    """
    Export the contents of a folder into a single text file while respecting
    .gitignore patterns and optionally excluding Jupyter notebook outputs.

    Parameters:
    - root_dir (str): Root directory to start exporting from.
    - output_file (str): Name of the output text file.
    - ignore_file (str): Path to the ignore file (e.g., .gitignore).
    - exclude_notebook_outputs (bool): If True, excludes output cells from .ipynb files.
    """
    spec = load_ignore_patterns(ignore_file)

    with open(output_file, 'w', encoding='utf-8', errors='replace') as out:
        # Print the directory structure header
        out.write("================\n")
        out.write("DIRECTORY STRUCTURE\n")
        out.write("================\n\n")

        # Print the directory structure
        print_structure(root_dir, out=out, spec=spec)

        out.write("\n")

        # Print the file contents header
        out.write("================\n")
        out.write("FILE CONTENTS\n")
        out.write("================\n\n")

        # Now, write the file contents
        for root, dirs, files in os.walk(root_dir):
            # Filter directories according to .gitignore spec
            dirs[:] = [d for d in dirs if not spec.match_file(os.path.join(root, d))]

            for filename in files:
                filepath = os.path.join(root, filename)
                if spec.match_file(filepath):
                    continue
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
