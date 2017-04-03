import queue

import zmq

from .constants import POLL_TIMEOUT
from .packets import serialize_packet, deserialize_packet


class Selector:
    def __init__(self,
                 read_socket: zmq.Socket,
                 write_socket: zmq.Socket,
                 consumed: queue.Queue,
                 produced: queue.Queue,
                 **kwargs):
        self.read_socket = read_socket
        self.write_socket = write_socket
        self._serialize = kwargs.get('serialize', serialize_packet)
        self._deserialize = kwargs.get('deserialize', deserialize_packet)
        self.consumed = consumed
        self.produced = produced

    def run(self):
        while True:
            self._consume()
            self._produce()

    def _consume(self):
        try:
            data = self.consumed.get_nowait()
            self.write_socket.send(self._serialize(data))
        except queue.Empty:
            pass

    def _produce(self):
        if self.read_socket.poll(POLL_TIMEOUT):
            data = self.read_socket.recv()
            self.produced.put_nowait(self._deserialize(data))


class ClientSelectorFactory:
    def __init__(self,
                 peer: str,
                 read_port: int,
                 write_port: int):
        assert read_port != write_port
        self.read_address = 'tcp://{0}:{1}'.format(peer, read_port)
        self.write_address = 'tcp://{0}:{1}'.format(peer, write_port)

    def create_selector(self,
                        consumed: queue.Queue,
                        produced: queue.Queue) -> Selector:
        context = zmq.Context()
        write_socket = context.socket(zmq.PUSH)
        write_socket.connect(self.write_address)

        read_socket = context.socket(zmq.PULL)
        read_socket.connect(self.read_address)

        return Selector(read_socket, write_socket, consumed, produced)


class ServerSelectorFactory:
    def __init__(self,
                 host: str,
                 read_port: int,
                 write_port: int):
        assert read_port != write_port
        self.read_address = 'tcp://{0}:{1}'.format(host, read_port)
        self.write_address = 'tcp://{0}:{1}'.format(host, write_port)

    def create_selector(self,
                        consumed: queue.Queue,
                        produced: queue.Queue) -> Selector:
        context = zmq.Context()
        read_socket = context.socket(zmq.PULL)
        read_socket.bind(self.read_address)

        write_socket = context.socket(zmq.PUSH)
        write_socket.bind(self.write_address)

        return Selector(read_socket, write_socket, consumed, produced)
