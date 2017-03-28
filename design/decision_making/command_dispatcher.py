""" Allows easy and modular computing for the execution
of each step """

from design.decision_making.constants import Step
from design.decision_making.commands import (BuildGameMapCommand,
                                             FinishCycleCommand,
                                             TravelToPaintingsAreaCommand,
                                             PrepareSearchForAntennaPositionCommand,
                                             SearchForAntennaPositionCommand,
                                             PrepareMarkingAntennaCommand,
                                             PrepareTravelToDrawingAreaCommand,
                                             PrepareToDrawCommand,
                                             AcquireInformationFromAntennaCommand,
                                             PrepareExitOfDrawingAreaCommand,
                                             FaceRelevantFigureForCaptureCommand,
                                             CaptureFigureCommand,
                                             PrepareTravelToAntennaAreaCommand,
                                             PrepareMovingToAntennaPositionCommand)
from design.telemetry.packets import PacketType


class CommandDispatcher():
    """ Allows easy dispatching and computing of commands for the Brain """

    def __init__(self, movement_strategies, interfacing_controller, pathfinder,
                 onboard_vision, antenna_information):

        self.movement_strategy = movement_strategies
        self.interfacing_controller = interfacing_controller
        self.pathfinder = pathfinder

        self.steps_using_rotation = [Step.ROTATE_BACK_AFTER_CAPTURE,
                                     Step.ROTATE_TO_FACE_PAINTING,
                                     Step.ROTATE_TO_STANDARD_HEADING]

        self.equivalencies = {(PacketType.GAME_MAP, Step.STANBY):
                              BuildGameMapCommand(
                                  Step.STANBY, interfacing_controller, pathfinder),
                              (None, Step.PREPARE_TRAVEL_TO_ANTENNA_ZONE):
                              PrepareTravelToAntennaAreaCommand(
                                  Step.PREPARE_TRAVEL_TO_ANTENNA_ZONE, interfacing_controller,
                                  pathfinder),
                              (None, Step.TERMINATE_SEQUENCE):
                              FinishCycleCommand(
                                  Step.TERMINATE_SEQUENCE, interfacing_controller, pathfinder),
                              (None, Step.COMPUTE_PAINTINGS_AREA): TravelToPaintingsAreaCommand(
                                  Step.COMPUTE_PAINTINGS_AREA, interfacing_controller,
                                  pathfinder, antenna_information),
                              (None, Step.PREPARE_SEARCH_FOR_ANTENNA):
                              PrepareSearchForAntennaPositionCommand(
                                  Step.PREPARE_SEARCH_FOR_ANTENNA, interfacing_controller,
                                  pathfinder),
                              (None, Step.SEARCH_FOR_ANTENNA):
                              SearchForAntennaPositionCommand(
                                  movement_strategies, Step.SEARCH_FOR_ANTENNA, interfacing_controller,
                                  pathfinder, antenna_information),
                              (None, Step.PREPARE_MOVING_TO_ANTENNA_POSITION):
                              PrepareMovingToAntennaPositionCommand(
                                  Step.PREPARE_MOVING_TO_ANTENNA_POSITION, interfacing_controller, pathfinder,
                              antenna_information),
                              (None, Step.PREPARE_MARKING_ANTENNA_POSITION):
                              PrepareMarkingAntennaCommand(
                                  Step.PREPARE_MARKING_ANTENNA_POSITION, interfacing_controller,
                                  pathfinder, antenna_information),
                              (None, Step.ACQUIRE_INFORMATION_FROM_ANTENNA):
                              AcquireInformationFromAntennaCommand(
                                  Step.ACQUIRE_INFORMATION_FROM_ANTENNA, interfacing_controller,
                                  pathfinder, antenna_information),
                              (None, Step.PREPARE_TRAVEL_TO_DRAWING_ZONE):
                              PrepareTravelToDrawingAreaCommand(
                                  Step.PREPARE_TRAVEL_TO_DRAWING_ZONE, interfacing_controller,
                                  pathfinder, onboard_vision, antenna_information),
                              (None, Step.PREPARE_TO_DRAW):
                              PrepareToDrawCommand(
                                  Step.PREPARE_TO_DRAW, interfacing_controller,
                                  pathfinder, onboard_vision, antenna_information),
                              (None, Step.PREPARE_EXIT_OF_DRAWING_ZONE):
                              PrepareExitOfDrawingAreaCommand(
                                  Step.PREPARE_EXIT_OF_DRAWING_ZONE, interfacing_controller,
                                  pathfinder),
                              (None, Step.PREPARE_CAPTURE_OF_PAINTING):
                              FaceRelevantFigureForCaptureCommand(
                                  Step.PREPARE_CAPTURE_OF_PAINTING, interfacing_controller,
                                  pathfinder, antenna_information),
                              (None, Step.CAPTURE_CORRECT_PAINTING):
                              CaptureFigureCommand(
                                  Step.CAPTURE_CORRECT_PAINTING, interfacing_controller,
                                  pathfinder, antenna_information, onboard_vision)}

    def get_relevant_command(self, packet_type, current_step):
        """ Obtains the relevant command according to the telemetry packet
        type and the current step of the robot

        :param packet_type: Type of the recieved telemetry packet
        :param current_step: Current step of the robot
        :returns: Command to execute
        :rtype: `design.decision_making.commands.Command` """

        command = self.equivalencies.get((packet_type, current_step))
        if command:
            return command
        elif current_step in self.steps_using_rotation:
            return self.movement_strategy.get_rotation_command(
                current_step, self.interfacing_controller, self.pathfinder)
        else:
            return self.movement_strategy.get_translation_command(
                current_step, self.interfacing_controller, self.pathfinder)
