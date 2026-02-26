from svg2gakko.json_builder import JSONBuilder
from svg2gakko.processor import CategoryProcessor
from svg2gakko.scanner import CategoryScanner
from svg2gakko.builder import Builder
from svg2gakko.errors import (
    InputDirectoryDoesntExistError,
    InputDirectoryIsNotDirectoryError,
)
import argparse
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "svg2gakko",
        description="Tool for conversion svg images to Gakko's JSON test format",
    )

    parser.add_argument(
        "input",
        help="Directory which will contain other directories (categories of questions) with SVG files.",
        type=str,
    )

    parser.add_argument(
        "output",
        help="Output JSON file path.",
        type=str,
    )

    parser.add_argument(
        "-i",
        "--input",
        help="Directory which will contain other directories (categories of questions) with SVG files.",
        type=str,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output JSON file path.",
        type=str,
    )
    return parser.parse_args()


def _check_input(input_path: str) -> bool:
    if input_path is None or not Path(input_path).exists():
        raise InputDirectoryDoesntExistError("Input directory doesn't exist or None.")
    if not Path(input_path).is_dir():
        raise InputDirectoryIsNotDirectoryError("Input directory is not a directory.")

    return True


def main() -> None:
    args = _parse_args()
    _check_input(args.input)

    Builder(
        CategoryScanner(),
        CategoryProcessor(),
        JSONBuilder(),
    ).build(args.input, args.output)
