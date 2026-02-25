from svg2gakko.errors import (
    NotAtLeastOneCorrectAnswersError,
    NotAllAnswerCorrectError,
    NotAtLeastTwoAnswersError,
)
from svg2gakko.question import Question, QuestionType, Answer
import pytest


def test_validation_single_choice_raise():
    answers = [Answer("Answer 1", False), Answer("Answer 2", False)]
    question = Question("Question 1", QuestionType.SINGLE_CHOICE_QUESTION, 4, answers)
    with pytest.raises(NotAtLeastOneCorrectAnswersError):
        question.to_dict()


def test_validation_single_choice():
    answers = [Answer("Answer 1", True), Answer("Answer 2", False)]
    question = Question("Question 1", QuestionType.SINGLE_CHOICE_QUESTION, 4, answers)

    question.to_dict()


def test_validation_multiple_choice_raise():
    answers = [Answer("Answer 1", False), Answer("Answer 2", False)]
    question = Question("Question 1", QuestionType.MULTIPLE_CHOICE_QUESTION, 4, answers)
    with pytest.raises(NotAtLeastOneCorrectAnswersError):
        question.to_dict()


def test_validation_multiple_choice():
    answers = [Answer("Answer 1", True), Answer("Answer 2", False)]
    question = Question("Question 1", QuestionType.MULTIPLE_CHOICE_QUESTION, 4, answers)

    question.to_dict()


def test_validation_single_no_answers():
    answers = []
    question = Question("Question 1", QuestionType.SINGLE_CHOICE_QUESTION, 4, answers)
    with pytest.raises(NotAtLeastTwoAnswersError):
        question.to_dict()


def test_validation_multiple_no_answers():
    answers = []
    question = Question("Question 1", QuestionType.MULTIPLE_CHOICE_QUESTION, 4, answers)
    with pytest.raises(NotAtLeastTwoAnswersError):
        question.to_dict()


def test_validation_text_no_answers():
    answers = []
    question = Question("Question 1", QuestionType.TEXT_QUESTION, 4, answers)

    question.to_dict()


def test_validation_text_false_answers():
    answers = [Answer("Answer 1", True), Answer("Answer 2", False)]
    question = Question("Question 1", QuestionType.TEXT_QUESTION, 4, answers)

    with pytest.raises(NotAllAnswerCorrectError):
        question.to_dict()
