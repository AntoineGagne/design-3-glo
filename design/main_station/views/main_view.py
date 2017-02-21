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

    def add_painting(self, paint_widget):
        self.ui.painting_layout.addWidget(paint_widget)

    def update_lcd(self):
        self.ui.chrono_lcd.display(self.model.chronograph.chrono_time)

    def setup_connections(self):
        self.ui.start_btn.clicked.connect(self.on_start)
        self.ui.pause_btn.clicked.connect(self.on_pause)
        self.ui.stop_btn.clicked.connect(self.on_stop)

    @pyqtSlot()
    def on_start(self):
        self.controller.activate_chronograph()

    @pyqtSlot()
    def on_stop(self):
        self.controller.stop_chronograph()

    @pyqtSlot()
    def on_pause(self):
        self.controller.pause_chronograph()

