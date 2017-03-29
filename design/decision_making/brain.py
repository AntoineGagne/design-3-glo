""" This module contains the decisional center of the robotic platform """

from design.decision_making.constants import Step
from design.decision_making.command_dispatcher import CommandDispatcher
from design.pathfinding.pathfinder import Pathfinder
from design.pathfinding.antenna_information import AntennaInformation
from design.pathfinding.servo_wheels_manager import ServoWheelsManager
from design.telemetry.packets import PacketType, Packet


class Brain():
    """Controls decisionmaking of the robot"""

    def __init__(self, telemetry, interfacing_controller, onboard_vision, movement_strategies):
        """Initializes robot on STANBY mode, waiting for game map objects
        to be transmitted in order to start its routine"""

        self.current_status = Step.STANBY
        self.base_station = telemetry
        self.dispatcher = CommandDispatcher(
            movement_strategies, interfacing_controller, Pathfinder(),
            onboard_vision, AntennaInformation(), ServoWheelsManager())

    def main(self):
        """Main loop of the robot. Polls on telemetry and acts according
        to what it recieves."""

        main_sequence_has_started = False

        ready_packet = Packet(PacketType.NOTIFICATION,
                              "STANDBY - Robot ready to roll! Cycle start when GAME_MAP is recieved.")
        self.base_station.put_command(ready_packet)

        while True:

            telemetry_recieved = self.base_station.fetch_command()
            if telemetry_recieved and telemetry_recieved.packet_type == PacketType.GAME_MAP:
                cycle_start_notification = Packet(PacketType.COMMAND, "START_CHRONOGRAPH")
                self.base_station.put_command(cycle_start_notification)
                main_sequence_has_started = True

            if main_sequence_has_started:

                command = self.dispatcher.get_relevant_command(telemetry_recieved.packet_type,
                                                               self.current_status)

                next_status, exit_telemetry = command.execute(telemetry_recieved.packet_data)
                self.current_status = next_status

                if exit_telemetry:
                    self.base_station.put_command(exit_telemetry)

                if self.current_status == Step.STANBY:
                    # Redébuter un cycle en attendant les données de jeu
                    # Missing reinit of some objects
                    self.base_station.put_command(ready_packet)
                    main_sequence_has_started = False

        self.current_status = Step.STANBY
