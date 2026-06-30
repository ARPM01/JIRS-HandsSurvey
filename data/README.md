# Data

This folder contains the primary dataset for the systematic review.

## Files

| File | Description |
|------|-------------|
| `included articles.xlsx` | Primary spreadsheet used for data entry during the review |
| `Robotic_hands_Included_articles.csv` | Export of the `Included articles (analysis)` sheet; read by all analysis scripts |

### Generated Markdown tables

Exported from `included articles.xlsx` by `excel_to_markdown.py`:

| File | Source sheet |
|------|-------------|
| [Robotic_hands.md](Robotic_hands.md) | `Robotic Hands` — catalog of commercial and research hands |
| [Included_articles.md](Included_articles.md) | `Included articles (analysis)` — per-paper annotation data |

---

## Scripts

### `excel_to_csv.py`

Exports the `Included articles (analysis)` sheet from `included articles.xlsx` to
`Robotic_hands_Included_articles.csv`. Uses cached formula results (`data_only=True`);
if any formula cells appear blank, open and re-save the workbook in Excel first.

```
python data/excel_to_csv.py
```

### `excel_to_markdown.py`

Exports the `Robotic Hands`, `Included articles (analysis)`, and `Drop Down Menu`
sheets from `included articles.xlsx` to Markdown tables in this folder.

```
python data/excel_to_markdown.py
```

---

## Table format (`Robotic_hands_Included_articles.csv`)

One row per included paper. A single hand may appear in multiple rows if it was
used in multiple papers; results are aggregated per hand during analysis (logical
OR across papers for skill columns).

### Bibliographic columns

| Column | Type | Description |
|--------|------|-------------|
| `Papers` | string | Full paper title |
| `Link` | string | URL to the paper |
| `HandName` | string | Canonical hand name (see `load_hands.py` for normalisation rules) |

### Mechanism feature columns

| Column | Type | Values | Description |
|--------|------|--------|-------------|
| `Num. of Fingers` | integer | 1 – 6 (">5" normalised to 6) | Number of fingers |
| `DoF` | integer | ≥ 1 | Total degrees of freedom |
| `Num. Actuators` | integer | ≥ 1 | Number of actuators |
| `Palm (used or not)` | boolean | Yes / No | Whether the palm is used as a contact surface |
| `Reposition / Opposition` | categorical | Yes / No / Switching / Neither of the two / Opposition / Reposition | Thumb reposition/opposition capability; normalised to boolean in `load_hands.py` (True = at least one mode available) |
| `Abduction / Adduction` | categorical | Yes / No / Switching / Neither of the two / Abduction / Adduction | Finger abduction/adduction capability; normalised to boolean |
| `Flexion/Extension` | categorical | Yes / No / Switching / Neither of the two / Flexion | Finger flexion/extension capability; normalised to boolean |

### Sensor feature columns

| Column | Type | Values | Description |
|--------|------|--------|-------------|
| `Tactile Feedback` | boolean | Yes / No | Tactile sensors used |
| `Kinesthetic Feedback` | boolean | Yes / No | Kinesthetic / proprioceptive sensors used |
| `Visual Feedback` | boolean | Yes / No | Visual feedback used |

### Skill columns (categories 1–15)

One boolean column per Dollar (2014) taxonomy category. Column names encode the
full taxonomy path followed by a colon and the representative skill name, e.g.:

```
Contact -> Prehensile -> Motion -> Within Hand -> Motion at Contact: Reorienting pen
```

| Value | Meaning |
|-------|---------|
| `Yes` / `True` | Skill demonstrated in the paper, or mechanical inference grants credit |
| `No` / `False` | Skill not demonstrated and mechanical requirements not met |

### In-hand manipulation DoF columns

Two additional numeric columns record the number of object DoF controlled during
in-hand manipulation, one for each in-hand category:

| Column | Description |
|--------|-------------|
| `Contact -> Prehensile -> Motion -> Within Hand -> No Motion at Contact: DoF` | Object DoF for cat. 14 (writing-type) |
| `Contact -> Prehensile -> Motion -> Within Hand -> Motion at Contact: DoF` | Object DoF for cat. 15 (reorientation-type) |

A value of `-` (missing) means the skill was not demonstrated in that paper.

### Comments column

Free-text field used during annotation to flag unusual cases, ambiguities, or
notes for co-author review. Dropped during loading (`load_hands.py`).
