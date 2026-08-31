"""Synthetic aggregate-JSON fixtures for the cascade_moca_app tests (Batch-1, Stage-2).

This module builds SMALL, fully synthetic dicts that mirror the *shape / data-contract*
of the app's exported aggregate JSON (``data/*.json``) — medians, hazard ratios, n
counts, transition probabilities. It contains **no participant rows and no values from
the real export** (every number here is invented). All the app's figure/section builders
in ``utils.plotting`` consume these dicts directly, so tests can exercise the real
builders on synthetic input with zero real-data access (DUA-safe).

Not a ``test_*`` file, so it is neither collected as tests nor scanned by the DUA
meta-test; it is imported by the sibling ``test_*`` modules.
"""

from __future__ import annotations

# 7 MoCA domains, matching utils.styling.DOMAINS.
DOMAINS = ["VIS", "NAME", "ATTEN", "LAN", "ABS", "DELAY", "ORI"]


def domain_profiles(subtypes: list[str] | None = None) -> dict:
    """Synthetic ``domain_profiles.json`` — {subtype: {n, tier, domains{...}, moca_*}}."""
    subtypes = subtypes or ["0A", "1A", "2A", "0B", "0C", "0D", "0E"]
    out = {}
    for i, sub in enumerate(subtypes):
        # deterministic, monotone-ish synthetic medians in [0,1]
        base = 0.3 + 0.05 * (i % 7)
        out[sub] = {
            "n": 30 + i,
            "tier": sub[-1],
            "domains": {
                d: {
                    "median": round(min(1.0, base + 0.03 * j), 3),
                    "q1": round(max(0.0, base + 0.03 * j - 0.1), 3),
                    "q3": round(min(1.0, base + 0.03 * j + 0.1), 3),
                    "mean": round(min(1.0, base + 0.03 * j), 3),
                    "std": 0.12,
                }
                for j, d in enumerate(DOMAINS)
            },
            "moca_total_mean": 20.0 - i,
            "moca_total_std": 3.0,
            "moca_total_med": 20.0 - i,
        }
    return out


def survival_curves(groups: list[str] | None = None) -> dict:
    """Synthetic ``survival_curves.json`` — keys are ``S-<subtype>``."""
    groups = groups or ["S-0A", "S-0B", "S-0C"]
    t = [0.0, 1.0, 2.0, 3.0, 4.0]
    out = {}
    for i, g in enumerate(groups):
        drop = 0.06 + 0.02 * i
        surv = [round(max(0.0, 1.0 - drop * k), 4) for k in range(len(t))]
        out[g] = {
            "time": list(t),
            "survival": surv,
            "ci_lo": [round(max(0.0, s - 0.05), 4) for s in surv],
            "ci_hi": [round(min(1.0, s + 0.05), 4) for s in surv],
            "n": 40 + i,
            "type": "cascade" if i == 0 else "subtype",
            "cascade": i == 0,
        }
    return out


def cox_results() -> dict:
    """Synthetic ``cox_results.json`` — {model: {reference, groups{subtype:{hr,ci_lo,ci_hi}}}}."""

    def grp(hr, lo, hi):
        return {"hr": hr, "ci_lo": lo, "ci_hi": hi}

    return {
        "All Subtypes": {
            "reference": "0E",
            "groups": {
                "0A": grp(3.2, 2.1, 4.9),
                "1A": grp(2.8, 1.7, 4.6),
                "0B": grp(2.1, 1.4, 3.2),
                "1B": grp(1.9, 1.2, 3.0),
                "0C": grp(1.5, 1.0, 2.3),
            },
        },
        "Cascade Only": {
            "reference": "0E",
            "groups": {
                "0A": grp(3.0, 2.0, 4.5),
                "0B": grp(2.0, 1.3, 3.1),
                "0C": grp(1.4, 0.95, 2.1),
            },
        },
        "Petersen MCI": {
            "reference": "naMCI-sd",
            "groups": {
                "aMCI-md": grp(2.4, 1.5, 3.8),
                "aMCI-sd": grp(1.8, 1.2, 2.7),
                "naMCI-md": grp(1.3, 0.9, 1.9),
            },
        },
    }


def cindex_results() -> dict:
    """Synthetic ``cindex_results.json`` — {model: {cindex, ci_lo, ci_hi, n}}."""
    return {
        "All Subtypes": {"cindex": 0.80, "ci_lo": 0.76, "ci_hi": 0.84, "n": 1000},
        "Cascade Only": {"cindex": 0.74, "ci_lo": 0.70, "ci_hi": 0.78, "n": 900},
        "Petersen MCI": {"cindex": 0.63, "ci_lo": 0.58, "ci_hi": 0.68, "n": 1000},
    }


def sojourn_times(subtypes: list[str] | None = None) -> dict:
    """Synthetic ``sojourn_times.json`` — {subtype: {n_spells,n_events,km_median,km_rmst,q_sojourn}}."""
    subtypes = subtypes or ["0A", "1A", "2A"]
    out = {}
    for i, s in enumerate(subtypes):
        out[s] = {
            "n_spells": 30 + i,
            "n_events": 15 + i,
            "km_median": round(3.5 - 0.5 * i, 3),
            "km_rmst": round(4.0 - 0.3 * i, 3),
            "q_sojourn": round(2.0 + 0.2 * i, 3),
        }
    return out


def transition_matrix() -> dict:
    """Synthetic ``transition_matrix.json`` — {src: {tgt: prob}} (rows sum ~1)."""
    return {
        "0A": {"0A": 0.5, "1A": 0.3, "2A": 0.2},
        "1A": {"1A": 0.7, "2A": 0.3},
        "2A": {"2A": 1.0},
    }


def pathway_info() -> dict:
    """Synthetic ``pathway_info.json`` (subset used by cascade_network_chart)."""
    return {
        "tier_order": ["A", "B", "C", "D", "E"],
        "tier_names": {
            "A": "MoCA 0-13",
            "B": "MoCA 14-17",
            "C": "MoCA 18-22",
            "D": "MoCA 23-24",
            "E": "MoCA 25-27",
        },
        "tier_stages": {
            "A": "Severe",
            "B": "Moderate",
            "C": "Probable MCI",
            "D": "Likely MCI",
            "E": "Normal",
        },
        "tier_colors": {
            "A": "#1F77B4",
            "B": "#FF7F0E",
            "C": "#2CA02C",
            "D": "#D62728",
            "E": "#9467BD",
        },
        "cascade_tier_colors": {
            "A": "#1E88E5",
            "B": "#FB8C00",
            "C": "#43A047",
            "D": "#E53935",
            "E": "#7E57C2",
        },
        "cascade_tier_bands": {
            "A": "#E3F2FD",
            "B": "#FFF3E0",
            "C": "#E8F5E9",
            "D": "#FFEBEE",
            "E": "#EDE7F6",
        },
        "cascade_subtypes": ["0A", "0B", "0C", "0D", "0E"],
        "pathways": {
            "steepest": {
                "subtypes": ["0C", "0B", "0A"],
                "color": "#C62828",
                "dash": "solid",
                "label": "Steepest Decline",
            },
            "predominant": {
                "subtypes": ["0E", "0D", "0C"],
                "color": "#1565C0",
                "dash": "dash",
                "label": "Predominant Pathway",
            },
            "fastest": {
                "subtypes": ["0E", "0C", "0A"],
                "color": "#2E7D32",
                "dash": "dot",
                "label": "Fastest Decline",
            },
        },
    }
