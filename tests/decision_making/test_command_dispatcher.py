""" Author: TREMBLAY, Alexandre
Last modified: February 24, 2017

Unit tests for the command dispatcher """

from design.decision_making.command_dispatcher import CommandDispatcher
from design.decision_making.commands import (RoutineCheckCommand,
                                             RotatingCheckCommand)
from design.decision_making.constants import Step


def test_when_no_matches_for_step_and_telemetry_command_get_relevant_command_returns_routine_check_command():
    """ Given no matches in the command dispatcher for the telemetry command recieved and the
    current step, return the RoutineCheckCommand """

    command_dispatcher = CommandDispatcher(None, None, None, None)

    command = command_dispatcher.get_relevant_command(None, None)

    assert isinstance(command, RoutineCheckCommand)


def test_when_step_is_rotation_towards_capture_get_relevant_command_returns_rotating_check_command():
    """ Given the step being rotate towards the figure, get_relevant_command returns
    RotatingCheckCommand """

    command_dispatcher = CommandDispatcher(None, None, None, None)

    command = command_dispatcher.get_relevant_command(None, Step.ROTATE_TO_FACE_PAINTING)

    assert isinstance(command, RotatingCheckCommand)
