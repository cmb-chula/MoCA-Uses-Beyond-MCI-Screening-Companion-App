"""Page 4: Interactive Cognitive Decline Cascade Network & Markov Transitions."""

import streamlit as st

from utils.data_loader import (
    load_transition_matrix, load_sojourn_times, load_pathway_info,
    load_domain_profiles, figure_path, show_data_missing,
)
from utils.sidebar import render_sidebar
from utils.plotting import cascade_network_chart, transition_heatmap, sojourn_bar_chart

render_sidebar()
st.header("Cognitive Decline Cascade")

info = load_pathway_info()
profiles = load_domain_profiles()
trans = load_transition_matrix()

# ── Interactive cascade network ────────────────────────────────
st.subheader("Cascade Network")

if info:
    st.markdown(
        "All 27 cognitive subtypes across 5 severity tiers. "
        "Three optimal pathways trace distinct routes from normal-borderline "
        "(Tier E) to severe impairment (Tier A)."
    )

    # Collect all subtypes for the multiselect
    all_subs = set()
    if trans:
        for src, targets in trans.items():
            all_subs.add(src)
            all_subs.update(targets.keys())
    if profiles:
        all_subs.update(profiles.keys())
    for pdata in info.get("pathways", {}).values():
        all_subs.update(pdata["subtypes"])
    all_subs = sorted(all_subs, key=lambda s: (s[-1], int(s[:-1]) if s[:-1].isdigit() else 0))

    # Build pathway node sets for quick-select buttons
    pathways = info.get("pathways", {})
    pw_node_sets = {}
    all_pw_nodes = set()
    for pname, pdata in pathways.items():
        pw_node_sets[pname] = pdata["subtypes"]
        all_pw_nodes.update(pdata["subtypes"])

    # --- Pathway highlight buttons ---
    st.markdown("**Highlight pathway edges:**")
    pw_cols = st.columns(5)
    pw_key = "cascade_pw"
    current_pw = st.session_state.get(pw_key, "all")

    pw_options = [
        ("all", "All 3 Pathways"),
        ("steepest", "Steepest"),
        ("predominant", "Predominant"),
        ("fastest", "Fastest"),
        ("none", "No Highlight"),
    ]
    for col, (val, label) in zip(pw_cols, pw_options):
        with col:
            if st.button(label, key=f"pw_{val}", use_container_width=True,
                         type="primary" if current_pw == val else "secondary"):
                st.session_state[pw_key] = val
                current_pw = val

    # --- Node quick-select buttons (populate multiselect) ---
    st.markdown("**Highlight nodes:**")
    qcols = st.columns(5)
    node_sel_key = "cascade_nodes"

    quick_options = [
        ("all_pw", "All Pathway Nodes", sorted(all_pw_nodes)),
        ("steepest_n", "Steepest Nodes", pw_node_sets.get("steepest", [])),
        ("predominant_n", "Predominant Nodes", pw_node_sets.get("predominant", [])),
        ("fastest_n", "Fastest Nodes", pw_node_sets.get("fastest", [])),
        ("clear", "Clear Selection", []),
    ]
    for col, (bkey, label, nodes) in zip(qcols, quick_options):
        with col:
            if st.button(label, key=f"qn_{bkey}", use_container_width=True):
                st.session_state[node_sel_key] = [f"S-{n}" for n in nodes]

    # Multiselect for individual node picking
    default_nodes = st.session_state.get(node_sel_key, [])
    selected_nodes = st.multiselect(
        "Select subtypes to highlight (or use buttons above)",
        [f"S-{s}" for s in all_subs],
        default=default_nodes,
        key=node_sel_key,
    )
    highlight_nodes = {s.replace("S-", "") for s in selected_nodes} if selected_nodes else None

    # --- Network chart ---
    fig = cascade_network_chart(
        info=info,
        transitions=trans,
        profiles=profiles,
        highlight_pathway=current_pw,
        highlight_nodes=highlight_nodes,
    )
    st.plotly_chart(fig, use_container_width=True, config={
        "responsive": True,
        "scrollZoom": True,
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    })

    # --- Pathway descriptions ---
    with st.expander("Pathway definitions"):
        for pname, pdata in pathways.items():
            arrow = " \u2192 ".join([f"S-{s}" for s in pdata["subtypes"]])
            color = pdata["color"]
            st.markdown(
                f'<span style="color:{color}; font-weight:bold">{pdata["label"]}</span>'
                f'<br><code>{arrow}</code>',
                unsafe_allow_html=True,
            )
else:
    # Fallback: static image
    net_path = figure_path("cascade_network.png")
    if net_path:
        st.image(str(net_path), use_container_width=True,
                 caption="Cascade with 3 pathways: Steepest (red), Predominant (blue), Fastest (green)")
    else:
        comp_path = figure_path("cascade_composite.png")
        if comp_path:
            st.image(str(comp_path), use_container_width=True)
        else:
            st.info("Cascade network figure not available.")

# ── Transition matrix heatmap ──────────────────────────────────
st.subheader("Annual Transition Probabilities")

if trans is None:
    show_data_missing("Transition matrix")
else:
    tier_filter = st.session_state.get("tier_filter")
    all_subs_t = sorted(trans.keys(), key=lambda x: (x[-1], int(x[:-1]) if x[:-1].isdigit() else 0))

    if tier_filter:
        src_subs = [s for s in all_subs_t if s[-1] == tier_filter]
        tier_idx = "EDCBA".index(tier_filter) if tier_filter in "EDCBA" else -1
        next_tier = "EDCBA"[tier_idx + 1] if 0 <= tier_idx < 4 else None
        tgt_subs = src_subs + ([s for s in all_subs_t if s[-1] == next_tier] if next_tier else [])
        tgt_subs = sorted(set(tgt_subs), key=lambda x: (x[-1], int(x[:-1]) if x[:-1].isdigit() else 0))
    else:
        tgt_subs = all_subs_t

    fig = transition_heatmap(trans, tgt_subs,
                             title="Annual Transition Probability Matrix" +
                                   (f" (Tier {tier_filter})" if tier_filter else ""))
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

# ── Sojourn times ──────────────────────────────────────────────
st.subheader("Sojourn Times by Pathway")

sojourn = load_sojourn_times()
if sojourn is None:
    show_data_missing("Sojourn times")
else:
    soj_path = figure_path("pathway_sojourn.png")
    if soj_path:
        st.image(str(soj_path), use_container_width=True,
                 caption="KM median sojourn time comparison across pathways")

    if info:
        pathway_choice = st.selectbox(
            "Select pathway",
            list(info.get("pathways", {}).keys()),
            format_func=lambda p: info["pathways"][p]["label"],
        )
        pathway_subs = info["pathways"][pathway_choice]["subtypes"]
        fig = sojourn_bar_chart(sojourn, pathway_subs,
                                title=f"Sojourn Times \u2014 {info['pathways'][pathway_choice]['label']}")
        st.plotly_chart(fig, use_container_width=True, config={"responsive": True})

    soj_tier_path = figure_path("sojourn_km_by_tier.png")
    if soj_tier_path:
        st.image(str(soj_tier_path), use_container_width=True,
                 caption="KM sojourn curves by MoCA tier")
