# Correlation Analysis

Statistical analysis for RQ1-RQ5. Run from `grasp_survey_scripts/`:

```
python correlation_analysis/compute_all_tests.py
```

Output CSVs are written to `correlation_analysis/`.

---

## Analysis levels

Every test runs twice:

- **Per-paper-hand** (N=128): one row per (paper, hand) pair; maximises N but introduces pseudo-replication
- **Per-hand** (N=93): one row per unique hand after aggregation; primary analysis

### Aggregation rules (per-hand)

| Column type | Rule |
|-------------|------|
| Skill columns (15 binary) | `any()` |
| Boolean features (palm, sensors, ...) | `any()` |
| In-hand DoF (cat.14, cat.15) | `max()` |
| Numeric features (fingers, DoF, actuators) | `max()` |

Hands with differing numeric values across entries are printed as warnings; value set to max.

---

## Outcome variables

- `skill_repertoire_size`: count of Dollar (2014) skill categories (0-15) shown in at least one paper
- `in-hand DoF (cat.14)`: highest object-DoF during Motion at Contact (NaN if not assessed)
- `in-hand DoF (cat.15)`: highest object-DoF during No Motion at Contact (NaN if not assessed)
- `num_sensors`: sensor modalities present (tactile + kinesthetic + visual), range 0-3

---

## Correlation coefficients

**Spearman $\rho$** -- used for all continuous correlations
- Robust to non-normality, outliers, and bounded/integer outcomes (e.g. skill_repertoire_size)
- Effect size: Cohen (1988) thresholds applied by convention (same scale as Pearson r)

**Rank-biserial $r_{rb}$** -- effect size for Mann-Whitney U (binary predictors)
- $r_{rb} = 2 \cdot U / (n_1 \cdot n_2) - 1$; range [-1, +1]; equivalent to Cliff's delta
- $r_{rb} = +1$: every observation in group+ exceeds every observation in group-
- $r_{rb} = 0$: groups are stochastically equal

## Significance testing

**Spearman $\rho$**
- H0: $\rho = 0$ (no monotone association)
- Test statistic: $t = \rho \cdot \sqrt(N-2) / \sqrt(1 - \rho^2)$, $df = N-2$
- Under H0 this follows a t-distribution; p-value from `scipy.stats.spearmanr`

**Mann-Whitney U**
- H0: P(group+ > group-) = 0.5 (stochastic equality, i.e. $r_{rb} = 0$)
- H1: P(group+ > group-) > 0.5 (one-sided; because all binary features are assumed a priori to increase dexterity)
- Test statistic: U = number of pairs where group+ observation exceeds group- observation (plus 0.5 per tie)
- One-sided test via `scipy.stats.mannwhitneyu(alternative="greater")`
- p-value uses exact distribution for small N, normal approximation otherwise

---

## The 15 tests

**Table A -- Continuous predictors (10 tests)**

| RQ | Predictor | Outcome |
|----|-----------|---------|
| RQ1 | Num. of Fingers | in-hand DoF cat.14, cat.15; skill_repertoire_size |
| RQ2 | DoF | in-hand DoF cat.14, cat.15; skill_repertoire_size |
| RQ2 | Num. Actuators | in-hand DoF cat.14, cat.15; skill_repertoire_size |
| RQ5 | num_sensors | skill_repertoire_size |

**Table B -- Binary predictors (5 tests, always Mann-Whitney U)**

| RQ | Predictor | Outcome |
|----|-----------|---------|
| RQ3 | Abduction / Adduction | skill_repertoire_size |
| RQ4 | Tactile Feedback | skill_repertoire_size |
| RQ4 | Kinesthetic Feedback | skill_repertoire_size |
| RQ3 | Abduction / Adduction | in-hand DoF cat.14 |
| RQ3 | Abduction / Adduction | in-hand DoF cat.15 |

---

## Effect sizes and CIs

**Spearman rho**
- CI: 95% percentile bootstrap (5000 resamples, seed 42)

**Mann-Whitney U / rank-biserial r_rb**
- Effect size: $r_{rb} = 2 \cdot U / (n1 \cdot n2) - 1$; range [-1, +1]; positive means feature -> larger repertoire
- Formula from Wendt (1972); equivalent to Cliff's delta
- CI: 95% percentile bootstrap (5000 resamples, seed 42), groups resampled independently

---

## Multiple-comparisons correction

All 15 p-values corrected jointly with Benjamini-Hochberg FDR ($\alpha = 0.05$) via
`statsmodels.stats.multitest.multipletests(method='fdr_bh')`.

- BH chosen over Bonferroni/Holm: controls false discovery rate rather than FWER, more power for exploratory analyses
- Joint correction: both tables share `skill_repertoire_size`; correcting together avoids under-correction

---

## Output files

- `results_continuous.csv`: Table A, both levels (rq, feature, outcome, method, N, stat, ci_lo, ci_hi, test_stat, df_val, p, p_fdr, level)
- `results_binary.csv`: Table B, both levels (rq, feature, outcome, n_pos, median_pos, q1_pos, q3_pos, n_neg, median_neg, q1_neg, q3_neg, U, r_rb, ci_lo, ci_hi, p, p_fdr, level)

---

## LaTeX tables

`results_to_latex.py` reads the two CSVs and writes the formatted tables to the manuscript:

```
python correlation_analysis/results_to_latex.py
```

Both tables (Spearman and Mann-Whitney) are combined into a single `table*` float with two side-by-side `minipage` environments, written to `manuscript/correlation/tab_correlation_analysis.tex`. The manuscript includes it via `\input{correlation/tab_correlation_analysis}`.

---

## Markdown tables

`results_to_markdown.py` reads the same two CSVs and writes both tables to [`results.md`](results.md):

```
python correlation_analysis/results_to_markdown.py
```

Significant entries (FDR-corrected p < 0.05) are **bold** with a `\*` marker. The output is intended for browsing on GitHub.
