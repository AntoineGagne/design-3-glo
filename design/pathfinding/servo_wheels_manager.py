""" This module contains a manager for all data and steps related to visual servowheel management
when telemetry translation movement strategy is used. """

from design.pathfinding.constants import STANDARD_HEADING, TranslationStatus, RotationStatus


class ServoWheelsManager():
    """ This class contains everything necessary to keep track of visual servoing parameters throughout
    translations and rotations. """

    def __init__(self, translation_lock, rotation_lock, logger):

        self.translation_lock = translation_lock
        self.rotation_lock = rotation_lock
        self.translation_status = TranslationStatus.MOVING
        self.rotation_status = RotationStatus.ROTATING
        self.logger = logger

    def reinitialize(self):
        self.translation_status = TranslationStatus.MOVING
        self.rotation_status = RotationStatus.ROTATING

    def is_current_translation_movement_done(self, wheels_controller):
        """ Returns true if the current translation order of the robot is completed, otherwise
        returns false.
        :param wheels_controller: Wheels controller, used to communicate with the wheels
        :returns: A boolean indicating if the order is completed """
        self.translation_lock.acquire()
        translation_is_done = False
        if wheels_controller.translation_done:
            self.logger.log("Servo Wheels Manager - Translation done!")
            translation_is_done = True
        self.translation_lock.release()
        return translation_is_done

    def is_current_rotation_movement_done(self, wheels_controller):
        """ Returns true if the current rotation order of the robot is completed, otherwise
        returns false.
        :param wheels_controller: Wheels controller, used to communicate with the wheels
        :returns: A boolean indicating if the order is completed """
        self.rotation_lock.acquire()
        rotation_is_done = False
        if wheels_controller.rotation_done:
            self.logger.log("Servo Wheels Manager - Rotation done!")
            rotation_is_done = True
        self.rotation_lock.release()
        return rotation_is_done

    def translating_start_heading_correction(self, current_heading, robot_status, wheels_controller):
        """ Starts a heading correction after a translation movement is completed.
        :param current_heading: Robot heading from telemetry
        :param robot_status: Robot status object
        :param wheels_controller: Used to send orders to the wheels """
        self.translation_status = TranslationStatus.CORRECTING_HEADING
        robot_status.heading = current_heading
        wheels_controller.rotate(
            robot_status.set_target_heading_and_get_angular_difference(STANDARD_HEADING))
        self.logger.log(
            "Servo Manager: Heading correction for translation has been started. Current heading = {0}".format(
                current_heading))

    def translating_start_position_correction(self, current_position, robot_status, wheels_controller):
        """ Starts a position correction after the heading correction is completed. Goes towards
        current target node
        :param current_position: Position from telemetry
        :param robot_status: Robot status object
        :param wheels_controller: Used to send orders to the wheels """
        self.translation_status = TranslationStatus.CORRECTING_POSITION
        vector = robot_status.generate_new_translation_vector_towards_current_target(current_position)
        wheels_controller.move(vector)
        self.logger.log(
            "Servo Manager: Position correction for translation has been started. Current position = {0} - Target = {1}".format(
                current_position, robot_status.target_position))

    def finish_translation_and_get_new_path_status_and_vector(self, current_position, pathfinder):
        """ Terminates the translation check movements and updates the current path status. Also
        returns a new vector if we stopped at an intermediate node. """
        self.translation_status = TranslationStatus.MOVING
        pathfinder.robot_status.set_position(current_position)
        path_status, new_vector = pathfinder.get_vector_to_next_node(current_position)
        self.logger.log(
            "Servo Manager: Finishing translation. Updated position = {0} - Path Status = {1} - Vector = {2}".format(
                pathfinder.robot_status.get_position(), path_status, new_vector))
        return (path_status, new_vector)

    def rotating_start_heading_correction(self, current_heading, robot_status, wheels_controller):
        """ Starts a heading correction after a translation movement is completed.
        :param current_heading: Robot heading from telemetry
        :param robot_status: Robot status object
        :param wheels_controller: Used to send orders to the wheels """
        self.rotation_status = RotationStatus.CORRECTING_HEADING
        robot_status.heading = current_heading
        wheels_controller.rotate(
            robot_status.set_target_heading_and_get_angular_difference(robot_status.target_heading))
        self.logger.log(
            "Servo Manager: Heading correction for rotation has been started. Current heading = {0} - Target heading = {1}".format(
                robot_status.heading, robot_status.target_heading))

    def finish_rotation_and_set_new_robot_position(self, current_position, robot_status):
        """ Terminates the rotation check movements and updates the current robot status position.
        :param current_position: Position from telemetry
        :param robot_status: Robot status object """
        self.rotation_status = RotationStatus.ROTATING
        robot_status.set_position(current_position)
        self.logger.log("Servo Manager: Finishing rotation. Updated position = {0}".format(robot_status.get_position()))
