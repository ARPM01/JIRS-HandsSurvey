"""
Statistical analysis for all five research questions.

TABLE A — Continuous / count features (Spearman ρ, 10 tests)
  Pairs tested: {fingers, DoF, actuators}  →  in-hand DoF (cat.14, cat.15)
                {fingers, DoF, actuators, num_sensors}  →  skill_repertoire_size

TABLE B — Binary features (Mann-Whitney U, 5 tests)
  {abduction/adduction, tactile, kinesthetic}  →  skill_repertoire_size
  {abduction/adduction}                         →  in-hand DoF (cat.14, cat.15)
  Mann-Whitney is used regardless of normality (it is always valid and nearly as
  powerful as Welch's t-test when normality holds).

Each table is printed twice: once per-paper-hand (raw data, one row per
paper-hand combination) and once per-hand (aggregated across papers by
HandName), so the publication-scope confound can be assessed directly.

All p-values are corrected with Benjamini-Hochberg FDR (α = 0.05).
Effect sizes and 95 % CIs are reported for every test.
"""

import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from load_hands import load_hands


# ── Normality helper ──────────────────────────────────────────────────────────

# ── Bootstrap helpers ────────────────────────────────────────────────────────

def _bootstrap_spearman_ci(x, y, n_boot=5000, alpha=0.05, seed=42):
    # Spearman ρ has no closed-form CI formula for small/moderate N (Fisher's
    # z-transform is only approximate for rank correlations), so we use the
    # percentile bootstrap instead.  5000 resamples give stable 95 % CI
    # estimates; the fixed seed ensures reproducibility.
    rng = np.random.default_rng(seed)
    n = len(x)
    idx = rng.integers(0, n, size=(n_boot, n))   # (n_boot, n)
    X, Y = x[idx], y[idx]                        # (n_boot, n)
    Rx = stats.rankdata(X, method="average", axis=1)
    Ry = stats.rankdata(Y, method="average", axis=1)
    # Pearson r of average-ranked rows = Spearman rho
    Rx -= Rx.mean(axis=1, keepdims=True)
    Ry -= Ry.mean(axis=1, keepdims=True)
    num = (Rx * Ry).sum(axis=1)
    denom = np.sqrt((Rx ** 2).sum(axis=1) * (Ry ** 2).sum(axis=1))
    # denom == 0 for near-constant resamples; nanpercentile excludes them.
    rhos = np.where(denom > 0, num / denom, np.nan)
    return (np.nanpercentile(rhos, 100 * alpha / 2),
            np.nanpercentile(rhos, 100 * (1 - alpha / 2)))


def _bootstrap_rankbiserial_ci(g1, g0, n_boot=5000, alpha=0.05, seed=42):
    # The rank-biserial correlation r_rb has no standard parametric CI, so
    # again we bootstrap.  Each iteration resamples both groups independently
    # (with replacement), recomputes U, and derives r_rb from it.
    rng = np.random.default_rng(seed)
    n1, n0 = len(g1), len(g0)
    # Draw all resamples at once: (n_boot, n_group)
    S1 = g1[rng.integers(0, n1, size=(n_boot, n1))]
    S0 = g0[rng.integers(0, n0, size=(n_boot, n0))]
    # Pairwise differences for every bootstrap resample: (n_boot, n1, n0)
    diff = S1[:, :, None] - S0[:, None, :]
    U = (diff > 0).sum(axis=(1, 2)) + 0.5 * (diff == 0).sum(axis=(1, 2))
    rbs = 2.0 * U / (n1 * n0) - 1.0
    return (np.percentile(rbs, 100 * alpha / 2),
            np.percentile(rbs, 100 * (1 - alpha / 2)))


# ── Test runners ─────────────────────────────────────────────────────────────

def spearman_test(x_series, y_series, label_x, label_y, rq, n_boot=5000):
    """Spearman ρ with 95 % percentile bootstrap CI.

    Robust to non-normality, outliers, and monotone non-linearities.
    The p-value is from scipy.stats.spearmanr; the CI uses the percentile
    bootstrap rather than Fisher's z-transform (only approximate for ρ).
    The t-statistic t = ρ*sqrt(N-2)/sqrt(1-ρ²), df = N-2, is reported
    for completeness.
    """
    xy = pd.concat([x_series, y_series], axis=1).dropna()
    xy.columns = ["x", "y"]
    n = len(xy)
    rho, p = stats.spearmanr(xy["x"].values, xy["y"].values)
    ci_lo, ci_hi = _bootstrap_spearman_ci(xy["x"].values, xy["y"].values, n_boot=n_boot)
    t_stat = rho * math.sqrt(n - 2) / math.sqrt(max(1 - rho ** 2, 1e-12))
    return dict(
        rq=rq, feature=label_x, outcome=label_y, method="Spearman ρ",
        N=n, stat=rho, ci_lo=ci_lo, ci_hi=ci_hi,
        test_stat=t_stat, df_val=n - 2, p=p,
    )


def mannwhitney_test(feature_col, outcome_col, df, rq, n_boot=5000, outcome_label=None):
    """Mann-Whitney U with rank-biserial r effect size and 95 % bootstrap CI.

    The binary features (e.g. has abduction/adduction: yes/no) split the
    sample into two groups.  Mann-Whitney U tests whether one group tends to
    produce higher skill_repertoire_size values than the other — without
    assuming normality in either group (a reasonable precaution for a count
    bounded by 15).

    Effect size — rank-biserial correlation r_rb:
      r_rb = 2*U / (n1*n2) - 1
    This is Cliff's δ re-expressed on [−1, +1]: r_rb = +1 means every
    observation in group-1 exceeds every observation in group-0; r_rb = 0
    means the groups are stochastically equal.  We call the "feature present"
    group group-1 (g1), so a positive r_rb means the feature is associated
    with a larger skill repertoire.

    The one-sided alternative tests H1: P(g1 > g0) > 0.5, i.e. hands that
    have the feature tend to show a broader skill repertoire.  A one-sided
    test is justified because all three binary features are expected a priori
    to be associated with greater capability (not less).
    """
    sub = df[[feature_col, outcome_col]].dropna()
    g1 = sub.loc[sub[feature_col] == True, outcome_col].values.astype(float)
    g0 = sub.loc[sub[feature_col] == False, outcome_col].values.astype(float)
    U, p = stats.mannwhitneyu(g1, g0, alternative="greater")
    # r_rb = 2*U/(n1*n2) - 1: positive when group+ has higher values
    r_rb = 2.0 * U / (len(g1) * len(g0)) - 1.0
    ci_lo, ci_hi = _bootstrap_rankbiserial_ci(g1, g0, n_boot=n_boot)
    q1p, med_p, q3p = np.percentile(g1, [25, 50, 75])
    q1n, med_n, q3n = np.percentile(g0, [25, 50, 75])
    return dict(
        rq=rq, feature=feature_col,
        outcome=outcome_label if outcome_label is not None else outcome_col,
        n_pos=len(g1),
        median_pos=med_p, q1_pos=q1p, q3_pos=q3p,
        n_neg=len(g0),
        median_neg=med_n, q1_neg=q1n, q3_neg=q3n,
        U=U, r_rb=r_rb, ci_lo=ci_lo, ci_hi=ci_hi, p=p,
    )


# ── Aggregation ──────────────────────────────────────────────────────────────

def aggregate_by_hand(df, skill_cols, dof_cols, bool_feat_cols, numeric_feat_cols):
    """Collapse multiple paper-entries for the same hand into one row.

    The raw data has one row per (paper, hand) pair.  The same physical hand
    (e.g. the Shadow Dexterous Hand, which appears in 15 papers) therefore
    contributes many rows, inflating N and creating pseudo-replication: the
    rows are not independent because they share the same hardware.  Aggregating
    by HandName gives one row per unique hand, restoring independence.

    Aggregation rules:
      skill columns   : any()  — skill is in repertoire if shown in any paper
      bool features   : any()  — most capable sensor/mechanism config observed
      in-hand DoF cols: max()  — highest DoF demonstrated across papers
      numeric features: max()  — most complex configuration seen (warns when
                                 values differ, which may indicate model variants)
    """
    # Warn about hands whose numeric features differ across entries
    inconsistent = []
    for hand, grp in df.groupby("HandName"):
        for col in numeric_feat_cols:
            vals = grp[col].dropna().unique()
            if len(vals) > 1:
                inconsistent.append((hand, col, sorted(vals.tolist())))
    if inconsistent:
        print("\nWARNING — hands with inconsistent numeric features "
              "(possible model variants merged by name normalisation):")
        for hand, col, vals in inconsistent:
            print(f"  {hand:<40} {col}: {vals}  → using max()")
        print()

    agg = {col: "any" for col in [*skill_cols, *bool_feat_cols]}
    agg.update({col: "max" for col in [*dof_cols, *numeric_feat_cols]})

    grouped = df.groupby("HandName", sort=False).agg(agg).reset_index()
    return grouped


# ── Test suite ────────────────────────────────────────────────────────────────

def run_all_tests(df, skill_cols, label, level):
    """Run the full battery of tests on df and return (cont_results, bin_results).

    Outcome variables derived here:
      skill_repertoire_size — number of skill categories (out of 15) for which
          at least one paper reports the hand as capable.  Summing the Boolean
          skill columns gives an integer in [0, 15].
      num_sensors — count of sensor modalities present (tactile / kinesthetic /
          visual), in [0, 3].  Used as a continuous proxy for RQ5.

    Test selection:
      Spearman ρ is used for all continuous predictors (robust to non-normality,
      outliers, and bounded/integer outcomes).  Mann-Whitney U is used for all
      binary predictors: it is always valid and retains ~95 % of the power of a
      t-test even when normality holds.

    FDR correction:
      All 15 p-values (10 from Table A + 5 from Table B) are corrected jointly
      with the Benjamini-Hochberg procedure at α = 0.05.  Joint correction is
      important because the tests share predictors and outcomes, making
      family-wise error control necessary.  BH controls the *false discovery
      rate* (expected proportion of false positives among rejections) rather
      than the more conservative family-wise error rate (FWER), which is
      appropriate given the exploratory nature of these analyses.
    """
    df = df.copy()
    # skill_repertoire_size: count of True entries across the 15 skill columns.
    # NaN is treated as False by sum(), which is intentional — a missing entry
    # means the skill was not reported, not that it was attempted and failed.
    df["skill_repertoire_size"] = df[skill_cols].sum(axis=1)
    df["num_sensors"] = df[["Tactile Feedback", "Kinesthetic Feedback",
                             "Visual Feedback"]].sum(axis=1)
    # Coerce Num. of Fingers to numeric; ">5" was already mapped to "6" by
    # load_hands(), but any remaining non-numeric strings become NaN.
    df["Num. of Fingers"] = pd.to_numeric(df["Num. of Fingers"], errors="coerce")

    cont_results = []

    # ── Spearman ρ: mechanism features → in-hand DoF ─────────────────────────
    for feat, rq in [("Num. of Fingers", "RQ1"), ("DoF", "RQ2"), ("Num. Actuators", "RQ2")]:
        for col, lbl in [(COL_DOF_MOTION,    "in-hand DoF (cat.14 Motion@Contact)"),
                         (COL_DOF_NO_MOTION, "in-hand DoF (cat.15 No-Motion@Contact)")]:
            cont_results.append(spearman_test(df[feat], df[col], feat, lbl, rq))

    # ── Spearman ρ: features → skill_repertoire_size ──────────────────────────
    for feat, rq in [("Num. of Fingers", "RQ1"), ("DoF", "RQ2"),
                     ("Num. Actuators", "RQ2"), ("num_sensors", "RQ5")]:
        cont_results.append(
            spearman_test(df[feat], df["skill_repertoire_size"],
                          feat, "skill_repertoire_size", rq)
        )

    # ── Mann-Whitney U: binary features → skill_repertoire_size ──────────────
    bin_results = []
    for feat, rq in [("Abduction / Adduction", "RQ3"),
                     ("Tactile Feedback",       "RQ4"),
                     ("Kinesthetic Feedback",   "RQ4")]:
        bin_results.append(mannwhitney_test(feat, "skill_repertoire_size", df, rq))

    # ── Mann-Whitney U: abduction/adduction → in-hand DoF (RQ3) ──────────────
    for col, lbl in [(COL_DOF_MOTION,    "in-hand DoF (cat.14 Motion@Contact)"),
                     (COL_DOF_NO_MOTION, "in-hand DoF (cat.15 No-Motion@Contact)")]:
        bin_results.append(
            mannwhitney_test("Abduction / Adduction", col, df, "RQ3",
                             outcome_label=lbl)
        )

    # FDR correction: collect all raw p-values from both families into a single
    # list, apply BH, then distribute the corrected values back.  Correcting
    # both families together (rather than separately) is more conservative and
    # accounts for the shared outcome variable (skill_repertoire_size) across
    # many tests.
    all_p = [r["p"] for r in cont_results] + [r["p"] for r in bin_results]
    _, p_fdr, _, _ = multipletests(all_p, alpha=0.05, method="fdr_bh")
    for i, r in enumerate(cont_results):
        r["p_fdr"] = p_fdr[i]
    for i, r in enumerate(bin_results):
        r["p_fdr"] = p_fdr[len(cont_results) + i]

    for r in cont_results + bin_results:
        r["level"] = level

    return cont_results, bin_results


# ── CSV output ───────────────────────────────────────────────────────────────

def save_results(all_cont, all_bin, out_dir):
    pd.DataFrame(all_cont).to_csv(
        os.path.join(out_dir, "results_continuous.csv"), index=False)
    pd.DataFrame(all_bin).to_csv(
        os.path.join(out_dir, "results_binary.csv"), index=False)


# ── Printing ──────────────────────────────────────────────────────────────────

def print_tables(cont_results, bin_results, label):
    W = 130
    n_sig = sum(r["p_fdr"] < 0.05 for r in cont_results + bin_results)

    print("\n" + "#" * W)
    print(f"# {label}")
    print("#" * W)

    print("\n" + "=" * W)
    print("TABLE A  Continuous / count features")
    print("=" * W)
    hdr = (f"{'RQ':<5} {'Method':<12} {'Feature':<20} {'Outcome':<38} "
           f"{'N':>4}  {'stat':>7}  {'95% CI':<20}  {'t':>7}  {'df':>4}  "
           f"{'p':>7}  {'p*':>7}")
    print(hdr)
    print("-" * W)
    for r in cont_results:
        sym = "r" if r["method"] == "Pearson r" else "ρ"
        ci_s = f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}]"
        sig = " *" if r["p_fdr"] < 0.05 else ""
        print(f"{r['rq']:<5} {r['method']:<12} {r['feature']:<20} {r['outcome']:<38} "
              f"{r['N']:>4}  {sym}={r['stat']:+.3f}  {ci_s:<20}  "
              f"{r['test_stat']:>+7.3f}  {r['df_val']:>4}  {r['p']:>7.4f}  "
              f"{r['p_fdr']:>7.4f}{sig}")

    print("\n" + "=" * W)
    print("TABLE B  Binary features  (Mann-Whitney U, outcome = skill_repertoire_size)")
    print("=" * W)
    hdr2 = (f"{'RQ':<5} {'Feature':<26} {'N+':<4} {'median+(IQR)':<18} "
            f"{'N-':<4} {'median-(IQR)':<18} {'U':>7}  {'r_rb':>6}  "
            f"{'95% CI':<20}  {'p':>7}  {'p*':>7}")
    print(hdr2)
    print("-" * W)
    for r in bin_results:
        mp = f"{r['median_pos']:.1f} ({r['q1_pos']:.1f}–{r['q3_pos']:.1f})"
        mn = f"{r['median_neg']:.1f} ({r['q1_neg']:.1f}–{r['q3_neg']:.1f})"
        ci_s = f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}]"
        sig = " *" if r["p_fdr"] < 0.05 else ""
        print(f"{r['rq']:<5} {r['feature']:<26} {r['n_pos']:<4} {mp:<18} "
              f"{r['n_neg']:<4} {mn:<18} {r['U']:>7.0f}  {r['r_rb']:>+6.3f}  "
              f"{ci_s:<20}  {r['p']:>7.4f}  {r['p_fdr']:>7.4f}{sig}")

    print(f"\nFDR (BH, α=0.05) — tests: {len(cont_results)+len(bin_results)},  "
          f"significant: {n_sig}")


# ── Constants ────────────────────────────────────────────────────────────────

# Full column names for the two in-hand manipulation DoF outcomes:
#   cat.14 — Motion at Contact: object DoF controlled while fingers move
#   cat.15 — No Motion at Contact: object DoF controlled with static contact
COL_DOF_MOTION    = "Contact -> Prehensile -> Motion -> Within Hand -> Motion at Contact: DoF"
COL_DOF_NO_MOTION = "Contact -> Prehensile -> Motion -> Within Hand -> No Motion at Contact: DoF"

BOOL_FEATS    = ["Palm (used or not)", "Reposition / Opposition",
                 "Abduction / Adduction", "Flexion/Extension",
                 "Tactile Feedback", "Kinesthetic Feedback", "Visual Feedback"]
NUMERIC_FEATS = ["Num. of Fingers", "DoF", "Num. Actuators"]
DOF_COLS      = [COL_DOF_MOTION, COL_DOF_NO_MOTION]


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    df = load_hands()

    # skill_categories: columns 13 onwards up to (but not including) the last
    # two, which are the numeric in-hand DoF columns.
    skill_categories = df.columns[13:-2]
    assert skill_categories[0] == "No Contact -> No Motion: Rest position", skill_categories[0]

    out_dir = os.path.dirname(os.path.abspath(__file__))

    # ── Per-paper-hand analysis (raw, one row per paper-hand combination) ────────
    # Maximises N (128) but introduces pseudo-replication: hands appearing in
    # multiple papers contribute correlated observations.  Serves as a
    # robustness check against the per-hand analysis below.
    cont_pp, bin_pp = run_all_tests(df, skill_categories,
                                    label="PER-PAPER-HAND  (one row per paper-hand combination, N=128)",
                                    level="per_paper")
    print_tables(cont_pp, bin_pp,
                 label="PER-PAPER-HAND  (one row per paper-hand combination, N=128)")

    # ── Per-hand analysis (aggregated across papers) ──────────────────────────
    # Aggregating by HandName removes pseudo-replication.  Each unique physical
    # hand is represented once with its broadest capability profile
    # (any/max aggregation — see aggregate_by_hand).  Primary analysis.
    df_hand = aggregate_by_hand(df, skill_categories, DOF_COLS, BOOL_FEATS, NUMERIC_FEATS)
    n_hands = len(df_hand)

    cont_ph, bin_ph = run_all_tests(df_hand, skill_categories,
                                    label=f"PER-HAND  (aggregated, N={n_hands})",
                                    level="per_hand")
    print_tables(cont_ph, bin_ph,
                 label=f"PER-HAND  (aggregated, N={n_hands})")

    save_results(cont_pp + cont_ph, bin_pp + bin_ph, out_dir)


if __name__ == "__main__":
    main()
