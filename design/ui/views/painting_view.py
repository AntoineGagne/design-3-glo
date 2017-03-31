"""
Sources:
http://stackoverflow.com/questions/37399515/how-to-make-a-widgets-height-a-fixed-proportion-to-its-width
"""
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QWidget
from pkg_resources import resource_filename
import PyQt5.QtGui as QtGui
import math
from design.ui.models.painting_model import PaintingModel
from design.ui.controllers.painting_controller import PaintingController


class PaintingView(QWidget):
    """
    Reimplementation to keep aspect ratio of widget
    """

    def __init__(self, painting_model: PaintingModel, painting_controller: PaintingController):
        super().__init__()
        self.model = painting_model
        self.controller = painting_controller

        # This is only for fun at the beginning
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
        self.painting_view = QtWidgets.QGraphicsView(self)
        self.painting_view.setResizeAnchor(0)  # stuff always on top left corner
        self.painting_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # and coordinates will start at top left corner
        self.painting_scene = QtWidgets.QGraphicsScene()
        self.painting_view.setScene(self.painting_scene)
        self.grid_layout.addWidget(self.painting_view, 0, 0)
        self.painting_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.painting_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.painting_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.radius = 5

        self.painting_scene.addPixmap(trump_painting)

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
        self.painting_view.setFixedSize(width, height)

    def update_world_image(self):
        # convert to QPixmap
        if self.model.painting_image is not None:
            height, width, channel = self.model.painting_image.shape
            bytes_per_line = 3 * width
            image = QtGui.QImage(self.model.painting_image.data, width, height, bytes_per_line,
                                 QtGui.QImage.Format_RGB888)
            self.scene_img = QtGui.QPixmap(image)
            pixmap_size = self.scene_img.size()
            self.setMinimumSize(pixmap_size)
            self._height_for_width_factor = 1.0 * pixmap_size.height() / pixmap_size.width()
            self.painting_scene.addPixmap(self.scene_img)

    def draw_path(self):
        print("Im about to drawing")
        path = self.model.painting_vertices
        path_to_paint = QtGui.QPainterPath()
        points_to_paint = QtGui.QPainterPath()
        if path:
            print("Im really drawing")
            self.painting_scene.clear()
            path_to_paint.moveTo(path[0][0], path[0][1])
            for i in range(len(path)):
                points_to_paint.addEllipse(path[i][0] - self.radius / 2, path[i][1] -
                                           self.radius / 2, self.radius, self.radius)
                if i == 0:
                    path_to_paint.moveTo(path[0][0], path[0][1])
                    i += 1
                path_to_paint.lineTo(path[i][0], path[i][1])

            self.painting_scene.addPath(path_to_paint, self.path_lines_pen)
            self.painting_scene.addPath(points_to_paint, self.path_points_pen)
