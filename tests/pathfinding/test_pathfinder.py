""" Author: TREMBLAY, Alexandre
Last modified: February 24th, 2017

Unit tests for pathfinder"""
import pytest

from design.pathfinding.pathfinder import (Pathfinder,
                                           PathStatus)
from design.pathfinding.robot_supposed_status import RobotSupposedStatus
from design.pathfinding.graph import Graph


def test_when_robot_pos_is_outside_threshold_verify_if_deviating_returns_true():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    real_robot_position = (22, 23)

    assert pathfinder.verify_if_deviating(real_robot_position) is True


def test_generate_new_vector_returns_correct_vector():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (20, 20)
    real_robot_position = (30, 30)

    assert (pathfinder.robot_status.generate_new_translation_vector_towards_current_target(real_robot_position) == (-10, -10))


def test_if_close_enough_to_next_node_switch_to_new_vector_and_return_moving_to_checkpoint_status():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    pathfinder.nodes_queue_to_checkpoint.append((20, 40))

    path_status, new_vector = pathfinder.get_vector_to_next_node((29.91, 29.91))

    assert path_status == PathStatus.MOVING_TOWARDS_CHECKPOINT
    assert new_vector == (-9.91, 10.09)
    assert pathfinder.robot_status.target_position == (20, 40)


def test_if_not_close_enough_to_next_node_carry_on_to_next_node_without_changing_anything():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    pathfinder.nodes_queue_to_checkpoint.append((20, 40))

    path_status, new_vector = pathfinder.get_vector_to_next_node((25, 25))

    assert path_status == PathStatus.MOVING_TOWARDS_CHECKPOINT
    assert new_vector is None
    assert pathfinder.robot_status.target_position == (30, 30)


def test_if_close_enough_to_next_node_and_it_is_checkpoint_return_checkpoint_reached_status():

    pathfinder = Pathfinder()
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    pathfinder.nodes_queue_to_checkpoint.clear()

    path_status, new_vector = pathfinder.get_vector_to_next_node((29.91, 29.91))

    assert path_status == PathStatus.CHECKPOINT_REACHED
    assert new_vector is None
    assert pathfinder.robot_status.target_position == (29.91, 29.91)


@pytest.mark.skip(reason="no way of currently testing this")
def test_if_generate_path_to_checkpoint_with_a_star_return_good_path():

    graph = Graph([((50, 100), "N"), ((75, 140), "S")])
    graph.generate_nodes_of_graph()
    graph.generate_graph()
    pathfinder = Pathfinder()
    pathfinder.graph = graph
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    pathfinder.generate_path_to_checkpoint((20, 100))

    assert len(pathfinder.nodes_queue_to_checkpoint) == 0


@pytest.mark.skip(reason="no way of currently testing this")
def test_if_generate_path_to_checkpoint_with_a_star_return_checkpoint_reached_status():

    pathfinder = Pathfinder()
    graph = Graph([((50, 100), "N"), ((75, 140), "S")])
    graph.generate_nodes_of_graph()
    graph.generate_graph()
    pathfinder.graph = graph
    pathfinder.robot_status = RobotSupposedStatus((20, 20), 90)
    pathfinder.robot_status.target_position = (30, 30)
    pathfinder.generate_path_to_checkpoint((20, 200))

    assert len(pathfinder.nodes_queue_to_checkpoint) == 4
