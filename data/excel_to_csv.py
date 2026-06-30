"""Export the 'Included articles (analysis)' sheet to Robotic_hands_Included_articles.csv.

Reads cached formula results (data_only=True); open and re-save the workbook in
Excel first if any formula cells appear blank in the output.

Run from grasp_survey_scripts/:
    python data/excel_to_csv.py
"""
import csv
import os

import openpyxl

_DIR = os.path.dirname(os.path.abspath(__file__))
_XLSX = os.path.join(_DIR, "included articles.xlsx")
_CSV = os.path.join(_DIR, "Robotic_hands_Included_articles.csv")
_SHEET = "Included articles (analysis)"

# Annotation-only columns not used by any analysis script.
_DROP_COLS = {
    "Comments", "Comments2",
    "Tactile Location", "Tactile Type", "Tactile Spatial Resolution",
    "Haptic in Skill?", "Proprio Angle", "Proprio Torque",
}


def main():
    wb = openpyxl.load_workbook(_XLSX, data_only=True)
    ws = wb[_SHEET]

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        print(f"Wrote {_CSV} (empty)")
        return

    header = rows[0]
    keep = [i for i, h in enumerate(header) if h not in _DROP_COLS]

    with open(_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in rows:
            if any(row[i] is not None for i in keep):
                writer.writerow(["" if row[i] is None else row[i] for i in keep])

    print(f"Wrote {_CSV}")


if __name__ == "__main__":
    main()
