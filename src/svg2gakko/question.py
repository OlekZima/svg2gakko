from cairocffi import Error
from dataclasses import dataclass
from enum import Enum


class QuestionType(Enum):
    SINGLE_CHOICE_QUESTION = 0
    MULTIPLE_CHOICE_QUESTION = 1
    TEXT_QUESTION = 2


@dataclass
class Answer:
    content: str
    correct: bool
    weight: int = 1

    def to_dict(self):
        return {
            "Content": self.content,
            "Correct": self.correct,
            "Weight": self.weight,
        }


@dataclass
class Question:
    content: str
    question_type: QuestionType
    number_of_options: int
    answers: list[Answer]
    points: int = 1

    def validate(self):
        if self.question_type.value in (0, 1):
            if len(self.answers) < 2:
                raise ValueError("For MULTIPLE/SINGLE_CHOICE_QUESTION you need at least 2 answers.")
            if not any(answer.correct for answer in self.answers):
                raise ValueError(
                    "For MULTIPLE/SINGLE_CHOICE_QUESTION at least one answer should be correct."
                )

        if not all(answer.correct for answer in self.answers):
            raise ValueError("For TEXT_QUESTION all of the answers should be correct.")

    def to_dict(self):
        self.validate()
        return {
            "Content": self.content,
            "NumberOfOptions": self.number_of_options,
            "QuestionType": self.question_type.value,
            "Points": self.points,
            "Answers": [answer.to_dict() for answer in self.answers],
        }
