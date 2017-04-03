import queue
import threading

from .selectors import Selector


class CommandHandler:
    def __init__(self,
                 selector: Selector,
                 consumed: queue.Queue,
                 produced: queue.Queue):
        self._consumed = consumed
        self._produced = produced

        self._selector = selector
        self._selector_thread = threading.Thread(target=self._selector.run,
                                                 daemon=True)
        self._selector_thread.start()

    def put_command(self, packet):
        try:
            self._consumed.put_nowait(packet)
        except queue.Full:
            pass

    def fetch_command(self):
        command = None
        try:
            command = self._produced.get_nowait()
        except queue.Empty:
            pass

        return command
