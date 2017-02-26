""" Author: TREMBLAY, Alexandre
Last modified: Febuary 1st, 2017

Contains classes and functions in order to simulate interaction with hardware components """

import logging

INTERFACING_LOGGER = logging.getLogger("interfacing_logger")
INTERFACING_LOGGER.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('interfacing.log', 'w')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
INTERFACING_LOGGER.addHandler(file_handler)


class SimulatedAntennaController():
    """Simulates interaction with antenna"""

    st_last_signal_line_read = -1

    def get_signal_strength(self):
        """Simulates getting signal strength from antenna detection circuitry"""

        with open("mockSignalStrength.txt", "r") as mock:
            SimulatedAntennaController.st_last_signal_line_read += 1
            signal_value = mock.readlines()[SimulatedAntennaController.st_last_signal_line_read]

        return int(signal_value)

    def get_information_from_signal(self):
        """Simulates getting information from the decoded signal recieved"""
        INTERFACING_LOGGER.debug("ANTENNA: get_info_from_signal() call recieved.")

        with open("mockSignalInfo.txt", "r") as mock:
            information = mock.readlines()

        return tuple(information)

    def start_sampling(self):
        """Starts sampling signal strength"""
        INTERFACING_LOGGER.debug("ANTENNA: Starting to sample.")

    def stop_sampling(self):
        """Stops sampling signal strength"""
        INTERFACING_LOGGER.debug("ANTENNA: Stopping sampling.")


class SimulatedWheelsController():
    """Simulates interaction with wheels"""

    def __init__(self):
        self.last_vector_given = None
        self.last_degrees_of_rotation_given = None

    def move(self, vector):
        """Simulates moving the robot according to a (dx, dy) vector"""

        self.last_vector_given = vector
        INTERFACING_LOGGER.debug(
            "WHEELS: Recieved vector [dx = %s, dy = %s]", vector[0], vector[1])

    def rotate(self, amount):
        """ Simulates rotating the robot according to its central axis from axis
        x amount of tenth-of-degrees """

        self.last_degrees_of_rotation_given = amount
        INTERFACING_LOGGER.debug(
            "WHEELS: Rotating %s degrees from current axis.", amount)

    def stop(self):
        """Simulates recieving a stop command"""
        INTERFACING_LOGGER.debug("WHEELS: Recieved stop() command!")


class SimulatedLightsController():
    """Simulates interaction with LED lights"""

    def light_green_led(self, duration):
        """Simulates lighting the green LED for a duration in milliseconds"""
        INTERFACING_LOGGER.debug("LIGHTS: Lighting green LED for %s ms", duration)

    def light_red_led(self, duration):
        """Simulates lighting the red LED for a duration in milliseconds"""
        INTERFACING_LOGGER.debug("LIGHTS: Lighting red LED for %s ms", duration)


class SimulatedLcdScreenController():
    """Simulates interaction with LCD screen"""

    def show(self, data):
        """Simulates showing data passed as parameter on the LCD screen"""
        INTERFACING_LOGGER.debug("LCD: Showing %s", data)


class SimulatedPenController():
    """Simulates interaction with pen"""

    def lower_pen(self):
        """Simulates lowering the pen"""
        INTERFACING_LOGGER.debug("PEN: Lowering pen.")

    def raise_pen(self):
        """Simulates raising the pen"""
        INTERFACING_LOGGER.debug("PEN: Raising pen.")
