import shutil
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from rich import print

from svg2gakko.constants import get_data_from_svg


class InputParser:
    """Parses an input directory with arbitrary structure, extracts metadata from SVG files,
    and reorganizes them into category directories with the naming convention expected by
    CategoryScanner:

        category_dir/
            1.svg       (question 1)
            1_1.svg     (question 1, answer 1)
            1_2.svg     (question 1, answer 2)
            2.svg       (question 2)
            2_1.svg     (question 2, answer 1)
            ...

    SVG files must contain metadata in the format: {category}::{question}::{type}
    where type is 'q' (question), '+' (correct answer), or '-' (incorrect answer).
    """

    @staticmethod
    def _organize(input_dir: Path, target_dir: Path) -> Path:
        """Core logic: find SVGs in input_dir, extract metadata, and write
        organized structure into target_dir.

        Recursively finds all SVG files, extracts their metadata using
        get_data_from_svg(), groups by category and question, then copies
        them into target_dir with the proper naming convention.

        Args:
            input_dir: Path to the input directory containing SVG files with metadata.
            target_dir: Path to the directory where organized files will be written.

        Returns:
            Path to the target directory containing reorganized category directories.
        """
        root = input_dir.resolve()
        target_dir = target_dir.resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        categories: Dict[int, Dict[int, Dict[str, List[Path]]]] = defaultdict(
            lambda: defaultdict(lambda: {"question": [], "answers": []})
        )

        svg_files = sorted(p for p in root.rglob("*.svg") if p.is_file())

        for svg_file in svg_files:
            category_n, question_n, type_char = get_data_from_svg(svg_file)

            if type_char == "q":
                categories[category_n][question_n]["question"].append(svg_file)
            elif type_char in ("+", "-"):
                categories[category_n][question_n]["answers"].append(svg_file)
            else:
                print(
                    f"[bold yellow][Warning][/bold yellow] Unknown type '{type_char}' in {svg_file}, skipping."
                )

        for category_n in sorted(categories):
            questions = categories[category_n]
            category_dir = target_dir / str(category_n)
            category_dir.mkdir(parents=True, exist_ok=True)

            print(f"[bold magenta][Category {category_n}][/bold magenta]")

            for question_n in sorted(questions):
                qa = questions[question_n]
                file_question_n = question_n + 1

                question_files = qa["question"]
                if not question_files:
                    print(
                        f"  [bold red][Warning][/bold red] Question {question_n} in category {category_n} "
                        f"has no question file, skipping answers."
                    )
                    continue

                if len(question_files) > 1:
                    print(
                        f"  [bold yellow][Warning][/bold yellow] Question {question_n} in category {category_n} "
                        f"has multiple question files, using first: {question_files[0].name}"
                    )

                question_src = question_files[0]
                question_dest = category_dir / f"{file_question_n}.svg"
                shutil.copy2(question_src, question_dest)
                print(
                    f"  [bold green][Question {file_question_n}][/bold green] "
                    f"{question_src.name} -> {question_dest.name}"
                )

                # Copy answer files
                for answer_idx, answer_src in enumerate(qa["answers"], start=1):
                    answer_dest = category_dir / f"{file_question_n}_{answer_idx}.svg"
                    shutil.copy2(answer_src, answer_dest)
                    print(
                        f"  Answer {file_question_n}_{answer_idx}: "
                        f"{answer_src.name} -> {answer_dest.name}"
                    )

        return target_dir

    @staticmethod
    def parse(input_dir: Path) -> Path:
        """Parse input directory and reorganize SVG files into a temp directory.

        Recursively finds all SVG files, extracts their metadata using
        get_data_from_svg(), and copies them into a structured temp directory
        organized by category with proper naming convention.

        Args:
            input_dir: Path to the input directory containing SVG files with metadata.

        Returns:
            Path to the temp directory containing reorganized category directories.
        """
        temp_dir = Path(tempfile.mkdtemp(prefix="svg2gakko_"))
        return InputParser._organize(input_dir, temp_dir)

    @staticmethod
    def reorganize(input_dir: Path) -> Path:
        """Reorganize SVG files in-place within the input directory.

        Finds all SVG files with metadata, reorganizes them into category
        directories with proper naming convention, and replaces the original
        directory contents with the organized structure. The original files
        and directory structure are removed and replaced.

        Args:
            input_dir: Path to the input directory containing SVG files with metadata.

        Returns:
            Path to the reorganized input directory (same as input_dir).
        """
        input_dir = input_dir.resolve()

        temp_dir = Path(tempfile.mkdtemp(prefix="svg2gakko_"))
        InputParser._organize(input_dir, temp_dir)

        for item in list(input_dir.iterdir()):
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

        for category_dir in sorted(temp_dir.iterdir()):
            target = input_dir / category_dir.name
            shutil.move(str(category_dir), str(target))

        shutil.rmtree(temp_dir, ignore_errors=True)

        return input_dir


if __name__ == "__main__":
    InputParser.parse(Path("tests/data/real/"))
