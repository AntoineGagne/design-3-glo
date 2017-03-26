import design.telemetry.packets as packets
import tests.utils as utils


def test_that_given_a_packet_when_deserialize_packet_then_it_returns_the_deserialized_packet():
    a_packet = packets.Packet(packets.PacketType.POSITION, (5, 5))

    binary_packet = packets.serialize_packet(a_packet)

    utils.compare_objects(packets.deserialize_packet(binary_packet), a_packet)
