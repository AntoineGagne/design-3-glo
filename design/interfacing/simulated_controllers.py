""" Author: TREMBLAY, Alexandre
Last modified: Febuary 1st, 2017

Contains classes and functions in order to simulate interaction with hardware components """

import logging

logging.basicConfig(filename='../../../simulation.log', level=logging.DEBUG)


class SimulatedAntennaController():
    """Simulates interaction with antenna"""

    def get_signal_strength(self):
        """Simulates getting signal strength from antenna detection circuitry"""
        logging.info("ANTENNA: Get_signal_strength() call recieved.")

    def get_info_from_signal(self):
        """Simulates getting information from the decoded signal recieved"""
        logging.info("ANTENNA: get_info_from_signal() call recieved.")


class SimulatedWheelsController():
    """Simulates interaction with wheels"""

    def move(self, vector):
        """Simulates moving the robot according to a (dx, dy) vector"""
        logging.info(
            "WHEELS: Recieved vector [dx = %s, dy = %s]", vector[0], vector[1])

    def stop(self):
        """Simulates recieving a stop command"""
        logging.info("WHEELS: Recieved stop() command!")


class SimulatedLightsController():
    """Simulates interaction with LED lights"""

    def light_green_led(self, duration):
        """Simulates lighting the green LED for a duration in milliseconds"""
        logging.info("LIGHTS: Lighting green LED for %s ms", duration)

    def light_red_led(self, duration):
        """Simulates lighting the red LED for a duration in milliseconds"""
        logging.info("LIGHTS: Lighting red LED for %s ms", duration)


class SimulatedLcdScreenController():
    """Simulates interaction with LCD screen"""

    def show(self, data):
        """Simulates showing data passed as parameter on the LCD screen"""
        logging.info("LCD: Showing %s", data)


class SimulatedPenController():
    """Simulates interaction with pen"""

    def lower_pen(self):
        """Simulates lowering the pen"""
        logging.info("PEN: Lowering pen.")

    def raise_pen(self):
        """Simulates raising the pen"""
        logging.info("PEN: Raising pen.")
