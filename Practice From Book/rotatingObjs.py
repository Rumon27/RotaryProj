import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button

def main():
    # --- Configuration ---
    initial_rpm = 15.0  # Initial Revolutions Per Minute
    radius = 1.0        # Orbit radius
    center_x, center_y = 0.0, 0.0

    # --- Setup Figure & Axes ---
    fig, ax = plt.subplots(figsize=(7, 7))
    plt.subplots_adjust(bottom=0.22)  # Space for the slider

    ax.set_xlim(-1.5 * radius, 1.5 * radius)
    ax.set_ylim(-1.5 * radius, 1.5 * radius)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_title("Rotating Point Around Fixed Center", fontsize=14, pad=15)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # --- Plot Static Elements ---
    circle = plt.Circle((center_x, center_y), radius, color='gray', linestyle=':', fill=False, alpha=0.7)
    ax.add_patch(circle)

    # Constant black point at center
    center_point, = ax.plot([center_x], [center_y], 'ko', markersize=10, label='Center (Constant)')

    # Rotating red point
    rotating_point, = ax.plot([center_x + radius], [center_y], 'ro', markersize=10, label='Rotating Point')

    # Line connecting center to rotating point
    arm_line, = ax.plot([center_x, center_x + radius], [center_y, 0], 'r--', alpha=0.5)

    ax.legend(loc='upper right')

    # Status text display
    info_text = ax.text(
        0.03, 0.95, '',
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )

    # --- RPM Slider & Reset Button ---
    ax_slider = plt.axes([0.15, 0.08, 0.7, 0.04])
    rpm_slider = Slider(
        ax=ax_slider,
        label='RPM: ',
        valmin=-60.0,
        valmax=60.0,
        valinit=initial_rpm,
        valstep=0.5
    )

    ax_button = plt.axes([0.8, 0.025, 0.1, 0.04])
    reset_button = Button(ax_button, 'Reset')

    def reset(event):
        rpm_slider.reset()

    reset_button.on_clicked(reset)

    # --- Animation State ---
    state = {
        'angle': 0.0,
        'last_time': time.perf_counter()
    }

    def update(frame):
        current_time = time.perf_counter()
        dt = current_time - state['last_time']
        state['last_time'] = current_time

        # Angular velocity: omega = (RPM * 2 * pi) / 60 rad/s
        rpm = rpm_slider.val
        omega = (rpm * 2.0 * np.pi) / 60.0

        # Increment angle smoothly using elapsed time
        state['angle'] = (state['angle'] + omega * dt) % (2.0 * np.pi)
        theta = state['angle']

        # Calculate new position of the red point
        x = center_x + radius * np.cos(theta)
        y = center_y + radius * np.sin(theta)

        # Update graphic elements
        rotating_point.set_data([x], [y])
        arm_line.set_data([center_x, x], [center_y, y])

        deg = np.degrees(theta)
        info_text.set_text(f"RPM: {rpm:.1f}\nAngle: {deg:.1f}°")

        return rotating_point, arm_line, info_text

    anim = FuncAnimation(fig, update, interval=16, blit=False, cache_frame_data=False)
    plt.show()

if __name__ == '__main__':
    main()