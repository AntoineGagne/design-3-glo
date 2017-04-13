""" This module contains the decisional center of the robotic platform """

from design.decision_making.constants import Step
from design.decision_making.command_dispatcher import CommandDispatcher
from design.pathfinding.capture_repositioning_manager import CaptureRepositioningManager
from design.pathfinding.pathfinder import Pathfinder
from design.pathfinding.antenna_information import AntennaInformation
from design.pathfinding.servo_wheels_manager import ServoWheelsManager
from design.telemetry.packets import PacketType, Packet


class Brain():
    """Controls decisionmaking of the robot"""

    def __init__(self, telemetry, interfacing_controller, logger, onboard_vision, movement_strategies, translation_lock,
                 rotation_lock):
        """Initializes robot on STANBY mode, waiting for game map objects
        to be transmitted in order to start its routine"""

        self.logger = logger
        self.pathfinder = Pathfinder(logger)
        self.antenna_information = AntennaInformation()
        self.current_status = Step.STANBY
        self.base_station = telemetry
        self.servo_wheels_manager = ServoWheelsManager(translation_lock, rotation_lock, logger)
        self.capture_repositioning_manager = CaptureRepositioningManager()
        self.interfacing_controller = interfacing_controller

        self.dispatcher = CommandDispatcher(
            movement_strategies, self.interfacing_controller, self.pathfinder, logger,
            onboard_vision, self.antenna_information, self.servo_wheels_manager,
            self.capture_repositioning_manager)

    def main(self):
        """Main loop of the robot. Polls on telemetry and acts according
        to what it recieves."""

        main_sequence_has_started = False

        ready_packet = Packet(PacketType.NOTIFICATION,
                              "STANDBY - Robot ready to roll! Cycle start when GAME_MAP is recieved.")
        self.base_station.put_command(ready_packet)

        while True:

            telemetry_recieved = self.base_station.fetch_command()
            if telemetry_recieved:
                if telemetry_recieved.packet_type == PacketType.GAME_MAP:
                    cycle_start_notification = Packet(PacketType.COMMAND, "START_CHRONOGRAPH")
                    self.base_station.put_command(cycle_start_notification)
                    main_sequence_has_started = True

            if main_sequence_has_started:

                telemetry_data = None
                if telemetry_recieved:
                    telemetry_data = telemetry_recieved.packet_data

                command = self.dispatcher.get_relevant_command(self.current_status)

                next_status, exit_telemetry = command.execute(telemetry_data)
                self.current_status = next_status

                if exit_telemetry:
                    if isinstance(exit_telemetry, list):
                        for exit_packet in exit_telemetry:
                            self.base_station.put_command(exit_packet)
                    elif isinstance(exit_telemetry, Packet):
                        self.base_station.put_command(exit_telemetry)

                if self.current_status == Step.STANBY:
                    self.base_station.put_command(ready_packet)
                    main_sequence_has_started = False
                    self.reinitialize_for_next_cycle()

    def reinitialize_for_next_cycle(self):
        self.logger.log("Reinitializing for next cycle")
        self.pathfinder.reinitialize()
        self.servo_wheels_manager.reinitialize()
        self.interfacing_controller.antenna.reinitialize()
        self.interfacing_controller.wheels.reinitialize()
        self.capture_repositioning_manager.reinitialize()
        self.antenna_information = AntennaInformation()
