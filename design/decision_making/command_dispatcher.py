""" Author: TREMBLAY, Alexandre
Last modified: Febuary 3rd, 2017

Allows easy and modular computing for the execution
of each step """

from design.decision_making.constants import Step
from design.decision_making.commands import (BuildGameMapCommand,
                                             RoutineCheckCommand,
                                             FinishCycleCommand,
                                             TravelToPaintingsAreaCommand,
                                             PrepareSearchForAntennaPositionCommand,
                                             SearchForAntennaPositionCommand,
                                             PrepareMarkingAntennaCommand,
                                             PrepareTravelToDrawingAreaCommand,
                                             PrepareToDrawCommand,
                                             AcquireInformationFromAntennaCommand,
                                             PrepareExitOfDrawingAreaCommand,
                                             RotatingCheckCommand,
                                             FaceRelevantFigureForCaptureCommand,
                                             CaptureFigureCommand,
                                             PrepareTravelToAntennaAreaCommand)


class CommandDispatcher():
    """ Allows easy dispatching and computing of commands for the Brain """

    def __init__(self, interfacing_controller, pathfinder, onboard_vision, antenna_info):

        self.interfacing_controller = interfacing_controller
        self.pathfinder = pathfinder

        self.equivalencies = {('GAME_MAP_DATA', Step.STANBY):
                              BuildGameMapCommand(
                                  Step.STANBY, interfacing_controller, pathfinder),
                              (None, Step.ROTATE_TO_STANDARD_HEADING):
                              RotatingCheckCommand(
                                  Step.ROTATE_TO_STANDARD_HEADING, interfacing_controller,
                                  pathfinder),
                              (None, Step.PREPARE_TRAVEL_TO_ANTENNA_ZONE):
                              PrepareTravelToAntennaAreaCommand(
                                  Step.PREPARE_TRAVEL_TO_ANTENNA_ZONE, interfacing_controller,
                                  pathfinder),
                              (None, Step.TERMINATE_SEQUENCE):
                              FinishCycleCommand(
                                  Step.TERMINATE_SEQUENCE, interfacing_controller, pathfinder),
                              (None, Step.COMPUTE_PAINTINGS_AREA): TravelToPaintingsAreaCommand(
                                  Step.COMPUTE_PAINTINGS_AREA, interfacing_controller,
                                  pathfinder),
                              (None, Step.PREPARE_SEARCH_FOR_ANTENNA):
                              PrepareSearchForAntennaPositionCommand(
                                  Step.PREPARE_SEARCH_FOR_ANTENNA, interfacing_controller,
                                  pathfinder),
                              (None, Step.SEARCH_FOR_ANTENNA):
                              SearchForAntennaPositionCommand(
                                  Step.SEARCH_FOR_ANTENNA, interfacing_controller,
                                  pathfinder),
                              (None, Step.PREPARE_MARKING_ANTENNA_POSITION):
                              PrepareMarkingAntennaCommand(
                                  Step.PREPARE_MARKING_ANTENNA_POSITION, interfacing_controller,
                                  pathfinder),
                              (None, Step.ACQUIRE_INFORMATION_FROM_ANTENNA):
                              AcquireInformationFromAntennaCommand(
                                  Step.ACQUIRE_INFORMATION_FROM_ANTENNA, interfacing_controller,
                                  pathfinder, antenna_info),
                              (None, Step.PREPARE_TRAVEL_TO_DRAWING_ZONE):
                              PrepareTravelToDrawingAreaCommand(
                                  Step.PREPARE_TRAVEL_TO_DRAWING_ZONE, interfacing_controller,
                                  pathfinder, onboard_vision, antenna_info),
                              (None, Step.PREPARE_TO_DRAW):
                              PrepareToDrawCommand(
                                  Step.PREPARE_TO_DRAW, interfacing_controller,
                                  pathfinder, onboard_vision, antenna_info),
                              (None, Step.PREPARE_EXIT_OF_DRAWING_ZONE):
                              PrepareExitOfDrawingAreaCommand(
                                  Step.PREPARE_EXIT_OF_DRAWING_ZONE, interfacing_controller,
                                  pathfinder),
                              (None, Step.PREPARE_CAPTURE_OF_PAINTING):
                              FaceRelevantFigureForCaptureCommand(
                                  Step.PREPARE_CAPTURE_OF_PAINTING, interfacing_controller,
                                  pathfinder, antenna_info),
                              (None, Step.ROTATE_TO_FACE_PAINTING):
                              RotatingCheckCommand(
                                  Step.ROTATE_TO_FACE_PAINTING, interfacing_controller,
                                  pathfinder),
                              (None, Step.CAPTURE_CORRECT_PAINTING):
                              CaptureFigureCommand(
                                  Step.CAPTURE_CORRECT_PAINTING, interfacing_controller,
                                  pathfinder, antenna_info, onboard_vision),
                              (None, Step.ROTATE_BACK_AFTER_CAPTURE):
                              RotatingCheckCommand(
                                  Step.ROTATE_BACK_AFTER_CAPTURE, interfacing_controller,
                                  pathfinder)}

    def get_relevant_command(self, command_name, current_step):
        """ Returns relevant command according to cmd_name and args"""

        command = self.equivalencies.get((command_name, current_step))
        if command:
            return command
        else:
            return RoutineCheckCommand(current_step, self.interfacing_controller, self.pathfinder)
