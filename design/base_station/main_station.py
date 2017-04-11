import datetime
import time
from PyQt5.QtWidgets import QApplication
from pkg_resources import resource_string

from design.ui.controllers.vertices_controller import VerticesController
from design.ui.models.vertices_model import VerticesModel
from design.ui.views.main_view import MainView
from design.ui.controllers.main_controller import MainController
from design.ui.models.main_model import MainModel
from design.ui.models.world_model import WorldModel
from design.ui.controllers.world_controller import WorldController
from design.ui.views.vertices_view import VerticesView
from design.ui.views.world_view import WorldView
from design.ui.views.painting_view import PaintingView
from design.vision import constants
from design.vision.world_utils import calculate_norm
from design.vision.world_vision import WorldVision
from design.vision.exceptions import RobotNotFound, GameMapNotFound, DrawingZoneNotFound, PositionGap
from design.telemetry.commands import CommandHandler
from design.telemetry.packets import Packet, PacketType
from PyQt5.QtCore import QTimer
from collections import deque
from design.ui.controllers.painting_controller import PaintingController
from design.ui.models.painting_model import PaintingModel


class MainApp(QApplication):
    def __init__(self, sys_argv, telemetry: CommandHandler, main_vision: WorldVision):
        super().__init__(sys_argv)
        self.robot_has_started = False
        self.game_map = {"drawing_zone": []}
        self.telemetry = telemetry
        self.main_vision = main_vision
        self.packet_handler = {PacketType.NOTIFICATION: self.handle_notification,
                               PacketType.COMMAND: self.handle_command,
                               PacketType.FIGURE_IMAGE: self.handle_figure_image,
                               PacketType.FIGURE_VERTICES: self.handle_figure_vertices,
                               PacketType.PATH: self.handle_received_path}
        self.last_robot_information = None
        self.setup_interface()

        self.telemetry_timer = QTimer()
        self.robot_timer = QTimer()
        self.setup_telemetry_timer()

        self.run_view()

    def setup_interface(self):
        self.add_main_view()
        self.add_world_view()
        self.add_painting_view()
        self.add_vertices_view()
        self._set_default_style()

    def add_main_view(self):
        self.main_model = MainModel()
        self.main_controller = MainController(self.main_model)
        self.main_view = MainView(self.main_model, self.main_controller)
        self.main_model.subscribe_update_function(self.find_robot)
        self.main_model.subscribe_update_function(self.detect_static_items)
        self.main_model.subscribe_update_function(self.send_new_game_map)

    def add_world_view(self):
        self.world_model = WorldModel()
        self.world_controller = WorldController(self.world_model)
        self.world_view = WorldView(self.world_model, self.world_controller)
        self.main_view.add_tab(self.world_view, "World Tab")

    def add_painting_view(self):
        self.painting_model = PaintingModel()
        self.painting_controller = PaintingController(self.painting_model)
        self.painting_view = PaintingView(self.painting_model, self.painting_controller)
        self.main_view.add_painting_widget(self.painting_view)

    def add_vertices_view(self):
        self.vertices_model = VerticesModel()
        self.vertices_controller = VerticesController(self.vertices_model)
        self.vertices_view = VerticesView(self.vertices_model, self.vertices_controller)
        self.main_view.add_vertices_widget(self.vertices_view)

    def setup_telemetry_timer(self):
        self.telemetry_timer.timeout.connect(self.check_if_packet_received)
        self.telemetry_timer.setInterval(1000)
        self.telemetry_timer.start()

    def _set_default_style(self):
        stylesheet = resource_string('design.ui.views',
                                     'style/qdarkstyle/style.qss')
        self.setStyleSheet(stylesheet.decode('utf-8'))

    def run_view(self):
        self.main_view.show()

    def find_robot(self):
        if self.main_model.find_robot_flag:
            self.send_robot_position()
            self.main_model.find_robot_flag = False

    def check_if_packet_received(self):
        received_packet = self.telemetry.fetch_command()
        if received_packet:
            self.packet_handler[received_packet.packet_type](received_packet.packet_data)

    def handle_notification(self, notification: str):
        self.main_controller.update_console_log(notification)
        if not self.robot_has_started:
            self.main_controller.send_new_game_map()
            self.robot_has_started = True

    def handle_command(self, command: str):
        if command == "START_CHRONOGRAPH":
            self.main_controller.update_console_log("START_CHRONOGRAPH COMMAND FROM ROBOT RECEIVED")
            self.world_controller.reset_paths()
            self.start_cycle_timer()
        if command == "STOP_CHRONOGRAPH":
            self.stop_cycle_timer()

    def handle_figure_image(self, picture):
        self.main_controller.update_console_log("ONBOARD IMAGE RECEIVED")
        self.painting_controller.update_world_image(picture)

    def handle_figure_vertices(self, vertices: list):
        self.main_controller.update_console_log("ONBOARD IMAGE VERTICES RECEIVED")
        self.vertices_controller.update_path(vertices)

    def handle_received_path(self, path: deque):
        new_path = list(path)
        path_converted = []
        for coordinate in new_path:
            path_converted.append(
                self.main_vision.converter.get_pixel_coordinates_translated(coordinate[1], coordinate[0], 0,
                                                                            self.main_vision.rotation_angle_of_table))
        self.world_controller.update_path(path_converted)

    def send_game_map(self):
        game_map_found = False
        while not game_map_found:
            try:
                self.game_map = self.main_vision.get_world_game_map()
                game_map_found = True
                self.change_axes()
                self.main_controller.update_console_log("GAME MAP FOUND \n {}".format(self.game_map))
                game_map_packet = Packet(packet_type=PacketType.GAME_MAP, packet_data=self.game_map)
                self.telemetry.put_command(game_map_packet)
                self.draw_game_map_on_ui()

            except GameMapNotFound:
                print("Game map not found")
                continue

    def draw_game_map_on_ui(self, static_items: bool = False):
        if static_items:
            self.world_controller.update_game_zone_coordinates(self.main_vision.game_map_pixels["table_corners"])
            self.world_controller.update_drawing_zone(self.main_vision.game_map_pixels["drawing_zone"])
        else:
            obstacles_coordinates = self.main_vision.game_map_pixels["obstacles"]
            arranged_coordinates = []
            for information in obstacles_coordinates:
                arranged_coordinates.append(information[0])
            self.world_controller.update_obstacles_coordinates(arranged_coordinates,
                                                               self.main_vision.game_map_pixels["base_obstacles"])
            self.world_controller.update_robot_position([self.main_vision.game_map_pixels["robot"][0]],
                                                        self.main_vision.game_map_pixels["base_robot"])
            self.world_controller.update_real_path(self.main_vision.game_map_pixels["robot"][0])
        self.world_controller.update_world_image(self.main_vision.actual_frame)

    def change_axes(self):
        for index, coordinate in enumerate(self.game_map["drawing_zone"]):
            self.game_map["drawing_zone"][index] = coordinate[::-1]

        for index, coordinate in enumerate(self.game_map["table_corners"]):
            self.game_map["table_corners"][index] = coordinate[::-1]

        for obstacle in self.game_map["obstacles"]:
            obstacle[0] = obstacle[0][::-1]

        self.game_map["robot"][0] = self.game_map["robot"][0][::-1]
        self.game_map["robot"][1] = 90 - self.game_map["robot"][1]

    def send_robot_position(self):
        try:
            self.game_map["robot"] = self.main_vision.detect_robot_fast()

            self.evaluate_position_gap([self.game_map["robot"][0], time.time()])

            self.game_map["robot"][0] = self.game_map["robot"][0][::-1]
            self.game_map["robot"][1] = 90 - self.game_map["robot"][1]

            if self.robot_has_started:
                information = self.game_map["robot"]
                information.append(datetime.datetime.now())
                packet = Packet(packet_type=PacketType.POSITION, packet_data=information)
                self.telemetry.put_command(packet)

            self.world_controller.update_robot_position([self.main_vision.game_map_pixels["robot"][0]],
                                                        self.main_vision.game_map_pixels["base_robot"])
            self.world_controller.update_real_path(self.main_vision.game_map_pixels["robot"][0])
            self.world_controller.update_world_image(self.main_vision.actual_frame)

        except RobotNotFound:
            print("Robot not found")
            pass
        except PositionGap:
            print("Gap")
            pass

    def start_cycle_timer(self):
        self.main_controller.activate_timer()
        self.main_controller.update_console_log("READY TO START NEW CYCLE")
        self.robot_timer.timeout.connect(self.send_robot_position)
        self.robot_timer.setInterval(250)
        if not self.robot_timer.isActive():
            self.robot_timer.start()

    def stop_cycle_timer(self):
        self.main_controller.deactivate_timer()
        self.main_controller.update_console_log("STOPPED ACTUAL CYCLE")
        self.robot_timer.timeout.disconnect(self.send_robot_position)
        print("timer disconnected")
        if self.robot_timer.isActive():
            self.robot_timer.stop()

    def detect_static_items(self):
        if self.main_model.detect_static_items:
            self.main_model.detect_static_items = False
            drawing_zone_found = False
            while not drawing_zone_found:
                try:
                    if self.main_vision.detect_static_items():
                        drawing_zone_found = True
                    self.draw_game_map_on_ui(True)
                    self.world_view.fit_to_image()
                    self.main_view.ui.detect_static_items_btn.setEnabled(False)

                except DrawingZoneNotFound:
                    print("DrawingZoneNotFound")
                    continue

    def send_new_game_map(self):
        if self.main_model.send_new_game_map_flag:
            self.main_model.send_new_game_map_flag = False
            self.main_controller.update_console_log("SENDING GAME MAP")
            self.send_game_map()

    def evaluate_position_gap(self, new_position: list):
        if self.last_robot_information:
            max_gap = constants.ROBOT_SPEED * (abs(new_position[1] - self.last_robot_information[1]))
            gap = calculate_norm(new_position[0][0],
                                 new_position[0][1],
                                 self.last_robot_information[0][0],
                                 self.last_robot_information[0][1])
            if gap > max_gap:
                print("Detected gap {} < {}".format(gap, max_gap))
                raise PositionGap
            else:
                self.last_robot_information = new_position
        else:
            self.last_robot_information = new_position
