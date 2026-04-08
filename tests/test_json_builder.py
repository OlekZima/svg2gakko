import json
from pathlib import Path

import pytest

from svg2gakko.json_builder import JSONBuilder
from svg2gakko.question import Answer, Question, QuestionType


class TestJSONBuilder:
    def test_initial_state(self):
        builder = JSONBuilder()
        assert builder.get_questions_count() == 0
        assert str(builder) == "[]"

    def test_add_valid_question(self):
        builder = JSONBuilder()
        question = Question("Test question", QuestionType.SINGLE_CHOICE_QUESTION)
        question.add_answers([Answer("A", True), Answer("B", False)])
        builder.add_question(question)
        assert builder.get_questions_count() == 1

    def test_add_invalid_question_raises(self):
        builder = JSONBuilder()
        question = Question("Test question", QuestionType.SINGLE_CHOICE_QUESTION)
        question.add_answers([Answer("A", False), Answer("B", False)])

        with pytest.raises(Exception) as exc_info:
            builder.add_question(question)

        assert "NotAtLeastOneCorrectAnswersError" in str(exc_info.type)
        assert builder.get_questions_count() == 0

    def test_dump_creates_file(self, tmp_path):
        builder = JSONBuilder()
        question = Question("Test question", QuestionType.SINGLE_CHOICE_QUESTION)
        question.add_answers([Answer("A", True), Answer("B", False)])
        builder.add_question(question)

        output_file = tmp_path / "output.json"
        builder.dump(output_file)

        assert output_file.exists()
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["Content"] == "Test question"
        assert data[0]["QuestionType"] == 0
        assert len(data[0]["Answers"]) == 2

    def test_dump_existing_file_overwrites(self, tmp_path):
        output_file = tmp_path / "output.json"
        output_file.write_text("old content")
        builder = JSONBuilder()
        question = Question("Test question", QuestionType.SINGLE_CHOICE_QUESTION)
        question.add_answers([Answer("A", True), Answer("B", False)])
        builder.add_question(question)
        builder.dump(output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["Content"] == "Test question"

    def test_dump_creates_parent_directories(self, tmp_path):
        builder = JSONBuilder()
        question = Question("Test question", QuestionType.SINGLE_CHOICE_QUESTION)
        question.add_answers([Answer("A", True), Answer("B", False)])
        builder.add_question(question)

        output_dir = tmp_path / "subdir"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "output.json"
        builder.dump(output_file)

        assert output_file.exists()

    def test_get_questions_count(self):
        builder = JSONBuilder()
        assert builder.get_questions_count() == 0

        question1 = Question("Q1", QuestionType.SINGLE_CHOICE_QUESTION)
        question1.add_answers([Answer("A", True), Answer("B", False)])
        builder.add_question(question1)
        assert builder.get_questions_count() == 1

        question2 = Question("Q2", QuestionType.MULTIPLE_CHOICE_QUESTION)
        question2.add_answers([Answer("C", True), Answer("D", False)])
        builder.add_question(question2)
        assert builder.get_questions_count() == 2

    def test_str_representation(self):
        builder = JSONBuilder()
        question = Question("Test question", QuestionType.SINGLE_CHOICE_QUESTION)
        question.add_answers([Answer("A", True), Answer("B", False)])
        builder.add_question(question)

        result = str(builder)
        assert isinstance(result, str)
        parsed = eval(result)
        assert len(parsed) == 1
        assert parsed[0]["Content"] == "Test question"

    def test_add_question_only_if_correct(self):
        builder = JSONBuilder()
        valid_question = Question("Valid", QuestionType.SINGLE_CHOICE_QUESTION)
        valid_question.add_answers([Answer("A", True), Answer("B", False)])
        builder.add_question(valid_question)
        assert builder.get_questions_count() == 1

        invalid_question = Question("Invalid", QuestionType.SINGLE_CHOICE_QUESTION)
        invalid_question.add_answers([Answer("A", False), Answer("B", False)])
        with pytest.raises(Exception):
            builder.add_question(invalid_question)
        assert builder.get_questions_count() == 1

    def test_dump_with_multiple_questions(self, tmp_path):
        builder = JSONBuilder()
        q1 = Question("Q1", QuestionType.SINGLE_CHOICE_QUESTION)
        q1.add_answers([Answer("A1", True), Answer("B1", False)])
        builder.add_question(q1)

        q2 = Question("Q2", QuestionType.MULTIPLE_CHOICE_QUESTION)
        q2.add_answers([Answer("A2", True), Answer("B2", True), Answer("C2", False)])
        builder.add_question(q2)

        output_file = tmp_path / "output.json"
        builder.dump(output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]["Content"] == "Q1"
        assert data[1]["Content"] == "Q2"
        assert data[0]["QuestionType"] == 0
        assert data[1]["QuestionType"] == 1
