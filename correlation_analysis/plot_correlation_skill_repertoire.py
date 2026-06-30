import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from load_hands import load_hands

_DIR = os.path.dirname(os.path.abspath(__file__))
_OUT = os.path.join(_DIR, "..", "manuscript", "figures")
os.makedirs(_OUT, exist_ok=True)


def _shapiro_wilk(arr, alpha=0.05):
    """Shapiro-Wilk normality test. Returns (n, W, p, is_normal).

    Mirrors the helper in compute_all_tests.py so that the same test-selection
    logic is applied consistently across all analysis scripts.
    """
    arr = np.asarray(arr, dtype=float)
    arr = arr[~np.isnan(arr)]
    n = len(arr)
    if n < 3:
        return n, float("nan"), float("nan"), False
    W, p = stats.shapiro(arr)
    return n, W, p, bool(p >= alpha)


df = load_hands()

skill_categories = df.columns[13:-2]
assert skill_categories[0] == "No Contact -> No Motion: Rest position"

df["skill_repertoire_size"] = df[skill_categories].sum(axis=1)

x = "Num. of Fingers"
y = "skill_repertoire_size"

df_filtered = df[[x, y]].dropna()
df_filtered[x] = df_filtered[x].astype(int)
n = len(df_filtered)

# ── Normality screening ───────────────────────────────────────────────────────
n_x, W_x, p_x, x_normal = _shapiro_wilk(df_filtered[x].values)
n_y, W_y, p_y, y_normal = _shapiro_wilk(df_filtered[y].values)

print("Normality (Shapiro-Wilk, α=0.05):")
print(f"  {x:<35} N={n_x}, W={W_x:.4f}, p={p_x:.4f}, normal={'yes' if x_normal else 'NO'}")
print(f"  {y:<35} N={n_y}, W={W_y:.4f}, p={p_y:.4f}, normal={'yes' if y_normal else 'NO'}")

# ── Test selection ────────────────────────────────────────────────────────────
# Pearson r when both variables are normal; Spearman ρ otherwise.
# This mirrors the selection logic in compute_all_tests.py.
if x_normal and y_normal:
    stat, p_raw = stats.pearsonr(df_filtered[x].values, df_filtered[y].values)
    method = "Pearson r"
    sym = "r"
else:
    stat, p_raw = stats.spearmanr(df_filtered[x].values, df_filtered[y].values)
    method = "Spearman ρ"
    sym = r"\rho"

# ── FDR-corrected p* ──────────────────────────────────────────────────────────
# Read p_fdr from the CSV produced by compute_all_tests.py so that the value
# shown on the figure is consistent with the joint FDR correction applied to
# all 13 tests in the battery.
csv = pd.read_csv(os.path.join(_DIR, "results_continuous.csv"))
row = csv[(csv["level"] == "per_paper") &
          (csv["feature"] == x) &
          (csv["outcome"] == y) &
          (csv["method"] == method)]
p_fdr = row["p_fdr"].iloc[0]

print(f"\nCorrelation: {x} vs. {y}")
print("=======================================================")
print(f"Method={method}, N={n}, stat={stat:+.3f}, p={p_raw:.4f}, p_fdr={p_fdr:.4f}")

# ── Plot ──────────────────────────────────────────────────────────────────────
sns.set_theme(context="paper", style="whitegrid", font_scale=0.8)
fig = plt.figure(figsize=(6.5, 2.5), dpi=100)
ax = plt.subplot(111)

sns.swarmplot(data=df_filtered, x=x, y=y, color="steelblue", marker="x",
              linewidth=1, size=5, native_scale=True, ax=ax)

p_str = "$p^*<0.001$" if p_fdr < 0.001 else f"$p^*={p_fdr:.3f}$"
ax.annotate(f"${sym}={stat:+.2f}$, {p_str}, $N={n}$",
            xy=(0.98, 0.95), xycoords="axes fraction",
            ha="right", va="top", fontsize=7)

ax.set_xlabel("Num. of Fingers")
ax.set_ylabel("Skill Repertoire Size")
ax.set_xticks(range(2, 7))
ax.set_ylim((0, 16))
ax.set_yticks(range(0, 16, 2))
sns.despine(ax=ax)
ax.xaxis.grid(True)
ax.yaxis.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(_OUT, "skill_repertoire_size.pdf"))
print("Saved skill_repertoire_size.pdf")
