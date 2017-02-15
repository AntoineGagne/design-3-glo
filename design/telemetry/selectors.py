"""Contains all the classes and functions related to non-blocking
   communication.
"""


from selectors import EVENT_READ, EVENT_WRITE

import queue
import selectors

from .sockets import Socket


class Selector:
    def __init__(self,
                 reader_socket: Socket,
                 writer_socket: Socket,
                 consumed,
                 produced):
        """Initialize the `Selector`.

        :param reader_socket: The socket that will receive inputs
        :type reader_socket: :mod:`sockets`.`Socket`
        :param writer_socket: The socket that will write outputs
        :type writer_socket: :mod:`sockets`.`Socket`
        :param consumed: The queue of elements that needs to be sent
        :param produced: The queue of elements that were read
        """
        self.selector = selectors.DefaultSelector()
        self._register_sockets(reader_socket, writer_socket)
        self.consumed = consumed
        self.produced = produced

    def run(self):
        """Loop and block until a socket is ready to be read from/written to."""
        while True:
            events = self.selector.select()
            for key, _ in events:
                callback = key.data
                callback(key.fileobj)

    def _register_sockets(self,
                          reader_socket: Socket,
                          writer_socket: Socket):
        """Register the sockets with the selector.

        :param reader_socket: The socket that will receive inputs
        :type reader_socket: :mod:`sockets`.`Socket`
        :param writer_socket: The socket that will write outputs
        :type writer_socket: :mod:`sockets`.`Socket`
        """
        reader_socket.setblocking(False)
        writer_socket.setblocking(False)
        self.selector.register(reader_socket,
                               EVENT_READ,
                               self._read_data)
        self.selector.register(writer_socket,
                               EVENT_WRITE,
                               self._write_data)

    def _read_data(self, socket_: Socket):
        """Read data from the socket and put it in the `produced` queue if
           there was some data to be read.

        :param socket_: The socket to read from
        :type socket_: :mod:`sockets`.`Socket`
        """
        data = socket_.receive()
        if data:
            self.produced.put_nowait(data)

    def _write_data(self, socket_: Socket):
        """Write some data in the queue if there was some to be written.

        :param socket_: The socket to write with
        :type socket_: :mod:`sockets`.`Socket`
        """
        try:
            data = self.consumed.get_nowait()
            socket_.send(data)
        except queue.Empty:
            pass
