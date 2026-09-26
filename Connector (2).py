from flask import Flask, Response
import cv2
import mss
import numpy as np

app = Flask(__name__)

sct = mss.mss()
monitor = sct.monitors[2]   # primary monitor


def generate():
    while True:
        screenshot = sct.grab(monitor)

        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # Reduce resolution to save bandwidth
        frame = cv2.resize(frame, (1280, 720))

        # JPEG compression
        _, buffer = cv2.imencode(
            ".jpg",
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, 70]
        )

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )


@app.route("/video")
def video():
    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


app.run(host="0.0.0.0", port=5000)