""" Author: TREMBLAY, Alexandre
Last modified: February 24, 2017

Unit tests for the command dispatcher """

from design.decision_making.movement_strategy import MovementStrategy
from design.decision_making.command_dispatcher import CommandDispatcher
from design.decision_making.commands import (RoutineCheckCommand,
                                             RotatingCheckCommand)
from design.decision_making.constants import Step, TranslationStrategyType, RotationStrategyType


def test_when_no_matches_for_step_and_telemetry_command_get_relevant_command_returns_routine_check_command():

    command_dispatcher = CommandDispatcher(
        MovementStrategy(TranslationStrategyType.VERIFY_CONSTANTLY_THROUGH_CINEMATICS, None),
        None, None, None, None, None)

    command = command_dispatcher.get_relevant_command(None, None)

    assert isinstance(command, RoutineCheckCommand)


def test_when_step_is_rotation_towards_capture_get_relevant_command_returns_rotating_check_command():

    command_dispatcher = CommandDispatcher(
        MovementStrategy(None, RotationStrategyType.VERIFY_CONSTANTLY_THROUGH_ANGULAR_CINEMATICS),
        None, None, None, None, None)

    command = command_dispatcher.get_relevant_command(None, Step.ROTATE_TO_FACE_PAINTING)

    assert isinstance(command, RotatingCheckCommand)
