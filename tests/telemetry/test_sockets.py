import threading

import design.telemetry.packets as packets
import design.telemetry.sockets as sockets


SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 8000
A_PACKET = packets.Packet(packets.PacketType.position, (5, 5))


def run_a_fake_server():
    server_socket = sockets.Socket()
    server_socket.accept(SERVER_ADDRESS, SERVER_PORT)
    server_socket.close()


def test_that_given_a_socket_and_a_server_when_connect_then_it_connects_to_the_server():
    server_thread = threading.Thread(target=run_a_fake_server, daemon=True)
    server_thread.start()

    socket = sockets.Socket()
    socket.connect(SERVER_ADDRESS, SERVER_PORT)
    socket.close()

    server_thread.join()


def test_that_given_a_socket_and_a_server_when_send_then_a_message_is_sent():
    server_thread = threading.Thread(target=run_a_fake_server, daemon=True)
    server_thread.start()

    socket = sockets.Socket()
    socket.connect(SERVER_ADDRESS, SERVER_PORT)
    socket.send(A_PACKET)
    socket.close()

    server_thread.join()
