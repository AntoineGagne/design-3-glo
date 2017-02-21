"""
    This is the main app class
     responsible for instantiating each of the views,
     controllers, and the model (and passing the
     references between them).
     Generally this is very minimal
"""
import sys
import time
import qdarkstyle
from PyQt5.QtWidgets import QApplication
from design.main_station.views.main_view import MainView
from design.main_station.controllers.main_controller import MainController
from design.main_station.models.main_model import MainModel
from design.main_station.models.world_model import WorldModel
from design.main_station.controllers.world_controller import WorldController
from design.main_station.views.world_view import WorldView
from design.main_station.views.painting_view import PaintingView
import threading


class MainApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        self.main_model = MainModel()
        self.main_controller = MainController(self.main_model)
        self.main_view = MainView(self.main_model, self.main_controller)

        self.world_model = WorldModel()
        self.world_controller = WorldController(self.world_model)
        self.main_view.add_tab(WorldView(self.world_model, self.world_controller), "World Tab")

        self.painting_view = PaintingView()
        self.main_view.add_painting(self.painting_view)

        self.run_view()

    def run_view(self):
        self.main_view.show()


if __name__ == '__main__':
    app = MainApp(sys.argv)  # A new instance of QApplication
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())  # setting up stylesheet
    sys.exit(app.exec_())  # and execute the app (exec_() must be called from the main thread)

