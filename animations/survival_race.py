"""
Animation 4: Survival Curve Race
KM curves draw with smooth scrolling X-axis and zooming Y-axis.
Uses discrete Transform steps (no updaters) to avoid rendering glitches.
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
PATHWAY_REPS = {
    "steepest": ["S-0C", "S-3B", "S-0A"],
    "predominant": ["S-2C", "S-4B", "S-0A"],
    "fastest": ["S-2C", "S-0B", "S-0A"],
}

FALLBACK_DATA = {
    "steepest": {
        "time": list(range(11)),
        "survival": [1.0, 0.82, 0.65, 0.52, 0.41, 0.33, 0.27, 0.22, 0.18, 0.15, 0.12],
    },
    "predominant": {
        "time": list(range(11)),
        "survival": [1.0, 0.88, 0.76, 0.66, 0.57, 0.50, 0.44, 0.39, 0.35, 0.31, 0.28],
    },
    "fastest": {
        "time": list(range(11)),
        "survival": [1.0, 0.75, 0.55, 0.40, 0.30, 0.22, 0.17, 0.13, 0.10, 0.08, 0.06],
    },
}


def load_pathway_survival():
    data_path = Path(__file__).parent.parent / "data" / "survival_curves.json"
    if not data_path.exists():
        return FALLBACK_DATA
    with open(data_path) as f:
        curves = json.load(f)
    result = {}
    for pw_name, reps in PATHWAY_REPS.items():
        all_times = None
        all_survs = []
        for sub in reps:
            if sub in curves:
                t = np.array(curves[sub]["time"])
                s = np.array(curves[sub]["survival"])
                if all_times is None:
                    all_times = t
                all_survs.append(np.interp(all_times, t, s))
        if all_survs and all_times is not None:
            result[pw_name] = {
                "time": all_times.tolist(),
                "survival": np.mean(all_survs, axis=0).tolist(),
            }
        else:
            result[pw_name] = FALLBACK_DATA[pw_name]
    return result


class SurvivalRace(Scene):
    def construct(self):
        self.camera.background_color = "#FFFFFF"

        title = Text(
            "Survival Race: Time to Dementia Conversion",
            font_size=28, color="#1B5E4E", font="Arial", weight=BOLD,
        ).to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=0.8)

        pw_data = load_pathway_survival()

        # Dense interpolation
        dense = {}
        max_time = 0
        for pw_name, pw_d in pw_data.items():
            t = np.array(pw_d["time"])
            s = np.array(pw_d["survival"])
            t_dense = np.linspace(t[0], t[-1], 500)
            s_dense = np.interp(t_dense, t, s)
            dense[pw_name] = (t_dense, s_dense)
            max_time = max(max_time, t[-1])

        # ── Plot geometry ─────────────────────────────────────
        PW = 9.0
        PH = 4.5
        CX, CY = 0.0, -0.3
        xl = CX - PW / 2
        xr = CX + PW / 2
        yb = CY - PH / 2
        yt = CY + PH / 2
        X_WIN = 4.0

        def compute_view(t_now):
            """Compute x_offset and y_range for a given time."""
            x_off = max(0, t_now - X_WIN)
            # Y range: track visible curves tightly
            s_min, s_max = 1.0, 0.0
            for pw_name in dense:
                td, sd = dense[pw_name]
                mask = (td <= t_now) & (td >= x_off - 0.3)
                if mask.any():
                    s_min = min(s_min, sd[mask].min())
                    s_max = max(s_max, sd[mask].max())
            if s_max <= s_min:
                return x_off, 0.0, 1.05
            spread = s_max - s_min
            if t_now < 2.0 or spread < 0.08:
                return x_off, 0.0, 1.05
            pad = max(0.05, spread * 0.25)
            y_lo = max(0, s_min - pad)
            y_hi = min(1.05, s_max + pad)
            if (y_hi - y_lo) < 0.15:
                mid = (y_hi + y_lo) / 2
                y_lo, y_hi = mid - 0.075, mid + 0.075
            return x_off, y_lo, y_hi

        def t2x(t_val, x_off):
            return xl + (t_val - x_off) / X_WIN * PW

        def s2y(s_val, y_lo, y_hi):
            frac = (s_val - y_lo) / (y_hi - y_lo) if y_hi > y_lo else 0.5
            return yb + frac * PH

        # ── Build a frame snapshot (all VMobjects for one time) ──
        def build_curves(t_now, x_off, y_lo, y_hi):
            """Return dict of pw_name → (VMobject curve, endpoint)."""
            out = {}
            for pw_name in dense:
                td, sd = dense[pw_name]
                mask = td <= t_now
                tv, sv = td[mask], sd[mask]
                vis = tv >= (x_off - 0.3)
                tv, sv = tv[vis], sv[vis]
                if len(tv) < 2:
                    out[pw_name] = (None, None)
                    continue
                pts = [np.array([t2x(t, x_off), s2y(s, y_lo, y_hi), 0])
                       for t, s in zip(tv, sv)]
                c = VMobject(stroke_color=PATHWAY_COLORS[pw_name], stroke_width=3.5)
                c.set_points_smoothly(pts)
                out[pw_name] = (c, pts[-1])
            return out

        def build_x_axis(x_off, y_lo, y_hi):
            grp = VGroup()
            grp.add(Line([xl, yb, 0], [xr, yb, 0], stroke_color="#333333", stroke_width=2))
            first_yr = max(0, int(np.floor(x_off)))
            last_yr = int(np.ceil(x_off + X_WIN)) + 1
            for yr in range(first_yr, last_yr + 1):
                xp = t2x(yr, x_off)
                if xl - 0.05 <= xp <= xr + 0.05:
                    grp.add(Line([xp, yb - 0.08, 0], [xp, yb + 0.05, 0],
                                 stroke_color="#333333", stroke_width=1.5))
                    # Tick labels as Dot placeholders (avoid Text in transforms)
            return grp

        def build_x_labels(x_off):
            grp = Group()
            first_yr = max(0, int(np.floor(x_off)))
            last_yr = int(np.ceil(x_off + X_WIN)) + 1
            for yr in range(first_yr, last_yr + 1):
                xp = t2x(yr, x_off)
                if xl - 0.05 <= xp <= xr + 0.05:
                    lbl = Text(f"{yr}", font_size=11, color="#666666", font="Arial")
                    lbl.move_to([xp, yb - 0.25, 0])
                    grp.add(lbl)
            return grp

        def build_y_axis(y_lo, y_hi):
            grp = VGroup()
            grp.add(Line([xl, yb, 0], [xl, yt, 0], stroke_color="#333333", stroke_width=2))
            span = y_hi - y_lo
            step = 0.25 if span > 0.5 else (0.10 if span > 0.25 else 0.05)
            tick_val = np.ceil(y_lo / step) * step
            while tick_val <= y_hi + 0.001:
                yp = s2y(tick_val, y_lo, y_hi)
                if yb - 0.01 <= yp <= yt + 0.01:
                    grp.add(Line([xl - 0.08, yp, 0], [xl + 0.05, yp, 0],
                                 stroke_color="#333333", stroke_width=1.5))
                    grp.add(DashedLine([xl, yp, 0], [xr, yp, 0],
                                       dash_length=0.04, stroke_color="#e8e8e8",
                                       stroke_width=0.6))
                tick_val += step
            return grp

        def build_y_labels(y_lo, y_hi):
            grp = Group()
            span = y_hi - y_lo
            step = 0.25 if span > 0.5 else (0.10 if span > 0.25 else 0.05)
            tick_val = np.ceil(y_lo / step) * step
            while tick_val <= y_hi + 0.001:
                yp = s2y(tick_val, y_lo, y_hi)
                if yb - 0.01 <= yp <= yt + 0.01:
                    lbl = Text(f"{tick_val:.0%}", font_size=10, color="#666666", font="Arial")
                    lbl.move_to([xl - 0.35, yp, 0])
                    grp.add(lbl)
                tick_val += step
            return grp

        # ── Initial frame ─────────────────────────────────────
        x_off0, y_lo0, y_hi0 = compute_view(0)
        x_axis = build_x_axis(x_off0, y_lo0, y_hi0)
        x_labels = build_x_labels(x_off0)
        y_axis = build_y_axis(y_lo0, y_hi0)
        y_labels = build_y_labels(y_lo0, y_hi0)

        ax_label_x = Text("Years", font_size=14, color="#333333", font="Arial"
                          ).move_to([CX, yb - 0.5, 0])
        ax_label_y = Text("Dementia-Free", font_size=14, color="#333333", font="Arial"
                          ).rotate(PI / 2).move_to([xl - 0.7, CY, 0])

        self.play(
            Create(x_axis), Create(y_axis),
            FadeIn(x_labels), FadeIn(y_labels),
            FadeIn(ax_label_x), FadeIn(ax_label_y),
            run_time=0.8,
        )

        # Legend
        legend = Group()
        for i, (pw_name, color) in enumerate(PATHWAY_COLORS.items()):
            dot = Dot(color=color, radius=0.06)
            txt = Text(PATHWAY_LABELS[pw_name], font_size=12, color=color,
                       font="Arial", weight=BOLD).next_to(dot, RIGHT, buff=0.08)
            row = Group(dot, txt).move_to([CX + 1.5, yt - 0.1 - i * 0.28, 0])
            legend.add(row)
        self.play(FadeIn(legend), run_time=0.4)

        # Year counter
        year_text = Text("Year 0.0", font_size=22, color="#333333",
                         font="Arial", weight=BOLD).move_to([xr - 1.0, yt + 0.3, 0])
        self.add(year_text)

        # Curve + dot placeholders
        curve_mobs = {}
        dot_mobs = {}
        for pw_name in dense:
            color = PATHWAY_COLORS[pw_name]
            c = VMobject(stroke_color=color, stroke_width=3.5)
            d = Dot(color=color, radius=0.08).move_to([t2x(0, 0), s2y(1.0, 0, 1.05), 0])
            curve_mobs[pw_name] = c
            dot_mobs[pw_name] = d
            self.add(c, d)

        # ── Animate in steps ──────────────────────────────────
        N_STEPS = 100
        TOTAL_TIME = 12.0  # seconds of animation
        dt = TOTAL_TIME / N_STEPS

        for step in range(1, N_STEPS + 1):
            frac = step / N_STEPS
            # ease-in-out: slow start, fast middle, slow end
            t_frac = smooth(frac)
            t_now = t_frac * max_time

            x_off, y_lo, y_hi = compute_view(t_now)
            curves_data = build_curves(t_now, x_off, y_lo, y_hi)

            anims = []

            # Curves + dots
            for pw_name in dense:
                new_c, end_pt = curves_data[pw_name]
                if new_c is not None:
                    anims.append(Transform(curve_mobs[pw_name], new_c))
                    anims.append(dot_mobs[pw_name].animate.move_to(end_pt))

            # X axis lines
            new_xa = build_x_axis(x_off, y_lo, y_hi)
            anims.append(Transform(x_axis, new_xa))

            # Y axis lines
            new_ya = build_y_axis(y_lo, y_hi)
            anims.append(Transform(y_axis, new_ya))

            # Text labels: replace (can't Transform Text smoothly)
            new_xl = build_x_labels(x_off)
            new_yl = build_y_labels(y_lo, y_hi)
            new_yr = Text(f"Year {t_now:.1f}", font_size=22, color="#333333",
                          font="Arial", weight=BOLD).move_to([xr - 1.0, yt + 0.3, 0])

            anims.extend([
                FadeOut(x_labels, run_time=dt * 0.3),
                FadeOut(y_labels, run_time=dt * 0.3),
                FadeOut(year_text, run_time=dt * 0.3),
            ])

            self.play(*anims, run_time=dt, rate_func=linear)

            # Swap text labels
            self.remove(x_labels, y_labels, year_text)
            x_labels = new_xl
            y_labels = new_yl
            year_text = new_yr
            self.add(x_labels, y_labels, year_text)

        self.wait(0.5)

        # ── Final survival labels ─────────────────────────────
        final_labels = Group()
        for pw_name in pw_data:
            s_final = dense[pw_name][1][-1]
            color = PATHWAY_COLORS[pw_name]
            pos = dot_mobs[pw_name].get_center()
            lbl = Text(f"{s_final:.0%}", font_size=16, color=color,
                       font="Arial", weight=BOLD).next_to(pos, RIGHT, buff=0.1)
            final_labels.add(lbl)
        self.play(FadeIn(final_labels), run_time=0.5)
        self.wait(2)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1)
