import os
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt

_OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "manuscript", "figures"
)
os.makedirs(_OUT, exist_ok=True)

hand_names = [
    "Human Hand",
    "Robotiq 2F-85/2F-140/Hand-E",
    "Robotiq 3-finger adaptive robot gripper",
    "RH-P12-RN",
    "GRIPKIT (EASY/ PLUS/ PRO/ E PRO/ P PRO)",
    "GRIPKIT Industrial (PZ PRO)",
    "BarrettHand",
    "SVH",
    "RH8D",
    "Allegro Hand",
    "Shadow dextrous hand",
    "Shadow dextrous hand lite",
    "Shadow dextrous hand extra lite",
    "Shadow dextrous hand super lite",
    "IH2 Azzurra",
]

# get 9 colors for each company that are far from each other
color_maps = ["tab10", "tab20", "Set1", "Set2", "Set3", "Paired", "Pastel1", "Pastel2"]


def get_colors_from_cmap(cmap_name, n):
    cmap = pl.get_cmap(cmap_name)
    colors = [cmap(i) for i in range(0, cmap.N, cmap.N // n)]
    return colors


num_colors = 10

# Get a list of colors from one of the color maps
colors = get_colors_from_cmap("tab20", num_colors)


colors_list = [
    colors[9],
    colors[0],
    colors[0],
    colors[1],
    colors[2],
    colors[2],
    colors[3],
    colors[4],
    colors[5],
    colors[6],
    colors[7],
    colors[7],
    colors[7],
    colors[7],
    colors[8],
]
lines = [
    "-",
    "--",
    "-.",
    ":",
    "",
]
lines_list = [
    lines[0],
    lines[0],
    lines[1],
    lines[0],
    lines[0],
    lines[1],
    lines[0],
    lines[0],
    lines[0],
    lines[0],
    lines[0],
    lines[1],
    lines[2],
    lines[3],
    lines[0],
]

titles = [
    "Number of Fingers",
    "DoF",
    "Controlled DoF",
    "Reposition/Opposition",
    "Abduction/Adduction",
    "Flexion",
]

data = [
    # Human Hand
    [5, 20, 16, 1, 1, 1],
    # 2F-85/2F-140/Hand-E
    [2.1, 2.2, 2.2, 0, 0, 0],
    # 3-finger adaptive robot gripper
    [3.01, 10.01, 10.01, 0.01, 0.01, 1.01],
    # RH-P12-RN
    [1.96, 1.96, 1.96, -0.04, -0.04, -0.04],
    # GRIPKIT (EASY/ PLUS/ PRO/ E PRO/ P PRO)
    [1.9, 1.8, 1.8, -0.06, -0.06, -0.06],
    # GRIPKIT Industrial (PZ PRO)
    [2.99, 2.99, 2.99, -0.01, -0.01, -0.01],
    # BarrettHand
    [3.02, 8.02, 8.02, 1.02, 0.02, 1.02],
    # SVH
    [4.96, 20.05, 20.05, 1.05, 1.05, 1.05],
    # RH8D
    [4.96, 19.07, 19.07, 1.07, 1.07, 1.07],
    # Allegro Hand
    [3.98, 15.98, 15.98, 0.98, -0.02, 0.98],
    # Shadow dextrous hand
    [4.96, 24.09, 20.09, 1.09, 1.09, 1.09],
    # Shadow dextrous hand lite
    [4.11, 13.11, 13.11, 1.11, 1.11, 1.11],
    # Shadow dextrous hand extra lite
    [3.13, 10.13, 10.13, 1.13, 1.13, 1.13],
    # Shadow dextrous hand super lite
    [2.15, 7.15, 7.15, 1.15, 1.15, 1.15],
    # IH2 Azzurra
    [4.96, 10.96, 10.96, 0.96, -0.04, 0.96],
]


labels_ticks = [
    list(range(0, 6))[-5:],
    list(range(0, 26, 5))[-5:],
    list(range(0, 26, 5))[-5:],
    [" ", "No", " ", "Yes", " "],
    [" ", "No", " ", "Yes", " "],
    [" ", "No", " ", "Yes", " "],
]


class Radar(object):

    def __init__(self, fig, titles, labels, rect=None):
        if rect is None:
            rect = [0.05, 0.05, 0.95, 0.95]

        self.n = len(titles)
        self.angles = [
            a if a <= 360.0 else a - 360.0
            for a in np.arange(90, 90 + 360, 360.0 / self.n)
        ]
        self.axes = [
            fig.add_axes(rect, projection="polar", label="axes%d" % i)
            for i in range(self.n)
        ]

        self.ax = self.axes[0]
        self.ax.set_thetagrids(
            self.angles, labels=titles, fontsize=16, weight="bold", color="black"
        )
        # Move the theta labels outward
        for label in self.ax.get_xticklabels():
            label.set_verticalalignment("baseline")
            label.set_y(label.get_position()[1] - 0.1)

        for ax in self.axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)
            self.ax.yaxis.grid(False)

        for ax, angle, label in zip(self.axes, self.angles, labels):
            ax.set_rgrids(
                range(1, len(label) + 1), labels=label, angle=angle, fontsize=16
            )
            ax.set_yticklabels([])

            for i, lbl in enumerate(label):
                ax.text(
                    np.deg2rad(angle - 2),
                    i + 1 + 0.3,
                    lbl,
                    ha="center",
                    va="center",
                    fontsize=16,
                )

            ax.spines["polar"].set_visible(False)
            ax.set_ylim(0, len(label))
            ax.xaxis.grid(True, color="black", linestyle="-", alpha=0.5)

    def plot(self, values, *args, **kw):
        angle = np.deg2rad(np.r_[self.angles, self.angles[0]])
        values = np.r_[values, values[0]]
        self.ax.plot(angle, values, *args, **kw)


fig = pl.figure(figsize=(20, 20))


radar = Radar(fig, titles, labels_ticks)
# first do nothing, second and third / 5, last three variables: *2+2
# adjust data to fit the y_ticks
data = np.array(data, dtype=float)
data[:, 0] = data[:, 0]
data[:, 1] = data[:, 1] / 5
data[:, 2] = data[:, 2] / 5
data[:, 3] = data[:, 3] * 2 + 2
data[:, 4] = data[:, 4] * 2 + 2
data[:, 5] = data[:, 5] * 2 + 2

for i in range(len(data)):
    radar.plot(data[i], lines_list[i], lw=2, color=colors_list[i], label=hand_names[i])

fig.set_size_inches(6, 10, forward=True)

# Save the main plot without the legend
fig.savefig(
    os.path.join(_OUT, "robotic_hands_plot_only.png"), dpi=300, bbox_inches="tight"
)
fig.savefig(
    os.path.join(_OUT, "robotic_hands_plot_only.pdf"), dpi=300, bbox_inches="tight"
)
fig.savefig(
    os.path.join(_OUT, "robotic_hands_plot_only.eps"), dpi=300, bbox_inches="tight"
)

# Create a separate figure for the legend
from matplotlib.legend import Legend

legend_fig = plt.figure(figsize=(6, 2))
legend_ax = legend_fig.add_subplot(111)
legend_ax.axis("off")

# Create a dummy plot to get the handles and labels
handles, labels = radar.ax.get_legend_handles_labels()


legend = legend_ax.legend(
    handles,
    labels,
    loc="center",
    ncol=2,
    fontsize=16,
    frameon=True,  # Show the frame (box)
    fancybox=False,  # Square corners
    shadow=False,  # No shadow
    edgecolor="black",  # Black border
)

legend.get_frame().set_edgecolor("black")
legend.get_frame().set_linewidth(2)

legend_fig.savefig(
    os.path.join(_OUT, "robotic_hands_legend.png"),
    dpi=300,
    bbox_inches="tight",
    pad_inches=0,
)
legend_fig.savefig(
    os.path.join(_OUT, "robotic_hands_legend.pdf"),
    dpi=300,
    bbox_inches="tight",
    pad_inches=0,
)
legend_fig.savefig(
    os.path.join(_OUT, "robotic_hands_legend.eps"),
    dpi=300,
    bbox_inches="tight",
    pad_inches=0,
)
