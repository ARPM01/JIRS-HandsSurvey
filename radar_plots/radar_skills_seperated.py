import os
from collections import OrderedDict
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt

_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manuscript", "figures")
os.makedirs(_OUT, exist_ok=True)

titles = ['Min. Number of Fingers', 'Min. DoF', 'Mechanism', 'Reposition/Opposition', 'Abduction/Adduction', 'Flexion/Extension']

skills = OrderedDict({
    "Open handed holding":         [0.01, 0.0, 1.01, -0.99, -0.99, -0.99],
    "Pointing / pushing":          [1.02, 0.1, 1.02, 0.02, 0.02, 0.02],
    "Scratching":                  [1.03, 1.0, 1.03, 0.04, 0.04, 1.04],
    "Grasping / holding":          [2.04, 1.1, 1.04, 0.06, 0.06, 1.06],
    "Flipping a page":             [2.05, 2.1, 2.05, 1.05, 0.05, 1.05],
    "Gesture: thumb up":           [2.06, 2.2, 2.06, 1.06, 0.06, 1.06],
    "Handwriting":                 [3.07, 4.0, 2.07, 1.07, 0.07, 1.07],
    "Tool use: screw driver":      [4, 6.0, 2.08, 1.08, 1.08, 1.08],
    "Gesture: sign language":      [5, 6.1, 2.09, 1.09, 0.09, 1.09],
    "Button up":                   [5.1, 7, 3.1, 1.1, 0.1, 1.1],
    "Fine motor skill: false cut": [8, 22, 3, 1, 1, 1],
    #"Lateral motion": [1, 1, 0, 0, 0, 0],
    #"Pressure": [1, 0, 0, 0, 0, 0],
    #"Static contact": [1, 0, 0, 0, 0, 0],
    #"Enclosure": [1, 1, 1, 0, 0, 1],
    #"Contour following": [1, 1, 0, 0, 0, 1],
    #"Function test": [1, 1, 0, 0, 0, 1],
    #"Part motion test": [1, 1, 0, 0, 0, 1],
})
skill_names = list(skills.keys())
data = list(skills.values())

# get 9 colors for each company that are far from each other
color_maps = ['tab10', 'tab20', 'Set1', 'Set2', 'Set3', 'Paired', 'Pastel1', 'Pastel2', 'Pastel3']
def get_colors_from_cmap(cmap_name, n):
    cmap = pl.get_cmap(cmap_name)
    colors = [cmap(i) for i in range(0, cmap.N, cmap.N // n)]
    return colors

# Number of colors you want
num_colors = 9

# Get a list of colors from one of the color maps
colors = get_colors_from_cmap(color_maps[1], num_colors)



colors_list=[colors[0],colors[0],colors[1],colors[1],colors[2],colors[2],colors[3],colors[3],colors[4],colors[4],colors[5],colors[5],colors[6],colors[6],colors[7],colors[7],colors[8],colors[8],colors[9],colors[9]]
lines=['-', '--', '-.', ':', '',]
lines_list=[lines[0],lines[1],lines[0],lines[1],lines[0],lines[1],lines[0],lines[1],lines[0],lines[1],lines[0],lines[1],lines[0],lines[1],lines[0],lines[1],lines[0],lines[1],lines[0],lines[1]]



labels_ticks=[list(range(0,9,2))[-5:],list(range(2,9,2)) + ["More"],[" ","Any","Hand","Two Hands", ""],[" ","No"," ","Yes"," "],[" ","No"," ","Yes"," "],[" ","No"," ","Yes"," "]]

class Radar(object):

    def __init__(self, fig, titles, labels, rect=None):
        if rect is None:
            rect = [0.05, 0.05, 0.95, 0.95]

        self.n = len(titles)
        self.angles = [a if a <=360. else a - 360. for a in np.arange(90, 90+360, 360.0/self.n)]
        self.axes = [fig.add_axes(rect, projection="polar", label="axes%d" % i) 
                        for i in range(self.n)]

        self.ax = self.axes[0]
        self.ax.set_thetagrids(self.angles, labels=titles, fontsize=16, weight="bold", color="black")
        # Move the theta labels outward
        for label in self.ax.get_xticklabels():
            label.set_verticalalignment('center')
            if label.get_text() in ['Min. DoF', 'Flexion']:
                label.set_y(label.get_position()[1] - 0.15) 
            else:
                label.set_y(label.get_position()[1] - 0.05)

        for ax in self.axes[1:]:
            ax.patch.set_visible(False)
            ax.grid("off")
            ax.xaxis.set_visible(False)
            self.ax.yaxis.grid(False)

        for ax, angle, label in zip(self.axes, self.angles, labels):
            ax.set_rgrids(range(1, len(label)+1), labels=label, angle=angle, fontsize=16)
            ax.spines["polar"].set_visible(False)
            ax.set_ylim(0, len(label))  
            ax.xaxis.grid(True,color='black',linestyle='-')

    def plot(self, values, *args, **kw):
        angle = np.deg2rad(np.r_[self.angles, self.angles[0]])
        values = np.r_[values, values[0]]
        self.ax.plot(angle, values, *args, **kw)

fig = pl.figure(figsize=(20, 20))



radar = Radar(fig, titles, labels_ticks)
# first , second / 2, third + 1, last three variables: *2+2
#adjust data to fit the y_ticks
data = np.array(data, dtype=float)
data[:,0] = data[:,0] / 2 + 1
data[:,1] = np.clip(data[:,1], 0, 10) / 2 + 0
data[:,2] = data[:,2] + 1
data[:,3] = data[:,3] * 2 + 2
data[:,4] = data[:,4] * 2 + 2
data[:,5] = data[:,5] * 2 + 2


for i in range(len(data)):
    radar.plot(data[i], lines_list[i], lw=2, color=colors_list[i], label=skill_names[i])

fig.set_size_inches(6, 10, forward=True)

# Save the main plot without the legend
fig.savefig(os.path.join(_OUT, 'Skills_plot_only.png'), dpi=300, bbox_inches="tight")
fig.savefig(os.path.join(_OUT, 'Skills_plot_only.pdf'), dpi=300, bbox_inches="tight")
fig.savefig(os.path.join(_OUT, 'Skills_plot_only.eps'), dpi=300, bbox_inches="tight")

# Create a separate figure for the legend
from matplotlib.legend import Legend

legend_fig = plt.figure(figsize=(6, 2))
legend_ax = legend_fig.add_subplot(111)
legend_ax.axis('off')

# Create a dummy plot to get the handles and labels
handles, labels = radar.ax.get_legend_handles_labels()


legend = legend_ax.legend(
    handles, labels,
    loc='center',
    ncol=2,
    fontsize=16,
    frameon=True,           # Show the frame (box)
    fancybox=False,         # Square corners
    shadow=False,           # No shadow
    edgecolor='black',      # Black border
)

legend.get_frame().set_edgecolor('black')
legend.get_frame().set_linewidth(2)

legend_fig.savefig(os.path.join(_OUT, 'Skills_legend.png'), dpi=300, bbox_inches="tight", pad_inches=0)
legend_fig.savefig(os.path.join(_OUT, 'Skills_legend.pdf'), dpi=300, bbox_inches="tight", pad_inches=0)
legend_fig.savefig(os.path.join(_OUT, 'Skills_legend.eps'), dpi=300, bbox_inches="tight", pad_inches=0)