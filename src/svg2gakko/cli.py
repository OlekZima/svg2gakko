from svg2gakko.errors import InputDirectoryDoesntExistError, InputDirectoryIsNotDirectoryError
import argparse
from pathlib import Path
from rich import print
from svg2gakko.parser import svg2base64gakko


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "svg2gakko",
        description="Tool for conversion svg images to Gakko's JSON test format",
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Directory which will contain other directories (categories of questions) with SVG files.",
        type=str,
    )
    return parser.parse_args()


def main() -> None:
    arguments = _parse_args()
    if arguments.input is None or not Path(arguments.input).exists():
        raise InputDirectoryDoesntExistError("Input directory doesn't exist or None.")
    if not Path(arguments.input).is_dir():
        raise InputDirectoryIsNotDirectoryError("Input directory is not a directory.")

    for item in Path(arguments.input).iterdir():
        for image in Path(item).iterdir():
            if image.name.split(sep=".")[-1] != "svg":
                print(f"[bold red][SKIP][/bold red] Found non SVG file: {image}\n")
            print(
                f"[bold green][CONVERT][/bold green] Found an SVG file {image}: {svg2base64gakko(image)}\n"
            )
