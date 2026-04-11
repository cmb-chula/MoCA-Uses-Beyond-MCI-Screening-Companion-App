"""
Animation 3: Markov Transition Flow
Probability mass flows between nodes — thicker flows for higher P,
with sojourn time pauses at each node.
"""
from manim import *
import numpy as np

# ── Data ──────────────────────────────────────────────────────────
TIER_Y = {"E": 2.4, "D": 1.2, "C": 0.0, "B": -1.2, "A": -2.4}
TIER_COLORS = {
    "E": "#7E57C2", "D": "#E53935", "C": "#43A047",
    "B": "#FB8C00", "A": "#1E88E5",
}

# CASCADE_RAW subtypes only (11 nodes)
CASCADE = ["0A", "0B", "0C", "1D", "2C", "2E", "3B", "3D", "4B", "7D", "7E"]

SUBTYPES_BY_TIER = {
    "E": ["2E", "7E"],
    "D": ["1D", "3D", "7D"],
    "C": ["0C", "2C"],
    "B": ["0B", "3B", "4B"],
    "A": ["0A"],
}

X_SPACING = {"A": 2.0, "B": 1.8, "C": 2.2, "D": 1.8, "E": 2.2}

# Key transition probabilities (from transition_matrix.json, simplified)
TRANSITIONS = [
    ("2E", "3D", 0.12), ("2E", "1D", 0.15), ("2E", "2C", 0.08),
    ("7E", "7D", 0.18), ("7E", "2C", 0.05),
    ("3D", "0C", 0.14), ("3D", "2C", 0.09),
    ("1D", "2C", 0.22), ("1D", "0C", 0.06),
    ("7D", "2C", 0.16), ("7D", "4B", 0.08),
    ("0C", "3B", 0.13), ("0C", "0B", 0.07),
    ("2C", "4B", 0.15), ("2C", "0B", 0.10), ("2C", "3B", 0.06),
    ("0B", "0A", 0.25), ("3B", "0A", 0.20), ("4B", "0A", 0.18),
]

# Sojourn RMST (years)
SOJOURN = {
    "2E": 1.08, "7E": 1.76, "1D": 0.96, "3D": 1.18, "7D": 2.39,
    "0C": 1.57, "2C": 1.39, "0B": 1.01, "3B": 1.26, "4B": 1.01,
    "0A": 2.42,
}


def compute_positions():
    pos = {}
    for tier, subs in SUBTYPES_BY_TIER.items():
        k = len(subs)
        xsp = X_SPACING[tier]
        for j, sub in enumerate(subs):
            pos[sub] = np.array([
                (j - (k - 1) / 2.0) * xsp,
                TIER_Y[tier],
                0,
            ])
    return pos


class MarkovFlow(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"
        pos = compute_positions()

        title = Text(
            "Markov Transition Flow: Cascade Subtypes",
            font_size=28, color="#1B5E4E", font="Arial", weight=BOLD,
        ).to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=0.8)

        # ── Nodes ─────────────────────────────────────────────
        node_mobs = {}
        node_group = Group()
        for sub in CASCADE:
            if sub not in pos:
                continue
            p = pos[sub]
            tier = sub[-1]
            circle = Circle(
                radius=0.28, fill_color=TIER_COLORS[tier],
                fill_opacity=0.6, stroke_color=TIER_COLORS[tier],
                stroke_width=2,
            ).move_to(p)
            txt = Text(sub, font_size=12, color="#FFFFFF", font="Arial", weight=BOLD).move_to(p)
            # Sojourn label below
            soj = SOJOURN.get(sub, 0)
            soj_txt = Text(
                f"{soj:.1f}y", font_size=9, color="#666666", font="Arial",
            ).next_to(circle, DOWN, buff=0.06)
            node_mobs[sub] = circle
            node_group.add(circle, txt, soj_txt)

        self.play(FadeIn(node_group), run_time=1)
        self.wait(0.5)

        # ── Static edge skeleton ──────────────────────────────
        edge_group = Group()
        for src, tgt, prob in TRANSITIONS:
            if src not in pos or tgt not in pos:
                continue
            p0, p1 = pos[src], pos[tgt]
            width = 0.5 + prob * 12  # scale width by probability
            edge = Line(
                p0 + DOWN * 0.3, p1 + UP * 0.3,
                stroke_color="#cccccc", stroke_width=width,
                stroke_opacity=0.3,
            )
            edge_group.add(edge)
        self.play(FadeIn(edge_group), run_time=0.6)

        # ── Animate flow particles ────────────────────────────
        top_transitions = sorted(TRANSITIONS, key=lambda x: -x[2])[:8]

        for src, tgt, prob in top_transitions:
            if src not in pos or tgt not in pos:
                continue
            p0, p1 = pos[src], pos[tgt]
            tier = src[-1]
            color = TIER_COLORS[tier]

            n_particles = max(1, int(prob * 15))
            particles = Group()
            for k in range(n_particles):
                dot = Dot(
                    point=p0 + DOWN * 0.3,
                    radius=0.05 + prob * 0.12,
                    color=color, fill_opacity=0.7,
                )
                particles.add(dot)

            anims = []
            for k, dot in enumerate(particles):
                offset = np.array([
                    np.random.uniform(-0.06, 0.06),
                    np.random.uniform(-0.02, 0.02),
                    0,
                ])
                anims.append(
                    dot.animate(rate_func=smooth, run_time=0.8).move_to(
                        p1 + UP * 0.3 + offset
                    )
                )

            self.play(FadeIn(particles, shift=DOWN * 0.1), run_time=0.15)
            self.play(*anims)

            # Glow target node
            pulse = Circle(
                radius=0.38, stroke_color=color, stroke_width=3,
                fill_opacity=0,
            ).move_to(pos[tgt])
            self.play(
                Create(pulse),
                pulse.animate.scale(1.3).set_opacity(0),
                FadeOut(particles),
                run_time=0.4,
            )
            self.remove(pulse)

        self.wait(1)

        # ── Final label ───────────────────────────────────────
        all_label = Text(
            "Probability flows concentrate toward S-0A (Severe)",
            font_size=18, color="#1E88E5", font="Arial",
        ).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(all_label), run_time=0.5)

        # Highlight 0A
        glow_0a = Circle(
            radius=0.4, fill_color="#1E88E5", fill_opacity=0.8,
            stroke_color="#FFFFFF", stroke_width=3,
        ).move_to(pos["0A"])
        self.play(
            Transform(node_mobs["0A"], glow_0a),
            run_time=0.6,
        )
        self.wait(2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1)
