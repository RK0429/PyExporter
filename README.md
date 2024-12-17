# My-Exporter

**A Python tool to export the contents of a folder into a single text file while respecting `.gitignore` and optional include patterns, maintaining the hierarchical structure, and optionally handling Jupyter notebook outputs.**

## Table of Contents

- [My-Exporter](#my-exporter)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Command-Line Interface](#command-line-interface)
    - [Programmatic Usage](#programmatic-usage)
  - [Configuration](#configuration)
  - [Jupyter Notebook Outputs](#jupyter-notebook-outputs)
  - [Converting Notebooks to Python](#converting-notebooks-to-python)
  - [Testing](#testing)
  - [Contributing](#contributing)
  - [License](#license)
  - [Contact](#contact)

## Features

- **Respect `.gitignore` Patterns:** Automatically excludes files and directories based on your `.gitignore` file.
- **Include Patterns:** Optionally specify an include file to define patterns of files that should always be included.
- **Hierarchical Structure:** Maintains the folder hierarchy in the exported output by using relative file paths as headers.
- **Customizable Output:** Specify the root directory, output file name, ignore file, and include file.
- **Handles Non-Text Files:** Gracefully handles non-text or unreadable files by indicating their presence without content.
- **Jupyter Notebooks:** By default, strips output cells from `.ipynb` files. You can choose to include them, or convert notebooks entirely to `.py` format while omitting all outputs.

## Installation

You can install `my-exporter` via [PyPI](https://pypi.org/) using `pip`:

```bash
pip install my-exporter
```

Alternatively, you can install it directly from the source:

```bash
git clone https://github.com/RK0429/my-exporter.git
cd my-exporter
pip install .
```

## Usage

### Command-Line Interface

After installation, the `my-exporter` CLI tool is available.

**Basic Usage:**

```bash
my-exporter --root-dir path/to/project --output-file exported.txt
```

**Options:**

- `--root-dir`: Specifies the root directory to start exporting from. Defaults to the current directory (`.`).
- `--output-file`: Defines the name of the output text file. Defaults to `output.txt`.
- `--ignore-file`: Specifies a custom ignore file (e.g., `.gitignore`). Defaults to `.gitignore`.
- `--include-file`: Specifies a file containing patterns of files to include, even if they might otherwise be ignored.
- `--include-nb-outputs`: If provided, Jupyter notebook output cells are included in the exported content. By default, they are stripped.
- `--export-nb-as-py`: If provided, Jupyter notebooks (`.ipynb`) are converted into Python files (`.py`-like format) with all outputs omitted.

**Examples:**

1. **Basic export:**

   ```bash
   my-exporter --root-dir ./my_project --output-file project_contents.txt
   ```

2. **Using a custom ignore file:**

   ```bash
   my-exporter --root-dir ./my_project --ignore-file .myignore
   ```

3. **Using an include file to ensure certain files are always included:**

   ```bash
   my-exporter --root-dir ./my_project --include-file include_patterns.txt
   ```

4. **Including Jupyter notebook outputs:**

   ```bash
   my-exporter --root-dir ./my_project --include-nb-outputs
   ```

5. **Converting Jupyter notebooks to Python files (excluding outputs):**

   ```bash
   my-exporter --root-dir ./my_project --export-nb-as-py
   ```

### Programmatic Usage

You can also use `my-exporter` as a library within your Python projects.

**Example:**

```python
from my_exporter import export_folder_contents

export_folder_contents(
    root_dir='path/to/project',
    output_file='exported_contents.txt',
    ignore_file='.gitignore',            # Optional
    include_file='include_patterns.txt', # Optional
    exclude_notebook_outputs=False,      # Set to False to include notebook outputs
    convert_notebook_to_py=False         # Set to True to convert notebooks to .py format
)
```

## Configuration

- **`.gitignore` Support:** The tool uses your `.gitignore` file to determine which files and directories to exclude. Ensure your `.gitignore` is properly configured in the root directory you are exporting.
- **Custom Ignore Files:** If you prefer to use a different ignore file, specify it using the `--ignore-file` option.
- **Include Patterns:** You can specify an `--include-file` containing patterns of files that should always be included in the export. These patterns can override `.gitignore` exclusions if desired.

## Jupyter Notebook Outputs

By default, `my-exporter` removes output cells from Jupyter notebooks (`.ipynb`) to keep the exported file clean and focused on code and markdown cells. If you want to include the output cells, use the `--include-nb-outputs` option or set `exclude_notebook_outputs=False` programmatically.

## Converting Notebooks to Python

If you use `--export-nb-as-py`, notebooks are converted into a `.py`-style format:

- **Code cells** are included as plain Python code.
- **Markdown cells** are included as commented-out text.
- **No output cells** are included, regardless of the `--include-nb-outputs` setting.

This option is useful if you want a clean, output-free representation of your notebooks as Python scripts.

## Testing

This project uses [pytest](https://pytest.org/) for testing.

To run tests:

```bash
pytest
```

Make sure `pytest` is installed, or install it using:

```bash
pip install pytest
```

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository:** Click the "Fork" button on the repository page.
2. **Create a Feature Branch:**  

   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Commit Your Changes:**  

   ```bash
   git commit -m "Add some feature"
   ```

4. **Push to the Branch:**  

   ```bash
   git push origin feature/my-new-feature
   ```

5. **Open a Pull Request:** Describe your changes and submit the pull request.

Please update tests as appropriate and adhere to the [PEP 8](https://pep8.org/) style guide.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

**Your Name**  
Email: [s.woods.m.29@gmail.com](mailto:s.woods.m.29@gmail.com)  
GitHub: [https://github.com/RK0429](https://github.com/RK0429)
