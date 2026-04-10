"""
Animation 4: Survival Curve Race
KM curves for cascade subtypes draw simultaneously, showing which
pathway leads to fastest dementia conversion.
"""
from manim import *
import numpy as np
import json
from pathlib import Path

PATHWAY_COLORS = {
    "steepest": "#C62828",
    "predominant": "#1565C0",
    "fastest": "#2E7D32",
}
PATHWAY_LABELS = {
    "steepest": "Steepest Decline",
    "predominant": "Predominant Pathway",
    "fastest": "Fastest Decline",
}
# Representative subtype per pathway (with survival data available)
PATHWAY_REPS = {
    "steepest": ["S-0C", "S-3B", "S-0A"],
    "predominant": ["S-2C", "S-4B", "S-0A"],
    "fastest": ["S-2C", "S-0B", "S-0A"],
}

# Fallback synthetic KM data if JSON not available
FALLBACK_DATA = {
    "steepest": {
        "time": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "survival": [1.0, 0.82, 0.65, 0.52, 0.41, 0.33, 0.27, 0.22, 0.18, 0.15, 0.12],
    },
    "predominant": {
        "time": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "survival": [1.0, 0.88, 0.76, 0.66, 0.57, 0.50, 0.44, 0.39, 0.35, 0.31, 0.28],
    },
    "fastest": {
        "time": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "survival": [1.0, 0.75, 0.55, 0.40, 0.30, 0.22, 0.17, 0.13, 0.10, 0.08, 0.06],
    },
}


def load_pathway_survival():
    """Load aggregated survival curves per pathway from representative subtypes."""
    data_path = Path(__file__).parent.parent / "data" / "survival_curves.json"
    if not data_path.exists():
        return FALLBACK_DATA

    with open(data_path) as f:
        curves = json.load(f)

    result = {}
    for pw_name, reps in PATHWAY_REPS.items():
        # Average survival across representative subtypes
        all_times = None
        all_survs = []
        for sub in reps:
            if sub in curves:
                t = np.array(curves[sub]["time"])
                s = np.array(curves[sub]["survival"])
                if all_times is None:
                    all_times = t
                # Interpolate to common time grid
                s_interp = np.interp(all_times, t, s)
                all_survs.append(s_interp)

        if all_survs and all_times is not None:
            mean_surv = np.mean(all_survs, axis=0)
            result[pw_name] = {
                "time": all_times.tolist(),
                "survival": mean_surv.tolist(),
            }
        else:
            result[pw_name] = FALLBACK_DATA[pw_name]

    return result


class SurvivalRace(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"

        # Title
        title = Text(
            "Survival Race: Time to Dementia Conversion",
            font_size=30, color="#1B5E4E", font="Arial", weight=BOLD,
        ).to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=0.8)

        # Load data
        pw_data = load_pathway_survival()

        # ── Axes ──────────────────────────────────────────────
        ax = Axes(
            x_range=[0, 10, 2],
            y_range=[0, 1.05, 0.25],
            x_length=9,
            y_length=4.5,
            axis_config={
                "color": "#333333",
                "stroke_width": 1.5,
                "include_tip": False,
                "font_size": 24,
            },
            tips=False,
        ).shift(DOWN * 0.3)

        x_label = Text("Years", font_size=18, color="#333333", font="Arial").next_to(ax, DOWN, buff=0.3)
        y_label = Text(
            "Dementia-Free Survival", font_size=18, color="#333333", font="Arial",
        ).rotate(PI / 2).next_to(ax, LEFT, buff=0.4)

        # Grid lines
        grid = VGroup()
        for y_val in [0.25, 0.5, 0.75, 1.0]:
            line = DashedLine(
                ax.c2p(0, y_val), ax.c2p(10, y_val),
                dash_length=0.05, stroke_color="#e0e0e0", stroke_width=0.8,
            )
            grid.add(line)

        self.play(Create(ax), FadeIn(x_label), FadeIn(y_label), FadeIn(grid), run_time=1)

        # Y-axis tick labels
        for y_val in [0, 0.25, 0.5, 0.75, 1.0]:
            tick = Text(
                f"{y_val:.0%}" if y_val in [0, 1.0] else f"{y_val:.0%}",
                font_size=12, color="#666666", font="Arial",
            ).next_to(ax.c2p(0, y_val), LEFT, buff=0.15)
            self.add(tick)

        # ── Draw curves simultaneously ────────────────────────
        curves = {}
        trackers = {}
        dots = {}

        for pw_name, pw_d in pw_data.items():
            t_arr = np.array(pw_d["time"])
            s_arr = np.array(pw_d["survival"])
            color = PATHWAY_COLORS[pw_name]

            # Create value tracker for animation progress
            tracker = ValueTracker(0)
            trackers[pw_name] = tracker

            # Build the full curve graph
            points = [ax.c2p(t, s) for t, s in zip(t_arr, s_arr)]

            curve = VMobject(stroke_color=color, stroke_width=3.5)
            curve.set_points_smoothly(points)
            curves[pw_name] = curve

            # Moving dot at curve tip
            dot = Dot(color=color, radius=0.08).move_to(points[0])
            dots[pw_name] = dot

        # Animate all three drawing simultaneously
        draw_anims = []
        for pw_name in pw_data:
            draw_anims.append(Create(curves[pw_name], run_time=5, rate_func=linear))
            # Move dot along curve
            draw_anims.append(
                MoveAlongPath(dots[pw_name], curves[pw_name], run_time=5, rate_func=linear)
            )

        # Add dots
        for dot in dots.values():
            self.add(dot)

        self.play(*draw_anims)
        self.wait(0.5)

        # ── Labels at curve endpoints ─────────────────────────
        legend = VGroup()
        for i, (pw_name, pw_d) in enumerate(pw_data.items()):
            t_arr = pw_d["time"]
            s_arr = pw_d["survival"]
            color = PATHWAY_COLORS[pw_name]
            label = PATHWAY_LABELS[pw_name]

            endpoint = ax.c2p(t_arr[-1], s_arr[-1])
            txt = Text(
                f"{label}\n({s_arr[-1]:.0%})",
                font_size=13, color=color, font="Arial", weight=BOLD,
            ).next_to(endpoint, RIGHT, buff=0.15)
            legend.add(txt)

        self.play(FadeIn(legend), run_time=0.6)
        self.wait(1)

        # ── Highlight fastest decliner ────────────────────────
        # Find which pathway has lowest final survival
        final_survs = {
            pw: pw_data[pw]["survival"][-1] for pw in pw_data
        }
        worst = min(final_survs, key=final_survs.get)

        highlight = Text(
            f"{PATHWAY_LABELS[worst]}: steepest drop to {final_survs[worst]:.0%}",
            font_size=20, color=PATHWAY_COLORS[worst], font="Arial", weight=BOLD,
        ).to_edge(DOWN, buff=0.3)
        self.play(Write(highlight), run_time=0.6)
        self.wait(2)
        self.play(FadeOut(VGroup(*self.mobjects)), run_time=1)
