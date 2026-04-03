"""Cached data loading functions for the Streamlit app."""

import json
from pathlib import Path

import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FIGURES_DIR = DATA_DIR / "figures"


def _load_json(filename: str) -> dict | None:
    """Load a JSON file from the data directory. Returns None if missing."""
    path = DATA_DIR / filename
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


@st.cache_data
def load_pathway_info() -> dict | None:
    return _load_json("pathway_info.json")


@st.cache_data
def load_domain_profiles() -> dict | None:
    return _load_json("domain_profiles.json")


@st.cache_data
def load_demographics() -> dict | None:
    return _load_json("demographics.json")


@st.cache_data
def load_transition_matrix() -> dict | None:
    return _load_json("transition_matrix.json")


@st.cache_data
def load_sojourn_times() -> dict | None:
    return _load_json("sojourn_times.json")


@st.cache_data
def load_survival_curves() -> dict | None:
    return _load_json("survival_curves.json")


@st.cache_data
def load_cox_results() -> dict | None:
    return _load_json("cox_results.json")


@st.cache_data
def load_cindex_results() -> dict | None:
    return _load_json("cindex_results.json")


@st.cache_data
def load_rfecv_accuracy() -> dict | None:
    return _load_json("rfecv_accuracy.json")


def figure_path(name: str) -> Path | None:
    """Return path to a figure if it exists, else None."""
    p = FIGURES_DIR / name
    return p if p.exists() else None


def data_available(filename: str) -> bool:
    """Check if a data file exists."""
    return (DATA_DIR / filename).exists()


def show_data_missing(name: str):
    """Display a warning when data is not yet exported."""
    st.warning(
        f"**{name}** data not available. "
        "Run `python scripts/export_for_app.py` on cuaim with MOCA_DATA_DIR set "
        "to generate the required data files.",
    )
