from PyQt5 import QtWidgets
import PyQt5.QtGui as QtGui


class WorldView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("world_tab")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.world_view = QtWidgets.QGraphicsView(self)
        self.world_view.setResizeAnchor(0)  # stuff always on top left corner
        self.world_view.setObjectName("world_view")
        self.world_scene = QtWidgets.QGraphicsScene()
        self.world_view.setScene(self.world_scene)
        self.gridLayout.addWidget(self.world_view, 0, 0, 1, 1)

    def update_world_image(self):
        scene_img = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(self.world_model.game_image))
        self.actual_scene.addItem(scene_img)

    def draw_path(self):
        ellipse = QtWidgets.QGraphicsEllipseItem(200, 200, 100, 100)
        self.actual_scene.addItem(ellipse)