""" Bundles interfacing controllers in a easy to inject bundle """


class InterfacingController():

    def __init__(self, wheels, antenna, pen, lights):
        self.wheels = wheels
        self.antenna = antenna
        self.pen = pen
        self.lights = lights
