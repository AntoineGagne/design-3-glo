""" This module contains all commands linked closely to the robot's rotation movement steps. """
from design.decision_making.constants import next_step
from design.decision_making.preparation_commands import Command
from design.pathfinding.constants import RotationStatus


class RotationCheckCommand(Command):
    """ Basic verification of a rotation's step progress. """

    def __init__(self, step, interfacing_controller, pathfinder, logger, servo_wheels_manager):
        super(RotationCheckCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.servo_wheels_manager = servo_wheels_manager

    def execute(self, telemetry_data):
        """ Executes the rotation check """
        if not self.is_positional_telemetry_recieved(telemetry_data):
            return (self.current_step, None)

        position = telemetry_data[0]
        orientation = telemetry_data[1]

        self.logger.log(
            "Rotation Check: Execution. Step = {0} - Telemetry position = {1} - Telemetry heading = {2}".format(
                self.current_step, position, orientation))

        if self.servo_wheels_manager.rotation_status == RotationStatus.ROTATING:
            if not self.servo_wheels_manager.is_current_rotation_movement_done(self.hardware.wheels):
                return (self.current_step, None)
            else:
                self.servo_wheels_manager.rotating_start_heading_correction(orientation, self.pathfinder.robot_status,
                                                                            self.hardware.wheels)
                return (self.current_step, None)
        elif self.servo_wheels_manager.rotation_status == RotationStatus.CORRECTING_HEADING:
            if not self.servo_wheels_manager.is_current_rotation_movement_done(self.hardware.wheels):
                return (self.current_step, None)
            else:
                self.servo_wheels_manager.finish_rotation_and_set_new_robot_position(position,
                                                                                     self.pathfinder.robot_status)
                return (next_step(self.current_step), None)


class TrustingRotationCheckCommand(Command):
    """ Basic verification of rotation's progress, but without using telemetry. """

    def __init__(self, step, interfacing_controller, pathfinder, logger, servo_wheels_manager):
        super(TrustingRotationCheckCommand, self).__init__(
            step, interfacing_controller, pathfinder, logger)
        self.servo_wheels_manager = servo_wheels_manager

    def execute(self, telemetry_data):
        """ Executes the rotation check """

        self.logger.log("Trusting Rotation Check: Execution. Step = {0}".format(self.current_step))

        if self.servo_wheels_manager.rotation_status == RotationStatus.ROTATING:
            if not self.servo_wheels_manager.is_current_rotation_movement_done:
                return (self.current_step, None)
            else:
                self.pathfinder.robot_status.heading = self.pathfinder.robot_status.target_heading
                return (next_step(self.current_step), None)
