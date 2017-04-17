""" Author: TREMBLAY, Alexandre
Last modified: February 24, 2017

Unit tests for the command dispatcher """

from design.decision_making.movement_strategy import MovementStrategy
from design.decision_making.command_dispatcher import CommandDispatcher
from design.decision_making.constants import Step, TranslationStrategyType, RotationStrategyType
from design.decision_making.rotation_commands import TrustingRotationCheckCommand
from design.decision_making.translation_commands import TranslationCheckCommand


def test_when_no_matches_for_step_and_telemetry_command_get_relevant_command_returns_translation_check_command():

    command_dispatcher = CommandDispatcher(
        MovementStrategy(TranslationStrategyType.BASIC_WHEEL_SERVOING, None),
        None, None, None, None, None, None, None)

    command = command_dispatcher.get_relevant_command(None)

    assert isinstance(command, TranslationCheckCommand)


def test_when_step_is_rotation_towards_capture_get_relevant_command_returns_trusting_rotation_check_command():

    command_dispatcher = CommandDispatcher(
        MovementStrategy(None, RotationStrategyType.BASIC_WHEEL_SERVOING),
        None, None, None, None, None, None, None)

    command = command_dispatcher.get_relevant_command(Step.ROTATE_TO_FACE_PAINTING)

    assert isinstance(command, TrustingRotationCheckCommand)
