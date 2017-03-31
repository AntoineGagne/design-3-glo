""" This module contains a manager for all data and steps related to visual servowheel management
when telemetry translation movement strategy is used. """

import math
import numpy

from design.pathfinding.constants import DEVIATION_THRESHOLD, STANDARD_HEADING


class ServoWheelsManager():

    def __init__(self):
        self.calculated_current_real_position = (-1, -1)
        self.last_recorded_position = (-1, -1)
        self.last_recorded_heading = -5000
        self.heading_correction_in_progress = False

    def is_real_translation_deviating(self, telemetry_position, telemetry_vector, supposed_vector, real_timestamp):
        """ Verifies if the robot's movement is deviating and returns true if so.
        :param telemetry_vector: Vector between telemetry's position and the origin of the current translation movement.
        :param supposed_vector: Vector between target position and origin of movement
        :param real_timestamp: Time at which the real position was computed on the base station
        :returns: A boolean indicating if the robot is indeed deviating. """

        angle = math.degrees(
            numpy.arccos(
                numpy.clip(numpy.dot(
                    telemetry_vector / numpy.linalg.norm(telemetry_vector),
                    supposed_vector / numpy.linalg.norm(supposed_vector)), -1.0, 1.0)))

        # time_elapsed_since_real_position_was_computed = (datetime.datetime.now() - real_timestamp).total_seconds()
        # self.calculated_current_real_position = telemetry_position + (
        #     (telemetry_vector[1] / telemetry_vector[0]) * time_elapsed_since_real_position_was_computed)
        self.calculated_current_real_position = telemetry_position

        # If the angle is above our deviation threshold, correct trajectory
        if angle >= DEVIATION_THRESHOLD:
            return True
        else:
            return False

    def has_the_robot_stopped_before_reaching_a_node(self, position):
        """ Verifies if the robot has stopped before even reaching a node, or went over it.
        :param position: Robot position
        :param target_node: Position of the current target"""

        print("Verifying if robot has stopped its translation...")
        if math.hypot(position[0] - self.last_recorded_position[0],
                      position[1] - self.last_recorded_position[1]) <= 1:
            self.last_recorded_position = position
            print("Robot has stopped moving!")
            return True
        else:
            self.last_recorded_position = position
            return False

    def has_robot_lost_its_heading(self, heading):
        """ Verifies if the robot has lost its heading after reaching its target node.
        :param heading: Current heading, in degrees
        :returns: A boolean indicating if the robot has lost its heading """
        if math.fabs(heading - STANDARD_HEADING) >= DEVIATION_THRESHOLD:
            return True
        else:
            return False

    def has_the_robot_stopped_before_completing_its_heading_correction(self, heading):
        """ Verifies if the robot has stopped correcting its heading.
        :param heading: Current heading
        :returns: A boolean indicating if the robot has most likely stopped """
        if math.fabs(math.fabs(heading - self.last_recorded_heading)) <= DEVIATION_THRESHOLD:
            self.last_recorded_heading = heading
            return True
        else:
            self.last_recorded_heading = heading
            return False
