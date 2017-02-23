import time


class Chronograph:
    @property
    def chrono_time(self):
        return self._chrono_time

    @chrono_time.setter
    def chrono_time(self, time):
        self._chrono_time = time

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, time):
        self._start_time = time

    def __init__(self):
        self._chrono_time = 0
        self._start_time = 0.0

    def time_start(self):
        self.start_time = time.time()

    def time_increment(self):
        self.chrono_time += 1

    def time_auto_increment(self):
        self.chrono_time = int(time.time() - self.start_time)
        return self.chrono_time

    def time_pause(self):
        self.start_time = self.chrono_time

    def time_stop(self):
        self.start_time = 0
        self.chrono_time = 0
