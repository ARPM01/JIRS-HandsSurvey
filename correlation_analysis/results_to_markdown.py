"""Read results_continuous.csv and results_binary.csv, write Markdown tables to
correlation_analysis/results.md.

Sister script to results_to_latex.py — same structure, plain-text formatting.

Run from any directory:
    python grasp_survey_scripts/correlation_analysis/results_to_markdown.py
"""
import os

import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
_OUT = os.path.join(_DIR, "results.md")

# ── Helpers ───────────────────────────────────────────────────────────────────

_OUTCOME_ABBREV = {
    "in-hand DoF (cat.14 Motion@Contact)":    "Motion DoF",
    "in-hand DoF (cat.15 No-Motion@Contact)": "No-Motion DoF",
    "skill_repertoire_size":                  "Skill rep. size",
}

_FEATURE_ABBREV = {
    "Num. of Fingers":       "# Fingers",
    "DoF":                   "DoF",
    "Num. Actuators":        "# Actuators",
    "num_sensors":           "# Sensors",
    "Abduction / Adduction": "Abd./Add.",
    "Tactile Feedback":      "Tactile",
    "Kinesthetic Feedback":  "Kinesthetic",
}


def _feat(name: str) -> str:
    return _FEATURE_ABBREV.get(name, name)


def _stat_cell(r) -> tuple[str, str]:
    return f"${r['stat']:+.3f}$", f"$[{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}]$"


def _pval_cell(p_fdr: float) -> str:
    s = f"${p_fdr:.3f}$" if p_fdr >= 0.001 else "$<0.001$"
    return f"**{s}**\\*" if p_fdr < 0.05 else s


def _rbs_cell(r) -> tuple[str, str]:
    return f"${r['r_rb']:+.3f}$", f"$[{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}]$"


def _md_row(*cells) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def _md_sep(*cols) -> str:
    return "| " + " | ".join("---" for _ in cols) + " |"


# ── Table A ───────────────────────────────────────────────────────────────────

def make_table_a(cont: pd.DataFrame) -> str:
    pp = cont[cont["level"] == "per_paper"].reset_index(drop=True)
    ph = cont[cont["level"] == "per_hand"].reset_index(drop=True)
    assert len(pp) == len(ph), "per-paper and per-hand row counts differ"

    dof_rows = pp[pp["outcome"].str.contains("in-hand DoF", na=False)].index.tolist()
    rep_rows = pp[pp["outcome"] == "skill_repertoire_size"].index.tolist()

    lines = [
        "## Spearman ρ — mechanism and sensor features vs. in-hand manipulation DoF "
        "and skill repertoire size",
        "",
        "PP = per-paper-hand, PH = per-hand. "
        "$p^*$ = FDR-corrected $p$-value (Benjamini–Hochberg, $\\alpha = 0.05$); "
        "**bold** entries with \\* are significant.",
        "",
        _md_row("RQ", "Feature", "Lvl", "$N$", "$\\rho$", "95% CI", "$p^*$"),
        _md_sep(*range(7)),
    ]

    def _emit_pair(r_pp, r_ph, feat):
        stat_pp, ci_pp = _stat_cell(r_pp)
        stat_ph, ci_ph = _stat_cell(r_ph)
        lines.append(_md_row(r_pp["rq"], feat, "PP", int(r_pp["N"]),
                             stat_pp, ci_pp, _pval_cell(r_pp["p_fdr"])))
        lines.append(_md_row("", "", "PH", int(r_ph["N"]),
                             stat_ph, ci_ph, _pval_cell(r_ph["p_fdr"])))

    def _emit_dof_rows(idx_list):
        outcomes_order = list(dict.fromkeys(pp.iloc[i]["outcome"] for i in idx_list))
        for outcome_val in outcomes_order:
            label = _OUTCOME_ABBREV.get(outcome_val, outcome_val)
            lines.append(_md_row(f"*Mechanism features vs. {label}*",
                                 "", "", "", "", "", ""))
            for i in idx_list:
                r_pp = pp.iloc[i]
                if r_pp["outcome"] != outcome_val:
                    continue
                _emit_pair(r_pp, ph.iloc[i], _feat(r_pp["feature"]))

    def _emit_rows(idx_list):
        for i in idx_list:
            r_pp = pp.iloc[i]
            _emit_pair(r_pp, ph.iloc[i], _feat(r_pp["feature"]))

    if dof_rows:
        _emit_dof_rows(dof_rows)
    if rep_rows:
        lines.append(_md_row("*Features vs. skill repertoire size*",
                             "", "", "", "", "", ""))
        _emit_rows(rep_rows)

    return "\n".join(lines)


# ── Table B ───────────────────────────────────────────────────────────────────

def make_table_b(binn: pd.DataFrame) -> str:
    pp = binn[binn["level"] == "per_paper"].reset_index(drop=True)
    ph = binn[binn["level"] == "per_hand"].reset_index(drop=True)
    assert len(pp) == len(ph)

    lines = [
        "## Mann–Whitney U — binary hand features vs. outcome variables",
        "",
        "$r_\\text{rb}$ = rank-biserial correlation (effect size). "
        "PP = per-paper-hand, PH = per-hand. "
        "$p^*$ = FDR-corrected $p$-value (Benjamini–Hochberg, $\\alpha = 0.05$); "
        "**bold** entries with \\* are significant.",
        "",
        _md_row("RQ", "Feature", "Lvl", "$N^+$", "$r_\\text{rb}$ [95% CI]", "$p^*$"),
        _md_sep(*range(6)),
    ]

    for outcome_val in list(dict.fromkeys(pp["outcome"].tolist())):
        mask = pp["outcome"] == outcome_val
        label = _OUTCOME_ABBREV.get(outcome_val, outcome_val)
        lines.append(_md_row(f"*Binary features vs. {label}*",
                             "", "", "", "", ""))
        for i in pp[mask].index:
            r_pp, r_ph = pp.iloc[i], ph.iloc[i]
            feat = _feat(r_pp["feature"])
            rbs_pp, ci_pp = _rbs_cell(r_pp)
            rbs_ph, ci_ph = _rbs_cell(r_ph)
            lines.append(_md_row(r_pp["rq"], feat, "PP", int(r_pp["n_pos"]),
                                 f"{rbs_pp} {ci_pp}", _pval_cell(r_pp["p_fdr"])))
            lines.append(_md_row("", "", "PH", int(r_ph["n_pos"]),
                                 f"{rbs_ph} {ci_ph}", _pval_cell(r_ph["p_fdr"])))

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    cont = pd.read_csv(os.path.join(_DIR, "results_continuous.csv"))
    binn = pd.read_csv(os.path.join(_DIR, "results_binary.csv"))

    table_a = make_table_a(cont)
    table_b = make_table_b(binn)

    with open(_OUT, "w") as f:
        f.write("# Correlation analysis results\n\n")
        f.write(table_a + "\n\n")
        f.write(table_b + "\n")

    print(f"Wrote {_OUT}")


if __name__ == "__main__":
    main()
