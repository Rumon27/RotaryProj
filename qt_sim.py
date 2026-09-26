import sys
import numpy as np
import time
import os

from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsPixmapItem,
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QBrush, QPixmap


# -----------------------------
# Configuration
# -----------------------------

TAG_DIR = "tags"
TAG_DISPLAY_SIZE = 30   # on-screen pixel size of each tag (matches old red_size)

points_data = [
    {"radius": 2, "rpm": 20, "angle0": 0, "tag_id": 0},
    {"radius": 3.25, "rpm": 25, "angle0": 2, "tag_id": 1},
    {"radius": 2, "rpm": 30, "angle0": 4, "tag_id": 2},

    # These will appear after
    {"radius": 4, "rpm": 15, "angle0": 1, "tag_id": 3},
    {"radius": 3, "rpm": 35, "angle0": 3, "tag_id": 4},
    {"radius": 4.5, "rpm": 40, "angle0": 5, "tag_id": 5},
]


# -----------------------------
# Figure / Scene
# -----------------------------

app = QApplication(sys.argv)

scene = QGraphicsScene()
scene.setBackgroundBrush(QBrush("white"))

view = QGraphicsView(scene)
view.resize(1000, 1000)
# second monitor starts at left=1920 (from list_monitors.py); place the
# window at a fixed, known spot there so screen-capture coordinates are predictable
view.move(1920, 0)

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
# Create a marker (now an ArUco tag image instead of a red circle)
# -----------------------------

def create_point(data):

    radius = data["radius"]
    angle = data["angle0"]
    tag_id = data["tag_id"]

    x = radius * np.cos(angle)
    y = radius * np.sin(angle)

    tag_path = os.path.join(TAG_DIR, f"tag_{tag_id}.png")
    pixmap = QPixmap(tag_path)
    pixmap = pixmap.scaled(TAG_DISPLAY_SIZE, TAG_DISPLAY_SIZE)

    point = QGraphicsPixmapItem(pixmap)

    # center the pixmap on its own position, same convention as the old
    # ellipse item (which was built with -size/2 offsets)
    point.setOffset(-TAG_DISPLAY_SIZE / 2, -TAG_DISPLAY_SIZE / 2)

    scene.addItem(point)

    point.setPos(
        x * scale,
        -y * scale
    )

    # Store the graphics object
    data["point"] = point


# -----------------------------
# Initially create 3 markers
# -----------------------------

for data in points_data[:3]:
     create_point(data)


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

        # Don't update markers
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

        # Update marker position
        data["point"].setPos(
            x * scale,
            -y * scale
        )


# -----------------------------
# Add next 3 markers
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

# add_timer.timeout.connect(add_more_points)

add_timer.start(15000)


# -----------------------------
# Show
# -----------------------------

view.show()

sys.exit(app.exec())