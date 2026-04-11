"""
Animation 2: Radar Profile Morphing
Domain radar shapes morph as patient transitions along the Steepest pathway
E→D→C→B→A, showing cognitive profile collapse.
"""
from manim import *
import numpy as np

# ── Data: median domain values (normalized 0-1) ──────────────
DOMAINS = ["VIS", "NAME", "ATTEN", "LAN", "ABS", "DELAY", "ORI"]
DOMAIN_LABELS = [
    "Visuospatial", "Naming", "Attention",
    "Language", "Abstraction", "Delayed\nRecall", "Orientation",
]

# Steepest pathway: 2E → 3D → 0C → 3B → 0A
PATHWAY_PROFILES = {
    "S-2E": [0.90, 0.667, 0.833, 0.667, 1.00, 0.80, 1.00],
    "S-3D": [1.00, 1.000, 0.667, 0.333, 1.00, 0.60, 1.00],
    "S-0C": [0.80, 1.000, 0.833, 0.667, 0.50, 0.20, 1.00],
    "S-3B": [0.60, 1.000, 0.500, 0.667, 0.50, 0.20, 0.50],
    "S-0A": [0.20, 0.667, 0.333, 0.000, 0.00, 0.20, 0.333],
}

TIER_COLORS = {
    "E": "#7E57C2", "D": "#E53935", "C": "#43A047",
    "B": "#FB8C00", "A": "#1E88E5",
}

TIER_STAGES = {
    "E": "Normal/Questionable", "D": "Likely MCI",
    "C": "Probable MCI", "B": "Moderate-Severe", "A": "Severe",
}

PATHWAY_ORDER = ["S-2E", "S-3D", "S-0C", "S-3B", "S-0A"]


def make_radar_polygon(values, center, radius, color, opacity=0.4):
    """Create a filled radar polygon from normalized values."""
    n = len(values)
    angles = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, n, endpoint=False)
    points = []
    for v, a in zip(values, angles):
        r = max(v, 0.02) * radius
        points.append(center + np.array([r * np.cos(a), r * np.sin(a), 0]))
    points.append(points[0])
    polygon = Polygon(
        *points,
        fill_color=color, fill_opacity=opacity,
        stroke_color=color, stroke_width=2.5,
    )
    return polygon


def make_radar_axes(center, radius):
    """Create radar grid circles and axis lines."""
    group = Group()
    for frac in [0.25, 0.5, 0.75, 1.0]:
        circ = Circle(
            radius=radius * frac, stroke_color="#cccccc",
            stroke_width=0.8, stroke_opacity=0.5,
        ).move_to(center)
        group.add(circ)
    n = len(DOMAINS)
    angles = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, n, endpoint=False)
    for a in angles:
        line = Line(
            center, center + np.array([radius * np.cos(a), radius * np.sin(a), 0]),
            stroke_color="#cccccc", stroke_width=0.8, stroke_opacity=0.5,
        )
        group.add(line)
    outer = Circle(
        radius=radius, stroke_color="#666666", stroke_width=1.5,
    ).move_to(center)
    group.add(outer)
    return group


def make_radar_labels(center, radius):
    """Create domain name labels around the radar."""
    group = Group()
    n = len(DOMAIN_LABELS)
    angles = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, n, endpoint=False)
    for label, a in zip(DOMAIN_LABELS, angles):
        pos = center + np.array([
            (radius + 0.4) * np.cos(a),
            (radius + 0.3) * np.sin(a),
            0,
        ])
        txt = Text(label, font_size=12, color="#333333", font="Arial").move_to(pos)
        group.add(txt)
    return group


class RadarMorphing(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        center = DOWN * 0.2  # shift radar slightly down to make room for title
        radius = 2.0  # slightly smaller to fit labels

        # Title
        title = Text(
            "Steepest Decline: Domain Profile Collapse",
            font_size=28, color="#C62828", font="Arial", weight=BOLD,
        ).to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=0.8)

        # Radar axes and labels
        axes = make_radar_axes(center, radius)
        labels = make_radar_labels(center, radius)
        self.play(FadeIn(axes), FadeIn(labels), run_time=0.6)

        # Initial radar polygon
        first = PATHWAY_ORDER[0]
        tier = first.split("-")[1][-1]
        color = TIER_COLORS[tier]
        polygon = make_radar_polygon(
            PATHWAY_PROFILES[first], center, radius, color, opacity=0.5,
        )

        # Subtype label
        sub_label = Text(
            first, font_size=24, color=color, font="Arial", weight=BOLD,
        ).to_edge(DOWN, buff=0.6)
        stage_label = Text(
            f"Tier {tier} \u2014 {TIER_STAGES[tier]}",
            font_size=16, color="#666666", font="Arial",
        ).next_to(sub_label, DOWN, buff=0.08)

        self.play(Create(polygon), FadeIn(sub_label), FadeIn(stage_label), run_time=1)
        self.wait(1)

        # Morph through each subtype
        for i in range(1, len(PATHWAY_ORDER)):
            sub = PATHWAY_ORDER[i]
            tier = sub.split("-")[1][-1]
            color = TIER_COLORS[tier]

            new_polygon = make_radar_polygon(
                PATHWAY_PROFILES[sub], center, radius, color, opacity=0.5,
            )
            new_sub_label = Text(
                sub, font_size=24, color=color, font="Arial", weight=BOLD,
            ).to_edge(DOWN, buff=0.6)
            new_stage_label = Text(
                f"Tier {tier} \u2014 {TIER_STAGES[tier]}",
                font_size=16, color="#666666", font="Arial",
            ).next_to(new_sub_label, DOWN, buff=0.08)

            self.play(
                Transform(polygon, new_polygon),
                Transform(sub_label, new_sub_label),
                Transform(stage_label, new_stage_label),
                run_time=1.5,
                rate_func=smooth,
            )
            self.wait(0.8)

        # Final hold — severe impairment
        final_box = SurroundingRectangle(
            polygon, color="#1E88E5", buff=0.2, stroke_width=2,
        )
        final_text = Text(
            "Severe Impairment", font_size=20, color="#1E88E5",
            font="Arial", weight=BOLD,
        ).next_to(final_box, RIGHT, buff=0.2)
        self.play(Create(final_box), Write(final_text), run_time=0.8)
        self.wait(2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1)
