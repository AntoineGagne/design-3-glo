"""Contains all the classes and functions related to communication with TCP
   sockets.
"""


import socket
import struct

from math import inf
from typing import Tuple

from .constants import CHUNK_SIZE, MESSAGE_DELIMITER
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
        self._delimiter = kwargs.get('delimiter', MESSAGE_DELIMITER)
        if not socket_:
            self.socket = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM)
        else:
            self.socket = socket_

    def accept(self, host: str, port: int) -> Tuple['Socket', str]:
        """Accept incoming connection to the socket.

        :param host: The host on which to bind (i.e. '127.0.0.1')
        :type host: str
        :param port: The port on which to bind (i.e. 8000)
        :type port: int
        :returns: A tuple that contains a `Socket` usable to receive/send data
                  to the other connected socket and the address of the connected socket
        :rtype: tuple<`Socket`, str>
        """
        self.socket.bind((host, port))
        self.socket.listen()
        socket_, address = self.socket.accept()
        return Socket(socket_), address

    def connect(self, host: str, port: int):
        """Connect with a specific host on a specific host.

        :param host: The host with which you want to connect (i.e. '127.0.0.1').
        :type host: str
        :param port: The port to connect to
        :type port: int
        :raises :mod:`socket`.`timeout`: On timeout
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
        return self._deserialize(message) if message else None

    def fileno(self) -> int:
        """Get the socket's file descriptor or -1 on failure.

        :returns: The socket's file descriptor
        :rtype: int
        """
        return self.socket.fileno()

    def setblocking(self, flag: bool):
        """Set blocking or non-blocking mode of the socket.

        :param flag: The flag that indicates if the socket is blocking or not.
                     If `False`, the socket is non-blocking otherwise, it is
                     blocking.
        :type flag: bool
        """
        self.socket.setblocking(flag)

    def _receive_all(self) -> bytes:
        """Block and iterate over the message stream until it has successfully
           received all of the message chunks.

        :returns: The message's chunks
        :rtype: bytes
        """
        chunks = bytearray()
        total_received = 0
        message_length = inf
        # Necessary because there could be more than one delimiter in a given
        # message
        delimiter_found = False
        while total_received < message_length:
            if self._delimiter in chunks and not delimiter_found:
                length, *chunks = chunks.split(self._delimiter)
                message_length = int.from_bytes(length, 'big')
                # If there was other delimiters
                chunks = self._delimiter.join(chunks)
                delimiter_found = True
            chunk = self.socket.recv(CHUNK_SIZE)
            if not chunk:
                break
            chunks.extend(chunk)
            total_received += len(chunk)

        return chunks

    def close(self):
        """Close the socket.

        :raises OSError: If an error occurs
        """
        self.socket.close()
