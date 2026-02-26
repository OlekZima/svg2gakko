from typing import Iterable
from svg2gakko.errors import (
    NotAtLeastTwoAnswersError,
    NotAtLeastOneCorrectAnswersError,
    NotAllAnswerCorrectError,
    NotAtLeastThreeNumberOfOptions,
    AnswersAreNotUnique,
)
from dataclasses import dataclass, field
from enum import Enum


class QuestionType(Enum):
    SINGLE_CHOICE_QUESTION = 0
    MULTIPLE_CHOICE_QUESTION = 1
    TEXT_QUESTION = 2


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class Question:
    content: str
    question_type: QuestionType
    _answers: list[Answer] = field(default_factory=list)
    number_of_options: int = 3
    points: int = 1

    def is_correct(self) -> bool:
        if self.number_of_options < 3:
            raise NotAtLeastThreeNumberOfOptions(
                "Questions should have at least 3 number of options."
            )

        if len(set(self._answers)) != len(self._answers):
            raise AnswersAreNotUnique("Some of the answers got non-unique content.")

        if self.question_type.value in (0, 1):
            if len(self._answers) < 2:
                raise NotAtLeastTwoAnswersError(
                    f"For MULTIPLE/SINGLE_CHOICE_QUESTION you need at least 2 answers.\n{self}"
                )
            if not any(answer.correct for answer in self._answers):
                raise NotAtLeastOneCorrectAnswersError(
                    f"For MULTIPLE/SINGLE_CHOICE_QUESTION at least 1 answer should be correct.\n{self}"
                )
        else:
            if not all(answer.correct for answer in self._answers):
                raise NotAllAnswerCorrectError(
                    f"For TEXT_QUESTION all of the answers should be correct.\n{self}"
                )
        return True

    def add_answer(self, answer: Answer) -> None:
        self._answers.append(answer)

    def add_answers(self, answers: Iterable[Answer]) -> None:
        self._answers.extend(answers)

    def get_answers_len(self) -> int:
        return len(self._answers)

    def to_dict(self):
        if self.is_correct():
            return {
                "Content": self.content,
                "NumberOfOptions": self.number_of_options,
                "QuestionType": self.question_type.value,
                "Points": self.points,
                "Answers": [answer.to_dict() for answer in self._answers],
            }
