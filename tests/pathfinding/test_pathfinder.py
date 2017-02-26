""" Author: TREMBLAY, Alexandre
Last modified: February 24th, 2017

Unit tests for pathfinder"""

from design.pathfinding.pathfinder import Pathfinder
from design.pathfinding.mutable_position import MutablePosition
from design.pathfinding.pathfinder import PathStatus
from design.pathfinding.constants import ROTATION_SPEED


def test_when_robot_pos_is_outside_threshold_verify_if_deviating_returns_true():
    """ Asserts that pathfinder finds that the robot is indeed deviating """

    pathfinder = Pathfinder()

    pathfinder.supposed_robot_position = MutablePosition(20, 20)
    real_robot_position = (22, 23)

    assert pathfinder.verify_if_deviating(real_robot_position) is True


def test_generate_new_vector_returns_correct_vector():
    """ Asserts that generate_new_vector method indeed works as expected """

    pathfinder = Pathfinder()
    pathfinder.next_node = (20, 20)
    real_robot_position = (30, 30)

    assert pathfinder.generate_new_vector(real_robot_position) == (-10, -10)


def test_if_close_enough_to_next_node_switch_to_new_vector_and_return_moving_to_checkpoint_status():
    """ Asserts that if the robot is within threshold of its next node, and there's still one
    in the queue, generate the relevant new vector and return it, along with the
    MOVING_TO_CHECKPOINT path status """

    pathfinder = Pathfinder()
    pathfinder.next_node = (30, 30)
    pathfinder.nodes_queue_to_checkpoint.put((20, 40))

    path_status, new_vector = pathfinder.get_vector_to_next_node((29.5, 29.8))

    assert path_status == PathStatus.MOVING_TOWARDS_CHECKPOINT
    assert new_vector == (-9.5, 10.2)
    assert pathfinder.next_node == (20, 40)


def test_if_not_close_enough_to_next_node_carry_on_to_next_node_without_changing_anything():
    """ Asserts that the robot carries on as usual if it is not close enough to the next node """

    pathfinder = Pathfinder()
    pathfinder.next_node = (30, 30)
    pathfinder.nodes_queue_to_checkpoint.put((20, 40))

    path_status, new_vector = pathfinder.get_vector_to_next_node((25, 25))

    assert path_status == PathStatus.MOVING_TOWARDS_CHECKPOINT
    assert new_vector is None
    assert pathfinder.next_node == (30, 30)


def test_if_close_enough_to_next_node_and_it_is_checkpoint_return_checkpoint_reached_status():
    """ Asserts that the checkpoint is reached when the robot is close enough to next node and
    the nodes queue is empty """

    pathfinder = Pathfinder()
    pathfinder.next_node = (30, 30)
    pathfinder.nodes_queue_to_checkpoint.queue.clear()

    path_status, new_vector = pathfinder.get_vector_to_next_node((29.5, 29.8))

    assert path_status == PathStatus.CHECKPOINT_REACHED
    assert new_vector is None
    assert pathfinder.next_node == (30, 30)


def test_current_heading_is_within_threshold_returns_true():
    """ Asserts that the verification method for robot heading returns true when the current
    heading closes in on the target heading specified """

    pathfinder = Pathfinder()
    pathfinder.target_heading = 90
    pathfinder.current_heading = 89.8

    assert pathfinder.current_heading_within_target_heading_threshold() is True


def test_current_heading_is_not_within_threshold_returns_false():
    """ Asserts that the verification method for robot heading returns false when the current
    heading is too far off the target heading specified """

    pathfinder = Pathfinder()
    pathfinder.target_heading = 90
    pathfinder.current_heading = 89

    assert pathfinder.current_heading_within_target_heading_threshold() is False


def test_when_delta_time_is_one_second_update_heading_adds_rotation_speed_to_current_heading():
    """ Asserts that the update_heading method adds the correct amount of degrees to the
    current_heading """

    pathfinder = Pathfinder()
    heading = 50
    pathfinder.current_heading = heading
    pathfinder.target_heading = 90

    pathfinder.update_heading(1)

    assert pathfinder.current_heading == heading + ROTATION_SPEED
