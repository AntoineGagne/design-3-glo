""" Author: TREMBLAY, Alexandre
Last modified: Febuary 2nd, 2017

Relevant constants and enum classes for the decisionmaking subpackage"""

from enum import Enum


NUMBER_OF_SECONDS_BETWEEN_ROUTINE_CHECKS = 0.25
NUMBER_OF_SECONDS_BETWEEN_ROTATION_CHECKS = 0.10
NUMBER_OF_SECONDS_BETWEEN_SIGNAL_SAMPLES = 0.10


class Step(Enum):
    """Defines the current global step according to which the robot
    is making decisions"""

    STANBY = 0
    ROTATE_TO_STANDARD_HEADING = 1
    PREPARE_TRAVEL_TO_ANTENNA_ZONE = 2
    TRAVEL_TO_ANTENNA_ZONE = 3
    PREPARE_SEARCH_FOR_ANTENNA = 4
    SEARCH_FOR_ANTENNA = 5
    PREPARE_MARKING_ANTENNA_POSITION = 6
    MARKING_ANTENNA_POSITION = 7
    ACQUIRE_INFORMATION_FROM_ANTENNA = 8
    COMPUTE_PAINTINGS_AREA = 9
    TRAVEL_TO_PAINTINGS_AREA = 10
    PREPARE_CAPTURE_OF_PAINTING = 11
    ROTATE_TO_FACE_PAINTING = 12
    CAPTURE_CORRECT_PAINTING = 13
    ROTATE_BACK_AFTER_CAPTURE = 14
    PREPARE_TRAVEL_TO_DRAWING_ZONE = 15
    TRAVEL_TO_DRAWING_ZONE = 16
    PREPARE_TO_DRAW = 17
    DRAWING = 18
    PREPARE_EXIT_OF_DRAWING_ZONE = 19
    EXITING_DRAWING_ZONE = 20
    TERMINATE_SEQUENCE = 21


def next_step(current_step):
    """ Gives next step """

    try:
        step_to_return = Step(current_step.value + 1)
    except ValueError as error:
        return Step.STANBY

    return step_to_return
