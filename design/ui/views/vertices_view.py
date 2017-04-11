from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QWidget
from pkg_resources import resource_filename
import PyQt5.QtGui as QtGui
import math

from design.ui.controllers.vertices_controller import VerticesController
from design.ui.models.vertices_model import VerticesModel


class VerticesView(QWidget):
    def __init__(self, vertices_model: VerticesModel, vertices_controller: VerticesController):
        super().__init__()
        self.model = vertices_model
        self.controller = vertices_controller
        trump_painting = QPixmap(
            resource_filename('design.ui',
                              'resources/donald-trump.png')
        )
        self.scene_img = None
        pixmap_size = trump_painting.size()
        self.setMinimumSize(pixmap_size)
        self._height_for_width_factor = 1.0 * pixmap_size.height() / pixmap_size.width()
        self.path_lines_pen = QtGui.QPen(QColor('#f44280'), 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.path_points_pen = QtGui.QPen(QColor('#95ff95'), 10)
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.vertices_view = QtWidgets.QGraphicsView(self)
        self.vertices_view.setResizeAnchor(0)
        self.vertices_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.vertices_scene = QtWidgets.QGraphicsScene()
        self.vertices_view.setScene(self.vertices_scene)
        self.grid_layout.addWidget(self.vertices_view, 0, 0)
        self.vertices_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.vertices_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.vertices_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.radius = 5

        self.vertices_scene.addPixmap(trump_painting)

        self._painting_graphics = QGraphicsView()

        self.model.subscribe_update_function(self.draw_path)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return math.ceil(width * self._height_for_width_factor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resizeImage(event.size())

    def _resizeImage(self, size):
        width = size.width()
        height = self.heightForWidth(width)
        self.vertices_view.setFixedSize(width, height)

    def draw_path(self):
        path = self.model.painting_vertices
        path_to_paint = QtGui.QPainterPath()
        points_to_paint = QtGui.QPainterPath()
        if path:
            self.vertices_scene.clear()
            path_to_paint.moveTo(path[0][0], path[0][1])
            for i in range(len(path)):
                points_to_paint.addEllipse(path[i][0] - self.radius / 2, path[i][1] -
                                           self.radius / 2, self.radius, self.radius)
                if i == 0:
                    path_to_paint.moveTo(path[0][0], path[0][1])
                    i += 1
                path_to_paint.lineTo(path[i][0], path[i][1])
            self.vertices_scene.addPath(path_to_paint, self.path_lines_pen)
            self.vertices_scene.addPath(points_to_paint, self.path_points_pen)
