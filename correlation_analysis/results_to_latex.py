"""Read results_continuous.csv and results_binary.csv, write LaTeX tables to the
manuscript's correlation/ subdirectory, and print the paths to stdout.

Run from any directory:
    python grasp_survey_scripts/correlation_analysis/results_to_latex.py
"""
import os

import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
_MANUSCRIPT_CORR_DIR = os.path.join(_DIR, "..", "manuscript", "correlation")

# ── Helpers ───────────────────────────────────────────────────────────────────

_OUTCOME_ABBREV = {
    "in-hand DoF (cat.14 Motion@Contact)":    "Motion DoF",
    "in-hand DoF (cat.15 No-Motion@Contact)": "No-Motion DoF",
    "skill_repertoire_size":                  r"Skill rep.\ size",
}

_FEATURE_ABBREV = {
    "Num. of Fingers":       r"\# Fingers",
    "DoF":                   "DoF",
    "Num. Actuators":        r"\# Actuators",
    "num_sensors":           r"\# Sensors",
    "Abduction / Adduction": "Abd./Add.",
    "Tactile Feedback":      "Tactile",
    "Kinesthetic Feedback":  "Kinesthetic",
}


def _esc(s):
    return str(s).replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def _stat_cell(r):
    stat_s = f"${r['stat']:+.3f}$"
    ci_s   = f"$[{r['ci_lo']:+.2f},\\,{r['ci_hi']:+.2f}]$"
    return stat_s, ci_s


def _pval_cell(p_fdr):
    s = f"{p_fdr:.3f}" if p_fdr >= 0.001 else r"$<$0.001"
    if p_fdr < 0.05:
        s = rf"\textbf{{{s}}}$^*$"
    return s


def _median_iqr(r, group):
    med = r[f"median_{group}"]
    q1  = r[f"q1_{group}"]
    q3  = r[f"q3_{group}"]
    return rf"${med:.1f}\,({q1:.1f}\text{{--}}{q3:.1f})$"


def _rbs_cell(r):
    rbs_s = f"${r['r_rb']:+.3f}$"
    ci_s  = f"$[{r['ci_lo']:+.2f},\\,{r['ci_hi']:+.2f}]$"
    return rbs_s, ci_s


# ── Table A (inner) ───────────────────────────────────────────────────────────

def _make_table_a_inner(cont: pd.DataFrame) -> list:
    pp = cont[cont["level"] == "per_paper"].reset_index(drop=True)
    ph = cont[cont["level"] == "per_hand"].reset_index(drop=True)
    assert len(pp) == len(ph), "per-paper and per-hand row counts differ"

    dof_rows = pp[pp["outcome"].str.contains("in-hand DoF", na=False)].index.tolist()
    rep_rows = pp[pp["outcome"] == "skill_repertoire_size"].index.tolist()

    lines = []
    lines.append(r"\centering")
    lines.append(
        r"\caption{Spearman $\rho$ for mechanism and sensor features vs.\ "
        r"in-hand manipulation DoF and skill repertoire size. "
        r"Level: PP\,=\,per-paper-hand ($N_\text{PP}$), PH\,=\,per-hand ($N_\text{PH}$). "
        r"$p^*$: FDR-corrected $p$-value (Benjamini--Hochberg, $\alpha=0.05$); "
        r"bold and starred entries are significant.}"
    )
    lines.append(r"\label{tab:correlation_analysis}")
    lines.append(r"\begin{tabular}{@{}lllcccc@{}}")
    lines.append(r"\toprule")
    lines.append(
        r"RQ & Feature & Lvl & $N$ & $\rho$ & 95\,\% CI & $p^*$ \\"
    )

    def _emit_pair(r_pp, r_ph, feat):
        stat_pp, ci_pp = _stat_cell(r_pp)
        stat_ph, ci_ph = _stat_cell(r_ph)
        lines.append(
            f"{r_pp['rq']} & {feat}"
            f" & PP & {int(r_pp['N'])} & {stat_pp} & {ci_pp} & {_pval_cell(r_pp['p_fdr'])} \\\\"
        )
        lines.append(
            f" & & PH & {int(r_ph['N'])} & {stat_ph} & {ci_ph}"
            f" & {_pval_cell(r_ph['p_fdr'])} \\\\[2pt]"
        )

    def _emit_dof_rows(idx_list):
        outcomes_order = list(dict.fromkeys(pp.iloc[idx]["outcome"] for idx in idx_list))
        for outcome_val in outcomes_order:
            out_label = _OUTCOME_ABBREV.get(outcome_val, _esc(outcome_val))
            lines.append(
                rf"\multicolumn{{7}}{{@{{}}l}}{{\quad\textit{{{out_label}}}}} \\[1pt]"
            )
            for idx in idx_list:
                r_pp = pp.iloc[idx]
                if r_pp["outcome"] != outcome_val:
                    continue
                feat = _FEATURE_ABBREV.get(r_pp["feature"], _esc(r_pp["feature"]))
                _emit_pair(r_pp, ph.iloc[idx], feat)

    def _emit_rows(idx_list):
        for idx in idx_list:
            r_pp = pp.iloc[idx]
            feat = _FEATURE_ABBREV.get(r_pp["feature"], _esc(r_pp["feature"]))
            _emit_pair(r_pp, ph.iloc[idx], feat)

    if dof_rows:
        lines.append(r"\midrule")
        lines.append(
            r"\multicolumn{7}{@{}l}{\textit{Mechanism features vs.\ in-hand DoF}} \\[2pt]"
        )
        _emit_dof_rows(dof_rows)

    if rep_rows:
        lines.append(r"\midrule")
        lines.append(
            r"\multicolumn{7}{@{}l}{\textit{Features vs.\ skill repertoire size}} \\[2pt]"
        )
        _emit_rows(rep_rows)

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    return lines


# ── Table B (inner) ───────────────────────────────────────────────────────────

def _make_table_b_inner(binn: pd.DataFrame) -> list:
    pp = binn[binn["level"] == "per_paper"].reset_index(drop=True)
    ph = binn[binn["level"] == "per_hand"].reset_index(drop=True)
    assert len(pp) == len(ph)

    lines = []
    lines.append(r"\centering")
    lines.append(
        r"\caption{Mann--Whitney $U$ test: binary hand features vs.\ outcome variables. "
        r"$r_\text{rb}$: rank-biserial correlation (effect size). "
        r"Level: PP\,=\,per-paper-hand ($N^+_\text{PP}$), PH\,=\,per-hand ($N^+_\text{PH}$). "
        r"$p^*$: FDR-corrected $p$-value (Benjamini--Hochberg, $\alpha=0.05$); "
        r"bold and starred entries are significant.}"
    )
    lines.append(r"\label{tab:mannwhitney}")
    lines.append(r"\begin{tabular}{@{}lllccc@{}}")
    lines.append(r"\toprule")
    lines.append(
        r"RQ & Feature & Lvl & $N^+$ & $r_\text{rb}$ [95\,\% CI] & $p^*$ \\"
    )

    outcomes_order = list(dict.fromkeys(pp["outcome"].tolist()))
    for outcome_val in outcomes_order:
        mask = pp["outcome"] == outcome_val
        out_label = _OUTCOME_ABBREV.get(outcome_val, _esc(outcome_val))
        lines.append(r"\midrule")
        lines.append(
            rf"\multicolumn{{6}}{{@{{}}l}}{{\textit{{Binary features vs.\ {out_label}}}}} \\[2pt]"
        )
        for i in pp[mask].index:
            r_pp = pp.iloc[i]
            r_ph = ph.iloc[i]
            feat = _FEATURE_ABBREV.get(r_pp["feature"], _esc(r_pp["feature"]))
            rbs_pp, ci_pp = _rbs_cell(r_pp)
            rbs_ph, ci_ph = _rbs_cell(r_ph)
            lines.append(
                f"{r_pp['rq']} & {feat}"
                f" & PP & {int(r_pp['n_pos'])} & {rbs_pp} {ci_pp} & {_pval_cell(r_pp['p_fdr'])} \\\\"
            )
            lines.append(
                f" & & PH & {int(r_ph['n_pos'])} & {rbs_ph} {ci_ph}"
                f" & {_pval_cell(r_ph['p_fdr'])} \\\\[2pt]"
            )

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    return lines


# ── Combined table ────────────────────────────────────────────────────────────

def make_combined_table(cont: pd.DataFrame, binn: pd.DataFrame) -> str:
    """Return a table* with Table A and Table B placed side by side.

    Uses minipage + \\captionof so each sub-table gets its own sequential
    table number rather than shared (a)/(b) sub-labels from subtable.
    """
    inner_a = _make_table_a_inner(cont)
    inner_b = _make_table_b_inner(binn)

    # Replace \caption with \captionof{table} so the captions work inside
    # a minipage (which is not itself a float environment).
    def _patch(lines):
        return [
            l.replace(r"\caption{", r"\captionof{table}{", 1) for l in lines
        ]

    lines = []
    lines.append(r"\begin{table*}[!t]")
    lines.append(r"\footnotesize")
    lines.append(r"\setlength{\tabcolsep}{3pt}")
    lines.append(r"\renewcommand{\arraystretch}{1.2}")
    lines.append(r"\begin{minipage}[t]{\columnwidth}")
    lines.extend(_patch(inner_a))
    lines.append(r"\end{minipage}\hfill")
    lines.append(r"\begin{minipage}[t]{\columnwidth}")
    lines.extend(_patch(inner_b))
    lines.append(r"\end{minipage}")
    lines.append(r"\end{table*}")
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    cont = pd.read_csv(os.path.join(_DIR, "results_continuous.csv"))
    binn = pd.read_csv(os.path.join(_DIR, "results_binary.csv"))

    out_a = os.path.join(_MANUSCRIPT_CORR_DIR, "tab_correlation_analysis.tex")

    with open(out_a, "w") as f:
        f.write(make_combined_table(cont, binn) + "\n")

    print(f"Wrote {out_a}")


if __name__ == "__main__":
    main()
