from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QColor


class WorldView(QtWidgets.QWidget):
    def __init__(self, model, controller):
        super().__init__()
        self.controller = controller
        self.model = model

        self.setObjectName("world_tab")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.world_view = QtWidgets.QGraphicsView(self)

        self.world_view.setResizeAnchor(0)  # stuff always on top left corner
        self.world_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)    # and coordinates will start at top left corner

        self.world_view.setObjectName("world_view")
        self.world_scene = QtWidgets.QGraphicsScene()
        self.world_view.setScene(self.world_scene)
        self.gridLayout.addWidget(self.world_view, 0, 0, 1, 1)

        self.world_view.setRenderHint(QtGui.QPainter.Antialiasing)

        self.setup_painting()
        self.draw_path()
        self.draw_drawing_square_coords()

        # the methods are called by the model when it executes announce_update
        self.model.subscribe_update_func(self.update_world_image)
        self.model.subscribe_update_func(self.draw_path)

    def setup_painting(self):
        # # The QBrush class defines the fill pattern of shapes drawn by QPainter
        # self.path_brush = QtGui.QBrush(QColor('#95ee95'))

        # The QPen class defines how a QPainter should draw lines and outlines of shapes
        # Note : the first arg of QPen could be as easily a QColor or a QBrush
        self.path_lines_pen = QtGui.QPen(QColor('#f44280'), 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.path_points_pen = QtGui.QPen(QColor('#95ff95'), 10)
        self.drawing_zone_pen = QtGui.QPen(QColor('#11ed23'), 10)
        self.radius = 10

    def update_world_image(self):
        scene_img = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(self.model.game_image))
        self.world_scene.addItem(scene_img)

    def draw_path(self):
        path = self.model.path_coords
        path_to_paint = QtGui.QPainterPath()
        points_to_paint = QtGui.QPainterPath()
        if path:
            path_to_paint.moveTo(path[0][0], path[0][1])
            for i in range(len(path)):
                points_to_paint.addEllipse(path[i][0] - self.radius / 2, path[i][1] -
                                           self.radius / 2, self.radius, self.radius)
                if i == 0:
                    path_to_paint.moveTo(path[0][0], path[0][1])
                    i += 1
                path_to_paint.lineTo(path[i][0], path[i][1])

            self.world_scene.addPath(path_to_paint, self.path_lines_pen)
            self.world_scene.addPath(points_to_paint, self.path_points_pen)

    def draw_drawing_square_coords(self):
        path = self.model.drawing_zone_coords
        path_to_paint = QtGui.QPainterPath()
        if path:
            path_to_paint.moveTo(path[0][0], path[0][1])
            for i in range(len(path)):
                path_to_paint.addEllipse(path[i][0] - self.radius / 2, path[i][1] - self.radius / 2, self.radius, self.radius)

            self.world_scene.addPath(path_to_paint, self.drawing_zone_pen)
