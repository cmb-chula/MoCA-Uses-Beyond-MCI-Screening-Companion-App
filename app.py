"""
MoCA Subtyping Interactive Explorer
===================================
Companion app for AAN 2026 poster:
"MoCA Uses Beyond MCI Screening: Data-Driven MoCA Score-Based Subtypes
for Prediction of Dementia Outcomes and Neuroimaging Feature Analysis"
"""

import streamlit as st

st.set_page_config(
    page_title="MoCA Subtyping Explorer",
    page_icon=":brain:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared sidebar + global CSS ───────────────────────────────
from utils.sidebar import render_sidebar
render_sidebar()

# ── Main page ───────────────────────────────────────────────────
st.title("MoCA Uses Beyond MCI Screening Companion App")
st.markdown(
    "**Dhup Bhukdee 1,2,3**, Arp-Arpa Kasemsantitham 1, Sira Sriswasdi 2,3, "
    "Chaipat Chunharas 1, for the Alzheimer's Disease Neuroimaging Initiative"
)
st.markdown(
    "*1. Center of Excellence in Cognitive Clinical & Computational Neuroscience | "
    "2. Center of Excellence in Computational Molecular Biology | "
    "3. Center for AI in Medicine \u2014 Chulalongkorn University, Bangkok, Thailand*"
)

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Key Findings")
    st.markdown(
        "- **27 cognitive subtypes** identified across 5 MoCA score tiers "
        "using Louvain community detection on 7-domain MoCA profiles\n"
        "- **3 distinct decline cascades** mapped through Markov multistate "
        "modeling: steepest, predominant, and fastest pathways\n"
        "- **Superior dementia prediction** vs. Petersen MCI criteria "
        "(C-index: 0.800 vs. 0.703)\n"
        "- **Neuroimaging validation**: distinct DTI, amyloid PET, and "
        "structural MRI signatures per subtype"
    )

with col2:
    st.markdown("### Methods")
    st.markdown(
        "1. **Cohort**: ADNI longitudinal (n=1,347)\n"
        "2. **Subtyping**: Pearson correlation \u00d7 5 MoCA tiers \u2192 Louvain clustering\n"
        "3. **Outcomes**: Cox PH + Kaplan\u2013Meier survival to dementia conversion\n"
        "4. **Imaging**: RFECV feature selection on DTI, amyloid PET, FreeSurfer sMRI\n"
        "5. **Cascade**: Continuous-time Markov chain modeling of subtype transitions"
    )

st.divider()
st.info("Use the **sidebar** to navigate pages and filter by MoCA tier.")
st.info("This webapp is intend to supplement the poster presented at AAN Annual Meeting 2026. It will be removed after the conference.")

