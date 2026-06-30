import os
import sys

import numpy as np
import pandas as pd
from cycler import cycle
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import seaborn as sns

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from load_hands import load_hands

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manuscript", "figures")
os.makedirs(_OUT, exist_ok=True)

def get_colors(color_map, num_colors):
    cmap = plt.get_cmap(color_map)
    return cycle([cmap(i) for i in range(0, cmap.N, cmap.N // num_colors)])
color_maps = ['tab10', 'tab20', 'Set1', 'Set2', 'Set3', 'Paired', 'Pastel1', 'Pastel2', 'Pastel3']
colors = get_colors(color_maps[0], 9)
lines = cycle(['-', '--', '-.', ':', '',])

df = load_hands()

# very hacky...
skill_categories = df.columns[13:]
assert skill_categories[0] == "No Contact -> No Motion: Rest position"
actuation_features = ["Palm (used or not)", "Reposition / Opposition", "Abduction / Adduction", "Flexion/Extension"]
sensor_features = ["Tactile Feedback", "Kinesthetic Feedback", "Visual Feedback"]
boolean_features = actuation_features + sensor_features
numeric_features = ["Num. of Fingers", "DoF", "Num. Actuators"]

groups = df.groupby("HandName")
hand_skills = groups[skill_categories].agg("any")

hand_boolean_features = groups[boolean_features].agg("any")
hand_numeric_features = groups[numeric_features].agg("max")
hand_features = hand_numeric_features.join(hand_boolean_features)

categories = ["Actuation Features", "Sensor Features", "Num. of Fingers", "DoF", "Num. of Actuators"]
feature_tick_labels = [
    [0, 1, 2, 3, 4],
    [0, 1, 2, 3],
    [0, 1, 2, 3, 4, 5, 6],
    [0, 5, 10, 15, 20, 25],
    [0, 5, 10, 15, 20, 25]
]
data_ranges = np.array([len(actuation_features), len(sensor_features), 6, 25, 25])


def generate_plot_data(hands):
    all_features = []
    for idx in range(len(hands)):
        n_actuation_features = np.count_nonzero(hand_boolean_features[actuation_features].iloc[idx])
        n_sensor_features = np.count_nonzero(hand_boolean_features[sensor_features].iloc[idx])
        data = np.array([n_actuation_features, n_sensor_features] + list(hand_features[numeric_features].iloc[idx]), dtype=float)
        all_features.append(data)
    all_features = np.vstack(all_features)
    return all_features


sns.set_theme(context="paper", style="ticks", rc={"axes.spines.right": False, "axes.spines.top": False})
fontsize = 8
fig = plt.figure(figsize=(6.5, 1.7), dpi=100)
all_features = generate_plot_data(hand_skills.index)
bar_texts = []  # (ax, text_obj, bar_width_in_data)
for i in range(len(categories)):
    ax = fig.add_subplot(1, 5, 1 + i)
    lo, hi = int(np.nanmin(all_features[:, i])), int(np.nanmax(all_features[:, i]) + 1)
    n_bins = min(hi - lo + 1, 8)
    bin_edges = np.linspace(lo, hi, n_bins)
    counts, edges_out, _ = ax.hist([all_features[:, i]], bins=bin_edges - 0.5, label=["All hands"])
    bar_counts = np.asarray(counts).ravel()
    bar_centers = (edges_out[:-1] + edges_out[1:]) / 2
    bar_width_data = edges_out[1] - edges_out[0]
    for cx, count in zip(bar_centers, bar_counts):
        if count > 0:
            txt = ax.text(cx + 0.08 * bar_width_data, count / 2, str(int(count)),
                          ha='center', va='center', rotation=90, color='white',
                          clip_on=False)
            txt.set_path_effects([pe.withStroke(linewidth=1.5, foreground='#4C72B0')])
            bar_texts.append((ax, txt, bar_width_data, count))
    xtick_locs = feature_tick_labels[i]
    xtick_labels = feature_tick_labels[i]
    ax.set_xticks(xtick_locs, xtick_labels)
    ax.tick_params(axis='x', labelsize=fontsize, rotation=60)
    ax.tick_params(axis='y', labelsize=fontsize)
    ax.locator_params(axis="y", integer=True)
    ax.set_xlabel(categories[i], fontsize=fontsize)
    ax.set_ylim((0, 58))
    ax.set_yticks(range(0, 51, 10))
    if i == 0:
        ax.set_ylabel("Number of Hands", fontsize=fontsize)
plt.tight_layout()

# Set each label's font size so its rendered height equals the bar width;
# switch to dark colour when the bar is too short to contain the text legibly.
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
for ax, txt, bar_width_data, count in bar_texts:
    ax_bbox = ax.get_window_extent(renderer)
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    pts_per_data_x = ax_bbox.width  * 72.0 / fig.dpi / (xlim[1] - xlim[0])
    pts_per_data_y = ax_bbox.height * 72.0 / fig.dpi / (ylim[1] - ylim[0])
    font_size = bar_width_data * pts_per_data_x
    txt.set_fontsize(font_size)
    bar_height_pts = count * pts_per_data_y
    text_height_pts = font_size * len(txt.get_text()) * 0.6
    if count < 5 or bar_height_pts < text_height_pts:
        txt.set_position((txt.get_position()[0], count + 0.5))
        txt.set_va('bottom')

plt.savefig(os.path.join(_OUT, "hand_features.pdf"), bbox_inches="tight", pad_inches=0.05)
plt.savefig(os.path.join(_OUT, "hand_features.png"), dpi=300)
