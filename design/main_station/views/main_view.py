"""
    We inherit from main_window that is designed with
    Qt Designer and add everything related to actions and
    models to enable real time data visualization
"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QGraphicsEllipseItem, QGraphicsPixmapItem
from PyQt5 import QtGui
from design.main_station.views.generated.ui_main_view import Ui_main_window


class MainView(QMainWindow):

    def __init__(self, world_model, world_controller, time_model, time_controller):
        super().__init__()
        self.world_ctrl = world_controller
        self.world_model = world_model

        self.time_ctrl = time_controller
        self.time_model = time_model

        self.build_ui()

        self.setup_world_tab()

        # the methods are called by the model when it executes announce_update
        self.world_model.subscribe_update_func(self.update_world)
        self.time_model.subscribe_update_func(self.update_lcd)

    def build_ui(self):
        self.ui = Ui_main_window()
        self.ui.setupUi(self)

        # setting up slot/signal connections
        self.setup_connections()

    def update_lcd(self):
        self.ui.chrono_lcd.display(self.time_model.timer)

    def setup_connections(self):
        """
        connecting signals to slots
        """
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
        self.world_ctrl.update_world_image()

    @pyqtSlot()
    def on_stop(self):
        self.actual_scene.clear()

    def setup_world_tab(self):
        self.actual_scene = QGraphicsScene()
        self.ui.world_view.setScene(self.actual_scene)
        self.ui.world_view.setResizeAnchor(0)  # stuff always on top left corner

    def update_world_image(self):
        scene_img = QGraphicsPixmapItem(QtGui.QPixmap(self.world_model.game_image))
        self.actual_scene.addItem(scene_img)

    def draw_path(self):
        ellipse = QGraphicsEllipseItem(200, 200, 100, 100)
        self.actual_scene.addItem(ellipse)
