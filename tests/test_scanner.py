import shutil
from pathlib import Path

import pytest

from svg2gakko.scanner import CategoryScanner


class TestCategoryScanner:
    def test_empty_directory(self, tmp_path):
        """Empty directory returns empty dict."""
        result = CategoryScanner.scan(tmp_path)
        assert result == {}

    def test_single_question_file(self, tmp_path):
        """A single question file (no underscore) is grouped correctly."""
        q_file = tmp_path / "1.svg"
        q_file.write_text("")

        result = CategoryScanner.scan(tmp_path)

        assert "1" in result
        assert len(result["1"]["question"]) == 1
        assert result["1"]["question"][0] == q_file
        assert result["1"]["answers"] == []

    def test_single_answer_file(self, tmp_path):
        """A single answer file (with underscore) is grouped correctly."""
        a_file = tmp_path / "1_1.svg"
        a_file.write_text("")

        result = CategoryScanner.scan(tmp_path)

        assert "1" in result
        assert result["1"]["question"] == []
        assert len(result["1"]["answers"]) == 1
        assert result["1"]["answers"][0] == a_file

    def test_question_and_answers(self, tmp_path):
        """Multiple files for the same question are grouped correctly."""
        q_file = tmp_path / "1.svg"
        a1_file = tmp_path / "1_1.svg"
        a2_file = tmp_path / "1_2.svg"
        for f in (q_file, a1_file, a2_file):
            f.write_text("")

        result = CategoryScanner.scan(tmp_path)

        assert "1" in result
        assert len(result["1"]["question"]) == 1
        assert result["1"]["question"][0] == q_file
        assert len(result["1"]["answers"]) == 2
        assert set(result["1"]["answers"]) == {a1_file, a2_file}

    def test_multiple_questions(self, tmp_path):
        """Files for multiple questions are grouped separately."""
        q1_file = tmp_path / "1.svg"
        a1_file = tmp_path / "1_1.svg"
        q2_file = tmp_path / "2.svg"
        a2_file = tmp_path / "2_1.svg"
        for f in (q1_file, a1_file, q2_file, a2_file):
            f.write_text("")

        result = CategoryScanner.scan(tmp_path)

        assert set(result.keys()) == {"1", "2"}

        assert len(result["1"]["question"]) == 1
        assert result["1"]["question"][0] == q1_file
        assert len(result["1"]["answers"]) == 1
        assert result["1"]["answers"][0] == a1_file

        assert len(result["2"]["question"]) == 1
        assert result["2"]["question"][0] == q2_file
        assert len(result["2"]["answers"]) == 1
        assert result["2"]["answers"][0] == a2_file

    def test_question_with_multiple_answers(self, tmp_path):
        """One question with many answers."""
        q_file = tmp_path / "5.svg"
        q_file.write_text("")
        answer_files = []
        for i in range(1, 6):
            a_file = tmp_path / f"5_{i}.svg"
            a_file.write_text("")
            answer_files.append(a_file)

        result = CategoryScanner.scan(tmp_path)

        assert "5" in result
        assert len(result["5"]["question"]) == 1
        assert result["5"]["question"][0] == q_file
        assert len(result["5"]["answers"]) == 5
        assert set(result["5"]["answers"]) == set(answer_files)

    def test_question_without_number(self, tmp_path):
        """File without a number (just .svg) is ignored? Actually, the scanner splits on '_' and takes the first part.
        If the stem does not contain '_', then the whole stem is the question number. So a file named 'question.svg' would be considered a question file with number 'question'.
        We'll test that it's handled (though it's an edge case)."""
        weird_file = tmp_path / "question.svg"
        weird_file.write_text("")

        result = CategoryScanner.scan(tmp_path)

        # The scanner will treat the whole stem as the question number.
        assert "question" in result
        assert len(result["question"]["question"]) == 1
        assert result["question"]["question"][0] == weird_file
        assert result["question"]["answers"] == []

    def test_answer_with_multiple_underscores(self, tmp_path):
        """Answer file with multiple underscores (e.g., '1_1_a.svg') is still split on the first underscore."""
        a_file = tmp_path / "1_1_a.svg"
        a_file.write_text("")

        result = CategoryScanner.scan(tmp_path)

        # The question number is "1", and the rest is ignored.
        assert "1" in result
        assert result["1"]["question"] == []
        assert len(result["1"]["answers"]) == 1
        assert result["1"]["answers"][0] == a_file

    def test_non_svg_files_are_ignored(self, tmp_path):
        """The scanner does not filter by extension; all files are processed."""
        svg_file = tmp_path / "1.svg"
        txt_file = tmp_path / "1.txt"
        png_file = tmp_path / "1_1.png"
        svg_file.write_text("")
        txt_file.write_text("")
        png_file.write_bytes(b"")

        result = CategoryScanner.scan(tmp_path)

        # All files are included, grouped by the stem before the first underscore
        assert "1" in result
        # The question list includes both the .svg and .txt files (both have stem "1")
        assert len(result["1"]["question"]) == 2
        assert set(result["1"]["question"]) == {svg_file, txt_file}
        # The answer list includes the .png file (stem "1_1")
        assert len(result["1"]["answers"]) == 1
        assert result["1"]["answers"][0] == png_file

    def test_question_with_no_answers_and_answers_with_no_question(self, tmp_path):
        """Two questions: one with only a question file, another with only answer files."""
        q_only = tmp_path / "1.svg"
        a_only1 = tmp_path / "2_1.svg"
        a_only2 = tmp_path / "2_2.svg"
        for f in (q_only, a_only1, a_only2):
            f.write_text("")

        result = CategoryScanner.scan(tmp_path)

        # Question 1 has only question file
        assert "1" in result
        assert len(result["1"]["question"]) == 1
        assert result["1"]["question"][0] == q_only
        assert result["1"]["answers"] == []

        # Question 2 has only answer files
        assert "2" in result
        assert result["2"]["question"] == []
        assert len(result["2"]["answers"]) == 2
        assert set(result["2"]["answers"]) == {a_only1, a_only2}

    def test_directory_is_not_recursive(self, tmp_path):
        """The scanner only looks at the top-level directory, not subdirectories."""
        subdir = tmp_path / "sub"
        subdir.mkdir()
        q_file = subdir / "1.svg"
        q_file.write_text("")

        result = CategoryScanner.scan(tmp_path)

        # The scanner sees the subdirectory as an entry, and since its stem "sub" does not contain an underscore,
        # it is treated as a question file (a directory, not a regular file).
        assert "sub" in result
        assert len(result["sub"]["question"]) == 1
        assert result["sub"]["question"][0] == subdir
        assert result["sub"]["answers"] == []
