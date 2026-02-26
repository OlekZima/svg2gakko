from pathlib import Path
from svg2gakko.question import Question
import json


class JSONBuilder:
    def __init__(self):
        self._questions: list[Question] = []

    def add_question(self, question: Question):
        if question.is_correct():
            self._questions.append(question.to_dict())

    def dump(self, file: Path | str):
        path_file = Path(file)
        if not path_file.exists():
            path_file.touch

        with open(file, "w", encoding="utf-8") as f:
            json.dump(self._questions, f, indent=4)

    def get_questions_count(self):
        return len(self._questions)

    def __str__(self) -> str:
        return str(self._questions)
