""" Unit tests for servo wheel manager """

import datetime
import time

from design.pathfinding.servo_wheels_manager import ServoWheelsManager


def test_given_two_non_deviating_vector_is_deviating_returns_false():

    real_position = (30.05, 60)
    real_vector = (20.05, 40)
    supposed_vector = (40, 80)
    real_timestamp = datetime.datetime.now()
    time.sleep(1)

    servo_wheel_manager = ServoWheelsManager()
    assert not servo_wheel_manager.is_real_translation_deviating(
        real_position, real_vector, supposed_vector, real_timestamp)


def test_given_two_deviating_vectors_is_deviating_returns_true():

    real_position = (35, 50)
    real_vector = (25, 40)
    supposed_vector = (40, 80)
    real_timestamp = datetime.datetime.now()
    time.sleep(1)

    servo_wheel_manager = ServoWheelsManager()
    assert servo_wheel_manager.is_real_translation_deviating(
        real_position, real_vector, supposed_vector, real_timestamp)


def test_given_two_very_close_positions_in_sequence_robot_has_stopped_returns_true():

    servo_wheel_manager = ServoWheelsManager()
    servo_wheel_manager.last_recorded_position = (20.5, 40.2)
    current_position = (20.6, 39.9)

    assert servo_wheel_manager.has_the_robot_stopped_before_reaching_a_node(current_position)


def test_given_two_far_apart_positions_in_sequence_robot_has_stopped_returns_false():

    servo_wheel_manager = ServoWheelsManager()
    servo_wheel_manager.last_recorded_position = (20.5, 40.2)
    current_position = (22, 42)

    assert not servo_wheel_manager.has_the_robot_stopped_before_reaching_a_node(current_position)


def test_given_two_similar_headings_has_robot_lost_its_heading_returns_false():

    current_heading = 89.8
    servo_wheel_manager = ServoWheelsManager()

    assert not servo_wheel_manager.has_robot_lost_its_heading(current_heading)


def test_given_two_far_apart_headings_has_robot_lost_its_heading_returns_true():

    current_heading = 87
    servo_wheel_manager = ServoWheelsManager()

    assert servo_wheel_manager.has_robot_lost_its_heading(current_heading)


def test_given_two_similar_headings_has_robot_completed_its_correction_returns_true():

    servo_wheel_manager = ServoWheelsManager()
    servo_wheel_manager.last_recorded_heading = 71
    current_heading = 71.3

    assert servo_wheel_manager.has_the_robot_stopped_before_completing_its_heading_correction(current_heading)


def test_given_two_far_apart_headings_has_robot_completed_its_correction_returns_false():

    servo_wheel_manager = ServoWheelsManager()
    servo_wheel_manager.last_recorded_heading = 71
    current_heading = 74.3

    assert not servo_wheel_manager.has_the_robot_stopped_before_completing_its_heading_correction(current_heading)
