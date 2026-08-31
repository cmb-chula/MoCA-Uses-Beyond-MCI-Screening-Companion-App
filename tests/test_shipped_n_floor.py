"""Fail if shipped aggregate JSON still carries a numeric n below the DUA floor.

Values and keys of offending cells are never printed (rule 4b).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from utils.cell_floor import (  # noqa: E402
    CELL_FLOOR,
    N_KEYS,
    format_n,
    n_field_is_publishable,
    n_is_below_floor,
)

DATA = Path(_REPO_ROOT) / "data"


def _count_below(obj: object) -> int:
    n = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in N_KEYS and n_is_below_floor(v):
                n += 1
            n += _count_below(v)
    elif isinstance(obj, list):
        for item in obj:
            n += _count_below(item)
    return n


def test_synthetic_subfloor_int_is_detected_marker_is_not():
    assert n_is_below_floor(0) is True
    assert n_is_below_floor(4) is True
    assert n_is_below_floor(5) is False
    assert n_is_below_floor(12) is False
    assert n_is_below_floor("<5") is False
    assert n_is_below_floor("n<5") is False
    assert n_field_is_publishable(4) is False
    assert n_field_is_publishable(5) is True
    assert n_field_is_publishable("<5") is True
    assert format_n(4) == "n<5"
    assert format_n("<5") == "n<5"
    assert format_n(12) == "n=12"


def test_shipped_json_has_no_numeric_n_below_floor():
    below = 0
    files = 0
    for path in sorted(DATA.glob("*.json")):
        files += 1
        below += _count_below(json.loads(path.read_text(encoding="utf-8")))
    assert files >= 1, "no shipped data/*.json files found"
    assert below == 0, (
        f"{below} numeric n-field(s) below floor {CELL_FLOOR} in shipped "
        "data/*.json (values and keys not printed)"
    )
