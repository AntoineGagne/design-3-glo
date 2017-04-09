""" This module allows the brain to decide if recieved telemetry makes sense, and discards it
if it does not. """

import math

from design.decision_making.constants import POSITION_SUDDEN_CHANGE_THRESHOLD, HEADING_SUDDEN_CHANGE_THRESHOLD


class IntegrityManager():

    def __init__(self):
        self.last_position = None
        self.last_heading = None

    def does_telemetry_make_sense(self, telemetry_data):
        """ Returns true if the recieved positional telemetry makes sense, otherwise
        returns false. """

        position = telemetry_data[0]
        heading = telemetry_data[1]

        if math.hypot(position[0] - self.last_position[0],
                      position[1] - self.last_position[1]) >= POSITION_SUDDEN_CHANGE_THRESHOLD or heading - \
                self.last_heading >= HEADING_SUDDEN_CHANGE_THRESHOLD and not (
                self.last_position is None or self.last_heading is None):
            return False

        self.last_position = position
        self.last_heading = heading

        return True
