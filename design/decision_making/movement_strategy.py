""" This module contains a movement strategy class
that allows injection of a correct movement strategy
for various test and integration cases much more easily """

from design.decision_making.constants import TranslationStrategyType, RotationStrategyType
from design.decision_making.commands import (RoutineCheckCommand,
                                             RotatingCheckCommand,
                                             RotatingCheckThroughTelemetryCommand,
                                             RoutineCheckWithVisualServoManagementCommand)


class MovementStrategy():
    """ Allows injection of a correct movement strategy
    for various test and integration cases much more easily """

    def __init__(self, translation_strategy_type, rotation_strategy_type):
        self.translation_strategy = translation_strategy_type
        self.rotation_strategy = rotation_strategy_type

    def get_translation_command(self, current_step, interfacing_controller, pathfinder, servo_wheels_manager):

        if self.translation_strategy == TranslationStrategyType.VERIFY_CONSTANTLY_THROUGH_CINEMATICS:
            return RoutineCheckCommand(current_step, interfacing_controller, pathfinder)
        elif self.translation_strategy == TranslationStrategyType.VERIFY_ONLY_ON_TELEMETRY_RECEPTION:
            return RoutineCheckWithVisualServoManagementCommand(current_step, interfacing_controller,
                                                                pathfinder, servo_wheels_manager)

    def get_rotation_command(self, current_step, interfacing_controller, pathfinder):

        if self.rotation_strategy == RotationStrategyType.VERIFY_CONSTANTLY_THROUGH_ANGULAR_CINEMATICS:
            return RotatingCheckCommand(current_step, interfacing_controller, pathfinder)
        elif self.rotation_strategy == RotationStrategyType.VERIFY_ONLY_ON_TELEMETRY_RECEPTION:
            return RotatingCheckThroughTelemetryCommand(current_step, interfacing_controller, pathfinder)
