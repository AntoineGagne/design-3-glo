""" This module has all necessary commands that can be executed by the robot.
A command always return a (next_step, exiting_telemetry_msg) tuple."""

import datetime
import time
import math
import numpy
from design.decision_making.constants import (Step,
                                              NUMBER_OF_SECONDS_BETWEEN_ROTATION_CHECKS,
                                              NUMBER_OF_SECONDS_BETWEEN_ROUTINE_CHECKS,
                                              next_step)
from design.pathfinding.exceptions import CheckpointNotAccessibleError
from design.pathfinding.pathfinder import PathStatus
from design.pathfinding.constants import (PointOfInterest,
                                          STANDARD_HEADING, TRANSLATION_SPEED, DEVIATION_THRESHOLD)
from design.telemetry.packets import (Packet, PacketType)
from design.vision.exceptions import PaintingFrameNotFound, VerticesNotFound


class Command():
    """ Allows execution of any command without the brain knowing the internals
    of said command """

    st_last_execution = datetime.datetime.now()

    def __init__(self, step, interfacing_controller, pathfinder):
        self.current_step = step
        self.hardware = interfacing_controller
        self.pathfinder = pathfinder

    def execute(self, data):
        """ Executes the command and returns the new step the robot should be in,
        as well as any message that must be sent towards the base station through
        telemetry """
        raise NotImplementedError("execute() must be implemented!")


class TranslationCommand(Command):

    def is_positional_telemetry_recieved(self, telemetry_data):
        """ Verifies if data recieved from telemetry is a POSITION packet. If
        not, it sleeps for an arbitrary amount of time and returns false. If it is
        a position packet, returns true immediately.
        :param telemetry_data: Data recieved by telemetry
        :returns: A boolean indicating if said telemetry is recieved and is a position packet
        :rtype: boolean """
        if telemetry_data is None or not isinstance(
                telemetry_data.packet_type, PacketType.POSITION):
            time.sleep(50)
            return False
        else:
            return True

    def update_current_vector_if_necessary_and_determine_next_step(self, robot_position_from_telemetry):
        """ Verifies if the robot is approaching a node. If it is a checkpoint,
        return the next step of the robot's routine, as the movement is completed.
        If it is not a checkpoint, simply change direction towards the next node and stay at the current step.
        If it is not approaching a node, carry on as usual and stay at the current step.
        :param robot_position_from_telemetry: Robot position recieved through telemetry, if applicables
        :returns: Updated step of the robot's routine.
        :rtype: `design.decision_making.constants.Step`"""
        path_status, new_vector = self.pathfinder.get_vector_to_next_node(
            robot_position_from_telemetry)  # This method only does so if necessary!

        if new_vector:
            self.hardware.wheels.move(new_vector)

        new_step = self.current_step
        if path_status == PathStatus.CHECKPOINT_REACHED:
            new_step = next_step(self.current_step)

        print("Updated step: {0}".format(new_step))

        return new_step


class BuildGameMapCommand(Command):
    """ Command that builds the game map according to corners, obstacles and
    points of interest """

    def execute(self, game_map_data):
        """ Builds game map """

        print("build game map")

        self.hardware.lights.turn_off_red_led()

        self.pathfinder.set_game_map(game_map_data)

        rotation_angle = (self.pathfinder.robot_status.
                          set_target_heading_and_get_angular_difference(STANDARD_HEADING))
        self.hardware.wheels.rotate(rotation_angle)

        return (next_step(self.current_step), None)


class PrepareTravelToAntennaAreaCommand(Command):
    """ Commands that sets the trajectory of the robot to go towards
    the antenna's general area """

    def execute(self, data):
        """ Executes preparation of travel to antenna command """

        print("prepare travel to antenna area")

        self.pathfinder.generate_path_to_checkpoint_a_to_b(self.pathfinder.get_point_of_interest(
            PointOfInterest.ANTENNA_START_SEARCH_POINT))

        new_vector = (self.pathfinder.robot_status.
                      generate_new_translation_vector_towards_current_target(
                          self.pathfinder.robot_status.get_position()))
        self.hardware.wheels.move(new_vector)

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class TravelToPaintingsAreaCommand(Command):
    """ Commands that sets the trajectory of the robot to the paintings
    section """

    def __init__(self, step, interfacing_controller, pathfinder, antenna_information):
        super(TravelToPaintingsAreaCommand, self).__init__(
            step, interfacing_controller, pathfinder)
        self.antenna_information = antenna_information

    def execute(self, telemetry_data):
        """ Sets trajectory of the robot to paintings area """

        print("prepare travel to painting")

        self.hardware.pen.raise_pen()

        print("Painting number: {0}".format(self.antenna_information.painting_number))
        figure_position = self.pathfinder.figures.get_position_to_take_figure_from(
            self.antenna_information.painting_number)

        self.pathfinder.generate_path_to_checkpoint(figure_position)
        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                self.pathfinder.robot_status.get_position()))

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class PrepareToDrawCommand(Command):
    """ Commands that lowers the pen and gives vectors list to draw """

    def __init__(self, step, interfacing_controller, pathfinder, onboard_vision,
                 antenna_information):
        super(PrepareToDrawCommand, self).__init__(
            step, interfacing_controller, pathfinder)
        self.vision = onboard_vision
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Starts drawing """

        print("prepare to draw")

        drawing_reference_origin = self.pathfinder.get_point_of_interest(
            PointOfInterest.DRAWING_ZONE)

        self.pathfinder.nodes_queue_to_checkpoint.clear()
        for vertex in self.vision.get_captured_vertices(self.antenna_information.zoom,
                                                        self.antenna_information.orientation):
            point_to_cross_x = drawing_reference_origin[0] + vertex[0]
            point_to_cross_y = drawing_reference_origin[1] + vertex[1]
            self.pathfinder.nodes_queue_to_checkpoint.append(
                (point_to_cross_x, point_to_cross_y))

        self.hardware.wheels.move(self.pathfinder.robot_status.generate_new_translation_vector_towards_new_target(
            self.pathfinder.nodes_queue_to_checkpoint.popleft()))
        self.hardware.pen.lower_pen()

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class PrepareExitOfDrawingAreaCommand(Command):
    """ Prepares the robot to leave the drawing zone """

    def execute(self, data):
        """ Executes exit of drawing area command """

        print("prepare exit of drawing area")

        self.hardware.pen.raise_pen()

        possible_exit_locations = self.pathfinder.get_point_of_interest(PointOfInterest.EXIT_DRAWING_ZONE_AFTER_CYCLE)

        for exit_location in possible_exit_locations:
            try:
                self.pathfinder.generate_path_to_checkpoint(exit_location)
                break
            except CheckpointNotAccessibleError:
                pass

        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                self.pathfinder.robot_status.get_position()))

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class FinishCycleCommand(Command):
    """ Command that stops the current cycle and notifies the base station """

    def execute(self, data):
        """ Stops current cycle """
        print("Cycle finished. Currently at position {0}".format(self.pathfinder.robot_status.get_position()))
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

    def __init__(self, movement_strategy, step, interfacing_controller, pathfinder, antenna_information):
        super(SearchForAntennaPositionCommand, self).__init__(
            step, interfacing_controller, pathfinder)
        self.movement_strategy = movement_strategy
        self.antenna_information = antenna_information

    def execute(self, robot_position_from_telemetry):
        """ Executes search for antenna command """

        # Executes normal routine check
        normal_routine_check = self.movement_strategy.get_translation_command(
            self.current_step, self.hardware, self.pathfinder)
        step, exit_telemetry = normal_routine_check.execute(
            robot_position_from_telemetry)

        if (datetime.datetime.now() - Command.st_last_execution).total_seconds() <= NUMBER_OF_SECONDS_BETWEEN_ROUTINE_CHECKS:
            return(step, None)

        current_signal_amplitude = self.hardware.antenna.get_signal_strength()
        if current_signal_amplitude is not None:
            print("Obtaining value = {0}".format(current_signal_amplitude))
            self.antenna_information.strength_curve[self.pathfinder.robot_status.get_position()] = current_signal_amplitude

        return_telemetry = None
        if step != self.current_step:
            return_telemetry = Packet(PacketType.NOTIFICATION, "Antenna search completed. Building curve and finding max...")

        return (step, return_telemetry)


class PrepareMovingToAntennaPositionCommand(Command):
    """ Generates a vector used by the robot to move right in front of the antenna's location. """

    def __init__(self, step, interfacing_controller, pathfinder, antenna_information):
        super(PrepareMovingToAntennaPositionCommand, self).__init__(
            step, interfacing_controller, pathfinder)
        self.antenna_information = antenna_information

    def execute(self, telemetry_data):

        print("prepare moving to antenna position")

        self.hardware.antenna.stop_sampling()
        try:
            position_x, position_y = max(self.antenna_information.strength_curve,
                                         key=self.antenna_information.strength_curve.get)

            self.pathfinder.generate_path_to_checkpoint_a_to_b((position_x, position_y))
            self.hardware.wheels.move(
                self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                    self.pathfinder.robot_status.get_position()))

            return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))
        except ValueError:
            return (Step.COMPUTE_PAINTINGS_AREA, Packet(PacketType.NOTIFICATION, "Antenna position has not been found! Aborting search."))


class PrepareMarkingAntennaCommand(Command):
    """ Prepares movement in order to mark the antenna's position. """

    def __init__(self, step, interfacing_controller, pathfinder, antenna_information):
        super(PrepareMarkingAntennaCommand, self).__init__(
            step, interfacing_controller, pathfinder)
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Executes marking antenna preparation command """

        print("prepare to mark")

        self.hardware.pen.lower_pen()

        position_x, position_y = self.pathfinder.robot_status.get_position()
        position_x = position_x - 2
        self.pathfinder.generate_path_to_checkpoint_a_to_b((position_x, position_y))

        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                self.pathfinder.robot_status.get_position()))

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class PrepareTravelToDrawingAreaCommand(Command):
    """ Prepares movement vector to travel to the center of the drawing zone """

    def __init__(self, current_step, interfacing_controller, pathfinder, vision, antenna_information):
        super(PrepareTravelToDrawingAreaCommand, self).__init__(current_step,
                                                                interfacing_controller, pathfinder)
        self.vision_data = vision
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Executes travel to drawing area command """

        print("Prepare travel to drawing area...")

        drawing_zone_origin_x, drawing_zone_origin_y = self.pathfinder.get_point_of_interest(
            PointOfInterest.DRAWING_ZONE)

        first_vertex_x, first_vertex_y = self.vision_data.get_captured_vertices(
            self.antenna_information.zoom, self.antenna_information.orientation)[0]

        position_x = drawing_zone_origin_x + first_vertex_x
        position_y = drawing_zone_origin_y + first_vertex_y

        self.pathfinder.generate_path_to_checkpoint((position_x, position_y))

        self.hardware.wheels.move(
            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(
                self.pathfinder.robot_status.get_position()))

        return (next_step(self.current_step), Packet(PacketType.PATH, self.pathfinder.get_current_path()))


class RoutineCheckCommand(TranslationCommand):
    """ Command that performs a routine check. Checks if robot is not
        deviating, otherwise corrects trajectory, and switches to new
        movement vector if the robot is within threshold if it's next
        node in the graph. """

    def execute(self, robot_position_from_telemetry):
        """ Performs the routine check command """

        time_passed = datetime.datetime.now() - Command.st_last_execution
        if time_passed.total_seconds() <= NUMBER_OF_SECONDS_BETWEEN_ROUTINE_CHECKS and \
           not robot_position_from_telemetry:
            return (self.current_step, None)

        Command.st_last_execution = datetime.datetime.now()

        self.pathfinder.robot_status.update_position()

        # Verifying current trajectory if we recieve our position from
        # telemetry
        if robot_position_from_telemetry:
            if self.pathfinder.verify_if_deviating(robot_position_from_telemetry):
                new_vector = (self.pathfinder.robot_status.
                              generate_new_translation_vector_towards_current_target(
                                  robot_position_from_telemetry))
                self.hardware.wheels.move(new_vector)

        return (self.update_current_vector_if_necessary_and_determine_next_step(robot_position_from_telemetry), None)


class RoutineCheckThroughTelemetryCommand(TranslationCommand):
    """ Command that performs a routine check. Checks if robot is not
        deviating, otherwise corrects trajectory, and switches to new
        movement vector if the robot is within threshold if it's next
        node in the graph. Only updates supposed position when it is recieved
        from telemetry."""

    def execute(self, telemetry_data):
        """ Performs the routine check command """

        if not self.is_positional_telemetry_recieved(telemetry_data):
            return (self.current_step, None)

        real_position = telemetry_data[0]
        position_timestamp = telemetry_data[2]

        self.pathfinder.robot_status.update_position(position_timestamp)

        # Build ORIGIN_TO_REAL_TARGET and ORIGIN_TO_REAL_POSITION_VECTOR
        origin_to_target_vector = self.pathfinder.robot_status.get_translation_vector()
        origin_to_real_position_vector = (real_position[0] - self.pathfinder.robot_status.origin_of_movement_vector[0],
                                          real_position[1] - self.pathfinder.robot_status.origin_of_movement_vector[1])

        # Calculate if there is a non-negligible angle between the two vectors: if there is, the robot
        # is deviating
        dot_product = numpy.dot(origin_to_real_position_vector, origin_to_target_vector)
        angle = math.acos(dot_product / (
            math.hypot(origin_to_target_vector[0], origin_to_target_vector[1]) * math.hypot(
                origin_to_real_position_vector[0], origin_to_real_position_vector[1])))

        return_telemetry = None
        if angle >= DEVIATION_THRESHOLD:
            time_elapsed_since_real_position_was_computed = (datetime.datetime.now() - position_timestamp).total_seconds()
            calculated_current_real_position = (real_position + (
                (origin_to_real_position_vector[1] / origin_to_real_position_vector[0]) * time_elapsed_since_real_position_was_computed))

            self.pathfinder.robot_status.generate_new_translation_vector_towards_current_target(calculated_current_real_position)
            return_telemetry = Packet(PacketType.PATH, self.pathfinder.get_current_path())

        return (self.update_current_vector_if_necessary_and_determine_next_step(real_position), return_telemetry)


class RoutineCheckWithoutDeviationChecksCommand(TranslationCommand):
    """ Command that performs a routine check. Switches to new
    movement vector if the robot is within threshold if it's next
    node in the graph. Only updates supposed position when it is recieved
    from telemetry. """

    def execute(self, telemetry_data):
        """ Performs de routine check command
        :param telemetry_data: Position data recieved by telemetry """

        if not self.is_positional_telemetry_recieved(telemetry_data):
            return (self.current_step, None)

        return (self.update_current_vector_if_necessary_and_determine_next_step(telemetry_data[0]), None)


class RotatingCheckCommand(Command):
    """ Verifies if rotation is completed, then progresses to the next step.
    Does not currently support verifying from telemetry heading. """

    st_last_rotating_check_execution = None

    def execute(self, data):
        """ Executes rotating check command """

        if not RotatingCheckCommand.st_last_rotating_check_execution:
            RotatingCheckCommand.st_last_rotating_check_execution = datetime.datetime.now()

        time_passed = (datetime.datetime.now() -
                       RotatingCheckCommand.st_last_rotating_check_execution).total_seconds()

        if time_passed <= NUMBER_OF_SECONDS_BETWEEN_ROTATION_CHECKS:
            return (self.current_step, None)

        self.pathfinder.robot_status.update_heading()

        RotatingCheckCommand.last_rotating_check_execution = datetime.datetime.now()

        if self.pathfinder.robot_status.heading_has_reached_target_heading_threshold():
            return (next_step(self.current_step), None)
        else:
            return (self.current_step, None)


class RotatingCheckThroughTelemetryCommand(Command):
    """ Verifies if rotation is completed, then progresses to the next step. """

    def execute(self, telemetry_data):
        """ Executes rotating check command """

        if telemetry_data is None or not isinstance(
                telemetry_data.packet_type, PacketType.POSITION):
            time.sleep(50)
            return (self.current_step, None)

        current_orientation = telemetry_data[1]
        if math.fabs(self.pathfinder.robot_status.target_heading - current_orientation) <= 0.25:
            return (next_step(self.current_step), None)
        else:
            return (self.current_step, None)


class AcquireInformationFromAntennaCommand(Command):
    """ Allows acquisition and safeguarding of the information
    emitted by the antenna """

    def __init__(self, step, interfacing_controller, pathfinder, antenna_information):
        super(AcquireInformationFromAntennaCommand, self).__init__(
            step, interfacing_controller, pathfinder)
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Executes acquisition command """

        print("prepare acquisition of signal data")

        antenna_data = self.hardware.antenna.get_information_from_signal()
        print("Acquire information from signal, painting nb: {0}".format(antenna_data))

        if antenna_data is None:
            return (self.current_step, None)
        else:
            self.antenna_information.painting_number = int(antenna_data.painting_number)
            self.antenna_information.zoom = int(antenna_data.zoom)
            self.antenna_information.orientation = float(antenna_data.orientation)
            return (next_step(self.current_step), None)


class FaceRelevantFigureForCaptureCommand(Command):
    """ Allows the robot to start its rotation towards a FOV zone where it can
    capture the relevant figure """

    def __init__(self, step, interfacing_controller, pathfinder, antenna_information):
        super(FaceRelevantFigureForCaptureCommand, self).__init__(
            step, interfacing_controller, pathfinder)
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Executes face relevant figure for capture command """

        orientation = self.pathfinder.figures.get_orientation_to_take_figure_from(
            self.antenna_information.painting_number)

        rotation_angle = (self.pathfinder.robot_status.
                          set_target_heading_and_get_angular_difference(orientation))
        self.hardware.wheels.rotate(rotation_angle)

        return (next_step(self.current_step), None)


class CaptureFigureCommand(Command):
    """ Allows the robot to capture the relevant figure """

    def __init__(self, step, interfacing_controller, pathfinder, antenna_information, onboard_vision):
        super(CaptureFigureCommand, self).__init__(step, interfacing_controller, pathfinder)
        self.antenna_information = antenna_information
        self.vision = onboard_vision

    def execute(self, data):
        """ Executes capture command """

        print("capture figure")

        capture_can_be_computed = False

        retry_translation_deltas = self.pathfinder.figures.get_figure_list_of_retries_movement_deltas(
            self.antenna_information.painting_number)
        for retry_delta_vector in retry_translation_deltas:
            while not capture_can_be_computed:
                try:
                    self.vision.capture()
                    self.vision.get_captured_vertices(2, 90)
                    capture_can_be_computed = True
                except (PaintingFrameNotFound, VerticesNotFound):
                    capture_can_be_computed = False
                    self.hardware.wheels.move(retry_delta_vector)
                    time.sleep(math.hypot(retry_delta_vector[0], retry_delta_vector[1]) / TRANSLATION_SPEED)

        self.hardware.lights.light_green_led(1000)

        rotation_angle = (self.pathfinder.robot_status.
                          set_target_heading_and_get_angular_difference(STANDARD_HEADING))
        self.hardware.wheels.rotate(rotation_angle)

        return (next_step(self.current_step), Packet(PacketType.FIGURE_IMAGE, self.vision.last_capture))
