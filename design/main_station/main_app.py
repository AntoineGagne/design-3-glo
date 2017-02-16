"""
    This is the main base station class
     responsible for instantiating each of the views,
     controllers, and the model (and passing the
     references between them).
     Generally this is very minimal
"""
import sys
import time
from PyQt5.QtWidgets import QApplication
from design.main_station.models.world_model import WorldModel
from design.main_station.controllers.world_controller import WorldController
from design.main_station.views.main_view import MainView
from design.main_station.controllers.time_controller import TimeController
from design.main_station.models.time_model import TimeModel
import threading

class BaseStation(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        self.world_model = WorldModel()
        self.world_controller = WorldController(self.world_model)

        self.time_model = TimeModel()
        self.time_controller = TimeController(self.time_model)

        self.main_view = MainView(self.world_model, self.world_controller, self.time_model, self.time_controller)

        self.main_view.show()

    def run(self):
        t = threading.Thread(target=self.printer)
        t.start()

    def printer(self):
        for i in range(20):
            self.time_controller.update_lcd_display(i)
            time.sleep(1)


if __name__ == '__main__':
    app = BaseStation(sys.argv)  # A new instance of QApplication
    app.run()
    sys.exit(app.exec_())  # and execute the app (exec_() must be called from the main thread)

