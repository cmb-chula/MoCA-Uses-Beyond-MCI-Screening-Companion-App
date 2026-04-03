"""Page 1: Study Overview & Demographics Table."""

import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from utils.data_loader import load_demographics, load_pathway_info, show_data_missing
from utils.styling import TIER_COLORS, TIER_NAMES, TIER_STAGES

render_sidebar()

# Tier background colors (light pastels matching poster bands)
TIER_BG = {
    "A": "#dbeafe",  # light blue
    "B": "#ffedd5",  # light orange
    "C": "#dcfce7",  # light green
    "D": "#fee2e2",  # light red
    "E": "#ede9fe",  # light purple
}

st.header("Study Overview")

st.markdown(
    "This study identifies **27 data-driven MoCA cognitive subtypes** across 5 severity "
    "tiers using Louvain community detection on 7-domain MoCA subscale profiles in the "
    "ADNI longitudinal cohort. Subtypes reveal hidden heterogeneity masked by total MoCA scores."
)

# ── Demographics table ──────────────────────────────────────────
st.subheader("Cohort Demographics by Subtype")

demo = load_demographics()
info = load_pathway_info()
tier_filter = st.session_state.get("tier_filter")

if demo is None:
    show_data_missing("Demographics")
    st.stop()

# Build rows
rows = []
for sub, d in sorted(demo.items(), key=lambda x: (x[0][-1], int(x[0][:-1]) if x[0][:-1].isdigit() else 0)):
    tier = d.get("tier", sub[-1])
    if tier_filter and tier != tier_filter:
        continue
    dash = "\u2014"
    pm = "\u00b1"
    age_m = d.get("age_mean")
    edu_m = d.get("edu_mean")
    moca_m = d.get("moca_mean")
    rows.append({
        "tier_letter": tier,
        "Subtype": f"S-{sub}",
        "Tier": f"{tier} {dash} {TIER_NAMES.get(tier, '')}",
        "Stage": TIER_STAGES.get(tier, ""),
        "n": d["n"],
        "Age": f"{age_m} {pm} {d.get('age_std', '')}" if age_m else dash,
        "% Female": str(d.get("pct_female", dash)),
        "Edu (yr)": f"{edu_m} {pm} {d.get('edu_std', '')}" if edu_m else dash,
        "MoCA": f"{moca_m} {pm} {d.get('moca_std', '')}" if moca_m else dash,
        "CDR 0": f"{d.get('cdr_0', dash)}%",
        "CDR 0.5": f"{d.get('cdr_05', dash)}%",
        "CDR 1+": f"{d.get('cdr_1plus', dash)}%",
    })

if rows:
    # Build colored HTML table
    cols = ["Subtype", "Tier", "Stage", "n", "Age", "% Female", "Edu (yr)", "MoCA", "CDR 0", "CDR 0.5", "CDR 1+"]
    html = '<table style="width:100%; border-collapse:collapse; font-size:14px;">'
    html += '<thead><tr style="background:#1B5E4E; color:white;">'
    for c in cols:
        html += f'<th style="padding:8px 10px; text-align:left; border-bottom:2px solid #D4AF37;">{c}</th>'
    html += '</tr></thead><tbody>'

    prev_tier = None
    for r in rows:
        tier = r["tier_letter"]
        bg = TIER_BG.get(tier, "#ffffff")
        tc = TIER_COLORS.get(tier, "#333")
        # Add tier separator
        if prev_tier and tier != prev_tier:
            html += f'<tr><td colspan="{len(cols)}" style="height:3px; background:#D4AF37; padding:0;"></td></tr>'
        prev_tier = tier

        html += f'<tr style="background:{bg};">'
        for c in cols:
            val = r[c]
            style = "padding:6px 10px; border-bottom:1px solid #e5e7eb;"
            if c == "Subtype":
                style += f" font-weight:700; color:{tc};"
            elif c == "Tier":
                style += f" color:{tc}; font-weight:600; font-size:12px;"
            elif c == "Stage":
                style += " font-style:italic; font-size:12px; color:#555;"
            html += f'<td style="{style}">{val}</td>'
        html += '</tr>'

    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)
    st.caption(f"Showing {len(rows)} subtypes" + (f" in Tier {tier_filter}" if tier_filter else ""))
else:
    st.info("No subtypes match the current tier filter.")

# ── Tier summary ────────────────────────────────────────────────
st.subheader("MoCA Tier Definitions")
tier_stages = info.get("tier_stages", {}) if info else {}
tier_html = '<table style="width:100%; border-collapse:collapse; font-size:14px;">'
tier_html += '<thead><tr style="background:#1B5E4E; color:white;">'
for c in ["Tier", "MoCA Range", "Clinical Stage"]:
    tier_html += f'<th style="padding:8px 12px; text-align:left; border-bottom:2px solid #D4AF37;">{c}</th>'
tier_html += '</tr></thead><tbody>'
for t in (info.get("tier_order", []) if info else list("EDCBA")):
    bg = TIER_BG.get(t, "#fff")
    tc = TIER_COLORS.get(t, "#333")
    stage = tier_stages.get(t, TIER_STAGES.get(t, ""))
    tier_html += f'<tr style="background:{bg};">'
    tier_html += f'<td style="padding:8px 12px; font-weight:700; color:{tc}; border-bottom:1px solid #e5e7eb;">Tier {t}</td>'
    tier_html += f'<td style="padding:8px 12px; border-bottom:1px solid #e5e7eb;">{TIER_NAMES.get(t, "")}</td>'
    tier_html += f'<td style="padding:8px 12px; font-style:italic; border-bottom:1px solid #e5e7eb;">{stage}</td>'
    tier_html += '</tr>'
tier_html += '</tbody></table>'
st.markdown(tier_html, unsafe_allow_html=True)
