"""Data-contract + loader tests (Batch-1, Stage-2).

The cascade_moca_app has NO participant data of its own — every page renders from the
aggregate JSON in ``data/*.json`` exported by the upstream cascade_moca pipeline. These
tests pin the *data contract* those JSON files must satisfy (required keys / dtypes /
shape) and verify ``utils.data_loader``'s IO logic (present -> dict, missing -> None,
correct filename per loader) against SYNTHETIC fixtures written under ``tmp_path`` — no
real export is ever read (DUA-safe; the autouse guard in conftest.py stays green).

Toy-model note: for a data-free companion APP the Stage-2 "statistical toy-model" analog
is exactly this JSON schema/contract check plus the figure-builder smoke tests in
``test_figure_builders.py`` (per the batch instructions). No loader-guard scaffolding is
needed because the builders take dicts as arguments — the test fully controls the input.
"""

from __future__ import annotations

import importlib
import json
import os
import sys

import pytest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (_REPO_ROOT, _TESTS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import synth_data as sd  # noqa: E402
from utils.cell_floor import n_field_is_publishable  # noqa: E402


# ── Contract validators ─────────────────────────────────────────────────────
def _require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def assert_domain_profiles_contract(d: dict):
    _require(isinstance(d, dict) and d, "domain_profiles must be a non-empty dict")
    for sub, rec in d.items():
        _require("n" in rec, f"{sub}: missing 'n'")
        _require(
            n_field_is_publishable(rec["n"]),
            f"{sub}.n: expected int >= 5 or the '<5' suppression marker",
        )
        for k, typ in (("tier", str), ("domains", dict)):
            _require(k in rec, f"{sub}: missing '{k}'")
            _require(isinstance(rec[k], typ), f"{sub}.{k}: expected {typ.__name__}")
        for dom, stats in rec["domains"].items():
            for sk in ("median", "q1", "q3"):
                _require(sk in stats, f"{sub}.domains.{dom}: missing '{sk}'")
                _require(
                    isinstance(stats[sk], (int, float)),
                    f"{sub}.domains.{dom}.{sk}: expected number",
                )


def assert_survival_curves_contract(d: dict):
    _require(isinstance(d, dict) and d, "survival_curves must be a non-empty dict")
    for g, c in d.items():
        for k in ("time", "survival", "ci_lo", "ci_hi"):
            _require(k in c, f"{g}: missing '{k}'")
            _require(isinstance(c[k], list), f"{g}.{k}: expected list")
        _require("n" in c and isinstance(c["n"], int), f"{g}: missing int 'n'")
        n = len(c["time"])
        for k in ("survival", "ci_lo", "ci_hi"):
            _require(len(c[k]) == n, f"{g}.{k}: length {len(c[k])} != time length {n}")


def assert_cox_contract(d: dict):
    _require(isinstance(d, dict) and d, "cox_results must be a non-empty dict")
    for model, m in d.items():
        _require("reference" in m, f"{model}: missing 'reference'")
        _require(
            "groups" in m and isinstance(m["groups"], dict),
            f"{model}: missing 'groups'",
        )
        for g, rec in m["groups"].items():
            for k in ("hr", "ci_lo", "ci_hi"):
                _require(k in rec, f"{model}.{g}: missing '{k}'")
                _require(
                    isinstance(rec[k], (int, float)),
                    f"{model}.{g}.{k}: expected number",
                )
            _require(rec["ci_lo"] <= rec["ci_hi"], f"{model}.{g}: ci_lo > ci_hi")


def assert_cindex_contract(d: dict):
    _require(isinstance(d, dict) and d, "cindex_results must be a non-empty dict")
    for model, rec in d.items():
        for k in ("cindex", "ci_lo", "ci_hi"):
            _require(k in rec, f"{model}: missing '{k}'")
            _require(isinstance(rec[k], (int, float)), f"{model}.{k}: expected number")
        _require("n" in rec and isinstance(rec["n"], int), f"{model}: missing int 'n'")


def assert_sojourn_contract(d: dict):
    _require(isinstance(d, dict) and d, "sojourn_times must be a non-empty dict")
    for s, rec in d.items():
        for k in ("n_spells", "n_events"):
            _require(k in rec and isinstance(rec[k], int), f"{s}: missing int '{k}'")
        _require("km_median" in rec, f"{s}: missing 'km_median'")


def assert_transition_contract(d: dict):
    _require(isinstance(d, dict) and d, "transition_matrix must be a non-empty dict")
    for src, targets in d.items():
        _require(isinstance(targets, dict), f"{src}: row must be a dict")
        for tgt, p in targets.items():
            _require(isinstance(p, (int, float)), f"{src}->{tgt}: prob must be number")
            _require(0.0 <= p <= 1.0 + 1e-9, f"{src}->{tgt}: prob {p} out of [0,1]")


def assert_pathway_info_contract(d: dict):
    _require("pathways" in d and isinstance(d["pathways"], dict), "missing 'pathways'")
    for pw, rec in d["pathways"].items():
        for k in ("subtypes", "color", "label"):
            _require(k in rec, f"pathway {pw}: missing '{k}'")
        _require(
            isinstance(rec["subtypes"], list) and rec["subtypes"],
            f"pathway {pw}: empty subtypes",
        )


# ── Contract tests on synthetic fixtures ─────────────────────────────────────
def test_synthetic_domain_profiles_satisfy_contract():
    assert_domain_profiles_contract(sd.domain_profiles())


def test_synthetic_survival_curves_satisfy_contract():
    assert_survival_curves_contract(sd.survival_curves())


def test_synthetic_cox_satisfy_contract():
    assert_cox_contract(sd.cox_results())


def test_synthetic_cindex_satisfy_contract():
    assert_cindex_contract(sd.cindex_results())


def test_synthetic_sojourn_satisfy_contract():
    assert_sojourn_contract(sd.sojourn_times())


def test_synthetic_transition_satisfy_contract():
    assert_transition_contract(sd.transition_matrix())


def test_synthetic_pathway_info_satisfies_contract():
    assert_pathway_info_contract(sd.pathway_info())


def test_domain_profiles_contract_rejects_numeric_n_below_floor():
    bad = sd.domain_profiles(["0A"])
    bad["0A"]["n"] = 4  # invented; not a shipped cell
    with pytest.raises(AssertionError):
        assert_domain_profiles_contract(bad)
    bad["0A"]["n"] = "<5"
    assert_domain_profiles_contract(bad)


def test_contract_has_teeth_missing_key_fails():
    """A malformed fixture (required key dropped) must fail the validator — proves
    the contract check is not vacuous."""
    bad = sd.survival_curves()
    first = next(iter(bad))
    del bad[first]["ci_hi"]
    with pytest.raises(AssertionError):
        assert_survival_curves_contract(bad)

    bad_cox = sd.cox_results()
    m = next(iter(bad_cox))
    g = next(iter(bad_cox[m]["groups"]))
    del bad_cox[m]["groups"][g]["hr"]
    with pytest.raises(AssertionError):
        assert_cox_contract(bad_cox)


def test_survival_contract_catches_length_mismatch():
    bad = sd.survival_curves()
    g = next(iter(bad))
    bad[g]["ci_lo"] = bad[g]["ci_lo"][:-1]  # truncate -> length mismatch
    with pytest.raises(AssertionError):
        assert_survival_curves_contract(bad)


# ── Loader IO tests (synthetic tmp files only) ───────────────────────────────
@pytest.fixture
def data_loader(monkeypatch, tmp_path):
    """Import utils.data_loader with DATA_DIR redirected at an empty tmp dir and a
    fresh Streamlit cache."""
    import utils.data_loader as dl

    dl = importlib.reload(dl)
    monkeypatch.setattr(dl, "DATA_DIR", tmp_path)
    monkeypatch.setattr(dl, "FIGURES_DIR", tmp_path / "figures")
    try:
        import streamlit as st

        st.cache_data.clear()
    except Exception:
        pass
    return dl


def test_load_json_missing_returns_none(data_loader):
    assert data_loader._load_json("does_not_exist.json") is None


def test_load_json_present_roundtrips(data_loader, tmp_path):
    payload = {"alpha": 1, "beta": [1, 2, 3]}
    (tmp_path / "thing.json").write_text(json.dumps(payload))
    assert data_loader._load_json("thing.json") == payload


def test_data_available(data_loader, tmp_path):
    assert data_loader.data_available("nope.json") is False
    (tmp_path / "yes.json").write_text("{}")
    assert data_loader.data_available("yes.json") is True


def test_figure_path(data_loader, tmp_path):
    figdir = tmp_path / "figures"
    figdir.mkdir()
    assert data_loader.figure_path("absent.png") is None
    (figdir / "present.png").write_bytes(b"\x89PNG")
    p = data_loader.figure_path("present.png")
    assert p is not None and p.name == "present.png"


# Each cached loader must read its OWN filename. Point DATA_DIR at a tmp dir holding a
# distinctly-marked JSON per file, then assert each loader returns its marker.
LOADER_FILES = {
    "load_pathway_info": "pathway_info.json",
    "load_domain_profiles": "domain_profiles.json",
    "load_demographics": "demographics.json",
    "load_transition_matrix": "transition_matrix.json",
    "load_sojourn_times": "sojourn_times.json",
    "load_survival_curves": "survival_curves.json",
    "load_cox_results": "cox_results.json",
    "load_cindex_results": "cindex_results.json",
    "load_rfecv_accuracy": "rfecv_accuracy.json",
}


@pytest.mark.parametrize("loader_name,filename", list(LOADER_FILES.items()))
def test_each_loader_reads_its_own_file(data_loader, tmp_path, loader_name, filename):
    # Write a distinctly-marked payload for every known file.
    for fn in LOADER_FILES.values():
        (tmp_path / fn).write_text(json.dumps({"_marker": fn}))
    try:
        import streamlit as st

        st.cache_data.clear()
    except Exception:
        pass
    fn = getattr(data_loader, loader_name)
    clear = getattr(fn, "clear", None)
    if callable(clear):
        clear()
    assert fn() == {"_marker": filename}


def test_loader_returns_none_when_file_absent(data_loader):
    # Empty DATA_DIR -> every loader returns None (graceful "data not exported yet").
    try:
        import streamlit as st

        st.cache_data.clear()
    except Exception:
        pass
    fn = data_loader.load_cox_results
    clear = getattr(fn, "clear", None)
    if callable(clear):
        clear()
    assert fn() is None
