import re
import tempfile
from pathlib import Path
from typing import Tuple

from svg2gakko.errors import SvgMetadataNotFoundError


TEMP_DIR_PARSER  = Path(tempfile.mkdtemp(prefix="svg2gakko_"))

def get_data_from_svg(file: Path) -> Tuple[int, int, str]:
    with open(file, encoding="utf-8") as svg_file:
        result = re.search(r"(\d+)::(\d+)::([q+-])", svg_file.read())
        if result is None:
            raise SvgMetadataNotFoundError(
                f"SVG file '{file}' does not contain the expected metadata pattern "
                f"({{category}}::{{question}}::{{type}})."
            )

        category_n, question_n, typee = result.groups()

        return int(category_n), int(question_n), typee


if __name__ == "__main__":
    print(get_data_from_svg(Path("tests/data/real/c1/output1.svg")))
