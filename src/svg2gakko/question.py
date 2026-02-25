from dataclasses import dataclass
from answer import Answer
from enum import Enum


class QuestionType(Enum):
    SINGLE_CHOICE_QUESTION = 0
    MULTIPLE_CHOICE_QUESTION = 1
    TEXT_QUESTION = 2


@dataclass
class Question:
    content: str
    question_type: QuestionType
    number_of_options: int
    answers: list[Answer]

    # def __init__(
    #     self,
    #     content: str,
    #     question_type: QuestionType,
    #     number_of_options: int,
    #     answers: list[Answer],
    # ):
    #     self.content = content
    #     self.question_type = question_type
    #     self.number_of_options = 3 if number_of_options < 3 else number_of_options
    #     self.answers = answers
