"""Shared sidebar and global CSS rendered on every page."""

import streamlit as st

_CSS = """
<style>
/* Sidebar: dark teal matching poster header */
[data-testid="stSidebar"] {
    background-color: #1B5E4E !important;
}
/* Sidebar text: white for labels, headings, markdown */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] [data-testid="stCaption"] {
    color: #FFFFFF !important;
}
/* Sidebar selectbox label: gold accent */
[data-testid="stSidebar"] .stSelectbox label {
    color: #D4AF37 !important;
    font-weight: 600;
}
/* Sidebar navigation links: white text */
[data-testid="stSidebar"] a,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a span,
[data-testid="stSidebar"] .st-emotion-cache-1rtdyuf,
[data-testid="stSidebar"] nav a,
[data-testid="stSidebar"] [data-testid="stPageLink"] p,
[data-testid="stSidebar"] li span {
    color: #FFFFFF !important;
}
/* Active page highlight */
[data-testid="stSidebar"] [aria-selected="true"],
[data-testid="stSidebar"] [data-active="true"] {
    background-color: rgba(212, 175, 55, 0.3) !important;
}
/* Sidebar input elements: dark text on white background */
[data-testid="stSidebar"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] [role="listbox"],
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div[role="button"] {
    color: #1A1A1A !important;
    background-color: #FFFFFF !important;
}
/* Dropdown menu items */
[data-testid="stSidebar"] [role="option"] span,
[data-testid="stSidebar"] [data-baseweb="menu"] li {
    color: #1A1A1A !important;
}
/* Sidebar select: keep white background, no gold border */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] svg,
[data-testid="stSidebar"] [data-baseweb="select"] path {
    color: #1A1A1A !important;
    fill: #1A1A1A !important;
}
/* Main content selectboxes & multiselects: teal + gold border */
[data-testid="stMain"] [data-baseweb="select"] > div {
    background-color: #1B5E4E !important;
    border-color: #D4AF37 !important;
}
[data-testid="stMain"] [data-baseweb="select"] > div > div,
[data-testid="stMain"] [data-baseweb="select"] span,
[data-testid="stMain"] [data-baseweb="select"] input,
[data-testid="stMain"] [data-baseweb="select"] input::placeholder,
[data-testid="stMain"] [data-baseweb="select"] svg,
[data-testid="stMain"] [data-baseweb="select"] path {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
/* Multiselect tags: gold background, dark text */
[data-testid="stMain"] [data-baseweb="tag"] {
    background-color: #D4AF37 !important;
}
[data-testid="stMain"] [data-baseweb="tag"] span,
[data-testid="stMain"] [data-baseweb="tag"] svg,
[data-testid="stMain"] [data-baseweb="tag"] path {
    color: #1A1A1A !important;
    fill: #1A1A1A !important;
    -webkit-text-fill-color: #1A1A1A !important;
}
/* Dropdown lists: dark text on white */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"],
[data-baseweb="popover"] li,
[data-baseweb="menu"] li {
    color: #1A1A1A !important;
    background-color: #FFFFFF !important;
    -webkit-text-fill-color: #1A1A1A !important;
}
[data-baseweb="popover"] [role="option"][aria-selected="true"],
[data-baseweb="popover"] li:hover {
    background-color: #E8E8E8 !important;
}
/* Top header bar accent */
[data-testid="stHeader"] {
    background-color: #1B5E4E;
}
/* Primary buttons: Chula gold */
.stButton > button[kind="primary"] {
    background-color: #D4AF37 !important;
    color: #1A1A1A !important;
    border: none;
    font-weight: 600;
}
.stButton > button[kind="primary"]:hover {
    background-color: #B8961F !important;
    color: #FFFFFF !important;
}
.stButton > button[kind="secondary"] {
    border: 1px solid #D4AF37;
    color: #1B5E4E;
}
.stButton > button[kind="secondary"]:hover {
    background-color: #f5f0e0;
}
/* Metrics */
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #1B5E4E;
}
/* Section headers */
h1, h2, h3 {
    color: #1B5E4E;
}
/* Divider: gold accent */
hr {
    border-color: #D4AF37 !important;
}
/* Expander headers */
details summary {
    color: #1B5E4E !important;
    font-weight: 600;
}
</style>
"""


def render_sidebar():
    """Inject global CSS and render the persistent sidebar. Call from every page."""
    st.markdown(_CSS, unsafe_allow_html=True)

    with st.sidebar:
        from pathlib import Path
        logo_path = Path(__file__).parent.parent / "data" / "figures" / "logo.png"
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        st.markdown("## MoCA Subtyping Explorer")
        st.markdown(
            "Data-driven MoCA cognitive subtypes reveal hidden heterogeneity "
            "in MCI and dementia, predicting dementia conversion and mapping to distinct "
            "neuroimaging signatures."
        )
        st.divider()

        # Tier filter
        tier_options = [
            "All",
            "E \u2014 MoCA 25\u201327 (Normal/ Questionable MCI)",
            "D \u2014 MoCA 23\u201324 (Likely MCI)",
            "C \u2014 MoCA 18\u201322 (Probable MCI)",
            "B \u2014 MoCA 14\u201317 (Moderate\u2013to-Severe)",
            "A \u2014 MoCA 0\u201313 (Severe Impairment)",
        ]
        selected_tier = st.selectbox("Filter by MoCA tier", tier_options)
        if selected_tier == "All":
            st.session_state["tier_filter"] = None
        else:
            st.session_state["tier_filter"] = selected_tier[0]

        st.divider()
        st.caption("*MoCA Uses Beyond MCI Screening*, AAN 2026")
        st.caption("Bhukdee et al. | Chulalongkorn University")
        st.markdown(
            '<p style="font-size:12px; line-height:1.6; color:#ccc; margin-top:8px;">'
            '<a href="mailto:dhup.bh@gmail.com" style="color:#D4AF37;">dhup.bh@gmail.com</a><br>'
            '<a href="https://orcid.org/0000-0003-1984-1996" style="color:#D4AF37;">ORCiD</a> · '
            '<a href="https://linkedin.com/in/dhup" style="color:#D4AF37;">LinkedIn</a><br>'
            '<a href="https://cccnlab.co/" style="color:#D4AF37;">CCCN Lab</a> · '
            '<a href="https://cmbcu.github.io/" style="color:#D4AF37;">CMB Lab</a>'
            '</p>',
            unsafe_allow_html=True,
        )
