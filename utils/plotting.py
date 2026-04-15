"""Reusable Plotly figure generators for the Streamlit app."""

import math
import numpy as np
import plotly.graph_objects as go

from utils.styling import (
    DOMAINS, DOMAIN_LABELS, DOMAIN_MAX,
    subtype_color, apply_plotly_style,
    PETERSEN_PALETTE, MODALITY_COLORS,
)


def radar_chart(profiles: dict, subtypes: list[str], title: str = "") -> go.Figure:
    """Create a radar chart comparing domain profiles across subtypes.

    Parameters
    ----------
    profiles : dict
        Full domain_profiles.json data.
    subtypes : list[str]
        Subtype labels to include (e.g., ["0A", "1A", "2A"]).
    title : str
        Chart title.
    """
    categories = [DOMAIN_LABELS.get(d, d) for d in DOMAINS]
    fig = go.Figure()

    for sub in subtypes:
        if sub not in profiles:
            continue
        vals = [profiles[sub]["domains"][d]["median"] for d in DOMAINS]
        # Close the polygon
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            name=f"S-{sub} (n={profiles[sub]['n']})",
            line=dict(color=subtype_color(sub), width=2),
            fill="toself",
            fillcolor=subtype_color(sub),
            opacity=0.15,
            hovertemplate=f"<b>S-{sub}</b><br>%{{theta}}: %{{r:.3f}}<extra></extra>",
        ))

    fig.update_layout(
        title=title,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=11)),
        ),
        showlegend=True,
        legend=dict(font=dict(size=11), orientation="h", yanchor="bottom", y=-0.25),
        margin=dict(l=60, r=60, t=60, b=80),
        height=500,
    )
    return fig


def grouped_bar_chart(profiles: dict, subtypes: list[str], title: str = "") -> go.Figure:
    """Create a grouped bar chart of domain profiles."""
    fig = go.Figure()
    categories = [DOMAIN_LABELS.get(d, d) for d in DOMAINS]

    for sub in subtypes:
        if sub not in profiles:
            continue
        vals = [profiles[sub]["domains"][d]["median"] for d in DOMAINS]
        errors = [profiles[sub]["domains"][d]["q3"] - profiles[sub]["domains"][d]["median"] for d in DOMAINS]
        fig.add_trace(go.Bar(
            name=f"S-{sub} (n={profiles[sub]['n']})",
            x=categories,
            y=vals,
            error_y=dict(type="data", array=errors, visible=True),
            marker_color=subtype_color(sub),
            hovertemplate=f"<b>S-{sub}</b><br>%{{x}}: %{{y:.3f}}<extra></extra>",
        ))

    fig.update_layout(
        title=title,
        barmode="group",
        xaxis_title="MoCA Domain",
        yaxis_title="Normalized Score (0-1)",
        yaxis=dict(range=[0, 1.05]),
        height=450,
        legend=dict(font=dict(size=11), orientation="h", yanchor="bottom", y=-0.3),
    )
    return apply_plotly_style(fig)


def km_survival_chart(curves: dict, groups: list[str], title: str = "") -> go.Figure:
    """Create Kaplan-Meier survival curves with confidence bands."""
    fig = go.Figure()

    for grp in groups:
        if grp not in curves:
            continue
        c = curves[grp]
        color = _km_color(grp, c)
        opacity = 1.0 if c.get("cascade", False) or c.get("type") == "petersen" else 0.4

        # Confidence band
        fig.add_trace(go.Scatter(
            x=c["time"] + c["time"][::-1],
            y=c["ci_hi"] + c["ci_lo"][::-1],
            fill="toself",
            fillcolor=_rgba(color, 0.1),
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        ))

        # Main line
        fig.add_trace(go.Scatter(
            x=c["time"],
            y=c["survival"],
            name=f"{grp} (n={c['n']})",
            line=dict(color=color, width=2.5 if opacity == 1.0 else 1.5),
            opacity=opacity,
            hovertemplate=f"<b>{grp}</b><br>Time: %{{x:.1f}} yr<br>Survival: %{{y:.3f}}<extra></extra>",
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Time since baseline (years)",
        yaxis_title="Dementia-free survival probability",
        yaxis=dict(range=[0, 1.05]),
        height=500,
        legend=dict(font=dict(size=10)),
    )
    return apply_plotly_style(fig)


def forest_plot(cox: dict, model_name: str, title: str = "") -> go.Figure:
    """Create a horizontal forest plot of hazard ratios."""
    if model_name not in cox:
        return go.Figure()

    data = cox[model_name]
    # Sort: tier E→A (reverse alpha on last char), then number 0→x
    tier_order = {"E": 0, "D": 1, "C": 2, "B": 3, "A": 4}
    def _sort_key(g):
        clean = g.replace("S-", "")
        if len(clean) >= 2 and clean[-1].isalpha():
            return (tier_order.get(clean[-1], 9), int(clean[:-1]) if clean[:-1].isdigit() else 99)
        return (9, g)  # Petersen groups go last
    groups = sorted(data["groups"].keys(), key=_sort_key)
    hrs = [data["groups"][g]["hr"] for g in groups]
    ci_lo = [data["groups"][g]["ci_lo"] for g in groups]
    ci_hi = [data["groups"][g]["ci_hi"] for g in groups]
    colors = [subtype_color(g.replace("S-", "")) if g.startswith("S-") or g[0].isdigit()
              else PETERSEN_PALETTE.get(g, "#666") for g in groups]

    fig = go.Figure()

    # Reference line at HR=1
    fig.add_vline(x=1, line_dash="dash", line_color="#999", line_width=1)

    # Error bars + points
    fig.add_trace(go.Scatter(
        x=hrs,
        y=groups,
        mode="markers",
        marker=dict(size=10, color=colors),
        error_x=dict(
            type="data",
            symmetric=False,
            array=[h - l for h, l in zip(ci_hi, hrs)],
            arrayminus=[h - l for h, l in zip(hrs, ci_lo)],
            thickness=1.5,
            width=4,
        ),
        hovertemplate="%{y}<br>HR: %{x:.2f}<br>CI: [%{customdata[0]:.2f}, %{customdata[1]:.2f}]<extra></extra>",
        customdata=list(zip(ci_lo, ci_hi)),
    ))

    fig.update_layout(
        title=f"{title} (ref: {data['reference']})",
        xaxis_title="Hazard Ratio",
        xaxis=dict(type="log"),
        height=max(300, len(groups) * 28 + 100),
        showlegend=False,
    )
    return apply_plotly_style(fig)


def domain_tier_heatmap(profiles: dict, title: str = "") -> go.Figure:
    """Domain score heatmap across all subtypes, grouped by tier.

    Rows = subtypes (sorted E→A top to bottom, 0→x within tier).
    Cols = 7 domains. Color = median (RdYlGn). Dot size = IQR spread.
    """
    from utils.styling import TIER_COLORS

    # Sort subtypes: tier E→A, then numeric index ascending
    _tier_ord = {"E": 0, "D": 1, "C": 2, "B": 3, "A": 4}
    subs = sorted(
        profiles.keys(),
        key=lambda s: (_tier_ord.get(s[-1], 9), int(s[:-1]) if s[:-1].isdigit() else 0),
    )

    n_rows = len(subs)
    n_cols = len(DOMAINS)

    # Build matrices
    z_med = np.full((n_rows, n_cols), np.nan)
    iqr = np.full((n_rows, n_cols), 0.0)
    text_vals = [["" for _ in range(n_cols)] for _ in range(n_rows)]
    hover = [["" for _ in range(n_cols)] for _ in range(n_rows)]

    for i, sub in enumerate(subs):
        pr = profiles[sub]
        for j, d in enumerate(DOMAINS):
            dd = pr["domains"].get(d, {})
            med = dd.get("median", np.nan)
            q1 = dd.get("q1", med)
            q3 = dd.get("q3", med)
            z_med[i, j] = med
            iqr[i, j] = max(0, (q3 - q1))
            text_vals[i][j] = f"{med:.2f}" if not np.isnan(med) else ""
            hover[i][j] = (
                f"S-{sub} \u2014 {DOMAIN_LABELS[d]}<br>"
                f"Median: {med:.2f}<br>IQR: {q1:.2f}\u2013{q3:.2f}<br>"
                f"n={pr.get('n', 0)}"
            )

    # Use raw S-xx strings as y categories; display HTML-colored tick text
    # that INCLUDES the n= count so we avoid a separate right-side column.
    y_labels = [f"S-{s}" for s in subs]
    y_ticktext = [
        (f"<b style='color:{TIER_COLORS.get(s[-1], '#333')}'>S-{s}</b><br>"
         f"<span style='color:#888;font-size:9px'>n={profiles[s].get('n', 0)}</span>")
        for s in subs
    ]
    x_labels = [DOMAIN_LABELS[d] for d in DOMAINS]

    # Heatmap (no built-in text — we add per-cell annotations for color control)
    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        z=z_med,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0.0, "#a50026"], [0.2, "#d73027"], [0.4, "#fdae61"],
            [0.6, "#fee08b"], [0.75, "#d9ef8b"], [0.9, "#66bd63"], [1.0, "#006837"],
        ],
        zmin=0, zmax=1,
        hovertext=hover,
        hovertemplate="%{hovertext}<extra></extra>",
        colorbar=dict(
            title=dict(text="Median score", font=dict(size=11), side="right"),
            tickvals=[0, 0.25, 0.5, 0.75, 1.0],
            ticktext=["Impaired", "0.25", "0.50", "0.75", "Preserved"],
            tickfont=dict(size=10),
            len=0.85,
            thickness=14,
            x=1.02,
            xpad=4,
        ),
    ))

    # Dot overlay — size proportional to IQR (larger dot = more variability)
    xs, ys, sizes, hovers = [], [], [], []
    for i in range(n_rows):
        for j in range(n_cols):
            v = iqr[i, j]
            if v > 0:
                xs.append(x_labels[j])
                ys.append(y_labels[i])
                sizes.append(4 + v * 18)
                hovers.append(f"IQR: {v:.2f}")
    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="markers",
        marker=dict(
            size=sizes,
            color="rgba(30,30,30,0.35)",
            line=dict(width=0),
        ),
        hovertext=hovers,
        hovertemplate="%{hovertext}<extra></extra>",
        showlegend=False,
    ))

    shapes = []
    annotations = []

    # Per-cell value labels with color that adapts to background
    for i in range(n_rows):
        for j in range(n_cols):
            v = z_med[i, j]
            if np.isnan(v):
                continue
            txt_color = "white" if (v < 0.28 or v > 0.78) else "#222"
            annotations.append(dict(
                x=x_labels[j], y=y_labels[i],
                xref="x", yref="y",
                text=f"{v:.2f}",
                showarrow=False,
                font=dict(size=10, color=txt_color, family="Arial"),
            ))
    tier_ranges = {}
    for i, sub in enumerate(subs):
        t = sub[-1]
        tier_ranges.setdefault(t, [i, i])
        tier_ranges[t][1] = i

    # (n= counts are now embedded in the y-axis tick labels)

    fig.update_layout(
        title=title,
        height=max(560, 30 * n_rows + 100),
        margin=dict(l=90, r=100, t=70, b=60),
        xaxis=dict(
            side="top",
            tickfont=dict(size=11),
            showgrid=False,
            zeroline=False,
            ticks="",
        ),
        yaxis=dict(
            autorange="reversed",
            tickmode="array",
            tickvals=y_labels,
            ticktext=y_ticktext,
            tickfont=dict(size=11),
            showgrid=False,
            zeroline=False,
            ticks="",
            automargin=False,
        ),
        shapes=shapes,
        annotations=annotations,
        plot_bgcolor="white",
    )
    return apply_plotly_style(fig)


def transition_heatmap(trans: dict, subtypes: list[str], title: str = "") -> go.Figure:
    """Create a transition probability heatmap."""
    n = len(subtypes)
    matrix = np.zeros((n, n))
    for i, src in enumerate(subtypes):
        if src in trans:
            for j, tgt in enumerate(subtypes):
                matrix[i, j] = trans[src].get(tgt, 0)

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=[f"S-{s}" for s in subtypes],
        y=[f"S-{s}" for s in subtypes],
        colorscale="YlOrRd",
        hovertemplate="From %{y} -> %{x}<br>P = %{z:.4f}<extra></extra>",
        colorbar=dict(title="P(transition)"),
    ))
    fig.update_layout(
        title=title,
        xaxis_title="To subtype",
        yaxis_title="From subtype",
        yaxis=dict(autorange="reversed"),
        height=600,
        width=700,
    )
    return apply_plotly_style(fig)


def cindex_bar_chart(cindex: dict, title: str = "") -> go.Figure:
    """Bar chart comparing C-indices across models."""
    models = list(cindex.keys())
    vals = [cindex[m]["cindex"] for m in models]
    lo = [cindex[m]["ci_lo"] for m in models]
    hi = [cindex[m]["ci_hi"] for m in models]
    ns = [cindex[m]["n"] for m in models]
    colors = ["#D4AF37", "#3498DB", "#E74C3C"][:len(models)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=models,
        y=vals,
        error_y=dict(
            type="data",
            symmetric=False,
            array=[h - v for h, v in zip(hi, vals)],
            arrayminus=[v - l for v, l in zip(vals, lo)],
        ),
        marker_color=colors,
        text=[f"{v:.3f}" for v in vals],
        textposition="outside",
        hovertemplate="%{x}<br>C-index: %{y:.3f}<br>95%CI: [%{customdata[0]:.3f}, %{customdata[1]:.3f}]<br>n=%{customdata[2]}<extra></extra>",
        customdata=list(zip(lo, hi, ns)),
    ))
    fig.update_layout(
        title=title,
        yaxis_title="Concordance Index",
        yaxis=dict(range=[0.5, max(hi) + 0.05] if hi else [0.5, 1]),
        height=400,
        showlegend=False,
    )
    return apply_plotly_style(fig)


def sojourn_bar_chart(sojourn: dict, subtypes: list[str], title: str = "") -> go.Figure:
    """Bar chart of sojourn times along a pathway."""
    subs = [s for s in subtypes if s in sojourn]
    medians = [sojourn[s].get("km_median") or 0 for s in subs]
    n_spells = [sojourn[s]["n_spells"] for s in subs]
    colors = [subtype_color(s) for s in subs]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"S-{s}" for s in subs],
        y=medians,
        marker_color=colors,
        text=[f"{v:.1f}y" if v else "N/A" for v in medians],
        textposition="outside",
        hovertemplate="%{x}<br>KM Median: %{y:.2f} years<br>n_spells=%{customdata}<extra></extra>",
        customdata=n_spells,
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Subtype",
        yaxis_title="KM Median Sojourn (years)",
        height=400,
        showlegend=False,
    )
    return apply_plotly_style(fig)


def _compute_node_positions(all_subtypes: list[str]) -> dict[str, dict]:
    """Compute (x, y) positions for all subtypes using the cascade layout algorithm.

    Matches cascade_3path.py: tiers stacked vertically, nodes centered
    horizontally within each tier.
    """
    from collections import defaultdict
    Y_SPACING = 13.0
    TIER_X_SPACING = {"A": 10.0, "B": 10.0, "C": 10.0, "D": 10.5, "E": 10.5}
    TIER_Y = {L: (4 - i) * Y_SPACING for i, L in enumerate("EDCBA")}

    by_tier = defaultdict(list)
    for s in all_subtypes:
        by_tier[s[-1]].append(s)
    for t in by_tier:
        by_tier[t].sort(key=lambda s: int(s[:-1]) if s[:-1].isdigit() else 0)

    positions = {}
    for tier, subs in by_tier.items():
        k = len(subs)
        xsp = TIER_X_SPACING.get(tier, 10.0)
        for j, sub in enumerate(subs):
            positions[sub] = {
                "x": (j - (k - 1) / 2.0) * xsp,
                "y": TIER_Y.get(tier, 0),
            }
    return positions


def cascade_network_chart(
    info: dict,
    transitions: dict | None,
    profiles: dict | None,
    highlight_pathway: str = "all",
    highlight_nodes: set | None = None,
) -> go.Figure:
    """Interactive cascade network with ALL subtypes and pathway highlighting.

    Parameters
    ----------
    info : pathway_info.json data
    transitions : transition_matrix.json {src: {tgt: prob}}
    profiles : domain_profiles.json for hover info
    highlight_pathway : "all" | "steepest" | "predominant" | "fastest" | "none"
    highlight_nodes : optional set of subtypes to highlight with their edges
    """
    pathways = info.get("pathways", {})
    tier_colors = info.get("cascade_tier_colors", info.get("tier_colors", {}))
    tier_bands = info.get("cascade_tier_bands", {})
    tier_names = info.get("tier_names", {})
    tier_stages = info.get("tier_stages", {})
    cascade_set = set(info.get("cascade_subtypes", []))

    # Discover ALL subtypes from transitions + profiles + pathway defs
    all_subs = set()
    if transitions:
        for src, targets in transitions.items():
            all_subs.add(src)
            all_subs.update(targets.keys())
    if profiles:
        all_subs.update(profiles.keys())
    for pdata in pathways.values():
        all_subs.update(pdata["subtypes"])
    all_subs = sorted(all_subs, key=lambda s: (s[-1], int(s[:-1]) if s[:-1].isdigit() else 0))

    # Compute positions for all subtypes
    positions = _compute_node_positions(all_subs)

    # Pathway edge sets: {(src, tgt): [pathway_names]}
    pathway_edges: dict[tuple, list[str]] = {}
    pathway_nodes: dict[str, set[str]] = {}
    for pname, pdata in pathways.items():
        subs = pdata["subtypes"]
        pathway_nodes[pname] = set(subs)
        for i in range(len(subs) - 1):
            key = (subs[i], subs[i + 1])
            pathway_edges.setdefault(key, []).append(pname)

    # All pathway node union (for "all" mode)
    all_pathway_nodes = set()
    for ns in pathway_nodes.values():
        all_pathway_nodes |= ns

    # Collect edges from transitions (no self-loops)
    edges = []
    if transitions:
        for src, targets in transitions.items():
            if src not in positions:
                continue
            for tgt, prob in targets.items():
                if tgt not in positions or src == tgt:
                    continue
                edges.append((src, tgt, prob))

    # Ensure pathway edges exist
    for (src, tgt) in pathway_edges:
        if not any(e[0] == src and e[1] == tgt for e in edges):
            edges.append((src, tgt, 0.0))

    fig = go.Figure()

    # ── Tier band rectangles ──────────────────────────────────
    TIER_Y = {"E": 52, "D": 39, "C": 26, "B": 13, "A": 0}
    band_h = 5.5
    # Compute x range from positions
    all_x = [p["x"] for p in positions.values()]
    x_lo, x_hi = min(all_x) - 6, max(all_x) + 6

    for tier in "EDCBA":
        band_color = tier_bands.get(tier, "#f5f5f5")
        ty = TIER_Y[tier]
        fig.add_shape(
            type="rect", x0=x_lo, x1=x_hi,
            y0=ty - band_h, y1=ty + band_h,
            fillcolor=band_color, opacity=0.45,
            line=dict(width=0), layer="below",
        )
        name = tier_names.get(tier, "")
        stage = tier_stages.get(tier, "")
        fig.add_annotation(
            x=x_hi - 0.5, y=ty + 2,
            text=f"<b>Tier {tier}</b> {name}",
            showarrow=False,
            font=dict(size=10, color=tier_colors.get(tier, "#666")),
            xanchor="right",
        )
        if stage:
            fig.add_annotation(
                x=x_hi - 0.5, y=ty - 2,
                text=f"<i>{stage}</i>",
                showarrow=False,
                font=dict(size=9, color=tier_colors.get(tier, "#888")),
                xanchor="right",
            )

    # ── Edge traces ───────────────────────────────────────────
    for src, tgt, prob in edges:
        edge_key = (src, tgt)
        edge_pathways = pathway_edges.get(edge_key, [])
        is_pathway_edge = len(edge_pathways) > 0

        # Pick primary pathway for color/dash
        primary_pw = edge_pathways[0] if edge_pathways else None

        # Visibility logic
        if highlight_nodes:
            if src not in highlight_nodes and tgt not in highlight_nodes:
                opacity, width = 0.04, 0.4
            else:
                opacity = 1.0
                width = 4.0 if is_pathway_edge else 2.5
        elif highlight_pathway == "none":
            opacity = 0.25 if is_pathway_edge else 0.15
            width = 1.5 if is_pathway_edge else 0.8
        elif highlight_pathway == "all":
            if is_pathway_edge:
                opacity, width = 1.0, 3.5
            else:
                opacity, width = 0.12, 0.7
        else:
            # Single pathway
            if primary_pw == highlight_pathway:
                opacity, width = 1.0, 4.0
            elif is_pathway_edge:
                opacity, width = 0.10, 0.8
            else:
                opacity, width = 0.05, 0.4

        # Edge color and dash
        if is_pathway_edge:
            color = pathways[primary_pw]["color"]
            dash = pathways[primary_pw].get("dash", "solid")
        else:
            color = "#999999"
            dash = "solid"

        x0, y0 = positions[src]["x"], positions[src]["y"]
        x1, y1 = positions[tgt]["x"], positions[tgt]["y"]

        dx, dy = x1 - x0, y1 - y0
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            shorten = 1.8 / length
            ax0 = x0 + dx * shorten
            ay0 = y0 + dy * shorten
            ax1 = x1 - dx * shorten
            ay1 = y1 - dy * shorten
        else:
            ax0, ay0, ax1, ay1 = x0, y0, x1, y1

        hover_text = f"S-{src} \u2192 S-{tgt}<br>P = {prob:.4f}" if prob > 0 else f"S-{src} \u2192 S-{tgt}"

        fig.add_trace(go.Scatter(
            x=[ax0, ax1, None], y=[ay0, ay1, None],
            mode="lines",
            line=dict(color=color, width=width, dash=dash),
            opacity=opacity,
            hoverinfo="text", hovertext=hover_text,
            showlegend=False,
        ))

        if opacity >= 0.12 and length > 0:
            fig.add_annotation(
                x=ax1, y=ay1, ax=ax0, ay=ay0,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=1.0,
                arrowwidth=max(0.8, width * 0.5),
                arrowcolor=_rgba(color, opacity),
                text="",
            )

    # ── Node traces ───────────────────────────────────────────
    # Determine which nodes belong to highlighted pathway(s)
    if highlight_pathway == "all":
        highlighted_nodes = all_pathway_nodes
    elif highlight_pathway in pathway_nodes:
        highlighted_nodes = pathway_nodes[highlight_pathway]
    else:
        highlighted_nodes = set()

    node_x, node_y, node_text, node_hover = [], [], [], []
    node_colors, node_line_colors, node_line_widths, node_sizes = [], [], [], []

    for sub in all_subs:
        if sub not in positions:
            continue
        pos = positions[sub]
        tier = sub[-1]
        in_cascade = sub in cascade_set
        in_highlight = sub in highlighted_nodes

        node_x.append(pos["x"])
        node_y.append(pos["y"])
        node_text.append(f"S-{sub}")

        # Hover
        hover_parts = [f"<b>S-{sub}</b> (Tier {tier})"]
        if in_cascade:
            hover_parts.append("\u2605 Cascade subtype")
        if profiles and sub in profiles:
            n = profiles[sub].get("n", "?")
            hover_parts.append(f"n = {n}")
            domains = profiles[sub].get("domains", {})
            for d in DOMAINS:
                if d in domains:
                    med = domains[d].get("median", 0)
                    hover_parts.append(f"{DOMAIN_LABELS.get(d, d)}: {med:.2f}")
        node_hover.append("<br>".join(hover_parts))

        tc = tier_colors.get(tier, "#888")

        if highlight_nodes:
            if sub in highlight_nodes:
                node_colors.append(tc)
                node_sizes.append(24)
                node_line_colors.append("#333")
                node_line_widths.append(2.5)
            else:
                node_colors.append(tc)
                node_sizes.append(11)
                node_line_colors.append("white")
                node_line_widths.append(1)
        elif highlight_pathway == "none":
            node_colors.append(tc)
            node_sizes.append(16 if in_cascade else 12)
            node_line_colors.append("white")
            node_line_widths.append(1.5)
        elif in_highlight:
            node_colors.append(tc)
            node_sizes.append(22)
            node_line_colors.append("#333")
            node_line_widths.append(2.5)
        elif in_cascade:
            node_colors.append(tc)
            node_sizes.append(15)
            node_line_colors.append("white")
            node_line_widths.append(1.5)
        else:
            node_colors.append(tc)
            node_sizes.append(11)
            node_line_colors.append("white")
            node_line_widths.append(1)

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(
            size=node_sizes, color=node_colors,
            line=dict(width=node_line_widths, color=node_line_colors),
        ),
        text=node_text,
        textposition="top center",
        textfont=dict(size=10, color="#1a1a1a"),
        hovertext=node_hover, hoverinfo="text",
        showlegend=False,
    ))

    # ── Pathway legend traces ─────────────────────────────────
    for pname, pdata in pathways.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="lines",
            line=dict(color=pdata["color"], width=3, dash=pdata.get("dash", "solid")),
            name=pdata["label"], showlegend=True,
        ))

    # ── Layout ────────────────────────────────────────────────
    fig.update_layout(
        xaxis=dict(visible=False, range=[x_lo - 2, x_hi + 2],
                    scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False, range=[-8, 60]),
        height=720,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.02,
                    font=dict(size=10)),
        dragmode="pan",
        hovermode="closest",
    )
    return fig


# ── Helpers ──────────────────────────────────────────────────────

def _km_color(group_name: str, curve_data: dict) -> str:
    """Determine color for a KM curve group."""
    if curve_data.get("type") == "petersen":
        return PETERSEN_PALETTE.get(group_name, "#666")
    clean = group_name.replace("S-", "")
    return subtype_color(clean)


def _rgba(hex_color: str, alpha: float) -> str:
    """Convert hex to rgba string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
