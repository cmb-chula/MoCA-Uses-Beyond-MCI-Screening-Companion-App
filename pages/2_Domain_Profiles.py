"""Page 2: MoCA Domain Profiles by Subtype."""

import streamlit as st

from utils.sidebar import render_sidebar
from utils.data_loader import load_domain_profiles, load_pathway_info, show_data_missing
from utils.plotting import radar_chart, grouped_bar_chart
from utils.styling import TIER_NAMES, TIER_STAGES

render_sidebar()

st.header("MoCA Domain Profiles by Subtype")

profiles = load_domain_profiles()
info = load_pathway_info()
tier_filter = st.session_state.get("tier_filter")

if profiles is None:
    show_data_missing("Domain profiles")
    st.stop()

# ── Organize subtypes by tier ───────────────────────────────────
tier_subtypes = {}
for sub, data in profiles.items():
    tier = data.get("tier", sub[-1])
    tier_subtypes.setdefault(tier, []).append(sub)
for t in tier_subtypes:
    tier_subtypes[t] = sorted(tier_subtypes[t], key=lambda x: int(x[:-1]) if x[:-1].isdigit() else 0)

# ── Tier selector ───────────────────────────────────────────────
available_tiers = sorted(tier_subtypes.keys(), reverse=True)
if tier_filter and tier_filter in available_tiers:
    default_idx = available_tiers.index(tier_filter)
else:
    default_idx = 0

selected_tier = st.selectbox(
    "Select MoCA Tier",
    available_tiers,
    index=default_idx,
    format_func=lambda t: f"Tier {t} — {TIER_NAMES.get(t, '')} ({TIER_STAGES.get(t, '')})",
)

subs_in_tier = tier_subtypes.get(selected_tier, [])

# ── Subtype multi-select ────────────────────────────────────────
selected_subs = st.multiselect(
    "Select subtypes to compare",
    subs_in_tier,
    default=subs_in_tier,
    format_func=lambda s: f"S-{s} (n={profiles[s]['n']})",
)

if not selected_subs:
    st.info("Select at least one subtype to display.")
    st.stop()

# ── Visualization toggle ────────────────────────────────────────
viz_type = st.radio("Chart type", ["Radar", "Bar"], horizontal=True)

if viz_type == "Radar":
    fig = radar_chart(profiles, selected_subs,
                      title=f"Tier {selected_tier} Domain Profiles (Median, normalized 0-1)")
else:
    fig = grouped_bar_chart(profiles, selected_subs,
                            title=f"Tier {selected_tier} Domain Profiles (Median +/- IQR)")

st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

# ── Cross-tier comparison ───────────────────────────────────────
st.subheader("Compare subtypes across tiers")
all_subs = sorted(profiles.keys(), key=lambda x: (x[-1], int(x[:-1]) if x[:-1].isdigit() else 0))
cross_subs = st.multiselect(
    "Select subtypes from any tier",
    all_subs,
    format_func=lambda s: f"S-{s} (Tier {s[-1]}, n={profiles[s]['n']})",
    key="cross_tier",
)

if cross_subs:
    if viz_type == "Radar":
        fig2 = radar_chart(profiles, cross_subs, title="Cross-Tier Domain Profile Comparison")
    else:
        fig2 = grouped_bar_chart(profiles, cross_subs, title="Cross-Tier Domain Profile Comparison")
    st.plotly_chart(fig2, use_container_width=True, config={"responsive": True})
