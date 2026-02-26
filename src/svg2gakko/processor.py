from svg2gakko.parser import svg2base64gakko
from rich import print
from pathlib import Path
from typing import List, Literal
from svg2gakko.question import Question, QuestionType, Answer


class CategoryProcessor:
    @classmethod
    def process(
        cls,
        qa_dict: dict[str, dict[Literal["question", "answers"], list[Path]]],
    ) -> List[Question]:
        questions: List[Question] = []

        for number in qa_dict.keys():
            question_path = qa_dict[number]["question"][0]
            answers_paths = qa_dict[number]["answers"]

            print(
                f"[bold green][Question][/bold green] Parsing question: {question_path}"
            )
            question = Question(
                content=svg2base64gakko(question_path),
                # TODO How do we read QuestionType from the file?
                question_type=QuestionType.SINGLE_CHOICE_QUESTION,
            )

            answers = [
                Answer(
                    svg2base64gakko(file),
                    # TODO How do we check if answer is correct?
                    True,
                )
                for file in answers_paths
            ]
            question.add_answers(answers)
            questions.append(question)

        return questions
