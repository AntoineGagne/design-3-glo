#! /usr/bin/env python
"""A script that starts the robot or the main station."""
from typing import Tuple

import cv2
import netifaces

import queue
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

import sys

from design.decision_making.brain import Brain
from design.decision_making.movement_strategy import MovementStrategy
from design.decision_making.constants import TranslationStrategyType
from design.decision_making.constants import RotationStrategyType
from design.interfacing.hardware_controllers import (AntennaController,
                                                     LightsController,
                                                     PenController)
from design.interfacing.interfacing_controller import InterfacingController
from design.interfacing.pen_driver import PenDriver
from design.interfacing.simulated_controllers import SimulatedWheelsController
from design.interfacing.stm32_driver import Stm32Driver
from design.telemetry.commands import CommandHandler
from design.telemetry.selectors import (ClientSelectorFactory,
                                        ServerSelectorFactory)
from design.vision.camera import Camera, CameraSettings
from design.vision.drawing_zone_detector import DrawingZoneDetector
from design.vision.obstacles_detector import ObstaclesDetector
from design.vision.robot_detector import RobotDetector
from design.vision.world_vision import WorldVision
from design.vision.onboard_vision import OnboardVision
from design.vision.vertices import HighFrequencyFilter, VerticesFinder
from design.ui.main_app import MainApp

CAMERA_SETTINGS_FILE = 'config/camera_optimized_values.json'


def parse_arguments():
    """Parse the command line arguments.

    :returns: The parsed arguments

    .. seealso::
        https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_args
    """
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
                            prog='main.py',
                            description='Start the main station or the robot.')
    subparser = parser.add_subparsers(title='Subcommands',
                                      description='Dispatch arguments to the '
                                                  'corresponding entity.')
    parent_parser = _create_parent_parser()
    main_station_parser = _create_main_station_parser(subparser, parent_parser)
    robot_parser = _create_robot_parser(subparser, parent_parser)
    return parser.parse_args()


def _create_parent_parser():
    """Create a parser that parse arguments common to subparsers."""
    parent_parser = ArgumentParser(add_help=False)
    networking_group = parent_parser.add_argument_group('networking arguments')
    networking_group.add_argument('-p',
                                  '--ports',
                                  nargs=2,
                                  type=int,
                                  required=True,
                                  metavar=('READ_PORT', 'WRITE_PORT'),
                                  help='The ports to bind to')
    vision_group = parent_parser.add_argument_group('vision arguments')
    vision_group.add_argument('-c',
                              '--camera_port',
                              default=cv2.CAP_ANY,
                              metavar='CAMERA_PORT',
                              help='The port of the camera to connect to')
    return parent_parser


def _create_main_station_parser(subparser, parent_parser):
    """Create a parser for the main station's specific arguments.

    :param subparser: The subparser to which we are adding the main station's
                      parser
    :param parent_parser: The common arguments
    :return: The main station's parser
    """
    main_station_parser = subparser.add_parser(
        'main_station',
        parents=[parent_parser],
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    main_station_parser.add_argument('-n',
                                     '--table-number',
                                     type=int,
                                     choices=tuple(range(1, 7)),
                                     default=1,
                                     metavar='TABLE_NUMBER',
                                     help='The table\'s number')
    main_station_parser.add_argument('-a',
                                     '--address',
                                     default='127.0.0.1',
                                     type=str,
                                     metavar='HOST_ADDRESS',
                                     dest='host',
                                     help='The host address on which to bind '
                                          'the socket')
    main_station_parser.set_defaults(function=start_main_station)
    return main_station_parser


def _create_robot_parser(subparser, parent_parser):
    """Create a parser for the robot's specific arguments.

    :param subparser: The subparser to which we are adding the main station's
                      parser
    :param parent_parser: The common arguments
    :return: The main station's parser
    """
    robot_parser = subparser.add_parser(
        'robot',
        parents=[parent_parser],
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    robot_parser.set_defaults(function=start_robot)
    return robot_parser


def start_main_station(arguments):
    """Start the main station and injects the dependencies.

    :param arguments: The command line arguments
    """
    command_handler = create_command_handler(arguments.host,
                                             arguments.ports,
                                             ClientSelectorFactory)
    obstacles_detector = ObstaclesDetector()
    robot_detector = RobotDetector()
    drawing_zone_detector = DrawingZoneDetector()
    camera = Camera(arguments.camera_port, CameraSettings(width=1600, height=1200), True)
    world_vision = WorldVision(arguments.table_number,
                               obstacles_detector,
                               drawing_zone_detector,
                               robot_detector,
                               camera)
    app = MainApp(sys.argv, command_handler, world_vision)
    sys.exit(app.exec_())


def start_robot(arguments):
    """Start the robot and inject the dependencies.

    :param arguments: The command line arguments
    """
    command_handler = create_command_handler(
        netifaces.ifaddresses('wlp4s0')[2][0]['addr'],
        arguments.ports,
        ServerSelectorFactory
    )
    onboard_vision = create_onboard_vision(arguments.camera_port)
    interfacing_controller = create_interfacing_controller()
    movement_strategy = create_movement_strategy()

    brain = Brain(
        command_handler,
        interfacing_controller,
        onboard_vision,
        movement_strategy
    )
    brain.main()


def create_interfacing_controller() -> InterfacingController:
    """Create the interfacing controller.

    :returns: The interfacing controller
    :rtype: :class:`design.interfacing.interfacing_controller.InterfacingController`
    """
    microcontroller_driver = Stm32Driver()
    prehensor_driver = PenDriver()
    return InterfacingController(
        SimulatedWheelsController(),
        AntennaController(microcontroller_driver),
        PenController(prehensor_driver),
        LightsController(microcontroller_driver)
    )


def create_movement_strategy() -> MovementStrategy:
    """Create the movement strategy.

    :returns: The movement strategy
    :rtype: :class:`design.decision_making.movement_strategy.MovementStrategy`
    """
    return MovementStrategy(
        TranslationStrategyType.VERIFY_CONSTANTLY_THROUGH_CINEMATICS,
        RotationStrategyType.VERIFY_CONSTANTLY_THROUGH_ANGULAR_CINEMATICS
    )


def create_command_handler(host: str,
                           ports: Tuple[int, int],
                           selector_factory) -> CommandHandler:
    """Create a command handler.

    :param host: The address of the sockets
    :type host: str
    :param ports: The read and write port of the sockets
    :type ports: tuple<int, int>
    :param selector_factory: The constructor of the corresponding selector
                             factory
    :returns: A command handler with the corresponding sockets
    :rtype :class:`design.telemetry.commands.CommandHandler`
    """
    consumer = queue.LifoQueue()
    producer = queue.LifoQueue()
    selector_factory = selector_factory(host, *ports)
    selector = selector_factory.create_selector(consumer, producer)

    return CommandHandler(selector, consumer, producer)


def create_onboard_vision(camera_port: int) -> OnboardVision:
    """Create an :class:`design.vision.onboard_vision.OnboardVision` object.

    :param camera_port: The port of the camera to connect to
    :returns: The onboard vision object
    :rtype: :class:`design.vision.onboard_vision.OnboardVision`
    """
    camera = Camera(camera_port, CameraSettings())
    vertices_finder = VerticesFinder(HighFrequencyFilter())
    return OnboardVision(vertices_finder, camera)


if __name__ == '__main__':
    arguments = parse_arguments()
    arguments.function(arguments)
