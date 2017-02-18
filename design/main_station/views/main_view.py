"""
    We inherit from main_window that is designed with
    Qt Designer and add everything related to actions and
    models to enable real time data visualization
"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow
from design.main_station.views.generated.ui_main_view import Ui_main_window


class MainView(QMainWindow):
    def __init__(self, model, controller):
        super().__init__()
        self.controller = controller
        self.model = model

        # then build the UI
        self.build_ui()

        # setting up slot/signal connections
        self.setup_connections()

        # the methods are called by the model when it executes announce_update
        self.model.subscribe_update_func(self.update_lcd)

    def build_ui(self):
        self.ui = Ui_main_window()
        self.ui.setupUi(self)

    def add_tab(self, tab_widget, tab_title):
        self.ui.tab_widget.addTab(tab_widget, tab_title)

    def update_lcd(self):
        self.ui.chrono_lcd.display(self.model.timer)

    def setup_connections(self):
        self.ui.start_btn.clicked.connect(self.on_start)
        self.ui.stop_btn.clicked.connect(self.on_stop)

    def update_world(self):
        """
        Is called by the world model
        """
        # self.actual_scene.clear()
        self.update_world_image()   # called first because it's the background
        self.draw_path()    # drawing the path on top of it

    @pyqtSlot()
    def on_start(self):
        """
        Simply calls a similar method
        in the controller.
        """
        print("ON START SLOT")

    @pyqtSlot()
    def on_stop(self):
        print("ON STOP SLOT")
