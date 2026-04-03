"""Page 3: Subtype Characteristics — heatmap + detail cards."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.sidebar import render_sidebar
from utils.data_loader import load_demographics, show_data_missing
from utils.styling import subtype_color, apply_plotly_style, TIER_NAMES, TIER_STAGES

render_sidebar()
st.header("Subtype Clinical Characteristics")

demo = load_demographics()
tier_filter = st.session_state.get("tier_filter")

if demo is None:
    show_data_missing("Demographics")
    st.stop()

# ── Build features matrix ───────────────────────────────────────
features = ["age_mean", "pct_female", "edu_mean", "moca_mean", "cdr_0", "cdr_05", "cdr_1plus"]
feature_labels = {
    "age_mean": "Age",
    "pct_female": "% Female",
    "edu_mean": "Education (yr)",
    "moca_mean": "MoCA",
    "cdr_0": "CDR 0 (%)",
    "cdr_05": "CDR 0.5 (%)",
    "cdr_1plus": "CDR 1+ (%)",
}

subtypes = sorted(demo.keys(), key=lambda x: (x[-1], int(x[:-1]) if x[:-1].isdigit() else 0))
if tier_filter:
    subtypes = [s for s in subtypes if s[-1] == tier_filter]

if not subtypes:
    st.info("No subtypes match the current tier filter.")
    st.stop()

# Build raw matrix
raw = []
for sub in subtypes:
    row = []
    for f in features:
        val = demo[sub].get(f)
        row.append(float(val) if val is not None and val != "—" else np.nan)
    raw.append(row)

raw_arr = np.array(raw)

# Z-score per column for heatmap
with np.errstate(invalid="ignore"):
    col_means = np.nanmean(raw_arr, axis=0)
    col_stds = np.nanstd(raw_arr, axis=0)
    col_stds[col_stds == 0] = 1
    z_arr = (raw_arr - col_means) / col_stds

# ── Heatmap ─────────────────────────────────────────────────────
st.subheader("Clinical Feature Heatmap (z-scored)")

fig = go.Figure(data=go.Heatmap(
    z=z_arr,
    x=[feature_labels.get(f, f) for f in features],
    y=[f"S-{s}" for s in subtypes],
    colorscale="RdBu_r",
    zmid=0,
    text=[[f"{v:.1f}" if not np.isnan(v) else "—" for v in row] for row in raw_arr],
    texttemplate="%{text}",
    textfont=dict(size=11),
    hovertemplate="%{y}<br>%{x}: %{text}<br>z-score: %{z:.2f}<extra></extra>",
    colorbar=dict(title="z-score"),
))

fig.update_layout(
    height=max(400, len(subtypes) * 26 + 100),
    yaxis=dict(autorange="reversed"),
    margin=dict(l=80, r=20, t=40, b=60),
)
st.plotly_chart(apply_plotly_style(fig), use_container_width=True, config={"responsive": True})

# ── Detail cards ────────────────────────────────────────────────
st.subheader("Subtype Details")

selected = st.selectbox("Select subtype for details", subtypes,
                        format_func=lambda s: f"S-{s} (n={demo[s]['n']})")

if selected:
    d = demo[selected]
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("n", d["n"])
        if d.get("age_mean"):
            st.metric("Age", f"{d['age_mean']} +/- {d.get('age_std', '?')}")

    with col2:
        if d.get("pct_female") is not None:
            st.metric("% Female", f"{d['pct_female']}%")
        if d.get("edu_mean"):
            st.metric("Education", f"{d['edu_mean']} +/- {d.get('edu_std', '?')} yr")

    with col3:
        if d.get("moca_mean"):
            st.metric("MoCA", f"{d['moca_mean']} +/- {d.get('moca_std', '?')}")
        tier = d.get('tier', '?')
        st.markdown(f"**Tier**: {tier} — {TIER_NAMES.get(tier, '')} ({TIER_STAGES.get(tier, '')})")

    # Diagnosis distribution
    if d.get("dx_dist"):
        st.markdown("**Diagnosis distribution:**")
        dx_df = pd.DataFrame([
            {"Diagnosis": k, "Percentage": v} for k, v in d["dx_dist"].items()
        ]).sort_values("Percentage", ascending=False)
        st.dataframe(dx_df, use_container_width=True, hide_index=True)
