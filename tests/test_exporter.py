# tests/test_exporter.py

import unittest
import os
from my_exporter import export_folder_contents


class TestExporter(unittest.TestCase):
    def setUp(self):
        # Setup a temporary directory structure for testing
        self.test_dir = 'test_project'
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, 'include_me.txt'), 'w') as f:
            f.write('This file should be included.')
        with open(os.path.join(self.test_dir, 'ignore_me.txt'), 'w') as f:
            f.write('This file should be ignored.')
        with open(os.path.join(self.test_dir, '.gitignore'), 'w') as f:
            f.write('ignore_me.txt\n')

        with open(os.path.join(self.test_dir, 'include_patterns.txt'), 'w') as f:
            f.write('include_me.txt\n')

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
        with open(output_file, 'r') as f:
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
        with open(output_file, 'r') as f:
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
        with open(output_file, 'r') as f:
            content = f.read()
        self.assertIn('include_me.txt', content)
        self.assertNotIn('ignore_me.txt', content)
        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()
