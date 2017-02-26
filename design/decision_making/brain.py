""" Author: TREMBLAY, Alexandre
Last modified: Febuary 2nd, 2017

This module contains the decisional center of the robotic platform"""

from design.interfacing.interfacing_controller import InterfacingController
from design.telemetry.telemetry_mock import TelemetryMock
from design.decision_making.constants import Step
from design.decision_making.command_dispatcher import CommandDispatcher
from design.pathfinding.pathfinder import Pathfinder
from design.vision.onboard_vision_mock import OnboardVisionMock
from design.pathfinding.antenna_information import AntennaInformation


class Brain():
    """Controls decisionmaking of the robot"""

    def __init__(self):
        """Initializes robot on STANBY mode, waiting for game map objects
        to be transmitted in order to start its routine"""

        self.current_status = Step.STANBY
        self.base_station = TelemetryMock()
        self.dispatcher = CommandDispatcher(
            InterfacingController(), Pathfinder(), OnboardVisionMock(), AntennaInformation())

    def main(self):
        """Main loop of the robot. Polls on telemetry and acts according
        to what it recieves."""

        self.base_station.bind(8080)

        main_sequence_has_started = False

        while True:

            telemetry_command, telemetry_data = self.base_station.poll()
            if telemetry_command == "GAME_MAP_DATA":
                main_sequence_has_started = True

            if main_sequence_has_started:

                command = self.dispatcher.get_relevant_command(telemetry_command,
                                                               self.current_status)

                next_status, exit_telemetry = command.execute(telemetry_data)
                self.current_status = next_status

                if exit_telemetry:
                    self.base_station.send(exit_telemetry)

                if self.current_status == Step.STANBY:
                    # Redébuter un cycle en attendant les données de jeu
                    main_sequence_has_started = False

        self.current_status = Step.STANBY
