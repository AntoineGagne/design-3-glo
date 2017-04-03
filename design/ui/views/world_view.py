from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGraphicsView, QWidget
from PyQt5.QtCore import Qt, pyqtSlot
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QColor
from design.ui.controllers.world_controller import WorldController
from design.ui.models.world_model import WorldModel


class WorldView(QWidget):
    def __init__(self, model: WorldModel, controller: WorldController):
        super().__init__()
        self.controller = controller
        self.model = model
        self.scene_img = None
        self.path_lines_pen = None
        self.path_points_pen = None
        self.drawing_zone_pen = None
        self.robot_pen = None
        self.obstacles_pen = None
        self.radius = None
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.button_reset_zoom = QtWidgets.QPushButton()
        self.horizontal_layout.addWidget(self.button_reset_zoom)
        self.button_zoom_in = QtWidgets.QPushButton()
        self.horizontal_layout.addWidget(self.button_zoom_in)
        self.button_zoom_out = QtWidgets.QPushButton()
        self.horizontal_layout.addWidget(self.button_zoom_out)
        self.grid_layout.addLayout(self.horizontal_layout, 0, 0)
        self.button_reset_zoom.setText("Reset Zoom")
        self.button_zoom_in.setText("Zoom In")
        self.button_zoom_out.setText("Zoom Out")
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontal_layout.addItem(spacer_item)
        self.world_view = QtWidgets.QGraphicsView(self)
        self.world_view.setResizeAnchor(0)
        self.world_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.world_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.world_scene = QtWidgets.QGraphicsScene()
        self.world_view.setScene(self.world_scene)
        self.grid_layout.addWidget(self.world_view, 1, 0)
        self.world_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.world_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.world_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._zoom = 0
        self.setup_painting()

        self.make_subscriptions()
        self.setup_connections()

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, zoom):
        self._zoom = zoom

    def make_subscriptions(self):
        self.model.subscribe_update_function(self.update_world_image)
        self.model.subscribe_update_function(self.draw_robot_coordinates)
        self.model.subscribe_update_function(self.draw_obstacles_coordinates)
        self.model.subscribe_update_function(self.draw_drawing_square_coordinates)
        self.model.subscribe_update_function(self.draw_path)
        self.model.subscribe_update_function(self.draw_real_path)
        self.model.subscribe_update_function(self.draw_game_zone_coordinates)

    def setup_connections(self):
        self.button_reset_zoom.clicked.connect(self.reset_zoom)
        self.button_zoom_in.clicked.connect(self.zoom_in)
        self.button_zoom_out.clicked.connect(self.zoom_out)

    def setup_painting(self):
        self.path_lines_pen = QtGui.QPen(QColor('#f44280'), 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.path_points_pen = QtGui.QPen(QColor('#95ff95'), 10)
        self.real_path_lines_pen = QtGui.QPen(QColor('#f44290'), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.real_path_points_pen = QtGui.QPen(QColor('#85ff95'), 10)
        self.drawing_zone_pen = QtGui.QPen(QColor('#11ed23'), 10)
        self.game_zone_pen = QtGui.QPen(QColor('#hhff53'), 10)
        self.robot_pen = QtGui.QPen(QColor('#4171f4'), 10)
        self.obstacles_pen = QtGui.QPen(QColor('#d33a74'), 10)
        self.radius = 10

    def fit_to_image(self):
        self.world_view.resetTransform()
        if not self.scene_img.isNull():
            view_rectangle = self.world_view.viewport().rect()
            factor = min(view_rectangle.width() / self.scene_img.width(),
                         view_rectangle.height() / self.scene_img.height())
            self.world_view.scale(factor, factor)
            self.zoom = 0

    def update_world_image(self):
        if self.model.game_image is not None:
            height, width, channel = self.model.game_image.shape
            bytes_per_line = 3 * width
            image = QtGui.QImage(self.model.game_image.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.scene_img = QtGui.QPixmap(image)
            self.world_scene.addPixmap(self.scene_img)

    @pyqtSlot()
    def reset_zoom(self):
        if self.scene_img is not None:
            self.fit_to_image()

    @pyqtSlot()
    def zoom_in(self):
        factor = 1.25
        self.zoom += 1
        self.update_zoom(factor)

    @pyqtSlot()
    def zoom_out(self):
        factor = 0.8
        self.zoom -= 1
        self.update_zoom(factor)

    def update_zoom(self, factor):
        self.world_view.scale(factor, factor)

    def draw_path(self):
        path = self.model.path_coordinates
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

    def draw_real_path(self):
        path = list(self.model.real_path)
        path_to_paint = QtGui.QPainterPath()
        if path:
            path_to_paint.moveTo(path[0][0], path[0][1])
            for i in range(len(path)):
                if i == 0:
                    path_to_paint.moveTo(path[0][0], path[0][1])
                    i += 1
                path_to_paint.lineTo(path[i][0], path[i][1])

            self.world_scene.addPath(path_to_paint, self.real_path_lines_pen)

    def draw_drawing_square_coordinates(self):
        path = self.model.drawing_zone_coordinates
        path_to_paint = QtGui.QPainterPath()
        if path:
            path_to_paint.moveTo(path[0][0], path[0][1])
            for i in range(len(path)):
                path_to_paint.addEllipse(path[i][0] - self.radius / 2, path[i][1] - self.radius / 2, self.radius,
                                         self.radius)

            self.world_scene.addPath(path_to_paint, self.drawing_zone_pen)

    def draw_robot_coordinates(self):
        path = self.model.robot_coordinates
        path_to_paint = QtGui.QPainterPath()
        if path:
            path_to_paint.moveTo(path[0][0], path[0][1])
            for i in range(len(path)):
                path_to_paint.addEllipse(path[i][0] - self.radius / 2, path[i][1] - self.radius / 2, self.radius + 10,
                                         self.radius + 10)

            self.world_scene.addPath(path_to_paint, self.robot_pen)

    def draw_obstacles_coordinates(self):
        path = self.model.obstacles_coordinates
        path_to_paint = QtGui.QPainterPath()
        if path:
            path_to_paint.moveTo(path[0][0], path[0][1])
            for i in range(len(path)):
                path_to_paint.addEllipse(path[i][0] - self.radius / 2, path[i][1] - self.radius / 2, self.radius,
                                         self.radius)

            self.world_scene.addPath(path_to_paint, self.obstacles_pen)

    def draw_game_zone_coordinates(self):
        path = self.model.game_zone_coordinates
        path_to_paint = QtGui.QPainterPath()
        if path:
            path_to_paint.moveTo(path[0][0], path[0][1])
            for i in range(len(path)):
                path_to_paint.addEllipse(path[i][0] - self.radius / 2, path[i][1] - self.radius / 2, self.radius,
                                         self.radius)

            self.world_scene.addPath(path_to_paint, self.game_zone_pen)
