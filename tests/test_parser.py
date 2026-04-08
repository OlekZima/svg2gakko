import base64
import re
from pathlib import Path

import pytest
from urllib.error import URLError

from svg2gakko.parser import svg2base64gakko


def test_parse_svg_returns_str():
    """svg2base64gakko returns a string for a valid SVG file."""
    result = svg2base64gakko(Path("tests/data/example.svg"))
    assert isinstance(result, str)


def test_parse_svg_structure():
    """Check that the output has the correct HTML structure."""
    result = svg2base64gakko(Path("tests/data/example.svg"))
    # Should start with <img
    assert result.startswith('<img')
    # Should end with <br>
    assert result.endswith('<br>')
    # Should contain style="width: ...px"
    assert 'style="width:' in result
    # Should contain src="data:image/jpeg;base64,"
    assert 'src="data:image/jpeg;base64,' in result


def test_parse_svg_width_extraction():
    """Check that the width is extracted from the SVG and included in the output."""
    result = svg2base64gakko(Path("tests/data/example.svg"))
    # The example.svg has width="236", so we expect style="width: 236px"
    assert 'style="width: 236px"' in result


def test_parse_svg_base64_valid():
    """Check that the base64 string is valid and can be decoded."""
    result = svg2base64gakko(Path("tests/data/example.svg"))
    # Extract the base64 part using regex
    match = re.search(r'src="data:image/jpeg;base64,([^"]+)"', result)
    assert match is not None
    base64_str = match.group(1)
    # Decode the base64 string, should not raise an exception
    decoded = base64.b64decode(base64_str)
    assert isinstance(decoded, bytes)
    # The decoded bytes should start with JPEG magic number: 0xFFD8
    assert decoded.startswith(b'\xff\xd8')


def test_parse_svg_nonexistent_file():
    """svg2base64gakko should raise URLError for a non-existent file."""
    with pytest.raises(URLError):
        svg2base64gakko(Path("non_existent.svg"))


def test_parse_svg_invalid_svg(tmp_path):
    """If the SVG is invalid, the function may raise an exception from cairosvg or PIL.
    We don't know exactly what exception, but we expect some exception."""
    invalid_svg = tmp_path / "invalid.svg"
    invalid_svg.write_text("not an svg")
    with pytest.raises(Exception):
        svg2base64gakko(invalid_svg)


def test_parse_svg_empty_svg(tmp_path):
    """An empty SVG might cause an error in the conversion. We expect an exception."""
    empty_svg = tmp_path / "empty.svg"
    empty_svg.write_text("")
    with pytest.raises(Exception):
        svg2base64gakko(empty_svg)


def test_parse_svg_without_width(tmp_path):
    """SVG without explicit width might still be processed (default width?).
    However, the function uses PIL to get the image width, which should be the actual width of the image.
    We'll create a minimal SVG with a rectangle but no width attribute on the root.
    The function should still work and return a width."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect x="10" y="10" width="80" height="80" fill="red"/>
</svg>"""
    svg_file = tmp_path / "no_width.svg"
    svg_file.write_text(svg_content, encoding="utf-8")
    result = svg2base64gakko(svg_file)
    # The result should still contain a width (the image width after conversion)
    assert 'style="width:' in result
    # The width should be a positive integer
    match = re.search(r'style="width: (\d+)px"', result)
    assert match is not None
    width = int(match.group(1))
    assert width > 0


def test_parse_svg_returns_same_for_same_input(tmp_path):
    """Multiple calls with the same SVG should return the same string."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50">
  <circle cx="25" cy="25" r="20" fill="blue"/>
</svg>"""
    svg_file = tmp_path / "circle.svg"
    svg_file.write_text(svg_content, encoding="utf-8")
    result1 = svg2base64gakko(svg_file)
    result2 = svg2base64gakko(svg_file)
    assert result1 == result2


def test_parse_svg_different_svgs_produce_different_outputs(tmp_path):
    """Different SVGs should produce different base64 strings (different images)."""
    svg1_content = """<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">
  <rect width="10" height="10" fill="red"/>
</svg>"""
    svg2_content = """<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">
  <rect width="10" height="10" fill="blue"/>
</svg>"""
    svg1 = tmp_path / "red.svg"
    svg2 = tmp_path / "blue.svg"
    svg1.write_text(svg1_content, encoding="utf-8")
    svg2.write_text(svg2_content, encoding="utf-8")
    result1 = svg2base64gakko(svg1)
    result2 = svg2base64gakko(svg2)
    # The base64 strings should be different
    # Extract the base64 part
    match1 = re.search(r'src="data:image/jpeg;base64,([^"]+)"', result1)
    match2 = re.search(r'src="data:image/jpeg;base64,([^"]+)"', result2)
    assert match1 is not None and match2 is not None
    assert match1.group(1) != match2.group(1)
