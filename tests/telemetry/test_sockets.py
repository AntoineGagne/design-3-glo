import threading
import socket

import design.telemetry.sockets as sockets


SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 8000


def given_a_fake_server():
    server_socket = socket.socket()
    server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
    server_socket.listen()
    server_socket.accept()
    server_socket.close()


def test_that_given_a_socket_and_a_server_when_connect_then_it_connects_to_the_server():
    server_thread = threading.Thread(target=given_a_fake_server, daemon=True)
    server_thread.start()

    socket = sockets.Socket()
    socket.connect(SERVER_ADDRESS, SERVER_PORT)
    socket.close()

    server_thread.join()
