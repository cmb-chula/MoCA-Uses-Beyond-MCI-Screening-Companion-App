"""Page 6: Neuroimaging Features — DTI + Amyloid + sMRI heatmaps + RFECV."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.data_loader import (
    load_rfecv_accuracy, load_pathway_info, figure_path, show_data_missing,
)
from utils.sidebar import render_sidebar
from utils.styling import MODALITY_COLORS, apply_plotly_style

render_sidebar()
st.header("Neuroimaging Feature Analysis")

st.markdown(
    "Recursive Feature Elimination with Cross-Validation (RFECV) identifies "
    "the most discriminative brain features per subtype across three modalities: "
    "**DTI** (white matter integrity), **Amyloid PET** (amyloid deposition), "
    "and **structural MRI** (cortical/subcortical morphometry)."
)

info = load_pathway_info()
rfecv = load_rfecv_accuracy()

# ── Static heatmaps ─────────────────────────────────────────────
st.subheader("Neuroimaging Feature Heatmaps")

heatmap_files = {
    "Poster Figure": "heatmap_poster_portrait.svg",
    "RFECV Importance": "rfecv_importance_landscape.png",
}

available = {k: v for k, v in heatmap_files.items() if figure_path(v)}
if available:
    selected_fig = st.selectbox("Select heatmap view", list(available.keys()))
    fig_path = figure_path(available[selected_fig])
    if fig_path:
        if str(fig_path).endswith(".svg"):
            with open(str(fig_path)) as f:
                svg_content = f.read()
            st.markdown(
                f'<div style="width:100%; overflow-x:auto;">{svg_content}</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"{selected_fig} — DTI + Amyloid + sMRI feature heatmap per subtype")
        else:
            st.image(str(fig_path), use_container_width=True,
                     caption=f"{selected_fig} — DTI + Amyloid + sMRI feature heatmap per subtype")
else:
    st.info("Heatmap figures not available. Run export script to copy figures from pipeline output.")

# ── Interactive RFECV results ───────────────────────────────────
st.subheader("RFECV Classification Accuracy")

if rfecv is None:
    show_data_missing("RFECV accuracy")
else:
    # Analysis scope selector
    scopes = [k for k in rfecv.keys() if k not in ("classifiers", "permutation")]
    if scopes:
        scope = st.selectbox(
            "Analysis scope",
            scopes,
            format_func=lambda s: {
                "all_subtypes": "All Subtypes (27 groups)",
                "cascade": "Cascade Subtypes (11 groups)",
                "steepest": "Steepest Pathway",
                "predominant": "Predominant Pathway",
                "fastest": "Fastest Pathway",
                "all3path": "All 3 Pathways Combined",
                "multimodal": "Multimodal (DTI+AMY+sMRI)",
            }.get(s, s),
        )

        scope_data = rfecv[scope]
        subgroups = sorted(scope_data.keys())
        accs = [scope_data[sg]["accuracy_mean"] for sg in subgroups]
        stds = [scope_data[sg]["accuracy_std"] for sg in subgroups]
        n_feats = [scope_data[sg]["best_n_features"] for sg in subgroups]

        # Color by modality
        colors = []
        for sg in subgroups:
            sg_upper = sg.upper()
            if "DTI" in sg_upper:
                colors.append(MODALITY_COLORS["DTI"])
            elif "AMY" in sg_upper or "SUVR" in sg_upper:
                colors.append(MODALITY_COLORS["Amyloid"])
            elif "SMRI" in sg_upper or sg_upper.startswith("ST"):
                colors.append(MODALITY_COLORS["sMRI"])
            else:
                colors.append("#888888")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=subgroups,
            y=accs,
            error_y=dict(type="data", array=stds, visible=True),
            marker_color=colors,
            text=[f"{a:.1%}" for a in accs],
            textposition="outside",
            hovertemplate="%{x}<br>Accuracy: %{y:.3f} +/- %{customdata[0]:.3f}<br>n_features: %{customdata[1]}<extra></extra>",
            customdata=list(zip(stds, n_feats)),
        ))

        fig.update_layout(
            title=f"RFECV Balanced Accuracy — {scope.replace('_', ' ').title()}",
            xaxis_title="Feature Subgroup",
            yaxis_title="Balanced Accuracy",
            yaxis=dict(range=[0, max(accs) + 0.15] if accs else [0, 1]),
            height=450,
            xaxis=dict(tickangle=45),
        )
        st.plotly_chart(apply_plotly_style(fig), use_container_width=True,
                        config={"responsive": True})

        # Table
        rows = [{"Subgroup": sg, "Accuracy": f"{scope_data[sg]['accuracy_mean']:.3f} +/- {scope_data[sg]['accuracy_std']:.3f}",
                 "n_features": scope_data[sg]["best_n_features"]} for sg in subgroups]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── Classifier comparison ───────────────────────────────────────
st.subheader("Classifier Comparison")

clf_fig = figure_path("classifier_comparison.png")
clf_multi = figure_path("classifier_multimodal.png")

if clf_fig:
    st.image(str(clf_fig), use_container_width=True,
             caption="RF vs. XGBoost vs. LightGBM — per-subgroup balanced accuracy")
if clf_multi:
    st.image(str(clf_multi), use_container_width=True,
             caption="Multimodal classifier comparison")
if not clf_fig and not clf_multi:
    st.info("Classifier comparison figures not available.")

# ── Permutation + SHAP ──────────────────────────────────────────
st.subheader("Statistical Validation")

col1, col2 = st.columns(2)
with col1:
    perm_path = figure_path("permutation_pathways.png")
    if perm_path:
        st.image(str(perm_path), use_container_width=True,
                 caption="Permutation test p-values by pathway x modality")

with col2:
    shap_path = figure_path("shap_top_features.png")
    if shap_path:
        st.image(str(shap_path), use_container_width=True,
                 caption="SHAP top features across modalities")

# ── Additional RFECV figures ────────────────────────────────────
with st.expander("View additional RFECV heatmaps"):
    for name, fname in [
        ("All Subtypes", "rfecv_all_subtypes_heatmap.png"),
        ("Cascade Subtypes", "rfecv_cascade_heatmap.png"),
    ]:
        p = figure_path(fname)
        if p:
            st.image(str(p), use_container_width=True, caption=f"RFECV heatmap — {name}")
