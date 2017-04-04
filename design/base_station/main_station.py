import datetime
from PyQt5.QtWidgets import QApplication
from pkg_resources import resource_string
from design.ui.views.main_view import MainView
from design.ui.controllers.main_controller import MainController
from design.ui.models.main_model import MainModel
from design.ui.models.world_model import WorldModel
from design.ui.controllers.world_controller import WorldController
from design.ui.views.world_view import WorldView
from design.ui.views.painting_view import PaintingView
from design.vision.world_vision import WorldVision
from design.vision.exceptions import RobotNotFound, GameMapNotFound
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
        self.first_game_map_flag = True
        self.game_map = None

        self.telemetry = telemetry
        self.main_vision = main_vision

        self.packet_handler = {PacketType.NOTIFICATION: self.handle_notification,
                               PacketType.COMMAND: self.handle_command,
                               PacketType.FIGURE_IMAGE: self.handle_figure_image,
                               PacketType.FIGURE_VERTICES: self.handle_figure_vertices,
                               PacketType.PATH: self.handle_received_path}

        self.main_model = MainModel()
        self.main_controller = MainController(self.main_model)
        self.main_view = MainView(self.main_model, self.main_controller)

        self.main_model.subscribe_update_function(self.find_robot)

        self.world_model = WorldModel()
        self.world_controller = WorldController(self.world_model)
        self.main_view.add_tab(WorldView(self.world_model, self.world_controller), "World Tab")

        self.painting_model = PaintingModel()
        self.painting_controller = PaintingController(self.painting_model)
        self.painting_view = PaintingView(self.painting_model, self.painting_controller)
        self.main_view.add_painting(self.painting_view)

        self.telemetry_timer = QTimer()

        self.setup_telemetry_timer()
        self._set_default_style()
        self.run_view()

    def setup_telemetry_timer(self):
        self.telemetry_timer.timeout.connect(self.check_if_packet_received)
        self.telemetry_timer.setInterval(250)
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
            self.main_model.start_new_cycle = True
            self.send_game_map()
            self.first_game_map_flag = False
            self.robot_has_started = True

    def handle_command(self, command: str):
        if command == "START_CHRONOGRAPH":
            self.start_cycle_timer()
        if command == "STOP_CHRONOGRAPH":
            self.stop_cycle_timer()

    def handle_figure_image(self):
        self.main_controller.update_console_log("ONBOARD IMAGE RECEIVED")

    def handle_figure_vertices(self, vertices: list):
        self.painting_controller.update_path(vertices)

    def handle_received_path(self, path: deque):
        new_path = list(path)
        path_converted = []
        for coordinate in new_path:
            path_converted.append(
                self.main_vision.converter.get_pixel_coordinates_translated(coordinate[1], coordinate[0], 0))
        self.world_controller.update_path(path_converted)

    def send_game_map(self):
        if self.main_model.start_new_cycle:
            game_map_found = False
            while not game_map_found:
                try:
                    self.game_map = self.main_vision.get_new_cycle_game_map(self.first_game_map_flag)
                    if self.game_map:
                        game_map_found = True

                    self.world_controller.reset_robot_real_path()
                    self.change_axes(self.first_game_map_flag)

                    game_map_packet = Packet(packet_type=PacketType.GAME_MAP, packet_data=self.game_map)
                    self.telemetry.put_command(game_map_packet)

                    self.draw_game_map_on_ui()

                    self.first_game_map_flag = False

                except GameMapNotFound:
                    print("Game map not found")
                    continue

    def draw_game_map_on_ui(self):
        obstacles_coordinates = self.main_vision.game_map["obstacles"]
        arranged_coordinates = []
        for information in obstacles_coordinates:
            arranged_coordinates.append(information[0])
        self.world_controller.update_obstacles_coordinates(arranged_coordinates)
        self.world_controller.update_game_zone_coordinates(self.main_vision.game_map["table_corners"])
        self.world_controller.update_drawing_zone(self.main_vision.game_map["drawing_zone"])
        self.world_controller.update_robot_position([self.main_vision.game_map["robot"][0]])
        self.world_controller.update_world_image(self.main_vision.actual_frame)

    def change_axes(self, first_time: bool = True):
        if first_time:
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
            new_robot_information = self.main_vision.detect_robot_fast()

            self.game_map["robot"][0] = new_robot_information[0][::-1]
            self.game_map["robot"][1] = 90 - new_robot_information[1]

            new_robot_information.append(datetime.datetime.now())
            position = Packet(packet_type=PacketType.POSITION, packet_data=new_robot_information)
            self.telemetry.put_command(position)

            self.world_controller.update_robot_position([self.main_vision.game_map["robot"][0]])
            self.world_controller.update_world_image(self.main_vision.actual_frame)

        except RobotNotFound:
            pass

    def start_cycle_timer(self):
        self.main_controller.activate_timer()
        self.main_controller.update_console_log("READY TO START NEW CYCLE")
        self.telemetry_timer.timeout.connect(self.send_robot_position)

    def stop_cycle_timer(self):
        self.main_controller.deactivate_timer()
        self.main_controller.update_console_log("STOPPED ACTUAL CYCLE")
        self.telemetry_timer.timeout.disconnect(self.send_robot_position)
