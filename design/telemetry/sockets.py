"""Contains all the classes and functions related to communication with TCP
   sockets.
"""


import socket
import struct

from math import inf

from .packets import serialize_packet, deserialize_packet, Packet


class Socket:
    """A wrapper over TCP sockets for communication over a network. The
       protocol used for its message is the following:

       <message_length><delimiter><message_data>

       where
            * <message_length>: Length of the message including the size
                                of the length field itself and the delimiter.
            * <delimiter>: Delimiter used to separate the message's content
                           and the message's length.
            * <message_data>: The content of the message.
    """

    def __init__(self, socket_=None, **kwargs):
        """Initialize a `Socket` object.

        :param socket_: An existing socket (default: `None`)
        :type socket_: :mod:`socket`.`socket`
        :param kwargs: See below

        :Keyword Arguments:
            * *serialize* (`function`): The function used to serialize
                                        messages
            * *deserialize* (`function`): The function used to deserialize
                                          messages
            * *delimiter* (`bytes`): The byte used to delimit the message's
                                     length from its content
        """
        self._serialize = kwargs.get('serialize', serialize_packet)
        self._deserialize = kwargs.get('deserialize', deserialize_packet)
        self._delimiter = kwargs.get('delimiter', b':')
        if not socket_:
            self.socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM)
        else:
            self.socket = socket_

    def connect(self, host: str, port: str):
        """Connect with a specific host on a specific host.

        :param host: The host with which you want to connect (i.e. '127.0.0.1').
        :type host: str
        :param port: The port to connect
        :type port: str
        """
        self.socket.connect((host, port))

    def send(self, message: Packet):
        """Send the given message to the connected peer.

        :param message: The message to send
        :type message: `Packet`
        :returns: `None` if the message was successfully sent
        :raises :mod:`socket`.`error`: If there was a problem sending the
                                       message
        """
        encoded_message = self._encode_message(message)
        return self.socket.sendall(encoded_message)

    def _encode_message(self, message: Packet) -> bytes:
        """Encode the given message according to the messages' protocol
           specified earlier.

        :param message: The message to encode
        :type message: `Packet`
        :returns: The bytes corresponding to the protocol encoded message
        :rtype: bytes
        """
        serialized_message = self._serialize(message)

        message_length = len(serialized_message)
        message_length += len(str(message_length))

        encoded_message = struct.pack('>Ic{0}s'.format(len(serialized_message)),
                                      message_length + 1,
                                      self._delimiter,
                                      serialized_message)
        return encoded_message

    def receive(self) -> Packet:
        """Receive a message.

        :returns: A deserialized message
        :rtype: `Packet`
        """
        message = self._receive_all()
        return self._deserialize(message)

    def _receive_all(self) -> bytes:
        """Block and iterate over the message stream until it has successfully
           received all of the message chunks.

        :returns: The message's chunks
        :rtype: bytes
        """
        chunks = bytearray()
        total_received = 0
        message_length = inf
        delimiter_found = False
        while total_received < message_length:
            if self._delimiter in chunks and not delimiter_found:
                length, *chunks = chunks.split(self._delimiter)
                message_length = int.from_bytes(length, 'big')
                chunks = b':'.join(chunks)
                delimiter_found = True
            chunk = self.socket.recv(1024)
            chunks.extend(chunk)
            total_received += len(chunk)

        return chunks
