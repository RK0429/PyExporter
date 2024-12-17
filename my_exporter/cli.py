# my_exporter/cli.py

import argparse

from .exporter import export_folder_contents


def main() -> None:
    """
    Entry point for the folder contents exporter CLI.

    This function parses command-line arguments and initiates the export process
    by invoking the `export_folder_contents` function with the appropriate parameters.

    Command-Line Arguments:
    - `--root-dir` (str, optional): Root directory to start exporting from. Defaults to the current directory (`.`).
    - `--output-file` (str, optional): Name of the output text file. Defaults to `'output.txt'`.
    - `--ignore-file` (str, optional): Path to the ignore file (e.g., `.gitignore`). Defaults to `'.gitignore'`.
    - `--include-file` (str, optional): Path to the include file. If not provided, no include patterns are applied.
    - `--include-nb-outputs` (bool, flag): If set, includes output cells in Jupyter notebooks. This flag is ignored if `--export-nb-as-py` is used.
    - `--export-nb-as-py` (bool, flag): If set, converts Jupyter notebooks to `.py` format, excluding all output cells.

    Example Usage:
        ```bash
        python cli.py --root-dir ./my_project --output-file project_export.txt --ignore-file .gitignore --include-file include.txt --export-nb-as-py
        ```
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Export folder contents.')

    parser.add_argument(
        '--root-dir',
        type=str,
        default='.',
        help='Root directory to start exporting from'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        default='output.txt',
        help='Output file name'
    )
    parser.add_argument(
        '--ignore-file',
        type=str,
        default='.gitignore',
        help='Ignore file pattern list'
    )
    parser.add_argument(
        '--include-file',
        type=str,
        default=None,
        help='Include file pattern list'
    )
    parser.add_argument(
        '--include-nb-outputs',
        action='store_true',
        help='Include output cells in Jupyter notebooks (ignored if --export-nb-as-py is used)'
    )
    parser.add_argument(
        '--export-nb-as-py',
        action='store_true',
        help='Convert Jupyter notebooks to .py format, excluding all output cells'
    )

    args: argparse.Namespace = parser.parse_args()

    # Determine whether to exclude notebook outputs based on the provided flags
    if args.export_nb_as_py:
        exclude_notebook_outputs: bool = True
    else:
        exclude_notebook_outputs = not args.include_nb_outputs

    # Initiate the export process with the parsed arguments
    export_folder_contents(
        root_dir=args.root_dir,
        output_file=args.output_file,
        ignore_file=args.ignore_file,
        include_file=args.include_file,
        exclude_notebook_outputs=exclude_notebook_outputs,
        convert_notebook_to_py=args.export_nb_as_py
    )
