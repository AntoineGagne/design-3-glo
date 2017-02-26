from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGraphicsView, QWidget
from PyQt5.QtCore import Qt, pyqtSlot
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QColor


class WorldView(QWidget):
    def __init__(self, model, controller):
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

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.pushBtn_resetZoom = QtWidgets.QPushButton()
        self.horizontalLayout.addWidget(self.pushBtn_resetZoom)
        self.pushBtn_zoomIn = QtWidgets.QPushButton()
        self.horizontalLayout.addWidget(self.pushBtn_zoomIn)
        self.pushBtn_zoomOut = QtWidgets.QPushButton()
        self.horizontalLayout.addWidget(self.pushBtn_zoomOut)
        self.pushBtn_updateImg = QtWidgets.QPushButton()
        self.horizontalLayout.addWidget(self.pushBtn_updateImg)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0)
        self.pushBtn_resetZoom.setText("Reset Zoom")
        self.pushBtn_zoomIn.setText("Zoom In")
        self.pushBtn_zoomOut.setText("Zoom Out")
        self.pushBtn_updateImg.setText("Update Image")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.world_view = QtWidgets.QGraphicsView(self)
        self.world_view.setResizeAnchor(0)  # stuff always on top left corner
        self.world_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # and coordinates will start at top left corner
        self.world_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)  # for mouse zooming
        self.world_scene = QtWidgets.QGraphicsScene()
        self.world_view.setScene(self.world_scene)
        self.gridLayout.addWidget(self.world_view, 1, 0)
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
        self.model.subscribe_update_func(self.update_world_image)
        self.model.subscribe_update_func(self.draw_robot_coords)
        self.model.subscribe_update_func(self.draw_obstacles_coords)
        self.model.subscribe_update_func(self.draw_drawing_square_coords)
        self.model.subscribe_update_func(self.draw_path)

    def setup_connections(self):
        self.pushBtn_updateImg.clicked.connect(self.make_image_update)
        self.pushBtn_resetZoom.clicked.connect(self.reset_zoom)
        self.pushBtn_zoomIn.clicked.connect(self.zoom_in)
        self.pushBtn_zoomOut.clicked.connect(self.zoom_out)

    def setup_painting(self):
        self.path_lines_pen = QtGui.QPen(QColor('#f44280'), 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.path_points_pen = QtGui.QPen(QColor('#95ff95'), 10)
        self.drawing_zone_pen = QtGui.QPen(QColor('#11ed23'), 10)
        self.robot_pen = QtGui.QPen(QColor('#4171f4'), 10)
        self.obstacles_pen = QtGui.QPen(QColor('#d33a74'), 10)
        self.radius = 10

    def fit_to_image(self):
        self.world_view.resetTransform()
        if not self.scene_img.isNull():
            viewrect = self.world_view.viewport().rect()
            factor = min(viewrect.width() / self.scene_img.width(),
                         viewrect.height() / self.scene_img.height())
            self.world_view.scale(factor, factor)
            self.zoom = 0

    def update_world_image(self):
        self.scene_img = QtGui.QPixmap(self.model.game_image)
        self.world_scene.addPixmap(self.scene_img)

    @pyqtSlot()
    def make_image_update(self):
        self.controller.update_world_image()

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
                path_to_paint.addEllipse(path[i][0] - self.radius / 2, path[i][1] - self.radius / 2, self.radius,
                                         self.radius)

            self.world_scene.addPath(path_to_paint, self.drawing_zone_pen)

    def draw_robot_coords(self):
        path = self.model.robot_coords
        path_to_paint = QtGui.QPainterPath()
        if path:
            path_to_paint.moveTo(path[0][0], path[0][1])
            for i in range(len(path)):
                path_to_paint.addEllipse(path[i][0] - self.radius / 2, path[i][1] - self.radius / 2, self.radius + 10,
                                         self.radius + 10)

            self.world_scene.addPath(path_to_paint, self.robot_pen)

    def draw_obstacles_coords(self):
        path = self.model.obstacles_coords
        path_to_paint = QtGui.QPainterPath()
        if path:
            path_to_paint.moveTo(path[0][0], path[0][1])
            for i in range(len(path)):
                path_to_paint.addEllipse(path[i][0] - self.radius / 2, path[i][1] - self.radius / 2, self.radius,
                                         self.radius)

            self.world_scene.addPath(path_to_paint, self.obstacles_pen)
