"""Script for generating raindrops.gif"""

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.animation import FuncAnimation
from matplotlib import animation

# Fixing random state for reproducibility
np.random.seed(19680801)

# Get the "spring" color map
spring_cmap = plt.get_cmap("spring")

# Create new Figure and an Axes which fills it.
fig = plt.figure(figsize=(18, 6))
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
ax.set_xlim(0, 1), ax.set_xticks([])
ax.set_ylim(0, 1), ax.set_yticks([])

# Create rain data
n_drops = 50
rain_drops = np.zeros(n_drops, dtype=[('position', float, (2,)),
                                      ('size',     float),
                                      ('growth',   float),
                                      ('color',    float, (4,))])

# initialize the raindrop colors
raindrop_colors = []
random_indices = np.random.randint(0, 256, n_drops)  # 256 is the number of colors in the "spring" colormap
for index in random_indices:
    color = spring_cmap(index / 255)  # Normalize the index to [0, 1]
    raindrop_colors.append(color)
    
rain_drops['color'] = raindrop_colors

# Initialize the raindrops in random positions and with
# random growth rates.
rain_drops['position'] = np.random.uniform(0, 1, (n_drops, 2))
rain_drops['growth'] = np.random.uniform(50, 200, n_drops)

# Construct the scatter which we will update during animation
# as the raindrops develop.
scat = ax.scatter(
    rain_drops['position'][:, 0], 
    rain_drops['position'][:, 1],
    s=rain_drops['size'], 
    lw=0.5, 
    edgecolors=rain_drops['color'],
    facecolors='none'
    )


def update(frame_number):
    # Get an index which we can use to re-spawn the oldest raindrop.
    current_index = frame_number % n_drops

    # Make all colors more transparent as time progresses.
    rain_drops['color'][:, 3] -= 1.0/len(rain_drops)
    rain_drops['color'][:, 3] = np.clip(rain_drops['color'][:, 3], 0, 1)

    # Make all circles bigger.
    rain_drops['size'] += rain_drops['growth']

    # Pick a new position for oldest rain drop, resetting its size,
    # color and growth factor.
    rain_drops['position'][current_index] = np.random.uniform(0, 1, 2)
    rain_drops['size'][current_index] = 5
    rain_drops['color'][current_index,3] = 1 # reset alpha channel to 1
    rain_drops['growth'][current_index] = np.random.uniform(50, 200)

    # Update the scatter collection, with the new colors, sizes and positions.
    scat.set_edgecolors(rain_drops['color'])
    scat.set_sizes(rain_drops['size'])
    scat.set_offsets(rain_drops['position'])


# Construct the animation, using the update function as the animation director.
ani = FuncAnimation(fig, update, interval=10, save_count=100)
plt.show()
