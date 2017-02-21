"""
The controller class does the real logic,
and passes on data to the model
"""
import time
import threading


class MainController:

    def __init__(self, model, chronograph):
        self.model = model
        self.chronograph = chronograph
        self._first_start = True

        # TODO check if its an appropriate place to start a thread...
        self._time_thread = threading.Thread(target=self.update_time)
        self._time_thread.start()

    def activate_chronograph(self):
        if self._first_start:
            self.model.chronograph.time_start()
            self._first_start = False
        self.model.chronograph_activated = True

    def pause_chronograph(self):
        self.deactivate_chronograph()

    def stop_chronograph(self):
        self._first_start = True
        self.deactivate_chronograph()

    def deactivate_chronograph(self):
        self.model.chronograph_activated = False

    def update_time(self):
        while True:
            time.sleep(1)
            while self.model.chronograph_activated:
                self.model.chronograph.time_auto_increment()
                self.model.announce_update()
                time.sleep(1)
