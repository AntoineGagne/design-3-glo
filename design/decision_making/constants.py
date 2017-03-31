""" Relevant constants and enum classes for the decisionmaking subpackage """

from enum import Enum


NUMBER_OF_SECONDS_BETWEEN_ROUTINE_CHECKS = 0.05
NUMBER_OF_SECONDS_BETWEEN_ROTATION_CHECKS = 0.05
NUMBER_OF_SECONDS_BETWEEN_SIGNAL_SAMPLES = 0.10


class TranslationStrategyType(Enum):
    """ Defines a type of translation movement
    strategy """
    VERIFY_ONLY_ON_TELEMETRY_RECEPTION = "TELEMETRY"
    VERIFY_CONSTANTLY_THROUGH_CINEMATICS = "CINEMATICS"


class RotationStrategyType(Enum):
    """ Defines a type of rotation movement
    strategy """
    VERIFY_ONLY_ON_TELEMETRY_RECEPTION = "TELEMETRY"
    VERIFY_CONSTANTLY_THROUGH_ANGULAR_CINEMATICS = "CINEMATICS"


class Step(Enum):
    """Defines the current global step according to which the robot
    is making decisions"""

    STANBY = 0
    ROTATE_TO_STANDARD_HEADING = 1
    PREPARE_TRAVEL_TO_ANTENNA_ZONE = 2
    TRAVEL_TO_ANTENNA_ZONE = 3
    PREPARE_SEARCH_FOR_ANTENNA = 4
    SEARCH_FOR_ANTENNA = 5
    PREPARE_MOVING_TO_ANTENNA_POSITION = 6
    MOVING_TO_ANTENNA_POSITION = 7
    ACQUIRE_INFORMATION_FROM_ANTENNA = 8
    PREPARE_MARKING_ANTENNA_POSITION = 9
    MARKING_ANTENNA_POSITION = 10
    COMPUTE_PAINTINGS_AREA = 11
    TRAVEL_TO_PAINTINGS_AREA = 12
    PREPARE_CAPTURE_OF_PAINTING = 13
    ROTATE_TO_FACE_PAINTING = 14
    CAPTURE_CORRECT_PAINTING = 15
    ROTATE_BACK_AFTER_CAPTURE = 16
    PREPARE_TRAVEL_TO_DRAWING_ZONE = 17
    TRAVEL_TO_DRAWING_ZONE = 18
    PREPARE_TO_DRAW = 19
    DRAWING = 20
    PREPARE_EXIT_OF_DRAWING_ZONE = 21
    EXITING_DRAWING_ZONE = 22
    TERMINATE_SEQUENCE = 23


def next_step(current_step):
    """ Gives next step """

    try:
        step_to_return = Step(current_step.value + 1)
    except ValueError as error:
        return Step.STANBY

    return step_to_return
