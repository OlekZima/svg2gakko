from svg2gakko.scanner import CategoryScanner
from svg2gakko.processor import CategoryProcessor
from typing import Literal
from svg2gakko.json_builder import JSONBuilder
from pathlib import Path
from rich import print


class Builder:
    def __init__(
        self,
        scanner: CategoryScanner,
        processor: CategoryProcessor,
        json_builder: JSONBuilder,
    ) -> None:
        self.processor = processor
        self.scanner = scanner
        self.json_builder = json_builder

    def build(self, path: str | Path, output_path: str | Path) -> None:
        for category in Path(path).iterdir():
            qa_dict: dict[str, dict[Literal["question", "answers"], list[Path]]] = (
                self.scanner.scan(category)
            )
            print(f"[bold magenta][Category {category.name}][/bold magenta]")
            questions = self.processor.process(qa_dict)

            [self.json_builder.add_question(question) for question in questions]

        self.json_builder.dump(Path(output_path))
