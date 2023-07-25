import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.axes_grid1.inset_locator import mark_inset, zoomed_inset_axes

from params import rocket_height, rocket_width

def rocket_trajectory(height, width, theta):
    # Generate rocket trajectory points
    t = np.linspace(0, 10, 100)  # Time steps
    x = t * np.cos(theta)  # X positions
    y = height * np.sin(t)  # Y positions

    return x, y

def anchor_point(x, y, theta):
    """ Given current position of center of mass and theta, returns anchor point for rectangle
    :param theta:
    """
    dx = (rocket_height * np.sin(theta) + rocket_width * np.cos(theta)) / 2
    dy = (rocket_height * np.cos(theta) - rocket_width * np.sin(theta)) / 2
    return (x - dx, y - dy)

def trans_angle(theta):
    """ Transforms theta from model convention to match matplotlib Rectangle convention"""
    return -theta * 180 / np.pi

def animate_rocket_trajectory(x, y, theta):
    """
    Animates rocket trajectory, writes animation to mp4 file
    :param x: iterable containing x points
    :param y: iterable containing y points
    :param theta: iterable containing theta values
    """

    # Add some extra frames on end of data
    extra_frames = 20
    params = [x, y, theta]
    for i, l in enumerate(params):
        dups = [l[-1] for f in range(extra_frames)]
        params[i] = np.append(l, dups)
    x, y, theta = params

    # Variables for scaling plot aspects
    max_x = max(x)
    max_y = max(y)
    fig, ax = plt.subplots()
    ax.set_xlim(min(x) - 10, max_x + 10)
    ax.set_ylim(0, max_y)

    rocket = plt.Rectangle(anchor_point(x[0], y[0], theta[0]), rocket_width, rocket_height, fc='r')  # Create the rocket rectangle
    ax.add_patch(rocket)

    # Create the zoomed-in inset axes
    axins = zoomed_inset_axes(ax, zoom=2.5, loc='upper left')
    axins.set_xlim(0, (1/7) * max_y)
    axins.set_ylim(0, (1/7) * max_y)
    axins.set_aspect('equal')

    # Add these lines to remove the labels on the inset axes
    axins.set_xticks([])
    axins.set_yticks([])

    # Plot the rocket in the inset axes
    rocket_inset = plt.Rectangle(anchor_point(x[0], y[0], theta[0]), rocket_width, rocket_height, fc='r')
    axins.add_patch(rocket_inset)

    # Mark the region of the zoomed-in inset in the main axes
    #mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")

    def update(frame):
        rocket.set_xy(anchor_point(x[frame], y[frame], theta[frame]))  # Update rocket position
        rocket.set_angle(trans_angle(theta[frame]))  # Set rocket orientation

        # Update the position of the rocket in the inset axes
        rocket_inset.set_xy(anchor_point(x[frame], y[frame], theta[frame]))
        rocket_inset.set_angle(trans_angle(theta[frame]))

        # Update the zoomed-in region based on the rocket's position
        x_center = x[frame]
        y_center = y[frame]
        axins.set_xlim(x_center - 30, x_center + 30)
        axins.set_ylim(y_center - 30, y_center + 30)

    ani = animation.FuncAnimation(fig, update, frames=len(x), interval=100)

    # Save the animation as a video file
    ani.save('rocket_trajectory.mp4', writer='ffmpeg')

# # Example usage
# height = 1.0
# width = 0.5
# theta = np.pi / 4  # 45 degrees
#
# animate_rocket_trajectory(height, width, theta)
