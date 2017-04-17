""" This module contains a movement strategy class
that allows injection of a correct movement strategy
for various test and integration cases much more easily """

from design.decision_making.constants import TranslationStrategyType, RotationStrategyType
from design.decision_making.rotation_commands import RotationCheckCommand, TrustingRotationCheckCommand
from design.decision_making.translation_commands import TranslationCheckCommand, TranslationCheckWithoutTelemetryCommand


class MovementStrategy():

    def __init__(self, translation_strategy_type, rotation_strategy_type):
        self.translation_strategy = translation_strategy_type
        self.rotation_strategy = rotation_strategy_type

    def get_translation_command(self, current_step, interfacing_controller, pathfinder, logger, servo_wheels_manager):

        if self.translation_strategy == TranslationStrategyType.BASIC_WHEEL_SERVOING:
            return TranslationCheckCommand(current_step, interfacing_controller,
                                           pathfinder, logger, servo_wheels_manager)
        elif self.translation_strategy == TranslationStrategyType.TRUST_MATERIAL_SERVOING:
            return TranslationCheckWithoutTelemetryCommand(current_step, interfacing_controller, pathfinder, logger,
                                                           servo_wheels_manager)

    def get_rotation_command(self, current_step, interfacing_controller, pathfinder, logger, servo_wheels_manager):

        if self.rotation_strategy == RotationStrategyType.BASIC_WHEEL_SERVOING:
            return RotationCheckCommand(current_step, interfacing_controller, pathfinder, logger, servo_wheels_manager)
        elif self.rotation_strategy == RotationStrategyType.TRUST_MATERIAL_SERVOING:
            return TrustingRotationCheckCommand(current_step, interfacing_controller, pathfinder, logger,
                                                servo_wheels_manager)
