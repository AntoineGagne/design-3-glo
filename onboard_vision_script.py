from queue import LifoQueue
import time

import netifaces

from design.vision.camera import Camera, CameraSettings
from design.vision.onboard_vision import OnboardVision
from design.telemetry.commands import CommandHandler
from design.telemetry.packets import Packet, PacketType
from design.telemetry.selectors import ServerSelectorFactory
from design.vision.vertices import VerticesFinder, HighFrequencyFilter


if __name__ == "__main__":
    onboard_vision = OnboardVision(
        VerticesFinder(HighFrequencyFilter),
        Camera(cv2.CAP_ANY, CameraSettings())
    )
    consumed = LifoQueue()
    produced = LifoQueue()
    selector_factory = ServerSelectorFactory(
        netifaces.ifaddresses('wlp4s0')[2][0]['addr'],
        8000,
        8001
    )
    selector = selector_factory.create_selector(consumed, produced)
    command_handler = CommandHandler(selector, consumed, produced)
    while True:
        try:
            onboard_vision.capture()
            vertices = onboard_vision.get_captured_vertices(0, 0)
            command_handler.put_command(
                Packet(PacketType.FIGURE_VERTICES, vertices)
            )
            time.sleep(5)
            break
        except:
            continue
