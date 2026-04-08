from typing import Literal
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class File:
    path: Path
    file_type: Literal["+", "-", "q"]
    weight: int = 1
