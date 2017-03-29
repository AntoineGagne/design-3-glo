"""Contains all the classes and functions related to non-blocking
   communication.
"""


import queue

import zmq

from .constants import POLL_TIMEOUT
from .packets import serialize_packet, deserialize_packet


class Selector:
    """Select sockets according to some events such as readable/writable and
       perform actions.
    """
    def __init__(self,
                 read_socket: zmq.Socket,
                 write_socket: zmq.Socket,
                 consumed: queue.Queue,
                 produced: queue.Queue,
                 **kwargs):
        """Initialize the `Selector`.

        :param read_socket: The socket that will receive inputs
        :type read_socket: :class:`zmq.Socket`
        :param write_socket: The socket that will write outputs
        :type write_socket: :class:`zmq.Socket`
        :param consumed: The packets to be sent
        :type consumed: :class:`queue.Queue`
        :param produced: The received packets
        :type produced: :class:`queue.Queue`
        :param kwargs: See below

        :Keyword Arguments:
            * *serialize* (function): The function used to serialize
                                      messages
            * *deserialize* (function): The function used to deserialize
                                        messages
        """
        self.read_socket = read_socket
        self.write_socket = write_socket
        self._serialize = kwargs.get('serialize', serialize_packet)
        self._deserialize = kwargs.get('deserialize', deserialize_packet)
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
            self.write_socket.send(self._serialize(data))
        except queue.Empty:
            pass

    def _produce(self):
        """Receive a packet and put it in the produced queue."""
        if self.read_socket.poll(POLL_TIMEOUT):
            data = self.read_socket.recv()
            self.produced.put_nowait(self._deserialize(data))


class ClientSelectorFactory:
    """Create a `Selector` object that contains the client side sockets."""
    def __init__(self,
                 peer: str,
                 read_port: int,
                 write_port: int):
        """Initialize the `ClientSelectorFactory`.

        :param peer: The address to connect to (i.e. '198.162.0.1')
        :type peer: str
        :param read_port: The port on which to bind the reader socket
                          (i.e. 8000)
        :type read_port: int
        :param write_port: The port on which to bind the writer socket
                           (i.e. 8000)
        :type write_port: int
        :raises AssertionError: If *read_port* and *write_port* are equal

        .. important:: The *reader_port* and *writer_port* must be different.
        """
        assert read_port != write_port
        self.read_address = 'tcp://{0}:{1}'.format(peer, read_port)
        self.write_address = 'tcp://{0}:{1}'.format(peer, write_port)

    def create_selector(self,
                        consumed: queue.Queue,
                        produced: queue.Queue) -> Selector:
        """Create the `Selector` object.

        :param consumed: The queue of elements that needs to be sent
        :type consumed: :class:`queue.Queue`
        :param produced: The queue of elements that were read
        :type produced: :class:`queue.Queue`
        :returns: A selector with the given sockets
        :rtype: :class:`design.telemetry.selectors.Selector`
        """
        context = zmq.Context()
        write_socket = context.socket(zmq.PUSH)
        write_socket.connect(self.write_address)

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
        :raises AssertionError: If *read_port* and *write_port* are equal

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
        :type consumed: :class:`queue.Queue`
        :param produced: The queue of elements that were read
        :type produced: :class:`queue.Queue`
        :returns: A selector with the given sockets
        :rtype: :class:`design.telemetry.selectors.Selector`
        """
        context = zmq.Context()
        read_socket = context.socket(zmq.PULL)
        read_socket.bind(self.read_address)

        write_socket = context.socket(zmq.PUSH)
        write_socket.bind(self.write_address)

        return Selector(read_socket, write_socket, consumed, produced)
