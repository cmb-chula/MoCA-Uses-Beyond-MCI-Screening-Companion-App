"""DUA rule 4b helpers: published n-cells below 5 are suppressed, never shown as a count."""

from __future__ import annotations

CELL_FLOOR = 5
SUPPRESSED_N = "<5"
N_KEYS = ("n", "n_spells", "n_events")


def is_suppressed_n(value: object) -> bool:
    return value in (SUPPRESSED_N, "n<5")


def n_is_below_floor(value: object) -> bool:
    """True only for a numeric count strictly below the floor. Markers are not below."""
    if is_suppressed_n(value):
        return False
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value < CELL_FLOOR
    if isinstance(value, float) and value.is_integer():
        return int(value) < CELL_FLOOR
    return False


def format_n(value: object) -> str:
    """Render a count as 'n<5' or 'n=12'. Never interpolates a sub-floor integer."""
    if is_suppressed_n(value) or n_is_below_floor(value):
        return "n<5"
    if value is None:
        return "n=?"
    return f"n={value}"


def n_field_is_publishable(value: object) -> bool:
    """Shipped JSON may carry an int at or above the floor, or the suppression marker."""
    if is_suppressed_n(value):
        return True
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value >= CELL_FLOOR
    return False
