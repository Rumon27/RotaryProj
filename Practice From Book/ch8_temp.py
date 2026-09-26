
import cv2
import numpy as np
import os


OPENCV_MAJOR_VERSION = int(cv2.__version__.split('.')[0])


class Pedestrian:

    def __init__(self, id, hsv_frame, track_window):

        self.id = id
        self.track_window = track_window

        self.term_crit = (
            cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS,
            10,
            1
        )

        # Initialize histogram
        x, y, w, h = track_window

        roi = hsv_frame[y:y+h, x:x+w]

        roi_hist = cv2.calcHist(
            [roi],
            [0, 2],
            None,
            [15, 16],
            [0, 180, 0, 256]
        )

        self.roi_hist = cv2.normalize(
            roi_hist,
            roi_hist,
            0,
            255,
            cv2.NORM_MINMAX
        )

    def update(self, frame, hsv_frame):

        # Calculate back projection
        back_proj = cv2.calcBackProject(
            [hsv_frame],
            [0, 2],
            self.roi_hist,
            [0, 180, 0, 256],
            1
        )

        # MeanShift tracking
        ret, self.track_window = cv2.meanShift(
            back_proj,
            self.track_window,
            self.term_crit
        )

        x, y, w, h = self.track_window

        # Draw tracking rectangle
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (255, 255, 0),
            2
        )

        # Draw ID
        cv2.putText(
            frame,
            'ID: %d' % self.id,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            1,
            cv2.LINE_AA
        )


def main():

    root = os.getcwd()

    video_path = os.path.join(
        root,
        "videos/pedestrians.avi"
    )

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Could not open video.")
        return

    # Create KNN background subtractor
    bg_subtractor = cv2.createBackgroundSubtractorKNN()

    history_length = 20
    bg_subtractor.setHistory(history_length)

    # Morphological kernels
    erode_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3)
    )

    dilate_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 7)
    )

    pedestrians = []

    num_history_frames_populated = 0

    while True:

        grabbed, frame = cap.read()

        if not grabbed:
            break

        # Background subtraction
        fg_mask = bg_subtractor.apply(frame)

        # Allow background model to build
        if num_history_frames_populated < history_length:

            num_history_frames_populated += 1

            cv2.imshow(
                "Pedestrians Tracked",
                frame
            )

            if cv2.waitKey(30) == 27:
                break

            continue

        # Threshold foreground mask
        _, thresh = cv2.threshold(
            fg_mask,
            127,
            255,
            cv2.THRESH_BINARY
        )

        # Remove small noise
        cv2.erode(
            thresh,
            erode_kernel,
            thresh,
            iterations=2
        )

        # Join nearby foreground regions
        cv2.dilate(
            thresh,
            dilate_kernel,
            thresh,
            iterations=2
        )

        # Find contours
        if OPENCV_MAJOR_VERSION >= 4:

            contours, hier = cv2.findContours(
                thresh,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

        else:

            _, contours, hier = cv2.findContours(
                thresh,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

        # Convert frame to HSV
        hsv_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2HSV
        )

        # Initialize pedestrians only once
        should_initialize_pedestrians = (
            len(pedestrians) == 0
        )

        id = 0

        for c in contours:

            if cv2.contourArea(c) > 500:

                x, y, w, h = cv2.boundingRect(c)

                # Draw detected contour rectangle
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    1
                )

                # Create pedestrian trackers
                if should_initialize_pedestrians:

                    pedestrians.append(
                        Pedestrian(
                            id,
                            hsv_frame,
                            (x, y, w, h)
                        )
                    )

                id += 1

        # Update each pedestrian
        for pedestrian in pedestrians:

            pedestrian.update(
                frame,
                hsv_frame
            )

        # Display
        cv2.imshow(
            "Pedestrians Tracked",
            frame
        )

        # Press ESC to quit
        k = cv2.waitKey(30)

        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
