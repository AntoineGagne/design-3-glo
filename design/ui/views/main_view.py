from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMainWindow
from design.ui.views.generated.ui_main_view import Ui_main_window
from design.ui.models.main_model import MainModel
from design.ui.controllers.main_controller import MainController


class MainView(QMainWindow):
    def __init__(self, model: MainModel, controller: MainController):
        super().__init__()
        self.controller = controller
        self.model = model

        self.timer = QTimer(self)
        self.ui = Ui_main_window()
        self.ui.setupUi(self)
        self.setup_buttons()
        self.model.subscribe_update_function(self.start_timer)
        self.model.subscribe_update_function(self.update_console_log)

    def add_tab(self, tab_widget, tab_title):
        self.ui.tab_widget.addTab(tab_widget, tab_title)

    def add_painting_widget(self, paint_widget):
        self.ui.painting_layout.addWidget(paint_widget)

    def add_vertices_widget(self, vertices_widget):
        self.ui.vertices_layout.addWidget(vertices_widget)

    @pyqtSlot()
    def detect_static_items(self):
        if not self.model.detect_static_items:
            self.controller.detect_static_items()
            self.ui.find_robot_btn.setEnabled(True)
            self.ui.send_game_map_btn.setEnabled(True)

    @pyqtSlot()
    def send_new_game_map(self):
        if not self.model.send_new_game_map_flag:
            self.controller.send_new_game_map()

    @pyqtSlot()
    def find_robot(self):
        self.controller.find_robot()

    @pyqtSlot()
    def update_lcd(self):
        if self.model.timer_is_on:
            self.controller.update_time()
            m, s = divmod(self.model.time, 60)
            h, m = divmod(m, 60)
            self.ui.chrono_lcd.display("%d:%02d:%02d" % (h, m, s))

    def setup_buttons(self):
        self.timer.timeout.connect(self.update_lcd)
        self.ui.send_game_map_btn.clicked.connect(self.send_new_game_map)
        self.ui.find_robot_btn.clicked.connect(self.find_robot)
        self.ui.detect_static_items_btn.clicked.connect(self.detect_static_items)
        self.ui.find_robot_btn.setEnabled(False)
        self.ui.send_game_map_btn.setEnabled(False)

    def start_timer(self):
        if not self.timer.isActive() and self.model.timer_is_on:
            self.timer.start(1000)

    def update_console_log(self):
        self.ui.console_log_textEdit.setPlainText(self.model.log_messages)
        self.ui.console_log_textEdit.moveCursor(QTextCursor.End)
