import os
import sys

import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from load_hands import load_hands

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manuscript", "figures")
os.makedirs(_OUT, exist_ok=True)

SKILL_COLORS = sns.color_palette("colorblind", 4)

df = load_hands()

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
hist_bins = [
    [0, 1, 2, 3, 4, 5],
    [0, 1, 2, 3, 4],
    [2, 3, 4, 5, 6, 7],
    [0, 5, 10, 15, 20, 25],
    [0, 5, 10, 15, 20, 25]
]
data_ranges = np.array([len(actuation_features), len(sensor_features), 6, 25, 25])


def generate_plot_data(hands):
    features = []
    for hand in hands:
        n_actuation_features = np.count_nonzero(hand_boolean_features.loc[hand, actuation_features])
        n_sensor_features = np.count_nonzero(hand_boolean_features.loc[hand, sensor_features])
        data = np.array([n_actuation_features, n_sensor_features] + list(hand_features.loc[hand, numeric_features]), dtype=float)
        features.append(data)
    if not features:
        return np.empty((0, 5))
    return np.vstack(features)


feature_valid = [
    hand_boolean_features[actuation_features].notna().all(axis=1),
    hand_boolean_features[sensor_features].notna().all(axis=1),
    hand_features["Num. of Fingers"].notna(),
    hand_features["DoF"].notna(),
    hand_features["Num. Actuators"].notna(),
]

sns.set_theme(context="paper", style="ticks", rc={"axes.spines.right": False, "axes.spines.top": False})
fontsize = 8
fig = plt.figure(figsize=(6.5, 2.3), dpi=100)
for i in range(len(categories)):
    ax = fig.add_subplot(1, 5, 1 + i)
    valid_i = feature_valid[i]
    valid_hands = hand_skills[valid_i].index

    all_features_i = generate_plot_data(valid_hands)
    all_hist_i = np.histogram(all_features_i[:, i], bins=hist_bins[i])
    n_all_hands = all_hist_i[0].sum()

    group = list(skill_categories[[5, 8, 11, 13]])
    # 5: Pushing coin (cat. 6)
    # 8: Rolling ball on table (cat. 9)
    # 11: Turning doorknob (cat. 12)
    # 13: Writing (cat. 14)
    bin_edges = np.asarray(all_hist_i[1], dtype=float)
    bin_full_w = bin_edges[1] - bin_edges[0]   # uniform bins
    group_w = 0.8 * bin_full_w   # leave 10 % gap on each side between groups
    sub_w = group_w / len(group)
    bin_centers = bin_edges[:-1] + bin_full_w / 2.0
    for offset, selected in enumerate(group):
        skill_hands = hand_skills[valid_i & hand_skills[selected]].index
        skill_features = generate_plot_data(skill_hands)
        skill_hist_i = np.histogram(skill_features[:, i], bins=hist_bins[i])
        n_skill_hands = skill_hist_i[0].sum()
        assert n_skill_hands <= n_all_hands, f"Failed: {n_skill_hands=} <= {n_all_hands=}"
        np.testing.assert_array_almost_equal(skill_hist_i[1], all_hist_i[1])

        percentage = skill_hist_i[0] / all_hist_i[0]

        # Center each group of 4 bars over the bin center
        x = bin_centers + (offset - (len(group) - 1) / 2.0) * sub_w
        label = selected.split(":")[0]
        ax.bar(x, percentage, width=sub_w, color=SKILL_COLORS[offset],
               edgecolor='white', linewidth=0.5, label=label)

    for edge in bin_edges[1:-1]:
        ax.axvline(edge, color='gray', linewidth=0.5, linestyle='--', zorder=0)
    for cx, count in zip(bin_centers, all_hist_i[0]):
        if count > 0:
            ax.text(cx, 1.02, f"N={count}", ha='center', va='bottom',
                    fontsize=fontsize - 1, color='black', rotation=90)
    ax.set_xticks(bin_centers, [str(int(b)) for b in bin_edges[:-1]])
    ax.tick_params(axis='x', labelsize=fontsize, rotation=60)
    ax.tick_params(axis='y', labelsize=fontsize, pad=1)
    ax.set_xlabel(categories[i], fontsize=fontsize)
    ax.set_ylim((0.0, 1.05))
    ax.set_yticks(np.arange(0.0, 1.1, 0.2))
    if i == 0:
        ax.set_ylabel("Fraction of Hands", fontsize=fontsize)
handles, labels = plt.subplot(153).get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=2, prop={"size": 5},
           bbox_to_anchor=(0.5, 1.0), bbox_transform=fig.transFigure)
plt.subplots_adjust(left=0.08, bottom=0.22, right=0.985, top=0.74, wspace=0.35, hspace=0)
#plt.show()
plt.savefig(os.path.join(_OUT, "skill_repertoire.pdf"), bbox_inches="tight", pad_inches=0.05)
plt.savefig(os.path.join(_OUT, "skill_repertoire.png"), dpi=300)
