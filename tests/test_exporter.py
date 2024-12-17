# tests/test_exporter.py

import unittest
import os
import json
from my_exporter import export_folder_contents


class TestExporter(unittest.TestCase):
    def setUp(self):
        """
        Setup a temporary directory structure for testing.
        This includes:
        - include_me.txt: A file that should be included based on include_patterns.txt.
        - ignore_me.txt: A file that should be ignored based on .gitignore.
        - sample_notebook.ipynb: A sample Jupyter notebook for testing export_as_py functionality.
        - .gitignore: Specifies files to ignore.
        - include_patterns.txt: Specifies files to always include.
        """
        # Create the main test directory
        self.test_dir = 'test_project'
        os.makedirs(self.test_dir, exist_ok=True)

        # Create files to be included and ignored
        with open(os.path.join(self.test_dir, 'include_me.txt'), 'w') as f:
            f.write('This file should be included.')
        with open(os.path.join(self.test_dir, 'ignore_me.txt'), 'w') as f:
            f.write('This file should be ignored.')

        # Create .gitignore to ignore 'ignore_me.txt'
        with open(os.path.join(self.test_dir, '.gitignore'), 'w') as f:
            f.write('ignore_me.txt\n')

        # Create include_patterns.txt to always include 'include_me.txt'
        with open(os.path.join(self.test_dir, 'include_patterns.txt'), 'w') as f:
            f.write('include_me.txt\n')

        # Create a sample Jupyter notebook
        self.nb_file = os.path.join(self.test_dir, 'sample_notebook.ipynb')
        nb_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": ["# Sample Notebook\n", "This is a markdown cell.\n"]
                },
                {
                    "cell_type": "code",
                    "source": ["print('Hello, World!')\n"],
                    "outputs": [
                        {
                            "output_type": "stream",
                            "name": "stdout",
                            "text": ["Hello, World!\n"]
                        }
                    ],
                    "execution_count": 1
                },
                {
                    "cell_type": "code",
                    "source": ["x = 10\n", "y = 20\n", "print(x + y)\n"],
                    "outputs": [
                        {
                            "output_type": "stream",
                            "name": "stdout",
                            "text": ["30\n"]
                        }
                    ],
                    "execution_count": 2
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5
        }
        with open(self.nb_file, 'w', encoding='utf-8') as f:
            json.dump(nb_content, f)

    def tearDown(self):
        """
        Remove the temporary directory after tests.
        """
        import shutil
        shutil.rmtree(self.test_dir)

    def test_only_include_file(self):
        """
        Test exporting with only an include file specified.
        Ensures that included files are present and ignored files are excluded.
        """
        output_file = 'output_include_only.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=None,
            include_file=os.path.join(self.test_dir, 'include_patterns.txt'),
            exclude_notebook_outputs=True,
            convert_notebook_to_py=False
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('include_me.txt', content)
        self.assertIn('sample_notebook.ipynb', content)
        self.assertNotIn('ignore_me.txt', content)
        os.remove(output_file)

    def test_only_ignore_file(self):
        """
        Test exporting with only an ignore file specified.
        Ensures that ignored files are excluded and other files are included.
        """
        output_file = 'output_ignore_only.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=os.path.join(self.test_dir, '.gitignore'),
            include_file=None,
            exclude_notebook_outputs=True,
            convert_notebook_to_py=False
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('include_me.txt', content)
        self.assertIn('sample_notebook.ipynb', content)
        self.assertNotIn('ignore_me.txt', content)
        os.remove(output_file)

    def test_both_include_and_ignore_files(self):
        """
        Test exporting with both include and ignore files specified.
        Ensures that included files are present, ignored files are excluded, and other files are handled appropriately.
        """
        output_file = 'output_both.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=os.path.join(self.test_dir, '.gitignore'),
            include_file=os.path.join(self.test_dir, 'include_patterns.txt'),
            exclude_notebook_outputs=True,
            convert_notebook_to_py=False
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('include_me.txt', content)
        self.assertIn('sample_notebook.ipynb', content)
        self.assertNotIn('ignore_me.txt', content)
        os.remove(output_file)

    def test_export_nb_as_py(self):
        """
        Test exporting with the --export-nb-as-py option.
        Ensures that Jupyter notebooks are converted to Python format without output cells,
        markdown cells are commented, and code cells are included correctly.
        """
        output_file = 'output_py_conversion.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=os.path.join(self.test_dir, '.gitignore'),
            include_file=os.path.join(self.test_dir, 'include_patterns.txt'),
            exclude_notebook_outputs=True,   # Should be True when converting to .py
            convert_notebook_to_py=True
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that the directory structure and other files are exported correctly
        self.assertIn('include_me.txt', content)
        self.assertIn('sample_notebook.ipynb', content)
        self.assertNotIn('ignore_me.txt', content)

        # Check that the notebook was converted to .py format
        # The converted content should have markers for markdown and code cells
        self.assertIn("# === Markdown Cell ===", content)
        self.assertIn("# # Sample Notebook", content)
        self.assertIn("# This is a markdown cell.", content)
        self.assertIn("# === Code Cell ===", content)
        self.assertIn("print('Hello, World!')", content)
        self.assertIn("x = 10", content)
        self.assertIn("y = 20", content)
        self.assertIn("print(x + y)", content)

        # Ensure that notebook outputs are not present
        self.assertNotIn("Hello, World!", content)
        self.assertNotIn("30", content)

        # Ensure markdown is commented out
        self.assertIn("# # Sample Notebook", content)
        self.assertIn("# This is a markdown cell.", content)

        os.remove(output_file)

    def test_export_nb_as_py_ignores_include_nb_outputs(self):
        """
        Test exporting with both --export-nb-as-py and --include-nb-outputs flags.
        Ensures that when --export-nb-as-py is used, output cells are excluded regardless of --include-nb-outputs.
        """
        output_file = 'output_py_conversion_with_include_flag.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=os.path.join(self.test_dir, '.gitignore'),
            include_file=os.path.join(self.test_dir, 'include_patterns.txt'),
            exclude_notebook_outputs=True,   # Should be True when converting to .py
            convert_notebook_to_py=True
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Ensure that output cells are still excluded
        self.assertNotIn("Hello, World!", content)
        self.assertNotIn("30", content)

        # Ensure that markdown and code cells are correctly processed
        self.assertIn("# === Markdown Cell ===", content)
        self.assertIn("# # Sample Notebook", content)
        self.assertIn("# This is a markdown cell.", content)
        self.assertIn("# === Code Cell ===", content)
        self.assertIn("print('Hello, World!')", content)
        self.assertIn("x = 10", content)
        self.assertIn("y = 20", content)
        self.assertIn("print(x + y)", content)

        os.remove(output_file)

    def test_export_nb_without_conversion_includes_stripped_json(self):
        """
        Test exporting Jupyter notebooks without converting to Python.
        Ensures that output cells are stripped when exclude_notebook_outputs is True.
        """
        output_file = 'output_not_converted_stripped.json.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=os.path.join(self.test_dir, '.gitignore'),
            include_file=os.path.join(self.test_dir, 'include_patterns.txt'),
            exclude_notebook_outputs=True,   # Strip outputs
            convert_notebook_to_py=False      # Do not convert
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that the notebook content is present as stripped JSON
        self.assertIn('{"cells": [', content)
        self.assertIn('"cell_type": "markdown"', content)
        self.assertIn('"cell_type": "code"', content)
        self.assertIn('"outputs": []', content)
        self.assertIn('"execution_count": null', content)

        # Ensure that original outputs are not present
        self.assertNotIn("Hello, World!", content)
        self.assertNotIn("30", content)

        os.remove(output_file)

    def test_export_nb_with_outputs_included_when_not_converting(self):
        """
        Test exporting Jupyter notebooks without converting to Python and with outputs included.
        Ensures that output cells are included in the exported content.
        """
        output_file = 'output_not_converted_with_outputs.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=os.path.join(self.test_dir, '.gitignore'),
            include_file=os.path.join(self.test_dir, 'include_patterns.txt'),
            exclude_notebook_outputs=False,  # Do not strip outputs
            convert_notebook_to_py=False      # Do not convert
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that the notebook content is present as JSON with outputs
        self.assertIn('"outputs": [', content)
        self.assertIn('"output_type": "stream"', content)
        self.assertIn('"text": ["Hello, World!\\n"]', content)
        self.assertIn('"text": ["30\\n"]', content)

        # Ensure that code and markdown cells are present
        self.assertIn('"cell_type": "markdown"', content)
        self.assertIn('"cell_type": "code"', content)
        self.assertIn('"source": ["# Sample Notebook\\n", "This is a markdown cell.\\n"]', content)
        self.assertIn('"source": ["print(\'Hello, World!\')\\n"]', content)
        self.assertIn('"source": ["x = 10\\n", "y = 20\\n", "print(x + y)\\n"]', content)

        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()
