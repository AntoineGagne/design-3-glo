from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsView, QWidget
from pkg_resources import resource_filename
import PyQt5.QtGui as QtGui
import math
from design.ui.models.painting_model import PaintingModel
from design.ui.controllers.painting_controller import PaintingController


class PaintingView(QWidget):
    def __init__(self, painting_model: PaintingModel, painting_controller: PaintingController):
        super().__init__()
        self.model = painting_model
        self.controller = painting_controller
        trump_painting = QPixmap(
            resource_filename('design.ui',
                              'resources/donald-trump.png')
        )
        self.scene_img = None
        pixmap_size = trump_painting.size()
        self.setMinimumSize(pixmap_size)
        self._height_for_width_factor = 1.0 * pixmap_size.height() / pixmap_size.width()
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.painting_view = QtWidgets.QGraphicsView(self)
        self.painting_view.setResizeAnchor(0)
        self.painting_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.painting_scene = QtWidgets.QGraphicsScene()
        self.painting_view.setScene(self.painting_scene)
        self.grid_layout.addWidget(self.painting_view, 0, 0)
        self.painting_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.painting_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.painting_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.radius = 5
        self.painting_scene.addPixmap(trump_painting)
        self._painting_graphics = QGraphicsView()
        self.model.subscribe_update_function(self.update_world_image)

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
