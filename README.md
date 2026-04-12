# svg2gakko [Work In Progress]

## Convert your SVG images into Gakko Test JSON format

> [!CAUTION]
> At the moment all questions are `MULTIPLE_CHOICE_QUESTION` type.

### Installation

1. Download `uv` package manager from [astral.sh](https://docs.astral.sh/uv/getting-started/installation/)
2. Download the repo `git clone https://github.com/OlekZima/svg2gakko/tree/main`
3. Create a venv and download packages by `uv sync`
4. Activate the environmet:
   - For Windows `cmd.exe`

    ```bash
    .venv\Scripts\activate.bat
    ```

   - For Windows PowerShell

    ```bash
    .venv\Scripts\activate.ps1
    ```

   - For Linux/MacOS

    ```bash
    source .venv/bin/activate
    ```

5. Install `svg2gakko` package in editable mode by `uv pip install -e .`

Alternatively, you can run it directly:

```bash
uv run main.py input output
```

### Usage

Run the CLI tool:

```txt
usage: svg2gakko [-h] [-i INPUT] [-o OUTPUT] [-r] input [output]

Tool for conversion svg images to Gakko's JSON test format

positional arguments:
  input                Directory which will contain other directories (categories of questions) with SVG files.
  output               Output JSON file path.

options:
  -h, --help           show this help message and exit
  -i, --input INPUT    Directory which will contain other directories (categories of questions) with SVG files.
  -o, --output OUTPUT  Output JSON file path.
  -r, --reorganize     Reorganize the input directory in-place with correct file structure and naming convention. SVG files are renamed and moved into
                       category directories based on their metadata. When this flag is set, no JSON output is produced and the output argument is not
                       required.
```

- `-i, --input`: Path to the directory containing question categories (each as a subdirectory with SVG files).

- `-o, --output`: Path to the JSON file that will be created if it doesn’t exist and filled with the generated data.

## Troubleshoting

As the `input`, pass a path to a directory that contains SVG files. Any hierarchy of files/directories is allowed.

As the `output`, provide a path to the JSON file that will be created (if it doesn’t exist) and filled with data.

`svg2gakko` as well as Gakko expects each question to consist of at least three files:

- Question file.
- 2 answers files.

### Note

- Contents of answers must be unique within the question.
