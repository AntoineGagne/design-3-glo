""" Author: TREMBLAY, Alexandre
Last modified: February 25th, 2017

Unit tests for commands """

import datetime
from design.decision_making.commands import RoutineCheckCommand
from design.pathfinding.pathfinder import Pathfinder
from design.decision_making.constants import Step
from design.interfacing.interfacing_controller import InterfacingController
from design.interfacing.simulated_controllers import (SimulatedWheelsController,
                                                      SimulatedAntennaController,
                                                      SimulatedLightsController,
                                                      SimulatedPenController)
from design.pathfinding.robot_supposed_status import RobotSupposedStatus


def test_given_telemetry_indicating_contradicting_position_when_routine_check_is_executed_then_correct_trajectory():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    pathfinder.robot_status.time_since_moving = datetime.datetime.now()
    telemetry_position = (20, 27)
    hardware = InterfacingController(SimulatedWheelsController(),
                                     SimulatedAntennaController(),
                                     SimulatedPenController(),
                                     SimulatedLightsController())

    command = RoutineCheckCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder)
    command.execute(telemetry_position)

    assert hardware.wheels.last_vector_given == (10, 3)


def test_given_telemetry_indicating_coherent_positions_when_routine_is_executed_then_do_not_correct_trajectory():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    pathfinder.robot_status.time_since_moving = datetime.datetime.now()
    telemetry_position = (20.2, 20.1)
    hardware = InterfacingController(SimulatedWheelsController(),
                                     SimulatedAntennaController(),
                                     SimulatedPenController(),
                                     SimulatedLightsController())

    command = RoutineCheckCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder)
    command.execute(telemetry_position)

    assert hardware.wheels.last_vector_given is None
