"""Author: TREMBLAY, Alexandre
Last modified: Febuary 4th, 2017

This module allows mocking of pathfinder object"""

import math
import datetime
import queue
from enum import Enum
from design.pathfinding.constants import TRANSLATION_THRESHOLD
from design.pathfinding.constants import ROTATION_SPEED
from design.pathfinding.constants import TRANSLATION_SPEED
from design.pathfinding.constants import ROTATION_THRESHOLD
from design.pathfinding.game_map import GameMap
from design.pathfinding.mutable_position import MutablePosition
from design.pathfinding.constants import PointOfInterest


class PathStatus(Enum):
    """ Enum of pathfinding status """
    MOVING_TOWARDS_CHECKPOINT = 0
    CHECKPOINT_REACHED = 1


class Pathfinder():
    """Mocks pathfinder object"""

    def __init__(self):
        """ TEST CASE """

        self.game_map = GameMap()
        self.nodes_queue_to_checkpoint = queue.Queue()  # in cm
        self.next_node = (0, 0)  # in cm
        self.supposed_robot_position = MutablePosition(0, 0)
        self.time_since_moving = -1
        self.last_node_crossed = (20, 20)
        self.target_heading = 90
        self.current_heading = 90

    def set_game_map(self, game_map_data):
        """ Sets game map elements like corners, objectives and
        obstacles """

        robot_information, game_map_information = game_map_data.split('$')

        self.supposed_robot_position.x = int(
            robot_information.split('/')[1].split(',')[0][1:])
        self.supposed_robot_position.y = int(
            robot_information.split('/')[1].split(',')[1][:-1])
        self.current_heading = int(robot_information.split('/')[3])

        self.game_map.parse(game_map_information)

        # Add checkpoint to antenna pos
        self.generate_path_to_checkpoint(self.get_point_of_interest(
            PointOfInterest.ANTENNA_START_SEARCH_POINT))

    def verify_if_deviating(self, current_robot_position):
        """ Returns true if deviating outside defined THRESHOLD,
        otherwise returns false """
        print("Verifying if deviating from {0}".format(
            self.supposed_robot_position))
        return not self.verify_if_close_to_point(current_robot_position,
                                                 self.supposed_robot_position.to_tuple())

    def get_current_robot_supposed_position(self):
        """ Returns supposed robot position """
        return self.supposed_robot_position.to_tuple()

    def get_current_vector(self):
        """ Returns (dx, dy) vector in the robot's referential
        to go through the wheels """

        return (self.next_node[0] - self.last_node_crossed[0],
                self.next_node[1] - self.last_node_crossed[1])

    def update_supposed_robot_position(self):
        """ Updates supposed robot position according to current time and speed
        of the robot """

        orientation = math.atan(self.get_current_vector()[1] /
                                self.get_current_vector()[0])

        if self.get_current_vector()[0] <= 0:
            orientation = orientation + math.pi

        print("Computed orientation: {0} deg".format(
            math.degrees(orientation)))

        delta_x = math.cos(orientation) * TRANSLATION_SPEED * \
            (datetime.datetime.now() - self.time_since_moving).total_seconds()

        delta_y = math.sin(orientation) * TRANSLATION_SPEED * \
            (datetime.datetime.now() - self.time_since_moving).total_seconds()

        current_x, current_y = self.last_node_crossed

        self.supposed_robot_position.x = current_x + delta_x
        self.supposed_robot_position.y = current_y + delta_y

        print("Update supposed position: dx={0}, dy={1} from ({2},{3})".format(
            delta_x, delta_y, current_x, current_y))
        print("Supposed robot position is now ({0},{1})".format(
            self.supposed_robot_position.x, self.supposed_robot_position.y))

    def generate_new_vector(self, current_robot_position):
        """ Computes new path to next objective according
        to which step you are in """

        self.last_node_crossed = tuple(current_robot_position)
        self.time_since_moving = datetime.datetime.now()
        return (self.next_node[0] - self.last_node_crossed[0],
                self.next_node[1] - self.last_node_crossed[1])

    def verify_if_close_to_point(self, position, target_position):
        """ Returns true if passed pos is within THRESHOLD of next node """

        distance = math.hypot(target_position[
            0] - position[0], target_position[1] - position[1])

        return distance <= TRANSLATION_THRESHOLD

    def get_vector_to_next_node(self, current_robot_position=None):
        """ If close enough to next node (within THRESHOLD), switch to new one """

        robot_position = (0, 0)

        if current_robot_position:
            robot_position = current_robot_position
        else:
            robot_position = self.supposed_robot_position.to_tuple()

        if self.verify_if_close_to_point(robot_position, self.next_node):
            # If we are close enough to the node we were moving towards,
            # set last crossed node to robot's position and set next node
            # to the next one we have in our nodes queue towards the checkpoint
            if not self.nodes_queue_to_checkpoint.empty():
                self.next_node = self.nodes_queue_to_checkpoint.get()
                self.last_node_crossed = tuple(robot_position)
                self.time_since_moving = datetime.datetime.now()
                return (PathStatus.MOVING_TOWARDS_CHECKPOINT,
                        self.generate_new_vector(robot_position))
            else:
                self.last_node_crossed = tuple(robot_position)
                self.time_since_moving = datetime.datetime.now()
                return (PathStatus.CHECKPOINT_REACHED, None)
        else:
            return (PathStatus.MOVING_TOWARDS_CHECKPOINT, None)

    def get_point_of_interest(self, point_of_interest):
        """ Returns any data about the specified point of interest within
        the game map """
        return self.game_map.get_point_of_interest(point_of_interest)

    def generate_path_to_checkpoint(self, checkpoint_position):
        """ Generates shortest path to checkpoint and updates the node queue
        accordingly. """
        self.nodes_queue_to_checkpoint.queue.clear()
        self.nodes_queue_to_checkpoint.put(checkpoint_position)
        self.next_node = self.nodes_queue_to_checkpoint.get()

    def set_target_heading(self, heading):
        """ Sets target heading for next rotation command """
        self.target_heading = heading

    def update_heading(self, delta_time):
        """ Updates heading """

        print("Before updating heading: current = {0} dg, target = {1} dg".format(
            self.current_heading, self.target_heading))
        print("dt = {0}".format(delta_time))

        angular_speed = ROTATION_SPEED
        if self.target_heading - self.current_heading < 0:
            angular_speed = -angular_speed

        self.current_heading = self.current_heading + \
            (angular_speed * delta_time)

        print("Update heading: current = {0} dg, target = {1} dg".format(
            self.current_heading, self.target_heading))

    def current_heading_within_target_heading_threshold(self):
        """ Returns true if within threshold, false otherwise """
        return (self.current_heading <=
                self.target_heading + (ROTATION_THRESHOLD / 2)) and (
                    self.current_heading >=
                    self.target_heading - (ROTATION_THRESHOLD / 2))
