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
from design.main_station.views.main_view import MainView
from design.main_station.controllers.main_controller import MainController
from design.main_station.models.main_model import MainModel
from design.main_station.models.world_model import WorldModel
from design.main_station.controllers.world_controller import WorldController
from design.main_station.views.world_view import WorldView
import threading


class BaseStation(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        self.main_model = MainModel()
        self.main_controller = MainController(self.main_model)
        self.main_view = MainView(self.main_model, self.main_controller)
        self.main_view.show()

        self.world_model = WorldModel()
        self.world_controller = WorldController(self.world_model)
        self.main_view.add_tab(WorldView(self.world_model, self.world_controller), "World Tab")

        self.world_controller.update_world_image()

    def run(self):
        t = threading.Thread(target=self.printer)
        t.start()

    def printer(self):
        for i in range(120):
            self.main_controller.update_lcd_display(i)
            time.sleep(1)


if __name__ == '__main__':
    app = BaseStation(sys.argv)  # A new instance of QApplication
    app.run()
    sys.exit(app.exec_())  # and execute the app (exec_() must be called from the main thread)

