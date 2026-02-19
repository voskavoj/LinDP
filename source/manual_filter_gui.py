import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from source.steps import Step

PICKER = 3

class CurveClassifierApp:
    def __init__(self, root, good_curves: list[Step], bad_curves: list[Step], name):
        self.root = root
        self.name = name
        self.root.title(name)


        # Store curves with state
        self.curves = []  # {df, lines, state}
        self.hovered_curve = None

        # Figure with subplots
        self.fig = Figure(figsize=(15, 10))
        self.ax_roll = self.fig.add_subplot(311)
        self.ax_pitch = self.fig.add_subplot(312)
        self.ax_yaw = self.fig.add_subplot(313)

        self.ax_roll.set_title("Roll")
        self.ax_pitch.set_title("Pitch")
        self.ax_yaw.set_title("Yaw")

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Toolbar (zoom & pan)
        toolbar = NavigationToolbar2Tk(self.canvas, root)
        toolbar.update()

        # Load curves
        self.load_curves(good_curves, bad_curves)

        # Events
        self.canvas.mpl_connect("pick_event", self.on_pick)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

        # Keyboard shortcut
        self.root.bind("<Return>", self.on_enter)

    def on_enter(self, event=None):
        """Close the app when Enter is pressed."""
        self.root.destroy()

    def update_suptitle(self):
        good_count = sum(1 for c in self.curves if c["state"] == "good")
        bad_count = sum(1 for c in self.curves if c["state"] == "bad")

        self.fig.suptitle(f"Good: {good_count}    Bad: {bad_count}", fontsize=14)

    # ---------- Load Data ----------
    def load_curves(self, good_curves, bad_curves):
        for step in good_curves:
            lines = self.plot_curve(step, "darkgreen")
            self.curves.append({"step": step, "lines": lines, "state": "good"})

        for step in bad_curves:
            lines = self.plot_curve(step, "orange")
            self.curves.append({"step": step, "lines": lines, "state": "bad"})

        self.update_suptitle()
        self.canvas.draw()

    def plot_curve(self, step, color):
        df = step.df
        x = df["Time"]
        line_roll, = self.ax_roll.plot(x, df["Roll"], ".-", color=color, picker=PICKER, linewidth=1.5)
        line_pitch, = self.ax_pitch.plot(x, df["Pitch"], ".-", color=color, picker=PICKER, linewidth=1.5)
        line_yaw, = self.ax_yaw.plot(x, df["Yaw"], ".-", color=color, picker=PICKER, linewidth=1.5)
        return [line_roll, line_pitch, line_yaw]

    # ---------- Click Toggle ----------
    def on_pick(self, event):
        clicked_line = event.artist

        for curve in self.curves:
            if clicked_line in curve["lines"]:
                if curve["state"] == "good":
                    curve["state"] = "bad"
                    new_color = "orange"
                else:
                    curve["state"] = "good"
                    new_color = "darkgreen"

                for line in curve["lines"]:
                    line.set_color(new_color)

                self.update_suptitle()
                self.canvas.draw()
                break

    # ---------- Hover Highlight ----------
    def on_hover(self, event):
        if event.inaxes is None:
            self.clear_highlight()
            return

        found_curve = None

        for curve in self.curves:
            for line in curve["lines"]:
                contains, _ = line.contains(event)
                if contains:
                    found_curve = curve
                    break
            if found_curve:
                break

        if found_curve is not self.hovered_curve:
            self.clear_highlight()
            self.hovered_curve = found_curve
            self.apply_highlight()

    def apply_highlight(self):
        if not self.hovered_curve:
            return
        for line in self.hovered_curve["lines"]:
            line.set_linewidth(3.5)
        self.canvas.draw_idle()

    def clear_highlight(self):
        if not self.hovered_curve:
            return
        for line in self.hovered_curve["lines"]:
            line.set_linewidth(1.5)
        self.hovered_curve = None
        self.canvas.draw_idle()

    # ---------- Results ----------
    def get_results(self):
        good = [c["step"] for c in self.curves if c["state"] == "good"]
        bad = [c["step"] for c in self.curves if c["state"] == "bad"]
        return good, bad


# ---------- Public API ----------
def classify_curves(good_curves, bad_curves, name):
    root = tk.Tk()
    app = CurveClassifierApp(root, good_curves, bad_curves, name)
    root.mainloop()
    return app.get_results()

# Create fake data
# def make_curve(seed):
#     t = np.linspace(0, 10, 200)
#     return pd.DataFrame({
#         "Time": t,
#         "Roll": np.sin(t + seed),
#         "Pitch": np.sin(t + seed + 0.5),
#         "Yaw": np.sin(t + seed + 1.0),
#     })
#
# good_curves = [make_curve(i) for i in range(3)]
# bad_curves = [make_curve(i + 10) for i in range(2)]
#
# # Run classifier
# good_updated, bad_updated = classify_curves(good_curves, bad_curves)
#
# print("Good:", len(good_updated))
# print("Bad:", len(bad_updated))