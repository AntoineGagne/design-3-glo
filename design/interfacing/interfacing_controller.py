""" Author: TREMBLAY, Alexandre
Last modified: Febuary 3rd, 2017

Bundles interfacing controllers in a easy to inject bundle"""

from design.interfacing.simulated_controllers import (SimulatedWheelsController,
                                                      SimulatedAntennaController,
                                                      SimulatedPenController,
                                                      SimulatedLcdScreenController,
                                                      SimulatedLightsController)


class InterfacingController():
    """ Bundles all interfacing in a easy to inject bundle """

    def __init__(self):
        self.wheels = SimulatedWheelsController()
        self.antenna = SimulatedAntennaController()
        self.pen = SimulatedPenController()
        self.lcd_screen = SimulatedLcdScreenController()
        self.lights = SimulatedLightsController()
