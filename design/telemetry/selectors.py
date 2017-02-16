"""Contains all the classes and functions related to non-blocking
   communication.
"""


import queue

import zmq

from .packets import serialize_packet, deserialize_packet


class Selector:
    """Select sockets according to some events such as readable/writable and
       perform actions.
    """
    def __init__(self,
                 read_socket: zmq.Socket,
                 write_socket: zmq.Socket,
                 consumed: queue.Queue,
                 produced: queue.Queue):
        """Initialize the `Selector`.

        :param read_socket: The socket that will receive inputs
        :type read_socket: :mod:`zmq`.`Socket`
        :param write_socket: The socket that will write outputs
        :type write_socket: :mod:`zmq`.`Socket`
        :param consumed: The packets to be sent
        :type consumed: :mod:queue.Queue
        :param produced: The received packets
        :type produced: :mod:queue.Queue
        """
        self.read_socket = read_socket
        self.write_socket = write_socket
        self.consumed = consumed
        self.produced = produced

    def run(self):
        """Loop and block until a socket is ready to be read from/written to."""
        while True:
            self._consume()
            self._produce()

    def _consume(self):
        """Send the oldest packet in the consumer queue."""
        try:
            data = self.consumed.get_nowait()
            self.write_socket.send(serialize_packet(data))
        except queue.Empty:
            pass

    def _produce(self):
        """Receive a packet and put it in the produced queue."""
        if self.read_socket.poll(10):
            data = self.read_socket.recv()
            print(data)
            self.produced.put_nowait(deserialize_packet(data))


class ClientSelectorFactory:
    """Create a `Selector` object that contains the client side sockets."""
    def __init__(self,
                 host: str,
                 read_port: int,
                 write_port: int):
        """Initialize the `ClientSelectorFactory`.

        :param host: The host on which to bind (i.e. '127.0.0.1')
        :type host: str
        :param read_port: The port on which to bind the reader socket
                          (i.e. 8000)
        :type read_port: int
        :param write_port: The port on which to bind the writer socket
                           (i.e. 8000)
        :type write_port: int

        .. important:: The *reader_port* and *writer_port* must be different.
        """
        assert read_port != write_port
        self.read_address = 'tcp://{0}:{1}'.format(host, read_port)
        self.write_address = 'tcp://{0}:{1}'.format(host, write_port)

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
        context = zmq.Context()
        write_socket = context.socket(zmq.PUSH)
        write_socket.bind(self.write_address)

        read_socket = context.socket(zmq.PULL)
        read_socket.connect(self.read_address)

        return Selector(read_socket, write_socket, consumed, produced)


class ServerSelectorFactory:
    """Create a `Selector` object that contains the server side sockets."""
    def __init__(self,
                 host: str,
                 read_port: int,
                 write_port: int):
        """Initialize the `ServerSelectorFactory`.

        :param host: The host on which to bind (i.e. '127.0.0.1')
        :type host: str
        :param read_port: The port on which to bind the reader socket
                          (i.e. 8000)
        :type read_port: int
        :param write_port: The port on which to bind the writer socket
                           (i.e. 8000)
        :type write_port: int

        .. important:: The *reader_port* and *writer_port* must be different.
        """
        assert read_port != write_port
        self.read_address = 'tcp://{0}:{1}'.format(host, read_port)
        self.write_address = 'tcp://{0}:{1}'.format(host, write_port)

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
        context = zmq.Context()
        read_socket = context.socket(zmq.PULL)
        read_socket.connect(self.read_address)

        write_socket = context.socket(zmq.PUSH)
        write_socket.bind(self.write_address)

        return Selector(read_socket, write_socket, consumed, produced)
