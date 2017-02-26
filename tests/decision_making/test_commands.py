""" Author: TREMBLAY, Alexandre
Last modified: February 25th, 2017

Unit tests for commands """

import datetime
from design.decision_making.commands import RoutineCheckCommand
from design.pathfinding.pathfinder import Pathfinder
from design.pathfinding.mutable_position import MutablePosition
from design.decision_making.constants import Step
from design.interfacing.interfacing_controller import InterfacingController


def test_given_telemetry_indicating_contradicting_position_when_routine_check_is_executed_then_correct_trajectory():
    """ Given telemetry that indicates that the supposed position and the real position are
    contradictory, RoutineCheckCommand will correct the trajectory towards the next node """

    pathfinder = Pathfinder()
    pathfinder.supposed_robot_position = MutablePosition(20, 20)
    pathfinder.next_node = (30, 30)
    pathfinder.time_since_moving = datetime.datetime.now()
    telemetry_position = (20, 27)
    hardware = InterfacingController()

    command = RoutineCheckCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder)
    command.execute(telemetry_position)

    assert hardware.wheels.last_vector_given == (10, 3)


def test_given_telemetry_indicating_coherent_positions_when_routine_is_executed_then_do_not_correct_trajectory():
    """ Given telemetry that indicates that both the supposed position and the real position
    are coherent with each other, RoutineCheckCommand will NOT correct the trajectory """

    pathfinder = Pathfinder()
    pathfinder.supposed_robot_position = MutablePosition(20, 20)
    pathfinder.next_node = (30, 30)
    pathfinder.time_since_moving = datetime.datetime.now()
    telemetry_position = (20.2, 20.1)
    hardware = InterfacingController()

    command = RoutineCheckCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder)
    command.execute(telemetry_position)

    assert hardware.wheels.last_vector_given is None
