import shutil
from pathlib import Path

import pytest

from svg2gakko.errors import SvgMetadataNotFoundError
from svg2gakko.input_parser import InputParser


def _make_svg(tmp_path: Path, filename: str, category: int, question: int, type_char: str) -> Path:
    """Helper to create a minimal SVG file with embedded metadata."""
    svg_file = tmp_path / filename
    svg_file.parent.mkdir(parents=True, exist_ok=True)
    svg_file.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg">'
        f'<g data-typst-label="{category}::{question}::{type_char}"/>'
        f'</svg>',
        encoding="utf-8",
    )
    return svg_file


class TestInputParser:
    def test_parse_single_category_single_question(self, tmp_path):
        """One category, one question with two answers."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q1.svg", 1, 0, "q")
        _make_svg(input_dir, "a1.svg", 1, 0, "+")
        _make_svg(input_dir, "a2.svg", 1, 0, "-")

        result_dir = InputParser.parse(input_dir)

        category_dir = result_dir / "1"
        assert category_dir.is_dir()
        assert (category_dir / "1.svg").exists()
        assert (category_dir / "1_1.svg").exists()
        assert (category_dir / "1_2.svg").exists()

    def test_parse_single_category_multiple_questions(self, tmp_path):
        """One category, two questions each with answers."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q1.svg", 1, 0, "q")
        _make_svg(input_dir, "a1_correct.svg", 1, 0, "+")
        _make_svg(input_dir, "a1_wrong.svg", 1, 0, "-")
        _make_svg(input_dir, "q2.svg", 1, 1, "q")
        _make_svg(input_dir, "a2_correct.svg", 1, 1, "+")
        _make_svg(input_dir, "a2_wrong.svg", 1, 1, "-")

        result_dir = InputParser.parse(input_dir)

        category_dir = result_dir / "1"
        files = sorted(f.name for f in category_dir.iterdir())
        assert "1.svg" in files
        assert "1_1.svg" in files
        assert "1_2.svg" in files
        assert "2.svg" in files
        assert "2_1.svg" in files
        assert "2_2.svg" in files

    def test_parse_multiple_categories(self, tmp_path):
        """Two categories, each with their own questions."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "cat1_q.svg", 1, 0, "q")
        _make_svg(input_dir, "cat1_a.svg", 1, 0, "+")
        _make_svg(input_dir, "cat2_q.svg", 2, 0, "q")
        _make_svg(input_dir, "cat2_a.svg", 2, 0, "-")

        result_dir = InputParser.parse(input_dir)

        assert (result_dir / "1" / "1.svg").exists()
        assert (result_dir / "1" / "1_1.svg").exists()
        assert (result_dir / "2" / "1.svg").exists()
        assert (result_dir / "2" / "1_1.svg").exists()

    def test_parse_nested_directories(self, tmp_path):
        """SVGs scattered across nested subdirectories are all found."""
        input_dir = tmp_path / "input"
        sub1 = input_dir / "subdir_a"
        sub2 = input_dir / "subdir_b"
        sub3 = input_dir / "deep" / "nested" / "dir"

        _make_svg(sub1, "q1.svg", 1, 0, "q")
        _make_svg(sub1, "a1.svg", 1, 0, "+")
        _make_svg(sub2, "q2.svg", 1, 1, "q")
        _make_svg(sub2, "a2.svg", 1, 1, "-")
        _make_svg(sub3, "a3.svg", 1, 1, "+")

        result_dir = InputParser.parse(input_dir)

        category_dir = result_dir / "1"
        files = sorted(f.name for f in category_dir.iterdir())
        assert "1.svg" in files
        assert "1_1.svg" in files
        assert "2.svg" in files
        assert "2_1.svg" in files
        assert "2_2.svg" in files

    def test_parse_question_numbering_is_one_based(self, tmp_path):
        """0-based question numbers from metadata become 1-based file names."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q0.svg", 1, 0, "q")
        _make_svg(input_dir, "a0.svg", 1, 0, "+")

        result_dir = InputParser.parse(input_dir)

        assert (result_dir / "1" / "1.svg").exists()
        assert (result_dir / "1" / "1_1.svg").exists()
        assert not (result_dir / "1" / "0.svg").exists()

    def test_parse_skips_question_without_question_file(self, tmp_path):
        """Answers without a question file are skipped."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "orphan_answer.svg", 1, 0, "+")

        result_dir = InputParser.parse(input_dir)

        category_dir = result_dir / "1"
        if category_dir.exists():
            files = list(category_dir.iterdir())
            assert len(files) == 0
        else:
            # Category dir may not even be created if no question files exist
            assert not category_dir.exists()

    def test_parse_uses_first_question_file_when_multiple(self, tmp_path):
        """When multiple question files exist for same question, first (sorted) is used."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q_aaa.svg", 1, 0, "q")
        _make_svg(input_dir, "q_bbb.svg", 1, 0, "q")
        _make_svg(input_dir, "a1.svg", 1, 0, "+")

        result_dir = InputParser.parse(input_dir)

        category_dir = result_dir / "1"
        question_files = [f for f in category_dir.iterdir() if "_" not in f.name]
        assert len(question_files) == 1
        assert question_files[0].name == "1.svg"

    def test_parse_multiple_answers_per_question(self, tmp_path):
        """Multiple answers are numbered sequentially."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q.svg", 1, 0, "q")
        _make_svg(input_dir, "a1.svg", 1, 0, "+")
        _make_svg(input_dir, "a2.svg", 1, 0, "-")
        _make_svg(input_dir, "a3.svg", 1, 0, "+")
        _make_svg(input_dir, "a4.svg", 1, 0, "-")

        result_dir = InputParser.parse(input_dir)

        category_dir = result_dir / "1"
        answer_files = sorted(f.name for f in category_dir.iterdir() if "_" in f.name)
        assert answer_files == ["1_1.svg", "1_2.svg", "1_3.svg", "1_4.svg"]

    def test_parse_returns_temp_dir_path(self, tmp_path):
        """parse() returns a Path to the temp directory."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q.svg", 1, 0, "q")
        _make_svg(input_dir, "a.svg", 1, 0, "+")

        result_dir = InputParser.parse(input_dir)

        assert isinstance(result_dir, Path)
        assert result_dir.exists()
        assert result_dir.is_dir()
        assert "svg2gakko_" in str(result_dir)

    def test_parse_correct_and_incorrect_answers(self, tmp_path):
        """Both '+' and '-' type answers are treated as answers (correct/incorrect)."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q.svg", 1, 0, "q")
        _make_svg(input_dir, "correct.svg", 1, 0, "+")
        _make_svg(input_dir, "wrong.svg", 1, 0, "-")

        result_dir = InputParser.parse(input_dir)

        category_dir = result_dir / "1"
        answer_files = sorted(f.name for f in category_dir.iterdir() if "_" in f.name)
        assert len(answer_files) == 2
        assert "1_1.svg" in answer_files
        assert "1_2.svg" in answer_files

    def test_parse_raises_on_missing_metadata(self, tmp_path):
        """SVGs without the metadata pattern raise SvgMetadataNotFoundError."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        bad_svg = input_dir / "no_metadata.svg"
        bad_svg.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>',
            encoding="utf-8",
        )

        with pytest.raises(SvgMetadataNotFoundError):
            InputParser.parse(input_dir)

    def test_parse_non_svg_files_ignored(self, tmp_path):
        """Non-SVG files in the directory are ignored."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q.svg", 1, 0, "q")
        _make_svg(input_dir, "a.svg", 1, 0, "+")

        # Add non-SVG files
        (input_dir / "readme.txt").write_text("hello")
        (input_dir / "image.png").write_bytes(b"\x89PNG")

        result_dir = InputParser.parse(input_dir)

        category_dir = result_dir / "1"
        all_files = list(category_dir.iterdir())
        assert all(f.suffix == ".svg" for f in all_files)

    def test_parse_empty_directory(self, tmp_path):
        """Empty input directory produces empty temp directory."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        result_dir = InputParser.parse(input_dir)

        assert result_dir.exists()
        subdirs = [d for d in result_dir.iterdir() if d.is_dir()]
        assert len(subdirs) == 0


class TestInputParserReorganize:
    def test_reorganize_basic(self, tmp_path):
        """Reorganize in-place: files are renamed and moved into category dirs."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q1.svg", 1, 0, "q")
        _make_svg(input_dir, "a1.svg", 1, 0, "+")
        _make_svg(input_dir, "a2.svg", 1, 0, "-")

        result_dir = InputParser.reorganize(input_dir)

        assert result_dir == input_dir.resolve()
        assert (input_dir / "1" / "1.svg").exists()
        assert (input_dir / "1" / "1_1.svg").exists()
        assert (input_dir / "1" / "1_2.svg").exists()

    def test_reorganize_removes_original_files(self, tmp_path):
        """Original files are removed after reorganization."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q1.svg", 1, 0, "q")
        _make_svg(input_dir, "a1.svg", 1, 0, "+")

        InputParser.reorganize(input_dir)

        # Original flat files should be gone
        assert not (input_dir / "q1.svg").exists()
        assert not (input_dir / "a1.svg").exists()
        # Only the category directory should remain
        top_level = list(input_dir.iterdir())
        assert len(top_level) == 1
        assert top_level[0].name == "1"

    def test_reorganize_flattens_nested_dirs(self, tmp_path):
        """Nested subdirectories are flattened; only category dirs remain."""
        input_dir = tmp_path / "input"
        sub1 = input_dir / "deep" / "nested"
        sub2 = input_dir / "another"

        _make_svg(sub1, "q1.svg", 1, 0, "q")
        _make_svg(sub1, "a1.svg", 1, 0, "+")
        _make_svg(sub2, "q2.svg", 2, 0, "q")
        _make_svg(sub2, "a2.svg", 2, 0, "-")

        InputParser.reorganize(input_dir)

        # Nested dirs should be gone
        assert not (input_dir / "deep").exists()
        assert not (input_dir / "another").exists()
        # Category dirs should exist
        assert (input_dir / "1" / "1.svg").exists()
        assert (input_dir / "2" / "1.svg").exists()

    def test_reorganize_multiple_categories(self, tmp_path):
        """Multiple categories are created in-place."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "cat1_q.svg", 1, 0, "q")
        _make_svg(input_dir, "cat1_a.svg", 1, 0, "+")
        _make_svg(input_dir, "cat2_q.svg", 2, 0, "q")
        _make_svg(input_dir, "cat2_a.svg", 2, 0, "-")

        result_dir = InputParser.reorganize(input_dir)

        assert result_dir == input_dir.resolve()
        assert (input_dir / "1" / "1.svg").exists()
        assert (input_dir / "1" / "1_1.svg").exists()
        assert (input_dir / "2" / "1.svg").exists()
        assert (input_dir / "2" / "1_1.svg").exists()

    def test_reorganize_returns_input_path(self, tmp_path):
        """reorganize() returns the same path as the input directory."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q.svg", 1, 0, "q")
        _make_svg(input_dir, "a.svg", 1, 0, "+")

        result_dir = InputParser.reorganize(input_dir)

        assert result_dir == input_dir.resolve()

    def test_reorganize_non_svg_files_removed(self, tmp_path):
        """Non-SVG files in the input directory are removed during reorganization."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q.svg", 1, 0, "q")
        _make_svg(input_dir, "a.svg", 1, 0, "+")
        (input_dir / "readme.txt").write_text("hello")
        (input_dir / "image.png").write_bytes(b"\x89PNG")

        InputParser.reorganize(input_dir)

        # Non-SVG files should be gone
        assert not (input_dir / "readme.txt").exists()
        assert not (input_dir / "image.png").exists()
        # Only category dir with SVGs remains
        category_dir = input_dir / "1"
        all_files = list(category_dir.iterdir())
        assert all(f.suffix == ".svg" for f in all_files)

    def test_reorganize_empty_directory(self, tmp_path):
        """Empty input directory stays empty after reorganization."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        result_dir = InputParser.reorganize(input_dir)

        assert result_dir == input_dir.resolve()
        subdirs = [d for d in result_dir.iterdir() if d.is_dir()]
        assert len(subdirs) == 0

    def test_reorganize_multiple_questions_with_answers(self, tmp_path):
        """Multiple questions with multiple answers are reorganized correctly."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        _make_svg(input_dir, "q0.svg", 1, 0, "q")
        _make_svg(input_dir, "a0_correct.svg", 1, 0, "+")
        _make_svg(input_dir, "a0_wrong.svg", 1, 0, "-")
        _make_svg(input_dir, "q1.svg", 1, 1, "q")
        _make_svg(input_dir, "a1_correct.svg", 1, 1, "+")
        _make_svg(input_dir, "a1_wrong.svg", 1, 1, "-")

        InputParser.reorganize(input_dir)

        category_dir = input_dir / "1"
        files = sorted(f.name for f in category_dir.iterdir())
        assert "1.svg" in files
        assert "1_1.svg" in files
        assert "1_2.svg" in files
        assert "2.svg" in files
        assert "2_1.svg" in files
        assert "2_2.svg" in files
