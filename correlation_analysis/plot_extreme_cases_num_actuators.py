import os
import sys

import seaborn as sns
import numpy as np
import pandas as pd
from cycler import cycle
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from load_hands import load_hands

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manuscript", "figures")
os.makedirs(_OUT, exist_ok=True)


sns.set_theme()
sns.set_style("whitegrid")


def get_colors(color_map, num_colors):
    cmap = plt.get_cmap(color_map)
    return cycle([cmap(i) for i in range(0, cmap.N, cmap.N // num_colors)])
color_maps = ['tab10', 'tab20', 'Set1', 'Set2', 'Set3', 'Paired', 'Pastel1', 'Pastel2', 'Pastel3']
colors = get_colors(color_maps[0], 9)
lines = cycle(['-', '--', '-.', ':', '',])

df = load_hands()

# very hacky...
skill_categories = df.columns[13:-2]
skill_dof = df.columns[-2:]
assert skill_categories[0] == "No Contact -> No Motion: Rest position"
actuation_features = ["Palm (used or not)", "Reposition / Opposition", "Abduction / Adduction", "Flexion/Extension"]
sensor_features = ["Tactile Feedback", "Kinesthetic Feedback", "Visual Feedback"]
boolean_features = actuation_features + sensor_features
numeric_features = ["Num. of Fingers", "DoF", "Num. Actuators"]

df = df[list(numeric_features) + list(skill_dof)]
print(df)

sns.set_theme(context="paper", style="whitegrid", font_scale=0.8)
fig = plt.figure(figsize=(6.5, 2.0), dpi=100)
ax = plt.subplot(111)

ax.add_patch(plt.Circle((1, 3), 0.4, color="gray", alpha=0.4, linewidth=0))
ax.text(1, 3.8, "(1)", horizontalalignment="center", verticalalignment="center")
ax.add_patch(plt.Circle((4, 6), 0.7, color="gray", alpha=0.4, linewidth=0))
ax.text(4, 5, "(2)", horizontalalignment="center", verticalalignment="center")

#'Num. of Fingers',
#'DoF',
#'Num. Actuators',
#'Contact -> Prehensile -> Motion -> Within Hand -> No Motion at Contact: DoF',
#'Contact -> Prehensile -> Motion -> Within Hand -> Motion at Contact: DoF'
x = "Num. Actuators"
y = "Contact -> Prehensile -> Motion -> Within Hand -> Motion at Contact: DoF"
df_mac_without_nan = df[[x, y]].dropna().astype(int).rename(columns={y: "DoF"}, errors="raise")
df_mac_without_nan["label"] = "Motion at Contact"
y = "Contact -> Prehensile -> Motion -> Within Hand -> No Motion at Contact: DoF"
df_nmac_without_nan = df[[x, y]].dropna().astype(int).rename(columns={y: "DoF"})
df_nmac_without_nan["label"] = "No Motion at Contact"
df_aggregated_results = pd.concat([df_mac_without_nan, df_nmac_without_nan])

print(df_aggregated_results.columns)
sns.swarmplot(data=df_aggregated_results, x=x, y="DoF", hue="label", marker="x", linewidth=1, size=5, native_scale=True, ax=ax)
#sns.regplot(data=df_aggregated_results, x=x, y="DoF", ax=ax, x_jitter=.3, marker="x")
#sns.regplot(data=df_aggregated_results, x=x, y="DoF", ax=ax, robust=True, x_jitter=.15, marker="x")
#sns.jointplot(data=df_aggregated_results, x=x, y="DoF", kind="reg", order=1)

ax.set_ylabel("Degrees of Freedom (DoF)")
ax.set_xticks(range(0, 25, 1))
ax.set_ylim((0, 6.8))
ax.set_yticks(range(0, 7, 1))
ax.set_xlabel("Num. of Actuators")
plt.legend(loc="upper center", bbox_to_anchor=(0.4, 1.12))
sns.despine(ax=ax)
ax.xaxis.grid(True)
ax.yaxis.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(_OUT, "num_actuators_vs_in_hand_dof_extreme_cases.pdf"), bbox_inches="tight", pad_inches=0)
#plt.show()

