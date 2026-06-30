# Radar Plots

Radar (spider) charts comparing hand mechanisms across six axes:
Number of Fingers, DoF, Controlled DoF, Reposition/Opposition,
Abduction/Adduction, and Flexion/Extension.

Each script saves two output files: a plot without a legend and a
separate legend figure, both in PNG, PDF, and EPS formats.

## Scripts

### radar_robotic_seperated.py

Plots 14 commercial and research robotic hands:
Robotiq 2F/3F, RH-P12-RN, GRIPKIT variants, BarrettHand, SVH, RH8D,
Allegro Hand, Shadow Dexterous Hand (4 variants), IH2 Azzurra.

Output: `robotic_hands_plot_only.{png,pdf,eps}`,
`robotic_hands_legend.{png,pdf,eps}`

### radar_prosthetic_seperated.py

Plots 9 commercial prosthetic hands:
Mia Hand, Steeper Myo Kinisi, SensorHand Speed, Ottobock BeBionic,
Ossur iLimb, Psyonic Ability Hand, Vincent Hand, Covvi Nexus Hand,
Taska Hand.

Output: `hands_prosthetic_plot_only.{png,pdf,eps}`,
`hands_prosthetic_legend.{png,pdf,eps}`

### radar_skills_seperated.py

Plots the minimum hand requirements for 11 manipulation skills, from
open-handed holding up to fine motor skills (false cut). The axes show
minimum fingers, minimum DoF, required mechanism complexity, and
required joint types.

Output: `Skills_plot_only.{png,pdf,eps}`,
`Skills_legend.{png,pdf,eps}`

## Setup

```
pip install numpy matplotlib
```

## Usage

Run each script from within the `radar_plots/` directory so that
output files are written to the correct location:

```
cd radar_plots
python radar_robotic_seperated.py
python radar_prosthetic_seperated.py
python radar_skills_seperated.py
```
