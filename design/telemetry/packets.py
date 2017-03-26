"""Contains all the things related to the packets sent/received by the
   networking.
"""


from datetime import datetime
from enum import Enum, unique
from typing import Any

import pickle
import zlib


@unique
class PacketType(Enum):
    """All the possible types of a packet sent/received by the telemetry
       package.
    """
    position = 1
    path = 2
    figure_image = 3
    figure_vertices = 4
    game_map = 5


class Packet:
    """Packets sent/received by the networking functions."""

    def __init__(self, packet_type: PacketType, packet_data: Any):
        """Initializes a packet.

        :param packet_type: The type of the packet (i.e. **position**)
        :type packet_type: :class:`design.telemetry.packets.PacketType`
        :param packet_data: The data associated with the packet.
                            It depends on the type of the packet
        :type packet_data: `Any`
        """
        self.packet_type = packet_type
        self.packet_data = packet_data
        self.timestamp = datetime.now().timestamp()


def serialize_packet(packet: Packet) -> bytes:
    """Serialize the packet into the `pickle` binary format.

    :param packet: The packet to serialize
    :type packet: :class:`design.telemetry.packets.Packet`
    :returns: The serialized and compressed packet
    :rtype: bytes
    """
    pickled_packet = pickle.dumps(packet, protocol=pickle.HIGHEST_PROTOCOL)
    return zlib.compress(pickled_packet)


def deserialize_packet(binary_packet: bytes) -> Packet:
    """Deserialize the bytes into a `Packet`.

    :param binary_packet: The serialized packet in a `pickle` binary format
    :type binary_packet: bytes
    :returns: The deserialized packet
    :rtype: :class:`design.telemetry.packets.Packet`
    """
    decompressed_packet = zlib.decompress(binary_packet)
    return pickle.loads(decompressed_packet)
