"""Contains all the classes and functions related to non-blocking
   communication.
"""


from selectors import EVENT_READ, EVENT_WRITE

import queue
import selectors

from .sockets import Socket


class Selector:
    """Select sockets according to some events such as readable/writable and
       perform actions.
    """
    def __init__(self,
                 reader_socket: Socket,
                 writer_socket: Socket,
                 consumed: queue.Queue,
                 produced: queue.Queue):
        """Initialize the `Selector`.

        :param reader_socket: The socket that will receive inputs
        :type reader_socket: :mod:`sockets`.`Socket`
        :param writer_socket: The socket that will write outputs
        :type writer_socket: :mod:`sockets`.`Socket`
        :param consumed: The queue of elements that needs to be sent
        :type consumed: :mod:`queue`.`Queue`
        :param produced: The queue of elements that were read
        :type produced: :mod:`queue`.`Queue`
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


class ClientSelectorFactory:
    """Create a `Selector` object that contains the client side sockets."""
    def __init__(self,
                 host: str,
                 reader_port: int,
                 writer_port: int):
        """Initialize the `ClientSelectorFactory`.

        :param host: The host on which to bind (i.e. '127.0.0.1')
        :type host: str
        :param reader_port: The port on which to bind the reader socket
                            (i.e. 8000)
        :type port: int
        :param writer_port: The port on which to bind the writer socket
                            (i.e. 8000)
        .. The *reader_port* and *writer_port* must be different.
        """
        assert reader_port != writer_port
        self.reader_address = (host, reader_port)
        self.writer_address = (host, writer_port)

    def create_selector(self,
                        consumed: queue.Queue,
                        produced: queue.Queue) -> Selector:
        """Create the `Selector` object.

        :param consumed: The queue of elements that needs to be sent
        :type consumed: :mod:`queue`.`Queue`
        :param produced: The queue of elements that were read
        :type produced: :mod:`queue`.`Queue`
        :returns: A selector with the given sockets
        :rtype: `Selector`
        """
        writer_socket = Socket()
        writer_socket.connect(*self.writer_address)

        reader_socket = Socket()
        reader_socket.connect(*self.reader_address)

        return Selector(reader_socket, writer_socket, consumed, produced)


class ServerSelectorFactory:
    """Create a `Selector` object that contains the server side sockets."""
    def __init__(self,
                 host: str,
                 reader_port: int,
                 writer_port: int):
        """Initialize the `ServerSelectorFactory`.

        :param host: The host on which to bind (i.e. '127.0.0.1')
        :type host: str
        :param reader_port: The port on which to bind the reader socket
                            (i.e. 8000)
        :type port: int
        :param writer_port: The port on which to bind the writer socket
                            (i.e. 8000)
        .. The *reader_port* and *writer_port* must be different.
        """
        assert reader_port != writer_port
        self.reader_address = (host, reader_port)
        self.writer_address = (host, writer_port)

    def create_selector(self,
                        consumed: queue.Queue,
                        produced: queue.Queue) -> Selector:
        """Create the `Selector` object.

        :param consumed: The queue of elements that needs to be sent
        :type consumed: :mod:`queue`.`Queue`
        :param produced: The queue of elements that were read
        :type produced: :mod:`queue`.`Queue`
        :returns: A selector with the given sockets
        :rtype: `Selector`
        """
        reader_socket = Socket()
        reader_socket_, _ = reader_socket.accept(*self.reader_address)

        writer_socket = Socket()
        writer_socket_, _ = writer_socket.accept(*self.writer_address)

        return Selector(reader_socket_, writer_socket_, consumed, produced)
