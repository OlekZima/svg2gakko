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
    for item in Path(_parse_args().input).iterdir():
        for image in Path(item).iterdir():
            if image.name.split(sep=".")[-1] != "svg":
                print(f"[bold red][SKIP][/bold red] Found non SVG file: {image}\n")
            print(
                f"[bold green][CONVERT][/bold green] Found an SVG file {image}: {svg2base64gakko(image)}\n"
            )
