#!/usr/bin/env bash
# Run all analysis scripts in dependency order.
# Execute from the grasp_survey_scripts/ directory:
#   bash run_all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

run() {
    echo "── $*"
    python "$@"
}

echo "=== Data export ==="
run data/excel_to_csv.py
run data/excel_to_markdown.py

echo ""
echo "=== Correlation analysis (RQ1–RQ5) ==="
run correlation_analysis/compute_all_tests.py
run correlation_analysis/results_to_latex.py
run correlation_analysis/results_to_markdown.py
run correlation_analysis/plot_correlation_skill_repertoire.py
run correlation_analysis/plot_extreme_cases_num_actuators.py

echo ""
echo "=== Descriptive plots ==="
run descriptive/plot_hand_feature_histogram.py
run descriptive/plot_percentage_histogram.py

echo ""
echo "=== Radar plots ==="
run radar_plots/radar_robotic_seperated.py
run radar_plots/radar_prosthetic_seperated.py
run radar_plots/radar_skills_seperated.py

echo ""
echo "=== Update manuscript figures ==="
echo "── manuscript/update_figures.sh"
bash manuscript/update_figures.sh

echo ""
echo "Done."
