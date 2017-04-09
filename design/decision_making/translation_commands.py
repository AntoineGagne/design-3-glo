""" This module contains all commands linked closely to translation movements for the robot. """

from design.decision_making.preparation_commands import Command
from design.decision_making.constants import next_step
from design.pathfinding.constants import TranslationStatus
from design.pathfinding.pathfinder import PathStatus


class TranslationCheckCommand(Command):
    """ Command that performs a routine check. Checks if robot is not
        deviating, otherwise corrects trajectory, and switches to new
        movement vector if the robot is within threshold if it's next
        node in the graph. """

    def __init__(self, step, interfacing_controller, pathfinder, logger, servo_wheels_manager):
        super(TranslationCheckCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.servo_wheels_manager = servo_wheels_manager

    def execute(self, telemetry_data):
        """ Performs the routine check command """

        if not self.is_positional_telemetry_recieved(telemetry_data):
            return (self.current_step, None)

        position = telemetry_data[0]
        orientation = telemetry_data[1]

        self.logger.log("Translation Check: Step = {0} - Telemetry position = {1} - Telemetry heading = {2}".format(
            self.current_step, position, orientation))

        if self.servo_wheels_manager.translation_status == TranslationStatus.MOVING:
            if not self.servo_wheels_manager.is_current_translation_movement_done(self.hardware.wheels):
                return (self.current_step, None)
            else:
                self.servo_wheels_manager.translating_start_heading_correction(orientation, self.pathfinder.robot_status, self.hardware.wheels)
                return (self.current_step, None)
        elif self.servo_wheels_manager.translation_status == TranslationStatus.CORRECTING_HEADING:
            if not self.servo_wheels_manager.is_current_rotation_movement_done(self.hardware.wheels):
                return (self.current_step, None)
            else:
                self.servo_wheels_manager.translating_start_position_correction(position, self.pathfinder.robot_status, self.hardware.wheels)
                return (self.current_step, None)
        elif self.servo_wheels_manager.translation_status == TranslationStatus.CORRECTING_POSITION:
            if not self.servo_wheels_manager.is_current_translation_movement_done(self.hardware.wheels):
                return (self.current_step, None)
            else:
                path_status, new_vector = self.servo_wheels_manager.finish_translation_and_get_new_path_status_and_vector(
                    position, self.pathfinder)
                if path_status == PathStatus.CHECKPOINT_REACHED:
                    return (next_step(self.current_step), None)
                elif path_status == PathStatus.INTERMEDIATE_NODE_REACHED:
                    self.hardware.wheels.move(new_vector)
                    return (self.current_step, None)
                else:
                    self.servo_wheels_manager.translating_start_position_correction(position, self.pathfinder.robot_status, self.hardware.wheels)
                    return (self.current_step, None)


class TranslationCheckWithoutTelemetryCommand(Command):
    """ Command that performs a routine check. Checks if robot is not
        deviating, otherwise corrects trajectory, and switches to new
        movement vector if the robot is within threshold if it's next
        node in the graph. """

    def __init__(self, step, interfacing_controller, pathfinder, logger, servo_wheels_manager):
        super(TranslationCheckWithoutTelemetryCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.servo_wheels_manager = servo_wheels_manager

    def execute(self, telemetry_data):
        """ Performs the routine check command """

        self.logger.log("Translation Check Without Telemetry: Step = {0}".format(self.current_step))

        if self.servo_wheels_manager.translation_status == TranslationStatus.MOVING:
            if not self.servo_wheels_manager.is_current_translation_movement_done(self.hardware.wheels):
                return (self.current_step, None)
            else:
                self.pathfinder.robot_status.set_position(self.pathfinder.robot_status.target_position)
                path_status, new_vector = self.pathfinder.get_vector_to_next_node(self.pathfinder.robot_status.get_position())
                if path_status == PathStatus.CHECKPOINT_REACHED:
                    return (next_step(self.current_step), None)
                elif path_status == PathStatus.INTERMEDIATE_NODE_REACHED:
                    self.hardware.wheels.move(new_vector)
                    return (self.current_step, None)
