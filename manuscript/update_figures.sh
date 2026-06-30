#!/usr/bin/env bash
# Copy generated figures from figures/ into the manuscript Fig*.pdf slots.
# Run from grasp_survey_scripts/manuscript/ or pass the manuscript directory as $1.
#
# Mapping (source → target):
#   figures/robotic_hands_plot_only.pdf          → Fig8a.pdf
#   figures/robotic_hands_legend.pdf             → Fig8b.pdf
#   figures/hands_prosthetic_plot_only.pdf       → Fig8c.pdf
#   figures/hands_prosthetic_legend.pdf          → Fig8d.pdf
#   figures/hand_features.pdf                    → Fig13.pdf
#   figures/skill_repertoire.pdf                 → Fig14.pdf
#   figures/num_actuators_vs_in_hand_dof_extreme_cases.pdf → Fig15.pdf
#   figures/Skills_plot_only.pdf                 → FigA1a.pdf
#   figures/Skills_legend.pdf                    → FigA1b.pdf

set -euo pipefail

DIR="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
SRC="$DIR/figures"

copy() {
    local src="$SRC/$1" dst="$DIR/$2"
    if [ ! -f "$src" ]; then
        echo "SKIP  $1 (not found)" >&2
        return
    fi
    cp "$src" "$dst"
    echo "OK    $1 → $2"
}

copy robotic_hands_plot_only.pdf          Fig8a.pdf
copy robotic_hands_legend.pdf             Fig8b.pdf
copy hands_prosthetic_plot_only.pdf       Fig8c.pdf
copy hands_prosthetic_legend.pdf          Fig8d.pdf
copy hand_features.pdf                    Fig13.pdf
copy skill_repertoire.pdf                 Fig14.pdf
copy num_actuators_vs_in_hand_dof_extreme_cases.pdf Fig15.pdf
copy Skills_plot_only.pdf                 FigA1a.pdf
copy Skills_legend.pdf                    FigA1b.pdf
