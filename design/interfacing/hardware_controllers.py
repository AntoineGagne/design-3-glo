""" Contains the classes that allow the decision-making module to
interact with hardware components, such as the wheels, the antenna
and the LEDs """

import math
from design.interfacing.stm32_driver import Response


class HardwareObserver():

    def notify(self, response_type):
        raise NotImplementedError("This method must be implemented. HardwareObserver acts as an interface.")


class AntennaController(HardwareObserver):
    """ Allows transparent communication with the antenna """

    def __init__(self, driver):

        self.stm32_driver = driver
        self.decode_routine_called = False
        self.new_signal_strength_value_available = False
        self.signal_data_available = False

        self.stm32_driver.register_hardware_observer(self)

    def notify(self, response_type):
        """ According to response, notify that new values for the signal's data and amplitude are available. """
        if response_type == Response.SIGNAL_STRENGTH:
            self.new_signal_strength_value_available = True
        elif response_type == Response.SIGNAL_DATA:
            self.signal_data_available = True

    def get_signal_strength(self):
        """ Returns the current filtered signal strength from the antenna
        :returns: Signal filtered amplitude
        :rtype: `int` """
        if self.new_signal_strength_value_available:
            return self.stm32_driver.signal_strength
        else:
            return None

    def get_information_from_signal(self):
        """ Obtain the drawing information within the antenna's emitted signal
        :returns: A tuple containing information about the drawing task at hand
        :rtype: `design.utils.AntennaInformation`"""
        if not self.decode_routine_called:
            self.stm32_driver.decode_manchester()
            self.decode_routine_called = True

        if self.signal_data_available:
            return self.stm32_driver.antenna_information
        else:
            return None

    def start_sampling(self):
        """Starts sampling signal strength"""
        self.stm32_driver.enable_sampling(True)

    def stop_sampling(self):
        """Stops sampling signal strength"""
        self.stm32_driver.enable_sampling(False)


class WheelsController():
    """Simulates interaction with wheels"""

    def __init__(self, driver):
        self.stm32_driver = driver
        self.last_vector_given = None
        self.last_degrees_of_rotation_given = None

    def move(self, vector):
        """ Send a translation vector to the robot
        :param vector: (dx, dy), both values in centimeters """
        self.last_vector_given = vector
        print("WHEELS - Recieved vector = {0}".format(vector))
        dx, dy = vector
        self.stm32_driver.translate_robot(int(dx * 10), int(dy * 10))

    def rotate(self, amount):
        """ Rotate a certain amount of degrees
        :param amount: Angular movement in degrees """
        self.last_degrees_of_rotation_given = amount
        print("WHEELS - Recieved deg= {0}".format(amount))
        self.stm32_driver.rotate_robot(math.radians(amount) * -1)

    def stop(self):
        """Simulates recieving a stop command"""
        self.last_vector_given = (0, 0)
        input()
        self.stm32_driver.stop_robot()


class LightsController():
    """Simulates interaction with LED lights"""

    def __init__(self, driver):
        self.stm32_driver = driver

    def light_green_led(self, duration):
        """ Turns on the green LED for a certain duration
        :param duration: Duration in milliseconds """
        self.stm32_driver.flash_green_led(round(duration))

    def turn_on_red_led(self):
        """ Turns on the red LED on the robot """
        self.stm32_driver.enable_red_led(True)

    def turn_off_red_led(self):
        """ Turns off the red LED on the robot """
        self.stm32_driver.enable_red_led(False)


class PenController():
    """Simulates interaction with pen"""

    def __init__(self, driver):
        self.pen_prehensor_driver = driver

    def lower_pen(self):
        """Simulates lowering the pen"""
        self.pen_prehensor_driver.lower_pen()

    def raise_pen(self):
        """Simulates raising the pen"""
        self.pen_prehensor_driver.raise_pen()
