import os
from pathlib import Path
from typing import List, Dict, Set, Tuple
from easylabeltool.my_logger import logger as _logger

ans_map: Dict[str, int] = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "E": 4,
    "F": 5,
    "G": 6,
    "H": 7,
    "I": 8,
    "J": 9,
    "K": 10,
    "L": 11,
}
supported_types: Tuple[str] = (
    "Descriptive",
    "Explanatory",
    "Predictive",
    "Reverse Inference",
    "Counterfactual",
    "Introspection",
)

abbr_to_qtype_map: Dict[str, str] = {
    "d": "Descriptive",
    "e": "Explanatory",
    "p": "Predictive",
    "r": "Reverse Inference",
    "c": "Counterfactual",
    "i": "Introspection",
    "1": "Descriptive",
    "2": "Explanatory",
    "3": "Predictive",
    "4": "Reverse Inference",
    "5": "Counterfactual",
    "6": "Introspection",
}


def bump_version(filepath: Path) -> Path:
    head, tail = os.path.split(filepath)
    name, ext = os.path.splitext(tail)
    suffix = 1
    while filepath.is_file():
        _logger.info(f"{filepath} already exist")
        suffix += 1
        new_name = f"{name}_v{str(suffix)}{ext}"
        filepath = Path(head) / new_name
    return filepath
