# svg2gakko

## Convert your SVG images into Gakko Test JSON format

### Installation

1. Download `uv` package manager from [astral.sh](https://docs.astral.sh/uv/getting-started/installation/)
2. Download the repo `git clone https://github.com/OlekZima/svg2gakko/tree/main`
3. Install `svg2gakko` package in editable mode by `uv pip install -e .`

### Usage

Run the CLI tool:

```txt
usage: svg2gakko [-h] [-i INPUT] [-o OUTPUT] input output

Tool for conversion svg images to Gakko's JSON test format

positional arguments:
  input                Directory which will contain other directories (categories of questions) with SVG files.
  output               Output JSON file path.

options:
  -h, --help           show this help message and exit
  -i, --input INPUT    Directory which will contain other directories (categories of questions) with SVG files.
  -o, --output OUTPUT  Output JSON file path.
```

- `-i, --input`: Path to the directory containing question categories (each as a subdirectory with SVG files).

- `-o, --output`: Path to the JSON file that will be created if it doesn’t exist and filled with the generated data.

## Troubleshoting

As the `input`, pass a path to a directory that contains subdirectories with SVG files.

Each subdirectory represents either a **question category** or a **single question**.

As the `output`, provide a path to the JSON file that will be created (if it doesn’t exist) and filled with data.

`svg2gakko` as well as Gakko expects each question to consist of at least three files:

1. A question file (e.g. `1.svg`), which is used as the question content.
2. Answer files named in the format `QuestionNumber_AnswerNumber.svg`.
    Each question must have at least two answers, unless its `QuestionType` is `TEXT_QUESTION`.
3. At least one answer must be incorrect, unless the `QuestionType` is `TEXT_QUESTION`.
4. Answer contents must be unique.

### Example file structure #1

```txt
data/
    category_1/
        1.svg
        1_1.svg
        1_2.svg
        2.svg
        2_1.svg
        2_2.svg
        2_3.svg
    category_2/
        3.svg
        3_1.svg
        3_2.svg
```

### Example file structure #2

```txt
questions/
    question_1/
        1.svg
        1_1.svg
        1_2.svg
    question_2/
        2.svg
        2_1.svg
        2_2.svg
        2_3.svg
    question_3/
        3.svg
        3_1.svg
        3_2.svg
        3_3.svg
        3_4.svg
```
