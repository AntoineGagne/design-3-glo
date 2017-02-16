"""Contains all the classes and functions related to communication with TCP
   sockets.
"""


import zmq

from .packets import serialize_packet, deserialize_packet, Packet


class SocketSendError(Exception):
    pass


class SocketReadError(Exception):
    pass


class Socket(zmq.Socket):
    """A wrapper over `ZMQ` sockets for communication over a network with a
       custom serializing protocol.
    """

    def __init__(self, *args, **kwargs):
        """Initialize a `Socket` object.

        :param args: See `zmq API documentation <https://pyzmq.readthedocs.io/en/latest/api/zmq.html#socket>`
        :param kwargs: See below

        :Keyword Arguments:
            * *serialize* (`function`): The function used to serialize
                                        messages
            * *deserialize* (`function`): The function used to deserialize
                                          messages
        """
        self._serialize = kwargs.get('serialize', serialize_packet)
        self._deserialize = kwargs.get('deserialize', deserialize_packet)
        super().__init__(*args, **kwargs)

    def send(self, message: Packet):
        """Send the given message to the connected peer.

        :param message: The message to send
        :type message: `Packet`
        :returns: `None` if the message was successfully sent
        :raises SocketSendError: If the send does not succeed for any reason
        """
        try:
            return super().send(self._serialize(message))
        except zmq.ZMQError as error:
            raise SocketSendError(*error.args)

    def recv(self) -> Packet:
        """Receive a message.

        :returns: A deserialized message
        :rtype: `Packet`
        :raises SocketReadError: If the
        """
        try:
            message = super().recv()
            return self._deserialize(message) if message else None
        except zmq.ZMQError as error:
            raise SocketReadError(*error.args)
