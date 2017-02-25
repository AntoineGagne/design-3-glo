""" Author: TREMBLAY, Alexandre
Last modified: Febuary 3rd, 2017

This module has all necessary commands that can be executed by the robot.
A command always return a (next_step, exiting_telemetry_msg) tuple."""

import datetime
from design.decision_making.constants import (Step,
                                              NUMBER_OF_SECONDS_BETWEEN_ROTATION_CHECKS,
                                              NUMBER_OF_SECONDS_BETWEEN_ROUTINE_CHECKS,
                                              NUMBER_OF_SECONDS_BETWEEN_SIGNAL_SAMPLES,
                                              next_step)
from design.pathfinding.pathfinder import PathStatus
from design.pathfinding.constants import (PointOfInterest,
                                          FigureFieldOfViewArea)


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


class BuildGameMapCommand(Command):
    """ Command that builds the game map according to corners, obstacles and
    points of interest """

    def execute(self, game_map_data):
        """ Builds game map """

        self.pathfinder.set_game_map(game_map_data)

        self.pathfinder.set_target_heading(90)
        self.hardware.wheels.rotate(90 - self.pathfinder.current_heading)

        return (next_step(self.current_step),
                "NOTIFY|Game map built, starting cycle and rotation to standard heading")


class PrepareTravelToAntennaAreaCommand(Command):
    """ Commands that sets the trajectory of the robot to go towards
    the antenna's general area """

    def execute(self, data):
        """ Executes preparation of travel to antenna command """

        new_vector = self.pathfinder.generate_new_vector(
            self.pathfinder.get_current_robot_supposed_position())
        self.hardware.wheels.move(new_vector)

        return (next_step(self.current_step),
                "NOTIFY|Starting to travel to antenna area")


class TravelToPaintingsAreaCommand(Command):
    """ Commands that sets the trajectory of the robot to the paintings
    section """

    def execute(self, telemetry_data):
        """ Sets trajectory of the robot to paintings area """

        self.hardware.pen.raise_pen()

        self.pathfinder.generate_path_to_checkpoint(
            self.pathfinder.get_point_of_interest(PointOfInterest.FIGURE_ZONE))
        self.hardware.wheels.move(self.pathfinder.generate_new_vector(
            self.pathfinder.get_current_robot_supposed_position()))

        return (next_step(self.current_step), "NOTIFY|Starting to travel to paintings area")


class PrepareToDrawCommand(Command):
    """ Commands that lowers the pen and gives vectors list to draw """

    def __init__(self, step, interfacing_controller, pathfinder, onboard_vision, antenna_info):
        super(PrepareToDrawCommand, self).__init__(
            step, interfacing_controller, pathfinder)
        self.vision = onboard_vision
        self.antenna_info = antenna_info

    def execute(self, data):
        """ Starts drawing """

        drawing_reference_origin = self.pathfinder.get_point_of_interest(
            PointOfInterest.DRAWING_ZONE)

        self.pathfinder.nodes_queue_to_checkpoint.queue.clear()
        for vertex in self.vision.get_captured_vertices(
                self.antenna_info.get_drawing_information()):
            point_to_cross_x = drawing_reference_origin[0] + vertex[0]
            point_to_cross_y = drawing_reference_origin[1] + vertex[1]
            self.pathfinder.nodes_queue_to_checkpoint.put(
                (point_to_cross_x, point_to_cross_y))

        self.hardware.pen.lower_pen()

        return (next_step(self.current_step), "NOTIFY|Starting to draw")


class PrepareExitOfDrawingAreaCommand(Command):
    """ Prepares the robot to leave the drawing zone """

    def execute(self, data):
        """ Executes exit of drawing area command """

        self.hardware.pen.raise_pen()

        self.pathfinder.generate_path_to_checkpoint(
            self.pathfinder.get_point_of_interest(PointOfInterest.FIGURE_ZONE))

        self.hardware.wheels.move(
            self.pathfinder.generate_new_vector(
                self.pathfinder.get_current_robot_supposed_position()))

        return (next_step(self.current_step), "NOTIFY|Preparing to exit drawing area")


class FinishCycleCommand(Command):
    """ Command that stops the current cycle and notifies the base station """

    def execute(self, data):
        """ Stops current cycle """
        self.hardware.lights.light_red_led(2000)
        return (Step.STANBY, "CMD|Stop chronograph")


class RoutineCheckCommand(Command):
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

        print("{0}|Executing routine check|{1}".format(
            datetime.datetime.now(), self.current_step))

        Command.st_last_execution = datetime.datetime.now()

        self.pathfinder.update_supposed_robot_position()

        # Verifying current trajectory if we recieve our position from
        # telemetry
        if robot_position_from_telemetry:
            print("Recieved telemetry: {0}".format(robot_position_from_telemetry))
            if self.pathfinder.verify_if_deviating(robot_position_from_telemetry):
                print("Deviating!")
                new_vector = self.pathfinder.generate_new_vector(
                    robot_position_from_telemetry)
                self.hardware.wheels.move(new_vector)

        # We then check if we're arriving at a node/checkpoint, and act
        # accordingly
        path_status, new_vector = self.pathfinder.get_vector_to_next_node(
            robot_position_from_telemetry)  # This method only does so if necessary!

        if new_vector:
            self.hardware.wheels.move(new_vector)

        telemetry_message = None
        new_step = self.current_step
        if path_status == PathStatus.CHECKPOINT_REACHED:
            telemetry_message = "NOTIFY|Checkpoint of {0} reached".format(
                self.current_step)
            new_step = next_step(self.current_step)
        else:
            telemetry_message = "ROBOT_POS|{0}".format(
                self.pathfinder.supposed_robot_position)

        return (new_step, telemetry_message)


class PrepareSearchForAntennaPositionCommand(Command):
    """ Starts sampling for antenna signal and gives movement vector along the
    wall so it can find the antenna's position easily """

    def execute(self, data):
        """ Starts search for antenna """

        self.hardware.antenna.start_sampling()

        self.pathfinder.generate_path_to_checkpoint(
            self.pathfinder.get_point_of_interest(PointOfInterest.ANTENNA_STOP_SEARCH_POINT))

        self.hardware.wheels.move(self.pathfinder.generate_new_vector(
            self.pathfinder.get_current_robot_supposed_position()))

        return (next_step(self.current_step), "NOTIFY|Starting to search for antenna position")


class SearchForAntennaPositionCommand(Command):
    """ Does mostly the same thing as RoutineCheckCommand but verifies signal strength
    gradient. If it changes direction, we have reached (and probably superseded) the antenna's
    position. """

    st_last_signal_strength = 0
    st_last_signal_sampling = datetime.datetime.now()

    def execute(self, robot_position_from_telemetry):
        """ Executes search for antenna command """

        # Executes normal routine check
        normal_routine_check = RoutineCheckCommand(
            self.current_step, self.hardware, self.pathfinder)
        step, exit_telemetry = normal_routine_check.execute(
            robot_position_from_telemetry)
        if step != self.current_step:
            # We have reached the end of search checkpoint without finding the
            # antenna.
            return (step, "NOTIFY|Reached end of antenna search without finding the antenna")

        # If we aren't done with the search yet, get current signal strength
        # and compare
        if (datetime.datetime.now() -
                SearchForAntennaPositionCommand.st_last_signal_sampling).total_seconds() >= \
                NUMBER_OF_SECONDS_BETWEEN_SIGNAL_SAMPLES:

            SearchForAntennaPositionCommand.st_last_signal_sampling = datetime.datetime.now()
            current_signal_strength = self.hardware.antenna.get_signal_strength()

            if current_signal_strength <= SearchForAntennaPositionCommand.st_last_signal_strength:
                self.hardware.wheels.stop()
                return (next_step(self.current_step), "NOTIFY|Found antenna position!")
            else:
                SearchForAntennaPositionCommand.st_last_signal_strength = current_signal_strength
                return (self.current_step, exit_telemetry)
        else:
            return (self.current_step, exit_telemetry)


class PrepareMarkingAntennaCommand(Command):
    """ Prepares movement in order to mark the antenna's position. """

    def execute(self, data):
        """ Executes marking antenna preparation command """

        self.hardware.antenna.stop_sampling()
        self.hardware.pen.lower_pen()

        position_x, position_y = self.pathfinder.get_current_robot_supposed_position()
        position_x = position_x - 5

        self.pathfinder.generate_path_to_checkpoint((position_x, position_y))

        self.hardware.wheels.move(self.pathfinder.generate_new_vector(
            self.pathfinder.get_current_robot_supposed_position()))

        return (next_step(self.current_step), "NOTIFY|Starting to mark")


class PrepareTravelToDrawingAreaCommand(Command):
    """ Prepares movement vector to travel to the center of the drawing zone """

    def __init__(self, current_step, interfacing_controller, pathfinder, vision, antenna_info):
        super(PrepareTravelToDrawingAreaCommand, self).__init__(current_step,
                                                                interfacing_controller, pathfinder)
        self.vision_data = vision
        self.antenna_info = antenna_info

    def execute(self, data):
        """ Executes travel to drawing area command """

        drawing_zone_origin_x, drawing_zone_origin_y = self.pathfinder.get_point_of_interest(
            PointOfInterest.DRAWING_ZONE)

        first_vertex_x, first_vertex_y = self.vision_data.get_captured_vertices(
            self.antenna_info.get_drawing_information())[0]

        position_x = drawing_zone_origin_x + first_vertex_x
        position_y = drawing_zone_origin_y + first_vertex_y

        self.pathfinder.generate_path_to_checkpoint((position_x, position_y))

        self.hardware.wheels.move(self.pathfinder.generate_new_vector(
            self.pathfinder.get_current_robot_supposed_position()))

        return (next_step(self.current_step), "NOTIFY|Starting to travel to drawing area")


class RotatingCheckCommand(Command):
    """ Verifies if rotation is completed, then progresses to the next step.
    Does not currently support verifying from telemetry heading. """

    def __init__(self, current_step, interfacing_controller, pathfinder):
        super(RotatingCheckCommand, self).__init__(current_step, interfacing_controller, pathfinder)
        self.last_rotating_check_execution = None

    def execute(self, data):
        """ Executes rotating check command """

        if not self.last_rotating_check_execution:
            self.last_rotating_check_execution = datetime.datetime.now()

        time_passed = (datetime.datetime.now() -
                       self.last_rotating_check_execution).total_seconds()

        if time_passed <= NUMBER_OF_SECONDS_BETWEEN_ROTATION_CHECKS:
            return (self.current_step, None)

        self.pathfinder.update_heading(time_passed)

        self.last_rotating_check_execution = datetime.datetime.now()

        if self.pathfinder.current_heading_within_target_heading_threshold():
            return (next_step(self.current_step), "NOTIFY|Finished rotating")
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

        self.antenna_information.set_information(
            self.hardware.antenna.get_information_from_signal())
        return (next_step(self.current_step), "NOTIFY|Acquired signal information")


class FaceRelevantFigureForCaptureCommand(Command):
    """ Allows the robot to start its rotation towards a FOV zone where it can
    capture the relevant figure """

    def __init__(self, step, interfacing_controller, pathfinder, antenna_information):
        super(FaceRelevantFigureForCaptureCommand, self).__init__(
            step, interfacing_controller, pathfinder)
        self.antenna_information = antenna_information

    def execute(self, data):
        """ Executes face relevant figure for capture command """

        figure = FigureFieldOfViewArea["FIGURE_{0}".format(
            self.antenna_information.get_painting_number())]
        self.pathfinder.set_target_heading(figure.value[0])
        self.hardware.wheels.rotate(90 - figure.value[0])

        return (next_step(self.current_step), "NOTIFY|Rotating to face capture area")


class CaptureFigureCommand(Command):
    """ Allows the robot to capture the relevant figure """

    def __init__(self, step, interfacing_controller, pathfinder, antenna_information,
                 onboard_vision):
        super(CaptureFigureCommand, self).__init__(step, interfacing_controller, pathfinder)
        self.antenna_information = antenna_information
        self.vision = onboard_vision

    def execute(self, data):
        """ Executes capture command """

        figure = FigureFieldOfViewArea["FIGURE_{0}".format(
            self.antenna_information.get_painting_number())]
        self.vision.capture(figure.value[1])

        self.pathfinder.set_target_heading(90)
        self.hardware.wheels.rotate(90 - self.pathfinder.current_heading)
        self.hardware.lights.light_green_led(1000)

        return (next_step(self.current_step), "NOTIFY|Captured figure and starting rotation back")
