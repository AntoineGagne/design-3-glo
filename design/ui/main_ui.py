"""
    We inherit from main_window that is designed with
    Qt Designer and add everything related to actions and
    models to enable real time data visualization
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsEllipseItem, QGraphicsPixmapItem
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, pyqtSlot, pyqtSignal, Qt
from ui.main_window import Ui_main_window
from base_station import BaseStation
import utils
import time


class MainWindow(QMainWindow, Ui_main_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__base_station = BaseStation()

        # display adjustments TODO
        self.world_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # QtGui.QWheelEvent on_wheel
        # self.world_view.wheelEvent()

        # setting up attributes
        self.__global_timer = QTimer(self)
        self.__game_start_time = 0
        self.actual_scene = QGraphicsScene()

        # setting up models
        self.position_model = QtGui.QStandardItemModel(self.list_view_test)

        # setting up slot/signal connections
        self.setup_connections()
        self.setup_world_tab()
        self.make_view_test()

    def setup_connections(self):
        self.start_btn.clicked.connect(self.start_timer)
        self.start_btn.clicked.connect(self.display_world)
        self.__global_timer.timeout.connect(self.update_time)
        self.stop_btn.clicked.connect(self.stop_timer)

    def setup_world_tab(self):
        self.world_view.setScene(self.actual_scene)
        self.world_view.setResizeAnchor(0)  # stuff always on top left corner

    def display_world(self):
        scene_img = QGraphicsPixmapItem(QtGui.QPixmap(utils.get_latest_image()))
        self.actual_scene.addItem(scene_img)
        self.draw_real_path()

    def make_view_test(self):
        self.list_view_test.setModel(self.position_model)
        foods = ['Cookie dough', 'Hummus', 'Spaghetti', 'spicy food', 'Chocolate whipped cream']
        for food in foods:
            item = QtGui.QStandardItem(food)
            self.position_model.appendRow(item)   # Add the item to the model

    def update_position(self, new_position):
        new_pos = QtGui.QStandardItem(new_position)
        self.position_model.appendRow(new_pos)

    @pyqtSlot()
    def start_timer(self):
        print("starting counter")
        self.__game_start_time = time.time()
        self.__global_timer.setInterval(500)  # interval set at 1000ms/2
        self.__global_timer.start()

    @pyqtSlot()
    def stop_timer(self):
        print("stopping counter")
        self.__global_timer.stop()

    @pyqtSlot()
    def update_time(self):
        elapsed_time = time.time() - self.__game_start_time
        # print(round(elapsed_time, 1))
        self.chrono_lcd.display(round(elapsed_time, 0))
        self.game_progress_bar.setValue(round(elapsed_time, 1))

    def draw_real_path(self):
        ellipse = QGraphicsEllipseItem(200, 200, 100, 100)
        self.actual_scene.addItem(ellipse)


def run_ui():
    app = QApplication(sys.argv)    # A new instance of QApplication
    main_window = MainWindow()      # We set the main_window to be MainWindow (design)
    main_window.show()              # Show the main_window
    sys.exit(app.exec_())           # and execute the app


if __name__ == "__main__":          # if we're running file directly and not importing it
    run_ui()                        # run the main function
