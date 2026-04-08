from typing import Literal
from pathlib import Path

from rich import print

from svg2gakko.input_parser import InputParser
from svg2gakko.json_builder import JSONBuilder
from svg2gakko.processor import CategoryProcessor
from svg2gakko.scanner import CategoryScanner


class Builder:
    def __init__(
        self,
        scanner: CategoryScanner,
        processor: CategoryProcessor,
        json_builder: JSONBuilder,
        input_parser: InputParser,
    ) -> None:
        self.processor = processor
        self.scanner = scanner
        self.json_builder = json_builder
        self.input_parser = input_parser

    def build(self, path: str | Path, output_path: str | Path) -> None:
        """Full pipeline: reorganize input into temp dir, scan, process, dump JSON."""
        # Preprocess: reorganize arbitrary input structure into category directories
        # with proper naming convention (N.svg for questions, N_A.svg for answers)
        organized_dir = self.input_parser.parse(Path(path))

        for category in sorted(organized_dir.iterdir()):
            if not category.is_dir():
                continue

            qa_dict: dict[str, dict[Literal["question", "answers"], list[Path]]] = (
                self.scanner.scan(category)
            )
            questions = self.processor.process(qa_dict)

            for question in questions:
                self.json_builder.add_question(question)

        self.json_builder.dump(Path(output_path))

    def reorganize(self, path: str | Path) -> None:
        """Reorganize the input directory in-place with correct file structure and names.

        Finds all SVG files with metadata, reorganizes them into category
        directories with proper naming convention, and replaces the original
        directory contents. No JSON output is produced.
        """
        self.input_parser.reorganize(Path(path))
        print("[bold green]Done.[/bold green] Input directory reorganized in-place.")
