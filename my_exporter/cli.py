# my_exporter/cli.py

import argparse
import sys

from .exporter import export_folder_contents
from .logger import logger  # <-- Import the logger


def none_or_str(value):
    """
    Convert the string 'None' to the Python None object.

    Args:
        value (str): The input string.

    Returns:
        Optional[str]: Returns None if the input is 'None', else returns the input string.
    """
    if value == 'None':
        return None
    return value


def main() -> None:
    """
    Entry point for the folder contents exporter CLI.

    This function parses command-line arguments and initiates the export process
    by invoking the `export_folder_contents` function with the appropriate parameters.

    Args:
        None

    Raises:
        SystemExit: If argument parsing fails or if an error occurs during export.

    Example:
        .. code-block:: bash

            python cli.py --root-dir ./my_project --output-file project_export.txt --ignore-file .gitignore --include-file include.txt --export-nb-as-py
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Export folder contents.')

    parser.add_argument(
        '--root-dir',
        type=str,
        default='.',
        help='Root directory to start exporting from.'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        default='output.txt',
        help='Name of the output text file.'
    )
    parser.add_argument(
        '--ignore-file',
        type=none_or_str,
        default='.gitignore',
        help='Path to the ignore file pattern list.'
    )
    parser.add_argument(
        '--include-file',
        type=str,
        default=None,
        help='Path to the include file pattern list.'
    )
    parser.add_argument(
        '--include-nb-outputs',
        action='store_true',
        help='Include output cells in Jupyter notebooks (ignored if --export-nb-as-py is used).'
    )
    parser.add_argument(
        '--export-nb-as-py',
        action='store_true',
        help='Convert Jupyter notebooks to .py format, excluding all output cells.'
    )

    # Parse the arguments
    args: argparse.Namespace = parser.parse_args()

    logger.debug(f"Parsed command-line arguments: {args}")

    # Determine whether to exclude notebook outputs based on the provided flags
    if args.export_nb_as_py:
        exclude_notebook_outputs: bool = True
        logger.debug("Flag '--export-nb-as-py' is set. Notebook outputs will be excluded.")
    else:
        exclude_notebook_outputs = not args.include_nb_outputs
        if exclude_notebook_outputs:
            logger.debug("Notebook outputs will be excluded based on '--include-nb-outputs' flag.")
        else:
            logger.debug("Notebook outputs will be included based on '--include-nb-outputs' flag.")

    logger.info("Starting the export process...")
    try:
        export_folder_contents(
            root_dir=args.root_dir,
            output_file=args.output_file,
            ignore_file=args.ignore_file,
            include_file=args.include_file,
            exclude_notebook_outputs=exclude_notebook_outputs,
            convert_notebook_to_py=args.export_nb_as_py
        )
    except Exception as e:
        logger.exception(f"An error occurred during the export process: {e}")
        sys.exit(1)
    else:
        logger.info(f"Export completed successfully. Output file created at '{args.output_file}'.")
