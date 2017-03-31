""" Contains classes and functions in order to simulate interaction with hardware components """

import logging

from design.pathfinding.antenna_information import AntennaInformation


INTERFACING_LOGGER = logging.getLogger("interfacing_logger")
INTERFACING_LOGGER.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('interfacing.log', 'w')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
INTERFACING_LOGGER.addHandler(file_handler)


class SimulatedAntennaController():
    """Simulates interaction with antenna"""

    def __init__(self):
        self.line_to_read = -1
        self.values = None

        with open("mockSignalStrength.txt", "r") as mock:
            self.values = mock.readlines()

    def get_signal_strength(self):
        """ Returns the current filtered signal strength from the antenna
        :returns: Signal filtered amplitude
        :rtype: `int` """
        self.line_to_read = self.line_to_read + 1
        print(self.line_to_read)
        return int(self.values[self.line_to_read])

    def get_information_from_signal(self):
        """ Obtain the drawing information within the antenna's emitted signal
        :returns: A tuple containing information about the drawing task at hand
        :rtype: `design.utils.AntennaInformation`"""

        INTERFACING_LOGGER.debug("ANTENNA: get_info_from_signal() call recieved.")

        with open("mockSignalInfo.txt", "r") as mock:
            information = mock.readlines()

        antenna_data = AntennaInformation()
        antenna_data.painting_number = information[0]
        antenna_data.zoom = information[1]
        antenna_data.orientation = information[2]

        print("Antenna paining number = {0}".format(antenna_data.painting_number))
        return antenna_data

    def start_sampling(self):
        """ Notify the robot to start taking samples of the signal's amplitude """
        INTERFACING_LOGGER.debug("ANTENNA: Starting to sample.")

    def stop_sampling(self):
        """ Notify the robot to stop taking samples of the signal's amplitude """
        INTERFACING_LOGGER.debug("ANTENNA: Stopping sampling.")


class SimulatedWheelsController():
    """Simulates interaction with wheels"""

    def __init__(self):
        self.last_vector_given = None
        self.last_degrees_of_rotation_given = None

    def move(self, vector):
        """ Send a translation vector to the robot
        :param vector: (dx, dy), both values in centimeters """

        self.last_vector_given = vector
        INTERFACING_LOGGER.debug(
            "WHEELS: Recieved vector [dx = %s, dy = %s]", vector[0], vector[1])

    def rotate(self, amount):
        """ Rotate a certain amount of degrees
        :param amount: Angular movement in degrees """

        self.last_degrees_of_rotation_given = amount
        INTERFACING_LOGGER.debug(
            "WHEELS: Rotating %s degrees from current axis.", amount)

    def stop(self):
        """ Notify the robot to stop its movements """
        INTERFACING_LOGGER.debug("WHEELS: Recieved stop() command!")


class SimulatedLightsController():
    """Simulates interaction with LED lights"""

    def light_green_led(self, duration):
        """ Turns on the green LED for a certain duration
        :param duration: Duration in milliseconds """
        INTERFACING_LOGGER.debug("LIGHTS: Lighting green LED for %s ms", duration)

    def turn_on_red_led(self):
        """ Turns on the red LED """
        INTERFACING_LOGGER.debug("LIGHTS: Turning on red LED")

    def turn_off_red_led(self):
        """ Turns off the red LED """
        INTERFACING_LOGGER.debug("LIGHTS: Turning off red LED")


class SimulatedPenController():
    """Simulates interaction with pen"""

    def lower_pen(self):
        """ Lowers the pen to start drawing """
        INTERFACING_LOGGER.debug("PEN: Lowering pen.")

    def raise_pen(self):
        """ Raises the pen to start drawing """
        INTERFACING_LOGGER.debug("PEN: Raising pen.")
