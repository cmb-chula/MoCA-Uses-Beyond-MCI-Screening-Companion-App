"""Color palettes, layout constants, and Plotly theming for the Streamlit app."""

# Tier colors — match cascade_moca/config.py exactly
TIER_COLORS = {
    "A": "#1F77B4",
    "B": "#FF7F0E",
    "C": "#2CA02C",
    "D": "#D62728",
    "E": "#9467BD",
}

TIER_NAMES = {
    "A": "MoCA 0\u201313",
    "B": "MoCA 14\u201317",
    "C": "MoCA 18\u201322",
    "D": "MoCA 23\u201324",
    "E": "MoCA 25\u201327",
}

TIER_STAGES = {
    "A": "Severe Impairment",
    "B": "Moderate\u2013to-Severe Impairment",
    "C": "Probable MCI",
    "D": "Likely MCI",
    "E": "Normal/ Questionable MCI",
}

PETERSEN_PALETTE = {
    "aMCI-sd": "#008080",
    "aMCI-md": "#DA70D6",
    "naMCI-sd": "#8B4513",
    "naMCI-md": "#000000",
}

MODALITY_COLORS = {
    "DTI": "#1f77b4",
    "Amyloid": "#ff7f0e",
    "sMRI": "#2ca02c",
}

CHULA_GOLD = "#D4AF37"
CHULA_DARK = "#1E1E1E"

# Domain display
DOMAIN_LABELS = {
    "VIS": "Visuospatial",
    "NAME": "Naming",
    "ATTEN": "Attention",
    "LAN": "Language",
    "ABS": "Abstraction",
    "DELAY": "Delayed Recall",
    "ORI": "Orientation",
}

DOMAIN_MAX = {"VIS": 5, "NAME": 3, "ATTEN": 6, "LAN": 3, "ABS": 2, "DELAY": 5, "ORI": 6}
DOMAINS = ["VIS", "NAME", "ATTEN", "LAN", "ABS", "DELAY", "ORI"]


def subtype_color(subtype: str) -> str:
    """Get color for a subtype label like '0A' or '3D'.

    Uses tier color with lightness variation by subtype index.
    """
    if not subtype or len(subtype) < 2:
        return "#888888"
    tier = subtype[-1]
    idx = int(subtype[:-1]) if subtype[:-1].isdigit() else 0
    base = TIER_COLORS.get(tier, "#888888")
    # Vary lightness: idx 0 = full saturation, higher = lighter
    return _lighten(base, idx * 0.08)


def _lighten(hex_color: str, amount: float) -> str:
    """Lighten a hex color by blending toward white."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return f"#{r:02x}{g:02x}{b:02x}"


def build_subtype_colormap(subtypes: list[str]) -> dict[str, str]:
    """Build a consistent color map for a list of subtypes."""
    return {s: subtype_color(s) for s in subtypes}


# Plotly layout defaults
PLOTLY_LAYOUT = dict(
    font=dict(family="Arial, Helvetica, sans-serif", size=13, color=CHULA_DARK),
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=60, r=20, t=50, b=60),
    hoverlabel=dict(font_size=12),
)


def apply_plotly_style(fig):
    """Apply consistent styling to a Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_xaxes(showgrid=False, showline=True, linewidth=1, linecolor="#ccc")
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor="#eee",
                     showline=True, linewidth=1, linecolor="#ccc")
    return fig
