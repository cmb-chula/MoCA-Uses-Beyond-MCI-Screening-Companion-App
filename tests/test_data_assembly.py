"""Data-assembly unit tests with EXACT expected outputs (Batch-1, Stage-2).

This app has no participant frames, but it DOES contain deterministic assembly logic
that turns aggregate JSON + subtype labels into figure geometry / colors / orderings.
These are this work's analog of the id-coercion / dedup / cutpoint assembly tests: they
pin exact outputs so a silent change in the layout math, label parsing, tier cutpoints,
color mapping, or matrix assembly goes RED. All inputs are literals / synthetic dicts.
"""

from __future__ import annotations

import os
import re
import sys

import numpy as np

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (_REPO_ROOT, _TESTS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import synth_data as sd  # noqa: E402
from utils import plotting as P  # noqa: E402
from utils import styling as S  # noqa: E402


# ── Node-layout assembly (exact geometry) ────────────────────────────────────
def test_compute_node_positions_tier_A_row():
    # Tier A sits at y=0 (bottom); x is centered with 10.0 spacing.
    pos = P._compute_node_positions(["0A", "1A", "2A"])
    assert pos["0A"] == {"x": -10.0, "y": 0.0}
    assert pos["1A"] == {"x": 0.0, "y": 0.0}
    assert pos["2A"] == {"x": 10.0, "y": 0.0}


def test_compute_node_positions_tier_E_row():
    # Tier E sits at y=52; x spacing is 10.5.
    pos = P._compute_node_positions(["0E", "1E"])
    assert pos["0E"] == {"x": -5.25, "y": 52.0}
    assert pos["1E"] == {"x": 5.25, "y": 52.0}


def test_compute_node_positions_sorts_by_numeric_prefix():
    # Input order scrambled; layout must sort within tier by the integer prefix.
    pos = P._compute_node_positions(["2A", "0A", "1A"])
    assert pos["0A"]["x"] < pos["1A"]["x"] < pos["2A"]["x"]


# ── Subtype label parsing + color mapping (id-coercion analog, exact) ─────────
def test_subtype_color_index_zero_is_base_tier_color():
    # "0A": tier A, index 0 -> unlightened tier color (lower-cased hex).
    assert S.subtype_color("0A") == "#1f77b4"
    assert S.subtype_color("0A") == S.TIER_COLORS["A"].lower()


def test_subtype_color_parses_multidigit_index():
    # "12D": tier D, index 12 -> lighten(base, 12*0.08).
    assert S.subtype_color("12D") == S._lighten(S.TIER_COLORS["D"], 12 * 0.08)


def test_subtype_color_non_digit_prefix_coerces_index_to_zero():
    # "XB": tier B, prefix not a digit -> index coerced to 0.
    assert S.subtype_color("XB") == S._lighten(S.TIER_COLORS["B"], 0.0)


def test_subtype_color_unknown_tier_falls_back_to_grey_base():
    assert S.subtype_color("5Z") == S._lighten("#888888", 5 * 0.08)


def test_subtype_color_short_labels_return_sentinel_grey():
    assert S.subtype_color("") == "#888888"
    assert S.subtype_color("A") == "#888888"
    assert S.subtype_color(None) == "#888888"


def test_lighten_endpoints_exact():
    assert S._lighten("#000000", 0.0) == "#000000"
    assert S._lighten("#000000", 1.0) == "#ffffff"
    assert S._lighten("#ffffff", 0.5) == "#ffffff"
    assert S._lighten("#1F77B4", 0.0) == "#1f77b4"  # normalizes case


def test_rgba_exact():
    assert P._rgba("#C62828", 0.1) == "rgba(198,40,40,0.1)"
    assert P._rgba("#000000", 1.0) == "rgba(0,0,0,1.0)"
    assert P._rgba("#ffffff", 0.5) == "rgba(255,255,255,0.5)"


# ── Forest-plot ordering (tier E->A, then numeric 0->x), exact ───────────────
def test_forest_plot_group_ordering_is_exact():
    cox = sd.cox_results()  # All Subtypes groups: 0A,1A,0B,1B,0C
    fig = P.forest_plot(cox, "All Subtypes")
    # single scatter trace; y holds the ordered group labels
    assert len(fig.data) == 1
    # tier rank C<B<A here (E->A ordering), then numeric ascending within tier.
    assert list(fig.data[0].y) == ["0C", "0B", "1B", "0A", "1A"]


# ── Transition matrix assembly (missing edge -> 0), exact ─────────────────────
def test_transition_heatmap_matrix_exact():
    trans = sd.transition_matrix()
    fig = P.transition_heatmap(trans, ["0A", "1A", "2A"])
    z = np.array(fig.data[0].z, dtype=float)
    expected = np.array(
        [
            [0.5, 0.3, 0.2],  # 0A row
            [0.0, 0.7, 0.3],  # 1A row: no 0A edge -> 0
            [0.0, 0.0, 1.0],  # 2A row: absorbing
        ]
    )
    assert np.allclose(z, expected)


# ── Tier score cutpoints (score -> tier contract), exact partition ────────────
def test_tier_name_cutpoints_partition_0_to_27():
    order = ["A", "B", "C", "D", "E"]
    bounds = {}
    for t in order:
        nums = re.findall(r"\d+", S.TIER_NAMES[t])
        assert len(nums) == 2, f"tier {t}: expected two bounds in {S.TIER_NAMES[t]!r}"
        bounds[t] = (int(nums[0]), int(nums[1]))
    # each bound is lo<=hi, tiers are contiguous, and together cover exactly 0..27
    assert bounds["A"][0] == 0
    assert bounds["E"][1] == 27
    for t in order:
        lo, hi = bounds[t]
        assert lo <= hi
    for prev, cur in zip(order, order[1:]):
        assert bounds[cur][0] == bounds[prev][1] + 1, (
            f"gap/overlap between {prev} and {cur}"
        )


# ── Cascade-network subtype UNION + dedup (multi-source assembly) ─────────────
def _node_trace(fig):
    for tr in fig.data:
        if getattr(tr, "mode", None) == "markers+text":
            return tr
    raise AssertionError("no node trace (mode='markers+text') found")


def test_cascade_network_unions_subtypes_from_transitions_and_pathways():
    info = sd.pathway_info()  # pathways cover {0A,0B,0C,0D,0E}
    trans = sd.transition_matrix()  # covers {0A,1A,2A}
    fig = P.cascade_network_chart(info, trans, None, highlight_pathway="all")
    node = _node_trace(fig)
    labels = set(node.text)
    # union of the two sources, deduped: 7 unique subtypes
    assert labels == {"S-0A", "S-1A", "S-2A", "S-0B", "S-0C", "S-0D", "S-0E"}
    assert len(node.text) == 7  # no duplicate node for 0A (in both sources)
    # a pathway-only subtype and a transition-only subtype both became nodes
    assert "S-0D" in labels  # pathway-only
    assert "S-2A" in labels  # transition-only
