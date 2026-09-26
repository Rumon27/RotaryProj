import heapq

import numpy as np

try:
    from scipy.optimize import linear_sum_assignment
    _HAS_SCIPY = True
except ImportError:
    _HAS_SCIPY = False


class CentroidTracker:
    def __init__(self, max_disappeared, max_distance,
                 pos_weight=1.0, radius_weight=1.0, velocity_weight=1.0,
                 velocity_window=5, max_velocity_jump=25.0,
                 jump_penalty=1e5):
        self.nextID = 0
        self.objects = {}           # id -> (x, y)
        self.disappeared = {}       # id -> frames missed
        self.available_ids = []     # freed IDs, reused before minting new ones

        self.radii = {}             # id -> last known radius from center
        self.angles = {}            # id -> last known angle (deg), relative to center
        self.velocity_history = {}  # id -> list of recent angular deltas (deg/frame)

        self.max_disappeared = max_disappeared
        self.max_distance = max_distance      # gate on the *combined* cost below

        self.pos_weight = pos_weight          # weight on predicted-position distance
        self.radius_weight = radius_weight    # weight on |radius difference|
        self.velocity_weight = velocity_weight  # weight on |implied vel - avg vel|
        self.velocity_window = velocity_window  # how many past deltas to average

        # if a candidate match would imply a frame-to-frame angular jump
        # more than this many degrees away from the track's own recent
        # average velocity, treat it as very unlikely to be the real match
        self.max_velocity_jump = max_velocity_jump
        self.jump_penalty = jump_penalty

    # ---------- helpers ----------

    def _get_new_id(self):
        if self.available_ids:
            return heapq.heappop(self.available_ids)
        new_id = self.nextID
        self.nextID += 1
        return new_id

    @staticmethod
    def _polar(point, center):
        cx, cy = center
        x, y = point
        dx = x - cx
        dy = y - cy
        r = float(np.hypot(dx, dy))
        theta = float(np.degrees(np.arctan2(dy, dx)) % 360)
        return r, theta

    @staticmethod
    def _angle_diff(a, b):
        """Signed shortest difference a - b, wrapped to [-180, 180]."""
        d = a - b
        d = (d + 180) % 360 - 180
        return d

    def _avg_velocity(self, object_id):
        hist = self.velocity_history.get(object_id, [])
        if not hist:
            return 0.0
        return sum(hist) / len(hist)

    # ---------- register / deregister ----------

    def register(self, centroid, center=None):
        object_id = self._get_new_id()
        self.objects[object_id] = centroid
        self.disappeared[object_id] = 0
        self.velocity_history[object_id] = []

        if center is not None:
            r, theta = self._polar(centroid, center)
            self.radii[object_id] = r
            self.angles[object_id] = theta
        else:
            self.radii[object_id] = None
            self.angles[object_id] = None

    def deregister(self, objectID):
        del self.objects[objectID]
        del self.disappeared[objectID]
        self.radii.pop(objectID, None)
        self.angles.pop(objectID, None)
        self.velocity_history.pop(objectID, None)
        heapq.heappush(self.available_ids, objectID)

    # ---------- assignment ----------

    def _assign(self, comp_table):
        """
        Returns (row_indices, col_indices) of the chosen matches.
        Uses the Hungarian algorithm (globally optimal) when scipy is
        available, otherwise falls back to a greedy argmin approach.
        """
        if _HAS_SCIPY:
            row_ind, col_ind = linear_sum_assignment(comp_table)
            return row_ind, col_ind

        closest_inputs = comp_table.argmin(axis=1)
        rows = np.arange(comp_table.shape[0])
        cols = closest_inputs
        return rows, cols

    # ---------- main update ----------

    def update(self, input_centroids, center=None):
        """
        center: (cx, cy) of the rotation center (e.g. the black circle).
                Pass None to fall back to plain nearest-position matching
                (radius/velocity terms are skipped that frame).
        """
        if len(input_centroids) == 0:
            for id in list(self.disappeared.keys()):
                self.disappeared[id] += 1
                if self.disappeared[id] > self.max_disappeared:
                    self.deregister(id)
            return self.objects

        if len(self.objects) == 0:
            for c in input_centroids:
                self.register(c, center)
            return self.objects

        object_ids = list(self.objects.keys())

        # --- predicted position for each existing object, using its
        #     average recent angular velocity, plus its known radius ---
        predicted_points = []
        object_radii = []
        object_avg_velocity = []
        for oid in object_ids:
            avg_v = self._avg_velocity(oid)
            object_avg_velocity.append(avg_v)
            if center is not None and self.angles[oid] is not None:
                predicted_theta = (self.angles[oid] + avg_v) % 360
                r = self.radii[oid]
                rad = np.radians(predicted_theta)
                px = center[0] + r * np.cos(rad)
                py = center[1] + r * np.sin(rad)
                predicted_points.append((px, py))
                object_radii.append(r)
            else:
                predicted_points.append(self.objects[oid])
                object_radii.append(None)

        inputs = np.array(input_centroids)

        input_radii = None
        input_thetas = None
        if center is not None:
            polar = [self._polar(pt, center) for pt in input_centroids]
            input_radii = [p[0] for p in polar]
            input_thetas = [p[1] for p in polar]

        comp_table = np.zeros((len(object_ids), len(inputs)))

        for i, oid in enumerate(object_ids):
            px, py = predicted_points[i]
            for j in range(len(inputs)):
                dx = px - inputs[j][0]
                dy = py - inputs[j][1]
                pos_dist = np.sqrt(dx ** 2 + dy ** 2)

                radius_term = 0.0
                if object_radii[i] is not None and input_radii is not None:
                    radius_term = abs(object_radii[i] - input_radii[j])

                velocity_term = 0.0
                jump_penalty = 0.0
                if (center is not None and self.angles[oid] is not None
                        and input_thetas is not None):
                    # what angular velocity would this specific match imply?
                    implied_v = self._angle_diff(input_thetas[j], self.angles[oid])
                    velocity_term = abs(implied_v - object_avg_velocity[i])

                    # only start penalizing once this track has enough
                    # history to trust its average (avoids punishing
                    # brand-new tracks that have no velocity estimate yet)
                    if (len(self.velocity_history[oid]) >= 2
                            and velocity_term > self.max_velocity_jump):
                        jump_penalty = self.jump_penalty

                comp_table[i][j] = (self.pos_weight * pos_dist
                                     + self.radius_weight * radius_term
                                     + self.velocity_weight * velocity_term
                                     + jump_penalty)

        rows, cols = self._assign(comp_table)

        used_rows = set()
        used_cols = set()

        for r, c in zip(rows, cols):
            if r in used_rows or c in used_cols:
                continue
            if comp_table[r, c] > self.max_distance:
                continue

            object_id = object_ids[r]
            new_centroid = input_centroids[c]
            self.objects[object_id] = new_centroid
            self.disappeared[object_id] = 0

            if center is not None:
                new_r, new_theta = self._polar(new_centroid, center)

                if self.angles[object_id] is not None:
                    delta = self._angle_diff(new_theta, self.angles[object_id])

                    hist = self.velocity_history[object_id]
                    hist.append(delta)
                    if len(hist) > self.velocity_window:
                        hist.pop(0)

                self.radii[object_id] = new_r
                self.angles[object_id] = new_theta

            used_rows.add(r)
            used_cols.add(c)

        unused_rows = set(range(comp_table.shape[0])) - used_rows
        unused_cols = set(range(comp_table.shape[1])) - used_cols

        for r in unused_rows:
            object_id = object_ids[r]
            self.disappeared[object_id] += 1
            if self.disappeared[object_id] > self.max_disappeared:
                self.deregister(object_id)

        for col in unused_cols:
            self.register(input_centroids[col], center)

        return self.objects