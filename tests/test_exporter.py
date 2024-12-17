# tests/test_exporter.py

import unittest
import os
import json
from my_exporter import export_folder_contents


class TestExporter(unittest.TestCase):
    def setUp(self):
        # Setup a temporary directory structure for testing
        self.test_dir = 'test_project'
        os.makedirs(self.test_dir, exist_ok=True)

        # Create a regular text file to include
        with open(os.path.join(self.test_dir, 'include_me.txt'), 'w', encoding='utf-8') as f:
            f.write('This file should be included.')

        # Create a file that should be ignored via .gitignore
        with open(os.path.join(self.test_dir, 'ignore_me.txt'), 'w', encoding='utf-8') as f:
            f.write('This file should be ignored.')

        # Create a .gitignore file
        with open(os.path.join(self.test_dir, '.gitignore'), 'w', encoding='utf-8') as f:
            f.write('ignore_me.txt\n')

        # Create an include patterns file
        with open(os.path.join(self.test_dir, 'include_patterns.txt'), 'w', encoding='utf-8') as f:
            f.write('include_me.txt\n')

        # Create a sample Jupyter notebook with a code cell and output
        nb_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["# This is a markdown cell"]
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "execution_count": 1,
                    "source": ["print('Hello World')"],
                    "outputs": [
                        {
                            "name": "stdout",
                            "output_type": "stream",
                            "text": ["Hello World\n"]
                        }
                    ]
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5
        }

        with open(os.path.join(self.test_dir, 'test_notebook.ipynb'), 'w', encoding='utf-8') as f:
            json.dump(nb_content, f, indent=2)

    def tearDown(self):
        # Remove the temporary directory after tests
        import shutil
        shutil.rmtree(self.test_dir)

    def test_only_include_file(self):
        output_file = 'output_include_only.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=None,
            include_file=os.path.join(self.test_dir, 'include_patterns.txt')
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('include_me.txt', content)
        self.assertNotIn('ignore_me.txt', content)
        os.remove(output_file)

    def test_only_ignore_file(self):
        output_file = 'output_ignore_only.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=os.path.join(self.test_dir, '.gitignore')
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('include_me.txt', content)
        self.assertNotIn('ignore_me.txt', content)
        os.remove(output_file)

    def test_both_include_and_ignore_files(self):
        output_file = 'output_both.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=os.path.join(self.test_dir, '.gitignore'),
            include_file=os.path.join(self.test_dir, 'include_patterns.txt')
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('include_me.txt', content)
        self.assertNotIn('ignore_me.txt', content)
        os.remove(output_file)

    def test_notebook_exclude_outputs(self):
        """
        Test that notebook outputs are excluded by default (exclude_notebook_outputs=True).
        """
        output_file = 'output_nb_exclude.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=os.path.join(self.test_dir, '.gitignore')
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        # The notebook should appear, but outputs should not be included in the exported content.
        self.assertIn('test_notebook.ipynb', content)
        # Outputs should not be present, only a placeholder line (if any).
        self.assertNotIn('Hello World', content)
        os.remove(output_file)

    def test_notebook_include_outputs(self):
        """
        Test that notebook outputs can be included if exclude_notebook_outputs=False.
        """
        output_file = 'output_nb_include.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=os.path.join(self.test_dir, '.gitignore'),
            exclude_notebook_outputs=False
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        # The notebook should appear and outputs should be present.
        self.assertIn('test_notebook.ipynb', content)
        self.assertIn('Hello World', content)
        os.remove(output_file)

    def test_notebook_convert_to_py(self):
        """
        Test that when convert_notebook_to_py=True,
        the notebook is converted to a .py-like format without outputs.
        """
        output_file = 'output_nb_py.txt'
        export_folder_contents(
            root_dir=self.test_dir,
            output_file=output_file,
            ignore_file=os.path.join(self.test_dir, '.gitignore'),
            convert_notebook_to_py=True
        )
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        # The notebook should appear in a .py-like representation.
        # Check that code cells and markdown are commented/formatted correctly.
        self.assertIn('test_notebook.ipynb', content)
        self.assertIn('# === Markdown Cell ===', content)
        self.assertIn('# This is a markdown cell', content)
        self.assertIn('# === Code Cell ===', content)
        self.assertIn("print('Hello World')", content)
        # No outputs should be present in the .py version
        self.assertNotIn('Hello World\n', content)
        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()
