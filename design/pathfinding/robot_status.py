""" This class contains information about the robot's
current supposed positions and movement vectors, as well
as its heading. """

import datetime
import math
from design.pathfinding.mutable_position import MutablePosition
from design.pathfinding.constants import (STANDARD_HEADING,
                                          ROTATION_THRESHOLD,
                                          TRANSLATION_THRESHOLD)


class RobotStatus():

    def __init__(self, position, heading):

        self.position = MutablePosition(position[0], position[1])
        self.heading = heading
        self.target_position = (0, 0)
        self.origin_of_movement_vector = position
        self.target_heading = STANDARD_HEADING

        print("Robot Status initialized with position = {0} and heading = {1}".format(
            self.get_position(), self.heading))

    def reinitialize(self, position, heading):
        self.__init__(position, heading)

    def get_translation_vector(self):
        return (self.target_position[0] - self.origin_of_movement_vector[0],
                self.target_position[1] - self.origin_of_movement_vector[1])

    def get_position(self):
        return self.position.to_tuple()

    def set_position(self, position):
        self.position.x = position[0]
        self.position.y = position[1]

    def generate_new_translation_vector_towards_new_target(self, target_position):
        self.origin_of_movement_vector = self.position.to_tuple()
        self.target_position = target_position
        self.time_since_moving = datetime.datetime.now()
        return (self.target_position[0] - self.origin_of_movement_vector[0],
                self.target_position[1] - self.origin_of_movement_vector[1])

    def generate_new_translation_vector_towards_current_target(self, current_robot_position):

        self.origin_of_movement_vector = tuple(current_robot_position)
        self.time_since_moving = datetime.datetime.now()

        vector = (self.target_position[0] - self.origin_of_movement_vector[0],
                  self.target_position[1] - self.origin_of_movement_vector[1])

        return vector

    def position_has_reached_target_position_within_threshold(self):

        print("Pos: {0} - Target pos: {1}".format(self.get_position(), self.target_position))

        distance = math.hypot(self.target_position[
            0] - self.position.x, self.target_position[1] - self.position.y)

        return distance <= TRANSLATION_THRESHOLD

    def set_target_heading_and_get_angular_difference(self, target_heading):
        self.target_heading = target_heading
        self.previous_rotation_check_time = datetime.datetime.now()
        return self.target_heading - self.heading

    def heading_has_reached_target_heading_threshold(self):
        return (self.heading <=
                self.target_heading + (ROTATION_THRESHOLD / 2)) and (
                    self.heading >=
                    self.target_heading - (ROTATION_THRESHOLD / 2))
