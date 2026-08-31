"""Figure-builder smoke tests (Batch-1, Stage-2).

For a data-free companion APP the Stage-2 "statistical toy-model through the package's
OWN wrapper" analog is: feed a synthetic aggregate-JSON fixture to each of the app's own
figure builders in ``utils.plotting`` and assert it returns a valid Plotly object with
the expected trace content. This uses the REAL builders (not raw plotly), so a regression
in a builder — a KeyError, a wrong-shaped trace, an empty figure where data was supplied —
goes RED. All input is synthetic (``tests/synth_data.py``); no real export is read.
"""

from __future__ import annotations

import os
import sys

import plotly.graph_objects as go
import pytest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (_REPO_ROOT, _TESTS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import synth_data as sd  # noqa: E402
from utils import plotting as P  # noqa: E402


def _n_traces(fig):
    return len(fig.data)


# ── radar / grouped bar ──────────────────────────────────────────────────────
def test_radar_chart_returns_figure_with_a_trace_per_subtype():
    prof = sd.domain_profiles(["0A", "1A", "2A"])
    fig = P.radar_chart(prof, ["0A", "1A", "2A"], title="t")
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) == 3
    # radar closes the polygon: r has one more point than the 7 domains
    assert len(fig.data[0].r) == len(sd.DOMAINS) + 1


def test_radar_chart_renders_suppressed_n_marker():
    prof = sd.domain_profiles(["0A"])
    prof["0A"]["n"] = "<5"
    fig = P.radar_chart(prof, ["0A"], title="t")
    assert "n<5" in fig.data[0].name
    assert "n=<5" not in fig.data[0].name


def test_radar_chart_skips_unknown_subtypes():
    prof = sd.domain_profiles(["0A"])
    fig = P.radar_chart(prof, ["0A", "9Z"])  # 9Z absent -> skipped, no KeyError
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) == 1


def test_grouped_bar_chart_returns_figure():
    prof = sd.domain_profiles(["0A", "0B"])
    fig = P.grouped_bar_chart(prof, ["0A", "0B"], title="t")
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) == 2
    assert list(fig.data[0].y) == [
        prof["0A"]["domains"][d]["median"] for d in sd.DOMAINS
    ]


# ── survival ─────────────────────────────────────────────────────────────────
def test_km_survival_chart_returns_figure():
    curves = sd.survival_curves(["S-0A", "S-0B"])
    fig = P.km_survival_chart(curves, ["S-0A", "S-0B"], title="t")
    assert isinstance(fig, go.Figure)
    # each group -> a CI band trace + a main line trace
    assert _n_traces(fig) == 4


def test_km_survival_chart_skips_absent_group():
    curves = sd.survival_curves(["S-0A"])
    fig = P.km_survival_chart(curves, ["S-0A", "S-9Z"])
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) == 2  # only S-0A rendered (band + line)


# ── forest ───────────────────────────────────────────────────────────────────
def test_forest_plot_returns_figure():
    cox = sd.cox_results()
    fig = P.forest_plot(cox, "All Subtypes", title="HR")
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) >= 1


def test_forest_plot_petersen_model():
    cox = sd.cox_results()
    fig = P.forest_plot(cox, "Petersen MCI", title="HR")
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) >= 1


def test_forest_plot_unknown_model_returns_empty_figure():
    fig = P.forest_plot(sd.cox_results(), "No Such Model")
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) == 0


# ── transition heatmap ───────────────────────────────────────────────────────
def test_transition_heatmap_returns_figure():
    trans = sd.transition_matrix()
    fig = P.transition_heatmap(trans, ["0A", "1A", "2A"], title="T")
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) == 1
    assert fig.data[0].type == "heatmap"


# ── c-index / sojourn ────────────────────────────────────────────────────────
def test_cindex_bar_chart_returns_figure():
    fig = P.cindex_bar_chart(sd.cindex_results(), title="C")
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) == 1
    assert list(fig.data[0].x) == ["All Subtypes", "Cascade Only", "Petersen MCI"]


def test_sojourn_bar_chart_returns_figure():
    fig = P.sojourn_bar_chart(sd.sojourn_times(), ["0A", "1A", "2A"], title="S")
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) == 1


def test_sojourn_bar_chart_skips_absent_subtypes():
    fig = P.sojourn_bar_chart(sd.sojourn_times(["0A"]), ["0A", "9Z"])
    assert isinstance(fig, go.Figure)
    assert list(fig.data[0].x) == ["S-0A"]


# ── cascade network ──────────────────────────────────────────────────────────
def test_cascade_network_chart_returns_figure():
    info = sd.pathway_info()
    trans = sd.transition_matrix()
    prof = sd.domain_profiles(["0A", "1A", "2A", "0B", "0C", "0D", "0E"])
    fig = P.cascade_network_chart(info, trans, prof, highlight_pathway="all")
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) >= 1


@pytest.mark.parametrize("mode", ["all", "none", "steepest", "predominant", "fastest"])
def test_cascade_network_chart_highlight_modes(mode):
    info = sd.pathway_info()
    fig = P.cascade_network_chart(
        info, sd.transition_matrix(), None, highlight_pathway=mode
    )
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) >= 1


def test_cascade_network_chart_highlight_nodes():
    info = sd.pathway_info()
    fig = P.cascade_network_chart(
        info, sd.transition_matrix(), None, highlight_nodes={"0A", "0B"}
    )
    assert isinstance(fig, go.Figure)
    assert _n_traces(fig) >= 1
