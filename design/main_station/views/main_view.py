"""
    We inherit from main_window that is designed with
    Qt Designer and add everything related to actions and
    models to enable real time data visualization
"""
import sys
import time

from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsEllipseItem, QGraphicsPixmapItem
import design.main_station.utils
from design.main_station.views.generated.ui_main_view import Ui_main_window


class MainView(QMainWindow, Ui_main_window):

    # properties to read/write widget value (getter and setter)
    @property
    def start(self):
        return self.ui.start_btn.isChecked()

    @start.setter
    def start(self, value):
        self.ui.start_btn.setChecked(value)

    def __init__(self, model, main_ctrl):
        self.model = model
        self.main_ctrl = main_ctrl
        super().__init__()
        self.build_ui()

        # setting up attributes
        self.__global_timer = QTimer(self)
        self.__game_start_time = 0
        self.actual_scene = QGraphicsScene()

        # setting up models
        self.position_model = QtGui.QStandardItemModel(self.list_view_test)
        # register func with model for future model update announcements
        self.model.subscribe_update_func(self.update_ui_from_model)

        # setting up views
        self.setup_world_tab()
        self.make_view_test()

    def build_ui(self):
        self.ui = Ui_main_window()
        self.ui.setupUi(self)

        # setting up slot/signal connections
        self.setup_connections()

        # display adjustments TODO
        self.world_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    def setup_connections(self):
        self.start_btn.clicked.connect(self.display_world)
        self.__global_timer.timeout.connect(self.update_time)
        self.stop_btn.clicked.connect(self.stop_timer)
        # connect signal to method (slot)
        self.ui.start_btn.clicked.connect(self.self.on_start)

    def update_ui_from_model(self):
        """
        The update_ui_from_model method is registered with the model and
        will be called by the model whenever relevant data in the model
        is changed so the new values can be seen in the UI.
        """
        self.start = self.model.start

    def setup_world_tab(self):
        self.world_view.setScene(self.actual_scene)
        self.world_view.setResizeAnchor(0)  # stuff always on top left corner

    def display_world(self):
        scene_img = QGraphicsPixmapItem(QtGui.QPixmap(design.main_station.utils.get_latest_image()))
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
    def on_start(self):
        """
        The event method (i.e. on_start) simply calls a similar method
        in the controller and passes minimal parameters. That way all serious
        logic is handled by the controller and the view can remain
        relatively simple.
        """
        self.main_ctrl.start(self.start_btn)

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


# def run_ui():
#     app = QApplication(sys.argv)    # A new instance of QApplication
#     main_window = MainView()      # We set the main_window to be MainWindow (design)
#     main_window.show()              # Show the main_window
#     sys.exit(app.exec_())           # and execute the app
#
#
# if __name__ == "__main__":          # if we're running file directly and not importing it
#     run_ui()
#     print("I've run the UI")# run the main function
