""" Author: TREMBLAY, Alexandre
Last modified: February 25th, 2017

Unit tests for commands """

import datetime
import time
from design.decision_making.commands import RoutineCheckWithVisualServoManagementCommand
from design.pathfinding.pathfinder import Pathfinder
from design.decision_making.constants import Step
from design.interfacing.interfacing_controller import InterfacingController
from design.interfacing.simulated_controllers import (SimulatedWheelsController,
                                                      SimulatedAntennaController,
                                                      SimulatedLightsController,
                                                      SimulatedPenController)
from design.pathfinding.robot_supposed_status import RobotSupposedStatus
from design.pathfinding.servo_wheels_manager import ServoWheelsManager
from design.telemetry.packets import PacketType


def test_given_telemetry_position_indicating_translation_deviation_while_traveling_routine_check_corrects_trajectory():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    time.sleep(1)

    telemetry_position = [(25.5, 24), 90, datetime.datetime.now()]
    hardware = InterfacingController(SimulatedWheelsController(),
                                     SimulatedAntennaController(),
                                     SimulatedPenController(),
                                     SimulatedLightsController())

    routine_check_command = RoutineCheckWithVisualServoManagementCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder, ServoWheelsManager())
    step, return_telemetry = routine_check_command.execute(telemetry_position)

    assert hardware.wheels.last_vector_given == (4.5, 6)
    assert step == Step.TRAVEL_TO_ANTENNA_ZONE
    assert return_telemetry.packet_type == PacketType.PATH


def test_given_telemetry_position_indicating_no_translation_deviation_while_traveling_routine_check_carries_on():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    time.sleep(1)

    telemetry_position = [(24, 24), 90, datetime.datetime.now()]
    hardware = InterfacingController(SimulatedWheelsController(),
                                     SimulatedAntennaController(),
                                     SimulatedPenController(),
                                     SimulatedLightsController())

    routine_check_command = RoutineCheckWithVisualServoManagementCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder, ServoWheelsManager())
    step, return_telemetry = routine_check_command.execute(telemetry_position)

    assert hardware.wheels.last_vector_given is None
    assert step == Step.TRAVEL_TO_ANTENNA_ZONE
    assert return_telemetry is None


def test_given_telemetry_position_indicating_it_has_stopped_routine_check_builds_new_vector_to_reach_target():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)

    previous_telemetry_position = [(24, 24), 90, datetime.datetime.now()]
    time.sleep(1)
    telemetry_position = [(24.2, 23.9), 90, datetime.datetime.now()]

    hardware = InterfacingController(SimulatedWheelsController(),
                                     SimulatedAntennaController(),
                                     SimulatedPenController(),
                                     SimulatedLightsController())

    routine_check_command = RoutineCheckWithVisualServoManagementCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder, ServoWheelsManager())
    previous_step, first_return_telemetry = routine_check_command.execute(previous_telemetry_position)
    at_the_moment_step, second_return_telemetry = routine_check_command.execute(telemetry_position)

    wheels_recieved_vector_x, wheels_recieved_vector_y = hardware.wheels.last_vector_given

    assert round(wheels_recieved_vector_x, 1) == 5.8
    assert round(wheels_recieved_vector_y, 1) == 6.1
    assert previous_step == Step.TRAVEL_TO_ANTENNA_ZONE
    assert at_the_moment_step == Step.TRAVEL_TO_ANTENNA_ZONE
    assert first_return_telemetry is None
    assert second_return_telemetry.packet_type == PacketType.PATH


def test_given_telemetry_position_indicating_target_node_and_is_checkpoint_is_reached_and_heading_is_kept_routine_check_goes_to_next_step():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    time.sleep(1)
    pathfinder.nodes_queue_to_checkpoint.clear()

    telemetry_position = [(29.9, 29.8), 90, datetime.datetime.now()]
    hardware = InterfacingController(SimulatedWheelsController(),
                                     SimulatedAntennaController(),
                                     SimulatedPenController(),
                                     SimulatedLightsController())

    routine_check_command = RoutineCheckWithVisualServoManagementCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder, ServoWheelsManager())
    step, return_telemetry = routine_check_command.execute(telemetry_position)

    assert hardware.wheels.last_vector_given is None
    assert step == Step.PREPARE_SEARCH_FOR_ANTENNA
    assert return_telemetry is None


def test_given_telemetry_position_indicating_target_node_and_is_not_checkpoint_is_reached_and_heading_is_kept_routine_check_goes_to_next_node_and_stays_at_current_step():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    time.sleep(1)
    pathfinder.nodes_queue_to_checkpoint.append((40, 40))

    telemetry_position = [(29.9, 30.1), 90, datetime.datetime.now()]
    hardware = InterfacingController(SimulatedWheelsController(),
                                     SimulatedAntennaController(),
                                     SimulatedPenController(),
                                     SimulatedLightsController())

    routine_check_command = RoutineCheckWithVisualServoManagementCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder, ServoWheelsManager())
    step, return_telemetry = routine_check_command.execute(telemetry_position)

    wheels_recieved_vector_x, wheels_recieved_vector_y = hardware.wheels.last_vector_given

    assert round(wheels_recieved_vector_x, 1) == 10.1
    assert round(wheels_recieved_vector_y, 1) == 9.9
    assert step == Step.TRAVEL_TO_ANTENNA_ZONE
    assert return_telemetry is None


def test_given_telemetry_position_indicating_reaching_node_and_heading_is_not_90_deg_launch_rotation_corrective_action():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    time.sleep(1)

    telemetry_position = [(29.9, 30), 87.9, datetime.datetime.now()]
    hardware = InterfacingController(SimulatedWheelsController(),
                                     SimulatedAntennaController(),
                                     SimulatedPenController(),
                                     SimulatedLightsController())

    routine_check_command = RoutineCheckWithVisualServoManagementCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder, ServoWheelsManager())
    step, return_telemetry = routine_check_command.execute(telemetry_position)

    assert round(hardware.wheels.last_degrees_of_rotation_given, 1) == 2.1
    assert routine_check_command.servo_wheels_manager.heading_correction_in_progress
    assert step == Step.TRAVEL_TO_ANTENNA_ZONE
    assert return_telemetry is None


def test_given_heading_corrective_action_when_standard_heading_is_reached_routine_check_carries_on_to_next_step():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    pathfinder.nodes_queue_to_checkpoint.clear()

    telemetry_position = [(29.9, 30), 89.9, datetime.datetime.now()]
    hardware = InterfacingController(SimulatedWheelsController(),
                                     SimulatedAntennaController(),
                                     SimulatedPenController(),
                                     SimulatedLightsController())

    servo_wheels_manager = ServoWheelsManager()
    servo_wheels_manager.calculated_current_real_position = (29.9, 30)
    servo_wheels_manager.heading_correction_in_progress = True

    routine_check_command = RoutineCheckWithVisualServoManagementCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder, servo_wheels_manager)
    step, return_telemetry = routine_check_command.execute(telemetry_position)

    assert not routine_check_command.servo_wheels_manager.heading_correction_in_progress
    assert step == Step.PREPARE_SEARCH_FOR_ANTENNA
    assert return_telemetry is None


def test_given_heading_corrective_action_when_rotation_has_stopped_before_reaching_standard_heading_routine_check_sends_a_new_rotation_command():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    pathfinder.nodes_queue_to_checkpoint.clear()

    previous_telemetry_position = [(29.9, 30), 87, datetime.datetime.now()]
    time.sleep(1)
    current_telemetry_position = [(29.9, 30), 87.2, datetime.datetime.now()]
    hardware = InterfacingController(SimulatedWheelsController(),
                                     SimulatedAntennaController(),
                                     SimulatedPenController(),
                                     SimulatedLightsController())

    servo_wheels_manager = ServoWheelsManager()
    servo_wheels_manager.calculated_current_real_position = (29.9, 30)
    servo_wheels_manager.heading_correction_in_progress = True

    routine_check_command = RoutineCheckWithVisualServoManagementCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder, servo_wheels_manager)
    previous_step, first_return_telemetry = routine_check_command.execute(previous_telemetry_position)

    routine_check_command = RoutineCheckWithVisualServoManagementCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder, servo_wheels_manager)
    now_step, second_return_telemetry = routine_check_command.execute(current_telemetry_position)

    assert round(hardware.wheels.last_degrees_of_rotation_given, 1) == 2.8
    assert routine_check_command.servo_wheels_manager.heading_correction_in_progress
    assert previous_step == Step.TRAVEL_TO_ANTENNA_ZONE
    assert now_step == Step.TRAVEL_TO_ANTENNA_ZONE
    assert first_return_telemetry is None
    assert second_return_telemetry is None


def test_given_heading_corrective_action_when_standard_heading_is_not_reached_routine_check_keeps_doing_current_corrective_action():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    pathfinder.nodes_queue_to_checkpoint.clear()

    first_telemetry_position = [(29.9, 30), 86, datetime.datetime.now()]
    time.sleep(1)
    second_telemetry_position = [(29.9, 30), 88, datetime.datetime.now()]
    hardware = InterfacingController(SimulatedWheelsController(),
                                     SimulatedAntennaController(),
                                     SimulatedPenController(),
                                     SimulatedLightsController())

    servo_wheels_manager = ServoWheelsManager()
    servo_wheels_manager.calculated_current_real_position = (29.9, 30)
    servo_wheels_manager.heading_correction_in_progress = True

    routine_check_command = RoutineCheckWithVisualServoManagementCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder, servo_wheels_manager)
    previous_step, first_return_telemetry = routine_check_command.execute(first_telemetry_position)

    routine_check_command = RoutineCheckWithVisualServoManagementCommand(Step.TRAVEL_TO_ANTENNA_ZONE, hardware, pathfinder, servo_wheels_manager)
    now_step, second_return_telemetry = routine_check_command.execute(second_telemetry_position)

    assert routine_check_command.servo_wheels_manager.heading_correction_in_progress
    assert previous_step == Step.TRAVEL_TO_ANTENNA_ZONE
    assert now_step == Step.TRAVEL_TO_ANTENNA_ZONE
    assert first_return_telemetry is None
    assert second_return_telemetry is None
