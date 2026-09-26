import sys
import numpy as np
import time

from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QBrush


# -----------------------------
# Configuration
# -----------------------------

points_data = [
    {"radius": 4.5, "rpm": 20, "angle0": 0},
    {"radius": 3.25, "rpm": 25, "angle0": 2},
    {"radius": 2, "rpm": 30, "angle0": 4},

    # These will appear after 5 seconds
    {"radius": 4, "rpm": 15, "angle0": 1},
    {"radius": 3, "rpm": 35, "angle0": 3},
    {"radius": 4.5, "rpm": 40, "angle0": 5},
]


# -----------------------------
# Figure / Scene
# -----------------------------

app = QApplication(sys.argv)

scene = QGraphicsScene()
view = QGraphicsView(scene)

view.setFixedSize(1000, 1000)

scale = 90

scene.setSceneRect(
    -5 * scale,
    -5 * scale,
    10 * scale,
    10 * scale
)


# -----------------------------
# Fixed black circle
# -----------------------------

black_size = 30

black_circle = QGraphicsEllipseItem(
    -black_size / 2,
    -black_size / 2,
    black_size,
    black_size
)

black_circle.setBrush(QBrush("black"))

scene.addItem(black_circle)

black_circle.setPos(0, 0)


# -----------------------------
# Create red circle
# -----------------------------

def create_point(data):

    radius = data["radius"]
    angle = data["angle0"]

    x = radius * np.cos(angle)
    y = radius * np.sin(angle)

    red_size = 30

    point = QGraphicsEllipseItem(
        -red_size / 2,
        -red_size / 2,
        red_size,
        red_size
    )

    point.setBrush(QBrush("red"))

    scene.addItem(point)

    point.setPos(
        x * scale,
        -y * scale
    )

    # Store the graphics object
    data["point"] = point


# -----------------------------
# Initially create 3 circles
# -----------------------------

for data in points_data[:3]:
     create_point(data)

# create_point(points_data[0])
# create_point(points_data[5])

# -----------------------------
# Animation timing
# -----------------------------

start_time = time.perf_counter()


# -----------------------------
# Update
# -----------------------------

def update():

    # Time since animation started
    t = time.perf_counter() - start_time

    for data in points_data:

        # Don't update circles
        # that haven't appeared yet
        if "point" not in data:
            continue

        rpm = data["rpm"]
        radius = data["radius"]
        angle0 = data["angle0"]

        # RPM -> radians/second
        angular_speed = rpm * 2 * np.pi / 60

        # Current angle
        angle = angle0 + angular_speed * t

        # Keep angle between 0 and 2π
        angle = angle % (2 * np.pi)

        # Calculate position
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        # Update circle position
        data["point"].setPos(
            x * scale,
            -y * scale
        )


# -----------------------------
# Add next 3 circles
# -----------------------------

def add_more_points():

    for data in points_data[3:6]:
        create_point(data)


# -----------------------------
# Animation timer
# -----------------------------

timer = QTimer()

timer.timeout.connect(update)

# Approximately 60 FPS
timer.start(16)


# -----------------------------
# Add 3 more after 15 seconds
# -----------------------------

add_timer = QTimer()

add_timer.setSingleShot(True)

#add_timer.timeout.connect(add_more_points)

add_timer.start(15000)


# -----------------------------
# Show
# -----------------------------

view.show()

sys.exit(app.exec())