""" This module has all preparation and action commands the robot can execute. """

import datetime
import time

from design.decision_making.constants import (Step,
                                              NUMBER_OF_SECONDS_BETWEEN_ROUTINE_CHECKS,
                                              next_step)
from design.pathfinding.exceptions import OutOfRetriesForCaptureError
from design.pathfinding.constants import (PointOfInterest,
                                          STANDARD_HEADING, PEN_TO_ANTENNA_OFFSET)
from design.telemetry.packets import (Packet, PacketType)
from design.vision.exceptions import PaintingFrameNotFound, VerticesNotFound


class Command():
    """ Allows execution of any command without the brain knowing the internals
    of said command """

    def __init__(self, step, interfacing_controller, pathfinder, logger):
        self.current_step = step
        self.hardware = interfacing_controller
        self.pathfinder = pathfinder
        self.logger = logger

    def is_positional_telemetry_recieved(self, telemetry_data):
        """ Verifies if data recieved from telemetry is a POSITION packet. If
        not, it sleeps for an arbitrary amount of time and returns false. If it is
        a position packet, returns true immediately.
        :param telemetry_data: Data recieved by telemetry
        :returns: A boolean indicating if said telemetry is recieved and is a position packet
        :rtype: boolean """
        if telemetry_data is None:
            return False
        elif not isinstance(telemetry_data, list):
            return False
        else:
            return True

    def execute(self, data):
        """ Executes the command and returns the new step the robot should be in,
        as well as any message that must be sent towards the base station through
        telemetry """
        raise NotImplementedError("execute() must be implemented!")


class BuildGameMapCommand(Command):
    """ Command that builds the game map according to corners, obstacles and
    points of interest """

    def execute(self, game_map_data):
        """ Builds game map """

        self.logger.log("Build Game Map: Execution.")

        self.hardware.lights.turn_off_red_led()

        self.pathfinder.set_game_map(game_map_data)

        rotation_angle = (self.pathfinder.robot_status.
                          set_target_heading_and_get_angular_difference(STANDARD_HEADING))
        self.logger.log("Build Game Map: Aligning westwards with rotation angle = {0}".format(rotation_angle))
        self.hardware.wheels.rotate(rotation_angle)

        return (next_step(self.current_step), None)


class PrepareTravelToAntennaAreaCommand(Command):
    """ Commands that sets the trajectory of the robot to go towards
    the antenna's general area """

    def execute(self, data):
        """ Executes preparation of travel to antenna command """

        if not self.is_positional_telemetry_recieved(data):
            return (self.current_step, None)

        self.logger.log("Prepare Travel to Antenna Area: Execution.")

        self.pathfinder.generate_path_to_checkpoint_a_to_b(self.pathfinder.get_point_of_interest(
            PointOfInterest.ANTENNA_START_SEARCH_POINT))

        self.pathfinder.robot_status.set_position(data[0])
        new_vector = (self.pathfinder.robot_status.
                      generate_new_translation_vector_towards_current_target(
                          self.pathfinder.robot_status.get_position()))

        self.logger.log("Prepare Travel to Antenna Area: Sending vector {0} to robot at position {1} to reach"
                        "the antenna's starting point.".format(new_vector, self.pathfinder.robot_status.get_position()))

        self.hardware.wheels.move(new_vector)

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class TravelToPaintingsAreaCommand(Command):
    """ Commands that sets the trajectory of the robot to the paintings
    section """

    def __init__(self, step, interfacing_controller, pathfinder, logger, antenna_information):
        super(TravelToPaintingsAreaCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.antenna_information = antenna_information

    def execute(self, telemetry_data):
        """ Sets trajectory of the robot to paintings area """

        if not self.is_positional_telemetry_recieved(telemetry_data):
            return (self.current_step, None)

        self.logger.log("Prepare Travel to Painting: Execution.")

        self.hardware.pen.raise_pen()

        self.logger.log(
            "Prepare Travel to Painting: painting_nb = {0}".format(self.antenna_information.painting_number))
        figure_position = self.pathfinder.figures.get_position_to_take_figure_from(
            self.antenna_information.painting_number)

        self.pathfinder.generate_path_to_checkpoint(figure_position)
        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                self.pathfinder.robot_status.get_position()))

        self.logger.log(
            "Prepare Travel to Painting: Sending {0} vector to robot at position {1} towards target {2}".format(
                self.hardware.wheels.last_vector_given, self.pathfinder.robot_status.get_position(),
                self.pathfinder.robot_status.target_position))

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class PrepareToDrawCommand(Command):
    """ Commands that lowers the pen and gives vectors list to draw """

    def __init__(self, step, interfacing_controller, pathfinder, logger, onboard_vision,
                 antenna_information):
        super(PrepareToDrawCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.vision = onboard_vision
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Starts drawing """

        self.logger.log("Prepare to Draw: Execution.")

        drawing_reference_origin = self.pathfinder.get_point_of_interest(
            PointOfInterest.DRAWING_ZONE)

        self.pathfinder.nodes_queue_to_checkpoint.clear()
        for vertex in self.vision.get_captured_vertices(self.antenna_information.zoom,
                                                        self.antenna_information.orientation):
            point_to_cross_x = drawing_reference_origin[0] + vertex[0]
            point_to_cross_y = drawing_reference_origin[1] + vertex[1]
            self.pathfinder.nodes_queue_to_checkpoint.append(
                (point_to_cross_x, point_to_cross_y))

        first_vertex_x, first_vertex_y = self.vision.get_captured_vertices(self.antenna_information.zoom,
                                                                           self.antenna_information.orientation)[0]

        first_vertex_x += drawing_reference_origin[0]
        first_vertex_y += drawing_reference_origin[1]
        self.pathfinder.nodes_queue_to_checkpoint.append((first_vertex_x, first_vertex_y))

        self.pathfinder.robot_status.set_position((first_vertex_x, first_vertex_y))

        self.logger.log("Prepare to Draw: Vertices to draw = {0}".format(self.pathfinder.nodes_queue_to_checkpoint))

        self.hardware.wheels.move(self.pathfinder.robot_status.generate_new_translation_vector_towards_new_target(
            self.pathfinder.nodes_queue_to_checkpoint.popleft()))
        self.hardware.pen.lower_pen()

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class PrepareExitOfDrawingAreaCommand(Command):
    """ Prepares the robot to leave the drawing zone """

    def execute(self, data):
        """ Executes exit of drawing area command """

        self.logger.log("Prepare Exit of Drawing Area: Execution.")

        self.hardware.pen.raise_pen()

        possible_exit_locations = self.pathfinder.get_point_of_interest(PointOfInterest.EXIT_DRAWING_ZONE_AFTER_CYCLE)

        for exit_location in possible_exit_locations:
            if self.pathfinder.is_checkpoint_accessible(exit_location):
                self.pathfinder.generate_path_to_checkpoint(exit_location)
                break

        self.logger.log("Prepare Exit of Drawing Area: Exit location at position = {0}".format(
            self.pathfinder.robot_status.target_position))

        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                self.pathfinder.robot_status.get_position()))

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class FinishCycleCommand(Command):
    """ Command that stops the current cycle and notifies the base station """

    def execute(self, data):
        """ Stops current cycle """
        self.logger.log("Cycle finished. Currently at position {0}".format(self.pathfinder.robot_status.get_position()))
        self.hardware.lights.turn_on_red_led()
        return (Step.STANBY, Packet(PacketType.COMMAND, "STOP_CHRONOGRAPH"))


class PrepareSearchForAntennaPositionCommand(Command):
    """ Starts sampling for antenna signal and gives movement vector along the
    wall so it can find the antenna's position easily """

    def execute(self, data):
        """ Starts search for antenna """

        print("prepare search for antenna position command")

        self.hardware.antenna.start_sampling()

        self.pathfinder.generate_path_to_checkpoint_a_to_b(
            self.pathfinder.get_point_of_interest(PointOfInterest.ANTENNA_STOP_SEARCH_POINT))

        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                self.pathfinder.robot_status.get_position()))

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class SearchForAntennaPositionCommand(Command):
    """ Does mostly the same thing as RoutineCheckCommand but starts sampling the signal's strength
    in order to build a curve, used to find the maximum value and thus, the antenna's position."""

    st_last_execution = datetime.datetime.now()

    def __init__(self, movement_strategy, step, interfacing_controller, pathfinder, logger, antenna_information,
                 servo_wheels_manager):
        super(SearchForAntennaPositionCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.logger = logger
        self.servo_wheels_manager = servo_wheels_manager
        self.movement_strategy = movement_strategy
        self.antenna_information = antenna_information

    def execute(self, robot_position_from_telemetry):
        """ Executes search for antenna command """

        if not self.is_positional_telemetry_recieved(robot_position_from_telemetry):
            return (self.current_step, None)

        self.logger.log("Search For Antenna Position: Execution.")

        # Executes normal routine check
        normal_routine_check = self.movement_strategy.get_translation_command(
            self.current_step, self.hardware, self.pathfinder, self.logger, self.servo_wheels_manager)
        step, exit_telemetry = normal_routine_check.execute(
            robot_position_from_telemetry)
        if (datetime.datetime.now() - SearchForAntennaPositionCommand.st_last_execution).total_seconds() \
                <= NUMBER_OF_SECONDS_BETWEEN_ROUTINE_CHECKS:
            return (step, None)

        SearchForAntennaPositionCommand.st_last_execution = datetime.datetime.now()

        current_signal_amplitude = self.hardware.antenna.get_signal_strength()
        if current_signal_amplitude is not None:
            self.logger.log("Search For Antenna Position: Obtaining value = {0} at position {1}".format(current_signal_amplitude,
                                                                                                        self.pathfinder.robot_status.get_position()))
            self.antenna_information.strength_curve[robot_position_from_telemetry[0]] = current_signal_amplitude

        return_telemetry = None
        if step != self.current_step:
            return_telemetry = Packet(PacketType.NOTIFICATION,
                                      "Antenna search completed. Building curve and finding max...")

        return (step, return_telemetry)


class PrepareMovingToAntennaPositionCommand(Command):
    """ Generates a vector used by the robot to move right in front of the antenna's location. """

    def __init__(self, step, interfacing_controller, pathfinder, logger, antenna_information):
        super(PrepareMovingToAntennaPositionCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.antenna_information = antenna_information

    def execute(self, telemetry_data):

        self.logger.log("Prepare Moving to Antenna Position: Execution.")

        self.hardware.antenna.stop_sampling()
        try:
            position_x, position_y = max(self.antenna_information.strength_curve,
                                         key=self.antenna_information.strength_curve.get)

            self.logger.log(
                "Prepare Moving to Antenna Position: Calculated position of max signal amplitude = {0}".format(
                    (position_x, position_y)))

            self.pathfinder.generate_path_to_checkpoint_a_to_b((position_x, position_y))
            self.hardware.wheels.move(
                self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                    self.pathfinder.robot_status.get_position()))

            self.logger.log(
                "Prepare Moving to Antenna Position: Sending vector = {0} to robot at position = {1} to target = {2}".format(
                    self.hardware.wheels.last_vector_given, self.pathfinder.robot_status.get_position(),
                    self.pathfinder.robot_status.target_position))

            return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))
        except ValueError:
            return (Step.COMPUTE_PAINTINGS_AREA,
                    Packet(PacketType.NOTIFICATION, "Antenna position has not been found! Aborting search."))

class PrepareMovingOfAntennaOffsetCommand(Command):

    def execute(self, data):

        self.logger.log("Prepare Moving of Antenna Offset: Execution.")

        position_x, position_y = self.pathfinder.robot_status.get_position()
        position_y = position_y + PEN_TO_ANTENNA_OFFSET

        self.pathfinder.generate_path_to_checkpoint_a_to_b((position_x, position_y))

        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                self.pathfinder.robot_status.get_position()))

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class PrepareMarkingAntennaCommand(Command):
    """ Prepares movement in order to mark the antenna's position. """

    def __init__(self, step, interfacing_controller, pathfinder, logger, antenna_information):
        super(PrepareMarkingAntennaCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Executes marking antenna preparation command """

        self.logger.log("Prepare Marking Antenna: Execution.")

        self.hardware.pen.lower_pen()

        position_x, position_y = self.pathfinder.robot_status.get_position()
        position_x = position_x - 0.8

        self.pathfinder.generate_path_to_checkpoint_a_to_b((position_x, position_y))

        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                self.pathfinder.robot_status.get_position()))

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class PrepareTravelToDrawingAreaCommand(Command):
    """ Prepares movement vector to travel to the center of the drawing zone """

    def __init__(self, current_step, interfacing_controller, pathfinder, logger, vision, antenna_information):
        super(PrepareTravelToDrawingAreaCommand, self).__init__(current_step,
                                                                interfacing_controller, pathfinder, logger)
        self.vision_data = vision
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Executes travel to drawing area command """

        self.logger.log("Prepare Travel to Drawing Area: Execution.")

        drawing_zone_origin_x, drawing_zone_origin_y = self.pathfinder.get_point_of_interest(
            PointOfInterest.DRAWING_ZONE)

        first_vertex_x, first_vertex_y = self.vision_data.get_captured_vertices(
            self.antenna_information.zoom, self.antenna_information.orientation)[0]

        position_x = drawing_zone_origin_x + first_vertex_x
        position_y = drawing_zone_origin_y + first_vertex_y

        self.logger.log("Prepare Travel to Drawing Area: Moving towards first vertex at position = {0}".format(
            (position_x, position_y)))

        self.pathfinder.generate_path_to_checkpoint((position_x, position_y))

        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                self.pathfinder.robot_status.get_position()))

        self.logger.log(
            "Prepare Travel to Drawing Area: Sending vector = {0} to robot at position = {1} to target = {2}".format(
                self.hardware.wheels.last_vector_given, self.pathfinder.robot_status.get_position(),
                self.pathfinder.robot_status.target_position))

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class AcquireInformationFromAntennaCommand(Command):
    """ Allows acquisition and safeguarding of the information
    emitted by the antenna """

    def __init__(self, step, interfacing_controller, pathfinder, logger, antenna_information):
        super(AcquireInformationFromAntennaCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Executes acquisition command """
        self.logger.log("Acquire Information From Antenna: Execution.")

        antenna_data = None
        antenna_data = self.hardware.antenna.get_information_from_signal()

        if antenna_data is None:
            self.logger.log("Acquire Information From Antenna: Not acquired yet.")
            return (self.current_step, None)
        elif antenna_data is not None and antenna_data.painting_number is None and antenna_data.zoom is None and antenna_data.orientation is None:
            self.logger.log(
                "Acquire Information From Antenna: Acquisition has failed. Going back to starting search point and retrying the entire sequence.")
            self.hardware.antenna.reinitialize()
            return (Step.PREPARE_TRAVEL_TO_ANTENNA_ZONE,
                    Packet(PacketType.NOTIFICATION, "Acquisition has failed. Going back to starting search point."))
        else:
            self.logger.log("Acquire Information From Antenna: Acquired! PNB = {0} - ZOOM = {1} - ORI = {2}".format(
                int(antenna_data.painting_number), int(antenna_data.zoom), int(antenna_data.orientation)))
            self.antenna_information.painting_number = int(antenna_data.painting_number)
            self.antenna_information.zoom = int(antenna_data.zoom)
            self.antenna_information.orientation = float(antenna_data.orientation)
            return (next_step(self.current_step), None)


class FaceRelevantFigureForCaptureCommand(Command):
    """ Allows the robot to start its rotation towards a FOV zone where it can
    capture the relevant figure """

    def __init__(self, step, interfacing_controller, pathfinder, logger, antenna_information):
        super(FaceRelevantFigureForCaptureCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Executes face relevant figure for capture command """

        self.logger.log("Face Relevant Figure for Capture: Execution.")

        orientation = self.pathfinder.figures.get_orientation_to_take_figure_from(
            self.antenna_information.painting_number)

        rotation_angle = (self.pathfinder.robot_status.
                          set_target_heading_and_get_angular_difference(orientation))

        self.logger.log(
            "Face Relevant Figure for Capture: Requested heading = {0} deg - Rotation angle = {0} deg".format(
                self.pathfinder.robot_status.target_position, rotation_angle))

        self.hardware.wheels.rotate(rotation_angle)

        return (next_step(self.current_step), None)


class CaptureFigureCommand(Command):
    """ Allows the robot to capture the relevant figure """

    def __init__(self, step, interfacing_controller, pathfinder, logger, antenna_information, onboard_vision):
        super(CaptureFigureCommand, self).__init__(step, interfacing_controller, pathfinder, logger)
        self.vision = onboard_vision
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Executes capture command """

        self.logger.log(
            "Capture Figure: Execution with zoom = {0} and orientation = {1}".format(self.antenna_information.zoom,
                                                                                     self.antenna_information.orientation))

        try:
            self.vision.capture()
            self.vision.get_captured_vertices(self.antenna_information.zoom, self.antenna_information.orientation)

            self.logger.log("Capture Figure: Success.")

            self.hardware.lights.light_green_led(1000)

            rotation_angle = (self.pathfinder.robot_status.
                              set_target_heading_and_get_angular_difference(STANDARD_HEADING))
            self.hardware.wheels.rotate(rotation_angle)

            self.logger.log("Capture Figure: Rotating to standard heading from heading = {0}".format(
                self.hardware.wheels.last_degrees_of_rotation_given))

            self.vision.pixel_coordinates.append(self.vision.pixel_coordinates[0])

            return (next_step(self.current_step), [Packet(PacketType.FIGURE_VERTICES, self.vision.pixel_coordinates),
                                                   Packet(PacketType.FIGURE_IMAGE, self.vision.last_capture)])
        except PaintingFrameNotFound:
            self.logger.log("Capture Figure: Failure - Painting Frame Not Found")
            return (Step.REPOSITION_FOR_CAPTURE_RETRY, None)
        except VerticesNotFound:
            self.logger.log("Capture Figure: Failure - Vertices Not Found")
            return (Step.REPOSITION_FOR_CAPTURE_RETRY, None)


class RepositionForCaptureRetryCommand(Command):
    """ This command randomizes a slight movement delta in order to retry the capture. """

    def __init__(self, step, interfacing_controller, pathfinder, logger, capture_repositioning_manager):
        super(RepositionForCaptureRetryCommand, self).__init__(step, interfacing_controller, pathfinder, logger)
        self.capture_repositioning_manager = capture_repositioning_manager

    def execute(self, telemetry_data):
        """ Executes the repositioning command """

        if not self.is_positional_telemetry_recieved(telemetry_data):
            return (self.current_step, None)

        self.logger.log("Reposition For Capture Retry: Execution.")

        heading = telemetry_data[1]

        try:
            vector = self.capture_repositioning_manager.get_new_retry_vector(heading)
            self.hardware.wheels.move(vector)
            time.sleep(2)
            return (Step.CAPTURE_CORRECT_PAINTING, None)
        except OutOfRetriesForCaptureError:
            self.logger.log("Reposition For Capture Retry: Out of retries! Aborting cycle.")
            return (Step.STANBY, Packet(PacketType.NOTIFICATION, "Out of capture retry attempts. Aborting cycle."))


class PrepareAlignWithCaptureCommand(Command):

    def __init__(self, step, interfacing_controller, pathfinder, logger, antenna_information):
        super(PrepareAlignWithCaptureCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.antenna_information = antenna_information

    def execute(self, telemetry_data):

        if not self.is_positional_telemetry_recieved(telemetry_data):
            return (self.current_step, None)

        self.logger.log("Prepare Align With Capture Command: Execution")
        figure_position = self.pathfinder.figures.get_position_to_take_figure_from(
            self.antenna_information.painting_number)

        self.pathfinder.generate_path_to_checkpoint_a_to_b(figure_position)
        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(telemetry_data[0]))

        return (next_step(self.current_step), self.pathfinder.get_current_path())


class PrepareRealignWithFirstVertexDrawnCommand(Command):

    def __init__(self, step, interfacing_controller, pathfinder, logger, onboard_vision,
                 antenna_information):
        super(PrepareRealignWithFirstVertexDrawnCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.vision = onboard_vision
        self.antenna_information = antenna_information

    def execute(self, telemetry_data):

        if not self.is_positional_telemetry_recieved(telemetry_data):
            return (self.current_step, None)

        self.logger.log("Prepare Realign With First Vertex Drawn: Execution.")

        drawing_zone_origin_x, drawing_zone_origin_y = self.pathfinder.get_point_of_interest(
            PointOfInterest.DRAWING_ZONE)

        first_vertex_x, first_vertex_y = self.vision.get_captured_vertices(
            self.antenna_information.zoom, self.antenna_information.orientation)[0]

        position_x = drawing_zone_origin_x + first_vertex_x
        position_y = drawing_zone_origin_y + first_vertex_y

        self.logger.log("Prepare Realign With First Vertex Drawn: Moving towards first vertex at position = {0}".format(
            (position_x, position_y)))

        self.pathfinder.generate_path_to_checkpoint_a_to_b((position_x, position_y))

        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(telemetry_data[0]))

        return (next_step(self.current_step), self.pathfinder.get_current_path())
