"""
    We inherit from main_window that is designed with
    Qt Designer and add everything related to actions and
    models to enable real time data visualization
"""
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QMainWindow
from design.main_station.views.generated.ui_main_view import Ui_main_window


class MainView(QMainWindow):
    def __init__(self, model, controller):
        super().__init__()
        self.controller = controller
        self.model = model

        self.timer = QTimer(self)

        # then build the UI
        self.ui = Ui_main_window()
        self.ui.setupUi(self)

        # setting up slot/signal connections
        self.setup_connections()

        # the methods are called by the model when it executes announce_update
        self.model.subscribe_update_function(self.start_timer)

    def add_tab(self, tab_widget, tab_title):
        self.ui.tab_widget.addTab(tab_widget, tab_title)

    def add_painting(self, paint_widget):
        self.ui.painting_layout.addWidget(paint_widget)

    @pyqtSlot()
    def update_lcd(self):
        if self.model.timer_is_on:
            self.controller.update_time()
            self.ui.chrono_lcd.display(self.model.time)

    def setup_connections(self):
        self.ui.start_btn.clicked.connect(self.on_start)
        self.ui.pause_btn.clicked.connect(self.on_pause)
        self.ui.stop_btn.clicked.connect(self.on_stop)
        self.timer.timeout.connect(self.update_lcd)

    @pyqtSlot()
    def on_start(self):
        self.controller.activate_timer()
        self.timer.start(1000)  # tick once every 1000 milisecond (1 sec)

    @pyqtSlot()
    def on_stop(self):
        self.controller.deactivate_timer()
        self.controller.reset_timer()
        self.timer.stop()

    @pyqtSlot()
    def on_pause(self):
        self.controller.deactivate_timer()
        self.timer.stop()

    def start_timer(self):
        if not self.timer.isActive() and self.model.timer_is_on:
            self.timer.start(1000)  # tick once every 1000 milisecond (1 sec)
