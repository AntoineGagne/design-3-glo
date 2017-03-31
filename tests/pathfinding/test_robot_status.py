""" Author: TREMBLAY, Alexandre
Last modified: March 3rd, 2017

Contains tests for robot_status class """

from design.pathfinding.robot_supposed_status import RobotSupposedStatus


def test_current_heading_is_within_threshold_returns_true():

    robot_status = RobotSupposedStatus((20, 20), 90)
    robot_status.target_heading = 90
    robot_status.heading = 89.95

    assert robot_status.heading_has_reached_target_heading_threshold() is True


def test_current_heading_is_not_within_threshold_returns_false():

    robot_status = RobotSupposedStatus((20, 20), 90)
    robot_status.target_heading = 90
    robot_status.heading = 89

    assert robot_status.heading_has_reached_target_heading_threshold() is False
