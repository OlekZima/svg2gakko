from pathlib import Path
from typing import Dict, Literal, List


class CategoryScanner:
    @classmethod
    def scan(cls, category_dir: Path) -> Dict:
        qa_dict: Dict[str, Dict[Literal["question", "answers"], List[Path]]] = {}

        for file in category_dir.iterdir():
            question_number = file.stem.split("_")[0]

            if question_number not in qa_dict:
                qa_dict[question_number] = {}
                qa_dict[question_number]["question"] = []
                qa_dict[question_number]["answers"] = []

            if "_" not in file.stem:
                qa_dict[question_number]["question"].append(file)
            else:
                qa_dict[question_number]["answers"].append(file)

        return qa_dict
