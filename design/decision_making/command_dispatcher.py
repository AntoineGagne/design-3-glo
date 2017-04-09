""" Allows easy and modular computing for the execution
of each step """

from design.decision_making.constants import Step, TranslationStrategyType
from design.decision_making.preparation_commands import (BuildGameMapCommand,
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
                                                         PrepareMovingToAntennaPositionCommand,
                                                         RepositionForCaptureRetryCommand)


class CommandDispatcher():
    """ Allows easy dispatching and computing of commands for the Brain """

    def __init__(self, movement_strategies, interfacing_controller, pathfinder, logger,
                 onboard_vision, antenna_information, servo_wheels_manager, capture_repositioning_manager):

        self.movement_strategy = movement_strategies
        self.interfacing_controller = interfacing_controller
        self.pathfinder = pathfinder
        self.logger = logger
        self.servo_wheels_manager = servo_wheels_manager

        self.steps_using_rotation = [Step.ROTATE_BACK_AFTER_CAPTURE,
                                     Step.ROTATE_TO_FACE_PAINTING,
                                     Step.ROTATE_TO_STANDARD_HEADING]

        self.equivalencies = {Step.STANBY:
                              BuildGameMapCommand(
                                  Step.STANBY, interfacing_controller, pathfinder, logger),
                              Step.PREPARE_TRAVEL_TO_ANTENNA_ZONE:
                              PrepareTravelToAntennaAreaCommand(
                                  Step.PREPARE_TRAVEL_TO_ANTENNA_ZONE, interfacing_controller,
                                  pathfinder, logger),
                              Step.TERMINATE_SEQUENCE:
                              FinishCycleCommand(
                                  Step.TERMINATE_SEQUENCE, interfacing_controller, pathfinder, logger),
                              Step.COMPUTE_PAINTINGS_AREA: TravelToPaintingsAreaCommand(
                                  Step.COMPUTE_PAINTINGS_AREA, interfacing_controller,
                                  pathfinder, logger, antenna_information),
                              Step.PREPARE_SEARCH_FOR_ANTENNA:
                              PrepareSearchForAntennaPositionCommand(
                                  Step.PREPARE_SEARCH_FOR_ANTENNA, interfacing_controller,
                                  pathfinder, logger),
                              Step.SEARCH_FOR_ANTENNA:
                              SearchForAntennaPositionCommand(
                                  movement_strategies, Step.SEARCH_FOR_ANTENNA, interfacing_controller,
                                  pathfinder, logger, antenna_information, servo_wheels_manager),
                              Step.PREPARE_MOVING_TO_ANTENNA_POSITION:
                              PrepareMovingToAntennaPositionCommand(
                                  Step.PREPARE_MOVING_TO_ANTENNA_POSITION, interfacing_controller, pathfinder, logger,
                                  antenna_information),
                              Step.PREPARE_MARKING_ANTENNA_POSITION:
                              PrepareMarkingAntennaCommand(
                                  Step.PREPARE_MARKING_ANTENNA_POSITION, interfacing_controller,
                                  pathfinder, logger, antenna_information),
                              Step.ACQUIRE_INFORMATION_FROM_ANTENNA:
                              AcquireInformationFromAntennaCommand(
                                  Step.ACQUIRE_INFORMATION_FROM_ANTENNA, interfacing_controller,
                                  pathfinder, logger, antenna_information),
                              Step.PREPARE_TRAVEL_TO_DRAWING_ZONE:
                              PrepareTravelToDrawingAreaCommand(
                                  Step.PREPARE_TRAVEL_TO_DRAWING_ZONE, interfacing_controller,
                                  pathfinder, logger, onboard_vision, antenna_information),
                              Step.PREPARE_TO_DRAW:
                              PrepareToDrawCommand(
                                  Step.PREPARE_TO_DRAW, interfacing_controller,
                                  pathfinder, logger, onboard_vision, antenna_information),
                              Step.PREPARE_EXIT_OF_DRAWING_ZONE:
                              PrepareExitOfDrawingAreaCommand(
                                  Step.PREPARE_EXIT_OF_DRAWING_ZONE, interfacing_controller,
                                  pathfinder, logger),
                              Step.PREPARE_CAPTURE_OF_PAINTING:
                              FaceRelevantFigureForCaptureCommand(
                                  Step.PREPARE_CAPTURE_OF_PAINTING, interfacing_controller,
                                  pathfinder, logger, antenna_information),
                              Step.CAPTURE_CORRECT_PAINTING:
                              CaptureFigureCommand(
                                  Step.CAPTURE_CORRECT_PAINTING, interfacing_controller,
                                  pathfinder, logger, antenna_information, onboard_vision),
                              Step.REPOSITION_FOR_CAPTURE_RETRY:
                              RepositionForCaptureRetryCommand(Step.REPOSITION_FOR_CAPTURE_RETRY, interfacing_controller,
                                                               pathfinder, logger, capture_repositioning_manager)}

    def get_relevant_command(self, current_step):
        """ Obtains the relevant command according to the current step of the robot

        :param current_step: Current step of the robot
        :returns: Command to execute
        :rtype: `design.decision_making.preparation_commands.Command` """

        if current_step == Step.PREPARE_TO_DRAW:
            self.movement_strategy.translation_strategy = TranslationStrategyType.TRUST_MATERIAL_SERVOING

        command = self.equivalencies.get(current_step)
        if command:
            return command
        elif current_step in self.steps_using_rotation:
            return self.movement_strategy.get_rotation_command(
                current_step, self.interfacing_controller, self.pathfinder, self.logger, self.servo_wheels_manager)
        else:
            return self.movement_strategy.get_translation_command(
                current_step, self.interfacing_controller, self.pathfinder, self.logger, self.servo_wheels_manager)
