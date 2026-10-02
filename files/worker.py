import time

import numpy as np
import cv2 as cv
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

import tracking_core as core
import db


class TrackerWorker(QThread):
    frame_ready = Signal(QImage)
    rpm_updated = Signal(dict)      # {tag_id: rpm}
    status = Signal(str)
    error = Signal(str)

    MAX_MISSED_FRAMES = 15
    LOG_INTERVAL_SEC = 0.5

    def __init__(self, source, region=None, parent=None):
        super().__init__(parent)
        self.source = source
        self.region = region
        self._running = False

    def stop(self):
        self._running = False

    def run(self):
        self._running = True

        cap = cv.VideoCapture(self.source)
        if not cap.isOpened():
            self.error.emit(f"Could not open source: {self.source}")
            return

        conn = db.get_connection()
        session_id = db.start_session(conn, self.source)
        self.status.emit(f"Session started: {session_id}")

        previous_angles = {}
        total_angles = {}
        rpm_lists = {}
        rpm_avgs = {}
        missed_frames = {}
        last_log_time = {}

        last_time = time.perf_counter()

        try:
            while self._running:
                success, raw_frame = cap.read()
                if not success:
                    self.error.emit("No frame from source")
                    break

                frame = core.crop_region(raw_frame, self.region)

                now = time.perf_counter()
                dt = now - last_time
                last_time = now

                black = core.find_black_circle(frame)
                markers = core.find_tagged_markers(frame)

                core.draw_circle(frame, black, (255, 255, 0), "black")

                seen_this_frame = set(markers.keys())

                if black is not None:
                    for tag_id, (mx, my, mr) in markers.items():
                        core.draw_circle(frame, (mx, my, mr), (0, 255, 255), f"ID {tag_id}")

                        angle = core.get_angle(black, (mx, my))

                        if tag_id not in previous_angles:
                            previous_angles[tag_id] = angle
                            total_angles[tag_id] = 0
                            rpm_lists[tag_id] = []
                            rpm_avgs[tag_id] = 0
                            missed_frames[tag_id] = 0
                            continue

                        diff = angle - previous_angles[tag_id]
                        if diff > 180:
                            diff -= 360
                        elif diff < -180:
                            diff += 360

                        total_angles[tag_id] += diff
                        previous_angles[tag_id] = angle
                        missed_frames[tag_id] = 0

                        if dt > 0:
                            rpm = (diff / 360) / dt * 60
                            rpm_lists[tag_id].append(rpm)
                            if len(rpm_lists[tag_id]) > 20:
                                rpm_lists[tag_id].pop(0)
                            rpm_avgs[tag_id] = sum(rpm_lists[tag_id]) / len(rpm_lists[tag_id])

                        last_log = last_log_time.get(tag_id, 0)
                        if now - last_log >= self.LOG_INTERVAL_SEC:
                            bx, by, _ = black
                            orbital_radius = float(np.hypot(mx - bx, my - by))
                            db.log_reading(
                                conn, session_id, tag_id,
                                timestamp=now, angle=angle,
                                radius=orbital_radius, rpm=-rpm_avgs[tag_id],
                            )
                            last_log_time[tag_id] = now

                    db.commit(conn)

                for tag_id in list(previous_angles.keys()):
                    if tag_id not in seen_this_frame:
                        missed_frames[tag_id] = missed_frames.get(tag_id, 0) + 1
                        if missed_frames[tag_id] > self.MAX_MISSED_FRAMES:
                            del previous_angles[tag_id]
                            del total_angles[tag_id]
                            del rpm_lists[tag_id]
                            del rpm_avgs[tag_id]
                            del missed_frames[tag_id]

                current_rpms = {tid: -rpm_avgs[tid] for tid in rpm_avgs}
                self.rpm_updated.emit(current_rpms)

                # BGR -> RGB -> QImage. .copy() is required: the numpy
                # buffer backing rgb would otherwise be overwritten (or
                # garbage collected) before the GUI thread finishes
                # reading it, causing flicker/garbage frames.
                rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bytes_per_line = ch * w
                qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
                self.frame_ready.emit(qimg)

        finally:
            db.end_session(conn, session_id)
            conn.close()
            cap.release()
            self.status.emit(f"Session ended: {session_id}")
