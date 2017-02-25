""" Author: TREMBLAY, Alexandre
Last modified: Febuary 2nd, 2017

Mocks telemetry for initial decisionmaking testing """

import logging
import datetime


class TelemetryMock():
    """Mocks telemetry by loading commands from file"""

    def __init__(self):

        self.commands = open("mockTelemetry.txt", "r").read().splitlines()
        self.timestamped_telemetry = {}
        for line in self.commands:
            key = "{0}{1}:{2}{3}:{4}{5}".format(
                line[0], line[1], line[3], line[4], line[6], line[7])
            self.timestamped_telemetry[key] = line[9:]

        self.logger = logging.getLogger("telemetry_mock_logger")
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('exiting_telemetry.log', 'w')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s|%(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def bind(self, port_number):
        """Mocks binding to port"""
        self.logger.debug("BIND: Binding to port %s", port_number)

    def send(self, data):
        """Mocks sending telemetry to base station"""

        if isinstance(data, str):
            self.logger.info("%s", data)
        else:
            self.logger.info("%s", data.to_string())

    def poll(self):
        """ Polls mocked telemetry """

        current_time = "{:%H:%M:%S}".format(datetime.datetime.now())
        if current_time in self.timestamped_telemetry:
            print("CONSUMMATING TELEMTRY!")
            polled_telemetry = self.timestamped_telemetry[current_time]
            del self.timestamped_telemetry[current_time]
            return polled_telemetry.split('|')
        else:
            return (None, None)
