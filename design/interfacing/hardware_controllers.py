""" Contains the classes that allow the decision-making module to
interact with hardware components, such as the wheels, the antenna
and the LEDs """

import math

import time

from design.interfacing.stm32_driver import Response


class HardwareObserver():

    def notify(self, response_type):
        raise NotImplementedError("This method must be implemented. HardwareObserver acts as an interface.")


class AntennaController(HardwareObserver):
    """ Allows transparent communication with the antenna """

    def __init__(self, driver, signal_strength_lock, signal_data_lock, logger):

        self.stm32_driver = driver
        self.logger = logger

        self.decode_routine_called = False
        self.new_signal_strength_value_available = False
        self.signal_data_available = False

        self.signal_strength_lock = signal_strength_lock
        self.signal_data_lock = signal_data_lock

        self.stm32_driver.register_hardware_observer(self)

    def notify(self, response_type):
        """ According to response, notify that new values for the signal's data and amplitude are available. """
        if response_type == Response.SIGNAL_STRENGTH:
            self.signal_strength_lock.acquire()
            self.new_signal_strength_value_available = True
            self.signal_strength_lock.release()
        elif response_type == Response.SIGNAL_DATA:
            self.signal_data_lock.acquire()
            self.signal_data_available = True
            self.signal_data_lock.release()

    def get_signal_strength(self):
        """ Returns the current filtered signal strength from the antenna
        :returns: Signal filtered amplitude
        :rtype: `int` """
        self.signal_strength_lock.acquire()
        if self.new_signal_strength_value_available:
            signal_strength = self.stm32_driver.get_signal_strength()
            self.logger.log("Antenna Controller - Acquired signal amplitude = {0}".format(signal_strength))
            self.signal_strength_lock.release()
            return signal_strength
        else:
            self.signal_strength_lock.release()
            return None

    def get_information_from_signal(self):
        """ Obtain the drawing information within the antenna's emitted signal
        :returns: A tuple containing information about the drawing task at hand
        :rtype: `design.utils.AntennaInformation`"""
        if not self.decode_routine_called:
            self.stm32_driver.decode_manchester()
            self.decode_routine_called = True

        self.signal_data_lock.acquire()
        if self.signal_data_available:
            self.logger.log("Antenna Controller - Signal data has been acquired!")
            self.signal_data_lock.release()
            return self.stm32_driver.antenna_information
        else:
            self.signal_data_lock.release()
            return None

    def start_sampling(self):
        """Starts sampling signal strength"""
        self.stm32_driver.enable_sampling(True)

    def stop_sampling(self):
        """Stops sampling signal strength"""
        self.stm32_driver.enable_sampling(False)


class WheelsController(HardwareObserver):
    """Simulates interaction with wheels"""

    def __init__(self, driver, translation_lock, rotation_lock, logger):
        self.stm32_driver = driver
        self.logger = logger

        self.translation_done = True
        self.rotation_done = True
        self.last_vector_given = None
        self.last_degrees_of_rotation_given = None

        self.translation_lock = translation_lock
        self.rotation_lock = rotation_lock

        self.stm32_driver.register_hardware_observer(self)

    def notify(self, response_type):
        """ Notifies the controller of the completion of a translation or rotation
        command. """
        if response_type == Response.TRANSLATION_FINISHED:
            self.translation_lock.acquire()
            self.translation_done = True
            self.translation_lock.release()
        elif response_type == Response.ROTATION_FINISHED:
            self.rotation_lock.acquire()
            self.rotation_done = True
            self.rotation_lock.release()

    def move(self, vector):
        """ Send a translation vector to the robot
        :param vector: (dx, dy), both values in centimeters """
        if math.hypot(vector[0], vector[1]) >= 0.2:
            self.last_vector_given = vector
            self.logger.log("Wheels Controller - Translating {0}, length = {1}".format(vector, math.hypot(vector[0], vector[1])))
            dx, dy = vector
            self.stm32_driver.translate_robot(int(dx * 10), int(dy * 10))
            self.translation_done = False
        else:
            self.logger.log("Wheels Controller - Recieved very small vector. Discarding and notifying translation as finished.")
            self.notify(Response.TRANSLATION_FINISHED)

    def rotate(self, amount):
        """ Rotate a certain amount of degrees
        :param amount: Angular movement in degrees """
        if math.fabs(amount) >= 1.5:
            self.last_degrees_of_rotation_given = amount
            self.logger.log("Wheels Controller - Rotating {0} degrees".format(amount))
            self.stm32_driver.rotate_robot(math.radians(amount) * -1)
            self.rotation_done = False
        else:
            self.notify(Response.ROTATION_FINISHED)

    def stop(self):
        """Simulates recieving a stop command"""
        self.last_vector_given = (0, 0)
        self.stm32_driver.stop_robot()
        self.rotation_done = True
        self.translation_done = True


class LightsController():
    """Simulates interaction with LED lights"""

    def __init__(self, driver, logger):
        self.stm32_driver = driver
        self.logger = logger

    def light_green_led(self, duration):
        """ Turns on the green LED for a certain duration
        :param duration: Duration in milliseconds """
        self.logger.log("Lights Controller - Flashing green LED.")
        self.stm32_driver.flash_green_led(round(duration))

    def turn_on_red_led(self):
        """ Turns on the red LED on the robot """
        self.logger.log("Lights Controller - Enable red LED.")
        self.stm32_driver.enable_red_led(True)

    def turn_off_red_led(self):
        """ Turns off the red LED on the robot """
        self.logger.log("Lights Controller - Disable red LED.")
        self.stm32_driver.enable_red_led(False)


class PenController():
    """Simulates interaction with pen"""

    def __init__(self, driver, logger):
        self.pen_prehensor_driver = driver
        self.logger = logger

    def lower_pen(self):
        """Simulates lowering the pen"""
        self.logger.log("Pen Controller - Lowering pen.")
        self.pen_prehensor_driver.lower_pen()
        time.sleep(2)

    def raise_pen(self):
        """Simulates raising the pen"""
        self.logger.log("Pen Controller - Raising pen.")
        self.pen_prehensor_driver.raise_pen()
