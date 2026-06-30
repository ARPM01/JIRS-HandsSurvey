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
    "Mia Hand",
    "steeper Myo Kinisi",
    "SensorHand Speed",
    "Ottobock BeBionic",
    "Ossur iLimb",
    "Psyonic Ability hand",
    "Vincent hand",
    "Covvi Nexus Hand",
    "Taska hand",
]

# get 9 colors for each company that are far from each other
color_maps = ["tab10", "tab20", "Set1", "Set2", "Set3", "Paired", "Pastel1", "Pastel2"]


def get_colors_from_cmap(cmap_name, n):
    cmap = pl.get_cmap(cmap_name)
    colors = [cmap(i) for i in range(0, cmap.N, cmap.N // n)]
    return colors


# Number of colors you want
num_colors = 10

# Get a list of colors from one of the color maps
colors = get_colors_from_cmap(color_maps[1], num_colors)

colors_list = [
    colors[9],
    colors[0],
    colors[1],
    colors[2],
    colors[2],
    colors[3],
    colors[4],
    colors[5],
    colors[6],
    colors[7],
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
    lines[0],
    lines[0],
    lines[1],
    lines[0],
    lines[0],
    lines[0],
    lines[0],
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
    # Mia Hand
    [5, 6, 4, 1, 0, 0],
    # steeper Myo Kinisi
    [5, 2, 2, 0, 0, 0],
    # SensorHand Speed
    [5, 2, 2, 0, 0, 0],
    # Ottobock BeBionic
    [5, 11.2, -1, 1.1, 0.1, 1.1],
    # Ossur iLimb
    [5, 11, 6, 1, 0, 1],
    # Psyonic Ability hand
    [5, 10, -1, 1, 0, 1],
    # Vincent hand
    [5, 9.7, 5.9, 0.9, 0, 0.9],
    # Covvi Nexus Hand
    [5.05, 11.05, -1, 1.05, 0.05, 1.05],
    # Taska hand
    [5, 10, -1, 1, 0, 1],
]  # -1 means no data


labels_ticks = [
    list(range(0, 6))[-5:],
    list(range(0, 26, 5))[-5:],
    list(range(0, 26, 5))[-5:],
    [" ", "No", " ", "Yes", " "],
    [" ", "No", " ", "Yes", " "],
    [" ", "No", " ", "Yes", " "],
]

labels_ticks[2] = [5, 10, "N/A", "", ""]


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

# anywhere where there is a -1, replace with 10
for i in range(len(data)):
    for j in range(len(data[i])):
        if data[i][j] == -1:
            data[i][j] = 15

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
    os.path.join(_OUT, "hands_prosthetic_plot_only.png"), dpi=300, bbox_inches="tight"
)
fig.savefig(
    os.path.join(_OUT, "hands_prosthetic_plot_only.pdf"), dpi=300, bbox_inches="tight"
)
fig.savefig(
    os.path.join(_OUT, "hands_prosthetic_plot_only.eps"), dpi=300, bbox_inches="tight"
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
    os.path.join(_OUT, "hands_prosthetic_legend.png"),
    dpi=300,
    bbox_inches="tight",
    pad_inches=0,
)
legend_fig.savefig(
    os.path.join(_OUT, "hands_prosthetic_legend.pdf"),
    dpi=300,
    bbox_inches="tight",
    pad_inches=0,
)
legend_fig.savefig(
    os.path.join(_OUT, "hands_prosthetic_legend.eps"),
    dpi=300,
    bbox_inches="tight",
    pad_inches=0,
)
