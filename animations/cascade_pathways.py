"""
Animation 1: Cascade Pathway Animation
Three decline pathways light up sequentially through the network E→A.
Nodes glow as activated, edges animate with color flow.
"""
from manim import *
import numpy as np

# ── Data ──────────────────────────────────────────────────────────
TIER_Y = {"E": 3.0, "D": 1.5, "C": 0.0, "B": -1.5, "A": -3.0}
TIER_COLORS = {
    "E": "#7E57C2", "D": "#E53935", "C": "#43A047",
    "B": "#FB8C00", "A": "#1E88E5",
}
TIER_BANDS = {
    "E": "#EDE7F6", "D": "#FFEBEE", "C": "#E8F5E9",
    "B": "#FFF3E0", "A": "#E3F2FD",
}
TIER_STAGES = {
    "E": "Normal/Questionable", "D": "Likely MCI",
    "C": "Probable MCI", "B": "Moderate-Severe", "A": "Severe",
}

# All 27 subtypes by tier
SUBTYPES = {
    "E": ["0E","1E","2E","3E","4E","5E","6E","7E"],
    "D": ["0D","1D","2D","3D","4D","5D","6D","7D"],
    "C": ["0C","1C","2C"],
    "B": ["0B","1B","2B","3B","4B"],
    "A": ["0A","1A","2A"],
}

PATHWAYS = {
    "steepest":    {"nodes": ["2E","3D","0C","3B","0A"], "color": "#C62828", "label": "Steepest Decline"},
    "predominant": {"nodes": ["7E","7D","2C","4B","0A"], "color": "#1565C0", "label": "Predominant Pathway"},
    "fastest":     {"nodes": ["2E","1D","2C","0B","0A"], "color": "#2E7D32", "label": "Fastest Decline"},
}

X_SPACING = {"A": 1.2, "B": 1.2, "C": 1.5, "D": 1.0, "E": 1.0}


def compute_positions():
    pos = {}
    for tier, subs in SUBTYPES.items():
        k = len(subs)
        xsp = X_SPACING[tier]
        for j, sub in enumerate(subs):
            pos[sub] = np.array([
                (j - (k - 1) / 2.0) * xsp,
                TIER_Y[tier],
                0,
            ])
    return pos


class CascadePathways(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        pos = compute_positions()

        # Title
        title = Text(
            "Cognitive Decline Cascade", font_size=36, color="#1B5E4E",
            font="Arial",
        ).to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=1)

        # ── Tier bands ────────────────────────────────────────
        bands = Group()
        for tier in "EDCBA":
            band = Rectangle(
                width=12, height=1.2,
                fill_color=TIER_BANDS[tier], fill_opacity=0.4,
                stroke_width=0,
            ).move_to([0, TIER_Y[tier], 0])
            label = Text(
                f"Tier {tier}", font_size=14, color=TIER_COLORS[tier],
                font="Arial", weight=BOLD,
            ).next_to(band, RIGHT, buff=0.15)
            stage = Text(
                TIER_STAGES[tier], font_size=11, color="#888888",
                font="Arial", slant=ITALIC,
            ).next_to(label, DOWN, buff=0.05, aligned_edge=LEFT)
            bands.add(band, label, stage)
        self.play(FadeIn(bands), run_time=0.8)

        # ── Nodes ─────────────────────────────────────────────
        nodes = {}
        node_group = Group()
        for sub, p in pos.items():
            tier = sub[-1]
            circle = Circle(
                radius=0.18, fill_color=TIER_COLORS[tier],
                fill_opacity=0.3, stroke_color=TIER_COLORS[tier],
                stroke_width=1.5,
            ).move_to(p)
            txt = Text(
                sub, font_size=10, color="#333333", font="Arial",
            ).move_to(p)
            nodes[sub] = {"circle": circle, "text": txt}
            node_group.add(circle, txt)
        self.play(FadeIn(node_group), run_time=1)
        self.wait(0.5)

        # ── Animate each pathway ──────────────────────────────
        for pw_name, pw_data in PATHWAYS.items():
            pw_nodes = pw_data["nodes"]
            pw_color = pw_data["color"]
            pw_label = pw_data["label"]

            # Show pathway label
            label = Text(
                pw_label, font_size=24, color=pw_color,
                font="Arial", weight=BOLD,
            ).to_edge(DOWN, buff=0.4)
            self.play(FadeIn(label), run_time=0.4)

            # Light up nodes and edges sequentially
            glows = []
            for i, sub in enumerate(pw_nodes):
                p = pos[sub]
                # Glow node
                glow = Circle(
                    radius=0.28, fill_color=pw_color,
                    fill_opacity=0.7, stroke_color=pw_color,
                    stroke_width=3,
                ).move_to(p)
                glow_txt = Text(
                    sub, font_size=12, color="#FFFFFF",
                    font="Arial", weight=BOLD,
                ).move_to(p)
                self.play(
                    Transform(nodes[sub]["circle"], glow),
                    Transform(nodes[sub]["text"], glow_txt),
                    run_time=0.3,
                )
                glows.append((sub, glow, glow_txt))

                # Draw edge to next node
                if i < len(pw_nodes) - 1:
                    next_sub = pw_nodes[i + 1]
                    p_next = pos[next_sub]
                    edge = Arrow(
                        start=p + DOWN * 0.2,
                        end=p_next + UP * 0.2,
                        color=pw_color, stroke_width=4,
                        buff=0, max_tip_length_to_length_ratio=0.15,
                    )
                    self.play(Create(edge), run_time=0.4)

            self.wait(1.0)

            # Fade out pathway highlights (reset nodes)
            fade_anims = [FadeOut(label)]
            for sub, glow, glow_txt in glows:
                tier = sub[-1]
                orig_circle = Circle(
                    radius=0.18, fill_color=TIER_COLORS[tier],
                    fill_opacity=0.3, stroke_color=TIER_COLORS[tier],
                    stroke_width=1.5,
                ).move_to(pos[sub])
                orig_txt = Text(
                    sub, font_size=10, color="#333333", font="Arial",
                ).move_to(pos[sub])
                fade_anims.extend([
                    Transform(nodes[sub]["circle"], orig_circle),
                    Transform(nodes[sub]["text"], orig_txt),
                ])
            self.play(*fade_anims, run_time=0.6)

        # ── All three together ────────────────────────────────
        all_label = Text(
            "All Three Pathways", font_size=24, color="#1B5E4E",
            font="Arial", weight=BOLD,
        ).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(all_label), run_time=0.4)

        all_edges = Group()
        for pw_name, pw_data in PATHWAYS.items():
            pw_nodes = pw_data["nodes"]
            pw_color = pw_data["color"]
            for i in range(len(pw_nodes) - 1):
                p0 = pos[pw_nodes[i]]
                p1 = pos[pw_nodes[i + 1]]
                edge = Arrow(
                    start=p0 + DOWN * 0.2, end=p1 + UP * 0.2,
                    color=pw_color, stroke_width=3.5, buff=0,
                    max_tip_length_to_length_ratio=0.12,
                )
                all_edges.add(edge)
            # Glow pathway nodes
            for sub in pw_nodes:
                glow = Circle(
                    radius=0.25, fill_color=pw_color,
                    fill_opacity=0.6, stroke_color=pw_color,
                    stroke_width=2.5,
                ).move_to(pos[sub])
                all_edges.add(glow)

        self.play(FadeIn(all_edges), run_time=2)
        self.wait(2)

        # Legend
        legend = Group()
        for i, (pw_name, pw_data) in enumerate(PATHWAYS.items()):
            dot = Dot(color=pw_data["color"], radius=0.08).shift(LEFT * 2 + DOWN * (3.5 + i * 0.3))
            txt = Text(
                pw_data["label"], font_size=14, color=pw_data["color"],
                font="Arial",
            ).next_to(dot, RIGHT, buff=0.1)
            legend.add(dot, txt)
        self.play(FadeIn(legend), run_time=0.5)
        self.wait(2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1)
