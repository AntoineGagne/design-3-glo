""" Author: TREMBLAY, Alexandre
Last modified: Febuary 2nd, 2017

Mocks telemetry for initial decisionmaking testing """

import logging
import datetime
from design.telemetry.packets import (Packet, PacketType)


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

    def put_command(self, packet):
        """ Mocks sending telemetry to base station
        :param packet: Telemetry packet to send to the base station """
        self.logger.info("%s", packet.packet_data)

    def fetch_command(self):
        """ Polls mocked telemetry
        :returns: Telemetry packet
        :rtype: `design.telemetry.packets.Packet` """

        current_time = "{:%H:%M:%S}".format(datetime.datetime.now())
        if current_time in self.timestamped_telemetry:
            polled_telemetry = self.timestamped_telemetry[current_time]
            del self.timestamped_telemetry[current_time]

            if PacketType[polled_telemetry.split('|')[0]] == PacketType.GAME_MAP:
                packet_data = {}
                packet_data["obstacles"] = [((47, 138), "N"), ((47, 180), "S"), ((60, 200), "O")]
                packet_data["robot"] = [(20, 20), 60]
                packet_data["table_corners"] = [(0, 0), (0, 231), (112, 231), (112, 0)]
                packet_data["drawing_zone"] = [(26, 27), (26, 87), (86, 87), (86, 27)]
                packet = Packet(PacketType[polled_telemetry.split('|')[0]], packet_data)
                return packet
            else:
                packet = Packet(PacketType[polled_telemetry.split('|')[0]],
                                polled_telemetry.split('|')[1])
                packet.timestamp = current_time
                return packet
        else:
            return Packet(None, None)
