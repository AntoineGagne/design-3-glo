""" This class contains information about the robot's
current supposed positions and movement vectors, as well
as its heading. """

import datetime
import math
from design.pathfinding.mutable_position import MutablePosition
from design.pathfinding.constants import (STANDARD_HEADING,
                                          ROTATION_SPEED,
                                          ROTATION_THRESHOLD,
                                          TRANSLATION_SPEED,
                                          TRANSLATION_THRESHOLD)


class RobotSupposedStatus():
    """ Contains information about the robot's heading, position
    and movement vectors """

    def __init__(self, position, heading):

        self.position = MutablePosition(position[0], position[1])
        self.heading = heading
        self.time_since_moving = -1
        self.previous_rotation_check_time = -1
        self.target_position = (0, 0)
        self.origin_of_movement_vector = position
        self.target_heading = STANDARD_HEADING

        print("Robot Status initialized with position = {0} and heading = {1}".format(
            self.get_position(), self.heading))

    def get_translation_vector(self):
        """ Returns the current translation movement vector """
        return (self.target_position[0] - self.origin_of_movement_vector[0],
                self.target_position[1] - self.origin_of_movement_vector[1])

    def get_position(self):
        """ Returns the current position of the robot """
        return self.position.to_tuple()

    def set_position(self, position):
        """ Sets a new position for the robot """
        self.position.x = position[0]
        self.position.y = position[1]

    def generate_new_translation_vector_towards_new_target(self, target_position):
        """ Generates a new vector towards a new target position """
        self.origin_of_movement_vector = self.position.to_tuple()
        self.target_position = target_position
        self.time_since_moving = datetime.datetime.now()
        return (self.target_position[0] - self.origin_of_movement_vector[0],
                self.target_position[1] - self.origin_of_movement_vector[1])

    def generate_new_translation_vector_towards_current_target(self, current_robot_position):
        """ Generates a new vector from the current real robot position """

        self.origin_of_movement_vector = tuple(current_robot_position)
        self.time_since_moving = datetime.datetime.now()
        return (self.target_position[0] - self.origin_of_movement_vector[0],
                self.target_position[1] - self.origin_of_movement_vector[1])

    def update_position(self, timestamp_as_final_time=None):
        """ Updates the current position of the robot through cinematics equations.
        If the timestamp_as_final_time argument is specified, the method will use that
        value as the time t (delta_t = t - t0). Otherwise, system time will be used."""

        orientation = 0
        try:
            orientation = math.atan(self.get_translation_vector()[1] /
                                    self.get_translation_vector()[0])
        except ZeroDivisionError as error:
            if self.get_translation_vector()[1] >= 0:
                orientation = 90
            else:
                orientation = -90

        if self.get_translation_vector()[0] <= 0:
            orientation = orientation + math.pi

        final_time = datetime.datetime.now()
        if timestamp_as_final_time is not None:
            final_time = timestamp_as_final_time

        delta_x = math.cos(orientation) * TRANSLATION_SPEED * \
            (final_time - self.time_since_moving).total_seconds()

        delta_y = math.sin(orientation) * TRANSLATION_SPEED * \
            (final_time - self.time_since_moving).total_seconds()

        current_x, current_y = self.origin_of_movement_vector

        self.position.x = current_x + delta_x
        self.position.y = current_y + delta_y

    def position_has_reached_target_position_within_threshold(self):
        """ Returns true if the current position has reached the target position,
        within threshold """
        distance = math.hypot(self.target_position[
            0] - self.position.x, self.target_position[1] - self.position.y)

        return distance <= TRANSLATION_THRESHOLD

    def set_target_heading_and_get_angular_difference(self, target_heading):
        """ Sets a new target heading to reach when updating the robot's heading,
        and returns the angular difference between the new target heading and the
        current heading """
        self.target_heading = target_heading
        self.previous_rotation_check_time = datetime.datetime.now()
        return self.target_heading - self.heading

    def update_heading(self):
        """ Updates the current heading of the robot """

        delta_time = (datetime.datetime.now() - self.previous_rotation_check_time).total_seconds()
        self.previous_rotation_check_time = datetime.datetime.now()

        angular_speed = ROTATION_SPEED
        if self.target_heading - self.heading < 0:
            angular_speed = -angular_speed

        self.heading = self.heading + (angular_speed * delta_time)

    def heading_has_reached_target_heading_threshold(self):
        """ Returns true if the current heading has reached the threshold
        of the targeted heading """
        return (self.heading <=
                self.target_heading + (ROTATION_THRESHOLD / 2)) and (
                    self.heading >=
                    self.target_heading - (ROTATION_THRESHOLD / 2))
