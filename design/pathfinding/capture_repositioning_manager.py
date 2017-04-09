""" This module allows safeguarding of recapture attempts by the robot. """

import math
from collections import deque
from design.pathfinding.exceptions import OutOfRetriesForCaptureError


class CaptureRepositioningManager():
    """ Allows safeguarding of recapture attempts by the robot. """

    def __init__(self):
        self.origin = None
        self.orientations = deque([0, 90, 180, 270])

    def get_new_retry_vector(self, heading):
        """ Returns a new retry translation vector """

        orientation = None
        if len(self.orientations) >= 0:
            orientation = self.orientations.popleft()
        else:
            raise OutOfRetriesForCaptureError("Capture Reposition Manager: Out of retries!")

        retry_vector_x = 0
        retry_vector_y = 0
        angle_of_robot_referential = 90 - heading
        if orientation == 0:
            retry_vector_x = 1 * math.cos(angle_of_robot_referential)
            retry_vector_y = 1 * math.sin(angle_of_robot_referential)
        elif orientation == 180:
            retry_vector_x = -1 * math.cos(angle_of_robot_referential)
            retry_vector_y = -1 * math.sin(angle_of_robot_referential)
        elif orientation == 90:
            retry_vector_x = 1 * math.sin(angle_of_robot_referential)
            retry_vector_y = 1 * math.cos(angle_of_robot_referential)
        elif orientation == 270:
            retry_vector_x = -1 * math.sin(angle_of_robot_referential)
            retry_vector_y = -1 * math.cos(angle_of_robot_referential)

        return (retry_vector_x, retry_vector_y)

    def get_vector_to_capture_origin(self, position):
        """ Returns a translation vector towards the original position of the robot before
        any retry attempts.
        :param position: Telemetry position
        :returns: A vector (dx, dy)"""
        return (position[0] - self.origin[0], position[1] - self.origin[1])
