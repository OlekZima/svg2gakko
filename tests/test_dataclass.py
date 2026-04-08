import pytest

from svg2gakko.errors import (
    AnswersAreNotUnique,
    NotAllAnswerCorrectError,
    NotAtLeastOneCorrectAnswersError,
    NotAtLeastThreeNumberOfOptions,
    NotAtLeastTwoAnswersError,
)
from svg2gakko.question import Answer, Question, QuestionType




class TestAnswer:
    def test_default_weight(self):
        answer = Answer("Option A", True)
        assert answer.weight == 1

    def test_custom_weight(self):
        answer = Answer("Option A", True, weight=3)
        assert answer.weight == 3

    def test_to_dict_keys(self):
        answer = Answer("Option A", True, weight=2)
        result = answer.to_dict()
        assert result == {
            "Content": "Option A",
            "Correct": True,
            "Weight": 2,
        }

    def test_to_dict_incorrect_answer(self):
        answer = Answer("Wrong", False)
        result = answer.to_dict()
        assert result["Correct"] is False

    def test_frozen(self):
        answer = Answer("A", True)
        with pytest.raises(AttributeError):
            answer.content = "B"




class TestQuestionConstruction:
    def test_default_fields(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION)
        assert q.number_of_options == 3
        assert q.points == 1
        assert q.category is None
        assert q.get_answers_len() == 0

    def test_custom_fields(self):
        q = Question("Q?", QuestionType.TEXT_QUESTION, number_of_options=5, points=2, category=7)
        assert q.number_of_options == 5
        assert q.points == 2
        assert q.category == 7

    def test_add_answer(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION)
        q.add_answer(Answer("A", True))
        assert q.get_answers_len() == 1

    def test_add_answers(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION)
        q.add_answers([Answer("A", True), Answer("B", False)])
        assert q.get_answers_len() == 2

    def test_add_answer_then_add_answers(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION)
        q.add_answer(Answer("A", True))
        q.add_answers([Answer("B", False), Answer("C", False)])
        assert q.get_answers_len() == 3




class TestQuestionToDict:
    def test_single_choice(self):
        q = Question("What?", QuestionType.SINGLE_CHOICE_QUESTION)
        q.add_answers([Answer("Yes", True), Answer("No", False)])
        result = q.to_dict()
        assert result["Content"] == "What?"
        assert result["QuestionType"] == 0
        assert result["NumberOfOptions"] == 3
        assert result["Points"] == 1
        assert len(result["Answers"]) == 2
        assert result["Answers"][0] == {"Content": "Yes", "Correct": True, "Weight": 1}

    def test_multiple_choice(self):
        q = Question("Pick two.", QuestionType.MULTIPLE_CHOICE_QUESTION)
        q.add_answers([Answer("A", True), Answer("B", True), Answer("C", False)])
        result = q.to_dict()
        assert result["QuestionType"] == 1
        assert len(result["Answers"]) == 3

    def test_text_question(self):
        q = Question("Name?", QuestionType.TEXT_QUESTION)
        q.add_answers([Answer("Alice", True)])
        result = q.to_dict()
        assert result["QuestionType"] == 2




class TestSingleChoiceValidation:
    def test_valid(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION)
        q.add_answers([Answer("A", True), Answer("B", False)])
        assert q.is_correct() is True

    def test_no_correct_answer_raises(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION)
        q.add_answers([Answer("A", False), Answer("B", False)])
        with pytest.raises(NotAtLeastOneCorrectAnswersError):
            q.is_correct()

    def test_no_answers_raises(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION)
        with pytest.raises(NotAtLeastTwoAnswersError):
            q.is_correct()

    def test_one_answer_raises(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION)
        q.add_answer(Answer("A", True))
        with pytest.raises(NotAtLeastTwoAnswersError):
            q.is_correct()

    def test_multiple_correct_allowed(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION)
        q.add_answers([Answer("A", True), Answer("B", True), Answer("C", False)])
        assert q.is_correct() is True




class TestMultipleChoiceValidation:
    def test_valid_with_correct(self):
        q = Question("Q?", QuestionType.MULTIPLE_CHOICE_QUESTION)
        q.add_answers([Answer("A", True), Answer("B", False)])
        assert q.is_correct() is True

    def test_zero_correct_is_valid(self):
        q = Question("Q?", QuestionType.MULTIPLE_CHOICE_QUESTION)
        q.add_answers([Answer("A", False), Answer("B", False)])
        assert q.is_correct() is True

    def test_no_answers_raises(self):
        q = Question("Q?", QuestionType.MULTIPLE_CHOICE_QUESTION)
        with pytest.raises(NotAtLeastTwoAnswersError):
            q.is_correct()

    def test_one_answer_raises(self):
        q = Question("Q?", QuestionType.MULTIPLE_CHOICE_QUESTION)
        q.add_answer(Answer("A", True))
        with pytest.raises(NotAtLeastTwoAnswersError):
            q.is_correct()

    def test_all_correct(self):
        q = Question("Q?", QuestionType.MULTIPLE_CHOICE_QUESTION)
        q.add_answers([Answer("A", True), Answer("B", True)])
        assert q.is_correct() is True




class TestTextQuestionValidation:
    def test_all_correct(self):
        q = Question("Q?", QuestionType.TEXT_QUESTION)
        q.add_answers([Answer("A", True), Answer("B", True)])
        assert q.is_correct() is True

    def test_single_correct(self):
        q = Question("Q?", QuestionType.TEXT_QUESTION)
        q.add_answer(Answer("A", True))
        assert q.is_correct() is True

    def test_no_answers_is_valid(self):
        q = Question("Q?", QuestionType.TEXT_QUESTION)
        assert q.is_correct() is True

    def test_one_incorrect_raises(self):
        q = Question("Q?", QuestionType.TEXT_QUESTION)
        q.add_answers([Answer("A", True), Answer("B", False)])
        with pytest.raises(NotAllAnswerCorrectError):
            q.is_correct()

    def test_all_incorrect_raises(self):
        q = Question("Q?", QuestionType.TEXT_QUESTION)
        q.add_answers([Answer("A", False), Answer("B", False)])
        with pytest.raises(NotAllAnswerCorrectError):
            q.is_correct()




class TestNumberOfOptionsValidation:
    def test_minimum_valid(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION, number_of_options=3)
        q.add_answers([Answer("A", True), Answer("B", False)])
        assert q.is_correct() is True

    def test_two_raises(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION, number_of_options=2)
        q.add_answers([Answer("A", True), Answer("B", False)])
        with pytest.raises(NotAtLeastThreeNumberOfOptions):
            q.is_correct()

    def test_one_raises(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION, number_of_options=1)
        q.add_answers([Answer("A", True), Answer("B", False)])
        with pytest.raises(NotAtLeastThreeNumberOfOptions):
            q.is_correct()

    def test_zero_raises(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION, number_of_options=0)
        q.add_answers([Answer("A", True), Answer("B", False)])
        with pytest.raises(NotAtLeastThreeNumberOfOptions):
            q.is_correct()




class TestAnswersUniqueness:
    def test_duplicate_content_raises(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION)
        q.add_answers([Answer("Same", True), Answer("Same", True)])
        with pytest.raises(AnswersAreNotUnique):
            q.is_correct()

    def test_unique_content_passes(self):
        q = Question("Q?", QuestionType.SINGLE_CHOICE_QUESTION)
        q.add_answers([Answer("A", True), Answer("B", False)])
        assert q.is_correct() is True

    def test_duplicate_in_three_answers_raises(self):
        q = Question("Q?", QuestionType.MULTIPLE_CHOICE_QUESTION)
        q.add_answers([Answer("A", True), Answer("B", False), Answer("A", True)])
        with pytest.raises(AnswersAreNotUnique):
            q.is_correct()
