"""This is the main app class responsible for instantiating each of the views,
   controllers, and the model (and passing the references between them).
   Generally this is very minimal.
"""
import datetime
from PyQt5.QtWidgets import QApplication
from pkg_resources import resource_string
import numpy
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
        # will check if the robot has already sent the first notification saying it's ready
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

        self.main_model.subscribe_update_function(self.prepare_new_cycle)
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
        self.telemetry_timer.setInterval(1000)  # 1000 ms
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

    def prepare_new_cycle(self):
        """
        This function must be called only from the model to which it's subscribed
        Will call appropriate functions in the world vision and send off a updated game map
        and update the UI
        :return:
        """
        if self.main_model.start_new_cycle:
            try:
                # get game map and send to telemetry
                self.game_map = self.main_vision.get_new_cycle_game_map()
                game_map_packet = Packet(packet_type=PacketType.GAME_MAP, packet_data=self.game_map)
                self.telemetry.put_command(game_map_packet)

                # draw the game map on UI
                self.world_controller.reset_robot_real_path()
                game_map_in_pixels = self.main_vision.get_game_map_in_pixels()

                obstacles_coordinates = game_map_in_pixels["obstacles"]
                arranged_coordinates = []
                for information in obstacles_coordinates:
                    arranged_coordinates.append(information[0])

                self.world_controller.update_obstacles_coordinates(arranged_coordinates)

                self.world_controller.update_drawing_zone(game_map_in_pixels["drawing_zone"])

                self.world_controller.update_robot_position([game_map_in_pixels["robot"][0]])
                self.world_controller.update_world_image(self.main_vision.actual_frame)
                self.main_model.start_new_cycle = False

            except GameMapNotFound:
                print("Game map not found")

    def check_if_packet_received(self):
        """
        This checks if telemetry has received a new packet and if
        that's the case it will handle it
        :return:
        """
        received_packet = self.telemetry.fetch_command()
        if received_packet:
            self.packet_handler[received_packet.packet_type](received_packet.packet_data)
            print("type : {}, data type {}".format(received_packet.packet_type, type(received_packet.packet_data)))

    def handle_notification(self, notification: str):
        self.main_controller.update_console_log(notification)
        if not self.robot_has_started:
            self.send_initial_game_map()
            self.robot_has_started = True

    def handle_command(self, command: str):
        """
        command : START_CHRONOGRAPH or STOP_CHRONOGRAPH
        :param command:
        :return:
        """
        if command == "START_CHRONOGRAPH":
            self.start_cycle_timer()
        if command == "STOP_CHRONOGRAPH":
            self.stop_cycle_timer()

    def handle_figure_image(self, image: numpy.ndarray):
        self.painting_controller.update_world_image(image)

    def handle_figure_vertices(self, vertices: list):
        self.painting_controller.update_path(vertices)

    def handle_received_path(self, path: deque):
        self.world_controller.update_path(list(path))

    def send_initial_game_map(self):
        """
        Will be called when it's the first time we started the game, only the robot can send
        a packet containing the signal saying it's ready to start the game
        Then this function sends off the initial game map by telemetry and update the UI
        """
        game_map_found = False
        while not game_map_found:
            try:
                # get game map and send to telemetry
                self.game_map = self.main_vision.get_initial_game_map()
                if self.game_map:
                    game_map_found = True

                print(self.game_map)
                game_map_packet = Packet(packet_type=PacketType.GAME_MAP, packet_data=self.game_map)
                self.telemetry.put_command(game_map_packet)

                # draw the game map on UI
                game_map_in_pixels = self.main_vision.get_game_map_in_pixels()

                obstacles_coordinates = game_map_in_pixels["obstacles"]
                arranged_coordinates = []
                for information in obstacles_coordinates:
                    arranged_coordinates.append(information[0])

                self.world_controller.update_obstacles_coordinates(arranged_coordinates)

                self.world_controller.update_drawing_zone(game_map_in_pixels["drawing_zone"])

                self.world_controller.update_robot_position([game_map_in_pixels["robot"][0]])
                self.world_controller.update_world_image(self.main_vision.actual_frame)
            except GameMapNotFound:
                print("Game map not found")
                continue

    def send_robot_position(self):
        try:
            new_robot_information = self.main_vision.detect_robot()
            new_robot_information.append(datetime.datetime.now())
            position = Packet(packet_type=PacketType.POSITION, packet_data=new_robot_information)
            self.telemetry.put_command(position)
            self.world_controller.update_robot_position([self.main_vision.game_map_in_pixels["robot"][0]])
            self.world_controller.update_world_image(self.main_vision.actual_frame)
        except RobotNotFound:
            pass

    def start_cycle_timer(self):
        """
        Thats called when the robot is ready to go and begin its path
        Will update the UI with the path and start the chronograph
        :return:
        """
        self.main_controller.activate_timer()
        self.main_controller.update_console_log("READY TO START NEW CYCLE")
        self.telemetry_timer.timeout.connect(self.send_robot_position)

    def stop_cycle_timer(self):
        self.main_controller.deactivate_timer()
        self.main_controller.update_console_log("STOPPED ACTUAL CYCLE")
        self.telemetry_timer.timeout.disconnect(self.send_robot_position)
