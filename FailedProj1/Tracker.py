import numpy as np
import heapq


class CentroidTracker:
    def __init__(self, max_disappeared, max_distance):
        self.nextID = 0
        self.objects = {}
        self.disappeared = {}
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        
        self.available_ids = []
        
    def get_new_id(self):
        if self.available_ids:
            return heapq.heappop(self.available_ids)
        
        new_id = self.nextID
        self.nextID += 1
        return new_id

    def register(self, centroid):
        object_id = self.get_new_id()
        self.objects[object_id] = centroid
        self.disappeared[object_id] = 0

    def deregister(self, objectID):
        del self.objects[objectID]
        del self.disappeared[objectID]
        heapq.heappush(self.available_ids, objectID)

    def update(self, input_centroids):
        if len(input_centroids) == 0:
            for id in list(self.disappeared.keys()):
                self.disappeared[id] += 1
                if self.disappeared[id] > self.max_disappeared:
                    self.deregister(id)
            return self.objects

        if len(self.objects) == 0:
            for c in input_centroids:
                self.register(c)
            return self.objects
        
  
            

        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())

        objects = np.array(object_centroids)
        inputs = np.array(input_centroids)

        comp_table = np.zeros((len(objects), len(inputs)))

        for i in range(len(objects)):
            for j in range(len(inputs)):
                dx = objects[i][0] - inputs[j][0]
                dy = objects[i][1] - inputs[j][1]
                

                comp_table[i][j] = np.sqrt(dx**2 + dy**2)

        closest_inputs = comp_table.argmin(axis=1)

        rows = np.arange(len(objects))
        cols = closest_inputs

        used_rows = set()
        used_cols = set()

        for r, c in zip(rows, cols):
            if r in used_rows or c in used_cols:
                continue
            if comp_table[r, c] > self.max_distance:
                continue

            object_id = object_ids[r]
            self.objects[object_id] = input_centroids[c]
            self.disappeared[object_id] = 0

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
            self.register(input_centroids[col])

        return self.objects
