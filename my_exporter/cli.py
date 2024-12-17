# my_exporter/cli.py

import argparse
from .exporter import export_folder_contents


def main():
    parser = argparse.ArgumentParser(description='Export folder contents.')
    parser.add_argument('--root-dir', default='.', help='Root directory to start from')
    parser.add_argument('--output-file', default='output.txt', help='Output file name')
    parser.add_argument('--ignore-file', default='.gitignore', help='Ignore file pattern list')
    parser.add_argument('--include-file', help='Include file pattern list')
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

    args = parser.parse_args()

    # If exporting as .py, always exclude notebook outputs
    if args.export_nb_as_py:
        exclude_notebook_outputs = True
    else:
        exclude_notebook_outputs = not args.include_nb_outputs

    export_folder_contents(
        root_dir=args.root_dir,
        output_file=args.output_file,
        ignore_file=args.ignore_file,
        include_file=args.include_file,
        exclude_notebook_outputs=exclude_notebook_outputs,
        convert_notebook_to_py=args.export_nb_as_py
    )
