"""Page 5: Survival Analysis — KM curves, Cox forest, C-index."""

import streamlit as st
import pandas as pd

from utils.data_loader import (
    load_survival_curves, load_cox_results, load_cindex_results,
    load_pathway_info, figure_path, show_data_missing,
)
from utils.sidebar import render_sidebar
from utils.plotting import km_survival_chart, forest_plot, cindex_bar_chart

render_sidebar()
st.header("Survival Analysis: Dementia Conversion")

curves = load_survival_curves()
cox = load_cox_results()
cindex = load_cindex_results()
info = load_pathway_info()

# ── KM Survival Curves ─────────────────────────────────────────
st.subheader("Kaplan-Meier Survival Curves")

if curves is None:
    show_data_missing("Survival curves")
    # Fall back to static figure
    fig_path = figure_path("survival_km.png")
    if fig_path:
        st.image(str(fig_path), use_container_width=True,
                 caption="Kaplan-Meier dementia-free survival by subtype")
else:
    # Group selector
    view = st.radio(
        "View",
        ["Cascade subtypes", "All subtypes", "Petersen MCI", "Custom"],
        horizontal=True,
    )

    cascade_subs = info.get("cascade_subtypes", []) if info else []

    if view == "Cascade subtypes":
        selected = [k for k, v in curves.items() if v.get("cascade") or v.get("type") == "petersen"]
    elif view == "All subtypes":
        selected = [k for k, v in curves.items() if v.get("type") == "subtype"]
    elif view == "Petersen MCI":
        selected = [k for k, v in curves.items() if v.get("type") == "petersen"]
    else:
        all_groups = sorted(curves.keys())
        selected = st.multiselect(
            "Select groups to compare",
            all_groups,
            default=[k for k in all_groups if curves[k].get("cascade")],
        )

    if selected:
        fig = km_survival_chart(curves, selected,
                                title="Kaplan-Meier: Time to Dementia Conversion")
        st.plotly_chart(fig, use_container_width=True, config={"responsive": True})
    else:
        st.info("Select groups to display survival curves.")

# ── Cox Forest Plots ────────────────────────────────────────────
st.subheader("Cox Proportional Hazards — Hazard Ratios")

if cox is None:
    show_data_missing("Cox results")
    fig_path = figure_path("survival_cox.png")
    if fig_path:
        st.image(str(fig_path), use_container_width=True,
                 caption="Cox PH forest plots: Subtype model vs. Petersen MCI")
else:
    model_names = list(cox.keys())
    if len(model_names) >= 2:
        col1, col2 = st.columns(2)
        with col1:
            fig1 = forest_plot(cox, model_names[0], title=model_names[0])
            st.plotly_chart(fig1, use_container_width=True, config={"responsive": True})
        with col2:
            fig2 = forest_plot(cox, model_names[-1], title=model_names[-1])
            st.plotly_chart(fig2, use_container_width=True, config={"responsive": True})
    elif model_names:
        fig = forest_plot(cox, model_names[0], title=model_names[0])
        st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

    # Additional models
    if len(model_names) > 2:
        for mn in model_names[1:-1]:
            with st.expander(f"View {mn} model"):
                fig = forest_plot(cox, mn, title=mn)
                st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

# ── C-index Comparison ──────────────────────────────────────────
st.subheader("Model Comparison: Concordance Index")

if cindex is None:
    show_data_missing("C-index results")
else:
    fig = cindex_bar_chart(cindex, title="Concordance Index (95% CI, 200 bootstrap resamples)")
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

    # Table
    rows = []
    for model, vals in cindex.items():
        rows.append({
            "Model": model,
            "n": vals["n"],
            "C-index": f"{vals['cindex']:.3f}",
            "95% CI": f"[{vals['ci_lo']:.3f}, {vals['ci_hi']:.3f}]",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── Combined static figure ──────────────────────────────────────
with st.expander("View combined poster figure"):
    combined = figure_path("survival_combined.png")
    if combined:
        st.image(str(combined), use_container_width=True,
                 caption="Combined KM + Cox + C-index poster figure")
    else:
        st.info("Combined figure not available.")
