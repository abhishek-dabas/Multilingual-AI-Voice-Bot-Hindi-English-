import time

class LatencyTracker:
    def __init__(self):
        self.timestamps = {} # Dicitionary for events

    def mark(self, key): # Called at critical pipeline points 
        self.timestamps[key] = time.time()

    def report(self): # Prints raw data
        print("---- Latency Report ----")
        for k, v in self.timestamps.items():
            print(f"{k}: {v}")
