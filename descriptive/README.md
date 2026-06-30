# Descriptive Analysis

Scripts that produce the descriptive plots used in the systematic review results section.
Both scripts read from `data/Robotic_hands_Included_articles.csv` via `load_hands.py` and
aggregate per hand (union across papers by hand name).

## Scripts

### plot_hand_feature_histogram.py

Plots histograms of hand characteristics across all hands in the dataset.
Five subplots show the distribution of:

- Number of actuation features (palm, reposition/opposition, abduction/adduction, flexion/extension)
- Number of sensor features (tactile, kinesthetic, visual feedback)
- Number of fingers
- Degrees of freedom (DoF)
- Number of actuators

Output: `hand_features.pdf`

### plot_percentage_histogram.py

Plots the fraction of hands that demonstrated each of four selected skill categories,
broken down by hand feature values. The four skill categories are:

- Pushing coin (non-prehensile, no motion at contact)
- Rolling ball on table (non-prehensile, motion at contact)
- Turning doorknob (prehensile, not within hand)
- Writing (prehensile, within hand)

Output: `skill_repertoire.pdf`

## Setup

```
pip install numpy pandas matplotlib seaborn
```

## Usage

Run from the `descriptive/` directory:

```
cd descriptive
python plot_hand_feature_histogram.py
python plot_percentage_histogram.py
```
