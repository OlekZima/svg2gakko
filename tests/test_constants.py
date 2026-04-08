import re
import tempfile
from pathlib import Path

import pytest

from svg2gakko.constants import TEMP_DIR_PARSER, get_data_from_svg
from svg2gakko.errors import SvgMetadataNotFoundError


class TestConstants:
    def test_temp_dir_parser_exists(self):
        """TEMP_DIR_PARSER should be a Path pointing to an existing directory."""
        assert isinstance(TEMP_DIR_PARSER, Path)
        assert TEMP_DIR_PARSER.exists()
        assert TEMP_DIR_PARSER.is_dir()
        assert TEMP_DIR_PARSER.name.startswith("svg2gakko_")


class TestGetDataFromSvg:
    def test_valid_metadata(self, tmp_path):
        """Extract category, question, and type from a valid SVG."""
        svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <g data-typst-label="5::12::q">
    <!-- some content -->
  </g>
</svg>"""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding="utf-8")

        category, question, type_char = get_data_from_svg(svg_file)

        assert category == 5
        assert question == 12
        assert type_char == "q"

    def test_valid_metadata_with_plus(self, tmp_path):
        """Extract metadata with '+' type (correct answer)."""
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg">
  <g data-typst-label="3::7::+"/>
</svg>"""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding="utf-8")

        category, question, type_char = get_data_from_svg(svg_file)

        assert category == 3
        assert question == 7
        assert type_char == "+"

    def test_valid_metadata_with_minus(self, tmp_path):
        """Extract metadata with '-' type (incorrect answer)."""
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg">
  <g data-typst-label="1::0::-"/>
</svg>"""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding="utf-8")

        category, question, type_char = get_data_from_svg(svg_file)

        assert category == 1
        assert question == 0
        assert type_char == "-"

    def test_metadata_with_extra_spaces(self, tmp_path):
        """The pattern should be matched even if there are extra spaces around the attribute value."""
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg">
  <g data-typst-label=" 5::12::q " />
</svg>"""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding="utf-8")

        category, question, type_char = get_data_from_svg(svg_file)

        assert category == 5
        assert question == 12
        assert type_char == "q"

    def test_metadata_anywhere_in_file(self, tmp_path):
        """The pattern can appear anywhere in the SVG content."""
        svg_content = """<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <defs/>
  <rect width="100" height="100" fill="red"/>
  <!-- some comment -->
  <g transform="translate(10,20)" data-typst-label="2::8::+">
    <text>Hello</text>
  </g>
</svg>"""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding="utf-8")

        category, question, type_char = get_data_from_svg(svg_file)

        assert category == 2
        assert question == 8
        assert type_char == "+"

    def test_no_metadata_raises(self, tmp_path):
        """If the SVG does not contain the metadata pattern, raise SvgMetadataNotFoundError."""
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100"/>
</svg>"""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding="utf-8")

        with pytest.raises(SvgMetadataNotFoundError) as exc_info:
            get_data_from_svg(svg_file)

        assert "does not contain the expected metadata pattern" in str(exc_info.value)
        assert svg_file.name in str(exc_info.value)

    def test_metadata_with_wrong_format_raises(self, tmp_path):
        """Pattern must be exactly three numbers separated by double colons and ending with q, +, or -."""
        # Missing one part
        svg_content = """<svg><g data-typst-label="5::q"/></svg>"""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding="utf-8")

        with pytest.raises(SvgMetadataNotFoundError):
            get_data_from_svg(svg_file)

    def test_metadata_with_invalid_type_raises(self, tmp_path):
        """Type must be q, +, or -. Other characters are not accepted."""
        svg_content = """<svg><g data-typst-label="5::12::x"/></svg>"""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding="utf-8")

        with pytest.raises(SvgMetadataNotFoundError):
            get_data_from_svg(svg_file)

    def test_metadata_with_non_numeric_numbers(self, tmp_path):
        """The first two parts must be integers. If they are not, the regex still matches, but int conversion will happen in get_data_from_svg.
        However, the regex pattern expects digits, so non-digits will not match. Let's test with digits."""
        svg_content = """<svg><g data-typst-label="ab::cd::q"/></svg>"""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding="utf-8")

        with pytest.raises(SvgMetadataNotFoundError):
            get_data_from_svg(svg_file)

    def test_multiple_metadata_patterns(self, tmp_path):
        """If there are multiple patterns, the first one is used (re.search finds the first match)."""
        svg_content = """<svg>
  <g data-typst-label="1::2::q"/>
  <g data-typst-label="3::4::+"/>
</svg>"""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding="utf-8")

        category, question, type_char = get_data_from_svg(svg_file)

        assert category == 1
        assert question == 2
        assert type_char == "q"

    def test_file_not_found_raises(self):
        """If the file does not exist, the function will raise a FileNotFoundError (built-in)."""
        non_existent = Path("/non/existent/file.svg")
        with pytest.raises(FileNotFoundError):
            get_data_from_svg(non_existent)

    def test_encoding_handled(self, tmp_path):
        """The file is opened with UTF-8 encoding. Ensure it works with special characters in the SVG (outside the pattern)."""
        svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <g data-typst-label="9::3::-">
    <text>© 2024</text>
  </g>
</svg>"""
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(svg_content, encoding="utf-8")

        category, question, type_char = get_data_from_svg(svg_file)

        assert category == 9
        assert question == 3
        assert type_char == "-"
