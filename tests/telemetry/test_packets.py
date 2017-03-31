import numpy as np

import design.telemetry.packets as packets
import tests.utils as utils


def test_that_given_a_packet_when_deserialize_packet_then_it_returns_the_deserialized_packet():
    a_packet = packets.Packet(packets.PacketType.POSITION, (5, 5))

    binary_packet = packets.serialize_packet(a_packet)

    utils.compare_objects(packets.deserialize_packet(binary_packet), a_packet)


def test_that_given_a_packet_containing_numpy_array_when_serializing_then_it_returns_the_serialized_packet():
    a_packet_containing_numpy_array = packets.Packet(
        packets.PacketType.POSITION,
        np.array([[[5, 5]],
                  [[4, 4]],
                  [[3, 3]],
                  [[2, 2]]])
    )
    serialized_packet = packets.serialize_packet(a_packet_containing_numpy_array)

    assert np.array_equal(
        a_packet_containing_numpy_array.packet_data,
        packets.deserialize_packet(serialized_packet).packet_data
    )
