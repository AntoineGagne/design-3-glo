from datetime import datetime
from enum import Enum, unique
from typing import Any

import dill as pickle
import zlib


@unique
class PacketType(Enum):
    POSITION = 1
    PATH = 2
    FIGURE_IMAGE = 3
    FIGURE_VERTICES = 4
    GAME_MAP = 5
    COMMAND = 6
    NOTIFICATION = 7


class Packet:
    def __init__(self, packet_type: PacketType, packet_data: Any):
        self.packet_type = packet_type
        self.packet_data = packet_data
        self.timestamp = datetime.now().timestamp()


def serialize_packet(packet: Packet) -> bytes:
    pickled_packet = pickle.dumps(packet, protocol=pickle.HIGHEST_PROTOCOL)
    return zlib.compress(pickled_packet)


def deserialize_packet(binary_packet: bytes) -> Packet:
    decompressed_packet = zlib.decompress(binary_packet)
    return pickle.loads(decompressed_packet)
