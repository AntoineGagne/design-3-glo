""" Unit tests for servo wheel manager """
from design.interfacing.simulated_controllers import SimulatedWheelsController
from design.pathfinding.constants import TranslationStatus, RotationStatus
from design.pathfinding.pathfinder import Pathfinder, PathStatus
from design.pathfinding.robot_status import RobotStatus
from design.pathfinding.servo_wheels_manager import ServoWheelsManager
from design.utils.execution_logger import ExecutionLogger

heading = 80
robot_status = RobotStatus((20, 20), 80)
wheels_controller = SimulatedWheelsController()
servo_wheels_manager = ServoWheelsManager(None, None, ExecutionLogger())


def test_given_start_of_heading_correction_for_translation_change_translation_status_and_send_rotation_vector_towards_standard_heading():
    heading = 80
    robot_status = RobotStatus((20, 20), 80)
    wheels_controller = SimulatedWheelsController()
    servo_wheels_manager = ServoWheelsManager(None, None, ExecutionLogger())

    servo_wheels_manager.translating_start_heading_correction(heading, robot_status, wheels_controller)

    assert int(wheels_controller.last_degrees_of_rotation_given) == 10
    assert servo_wheels_manager.translation_status == TranslationStatus.CORRECTING_HEADING


def test_given_start_of_position_correction_for_translation_change_translation_status_and_send_translation_vector_towards_current_target_node():
    position = (40, 50)
    robot_status = RobotStatus((30, 30), 90)
    robot_status.target_position = (60, 65)

    wheels_controller = SimulatedWheelsController()
    servo_wheels_manager = ServoWheelsManager(None, None, ExecutionLogger())

    servo_wheels_manager.translating_start_position_correction(position, robot_status, wheels_controller)

    vector_x, vector_y = robot_status.get_translation_vector()

    assert int(vector_x) == 20
    assert int(vector_y) == 15
    assert servo_wheels_manager.translation_status == TranslationStatus.CORRECTING_POSITION

    position = (50.1, 54.9)
    robot_status = RobotStatus((45, 50), 90)
    robot_status.target_position = (50, 55)
    pathfinder = Pathfinder(ExecutionLogger())
    pathfinder.robot_status = robot_status
    pathfinder.nodes_queue_to_checkpoint.append((100, 150))
    servo_wheels_manager = ServoWheelsManager(None, None, ExecutionLogger())


def test_given_at_intermediary_node_when_finishing_translation_then_translation_status_is_updated_and_new_vector_towards_next_node_is_generated():
    position = (50.1, 54.9)
    robot_status = RobotStatus((45, 50), 90)
    robot_status.target_position = (50, 55)
    pathfinder = Pathfinder(ExecutionLogger())
    pathfinder.robot_status = robot_status
    pathfinder.nodes_queue_to_checkpoint.append((100, 150))
    servo_wheels_manager = ServoWheelsManager(None, None, ExecutionLogger())

    path_status, new_vector = servo_wheels_manager.finish_translation_and_get_new_path_status_and_vector(position,
                                                                                                         pathfinder)
    new_vector_x, new_vector_y = new_vector

    assert servo_wheels_manager.translation_status == TranslationStatus.MOVING
    assert round(new_vector_x, 1) == 49.9
    assert round(new_vector_y, 1) == 95.1
    assert path_status == PathStatus.INTERMEDIATE_NODE_REACHED


def test_given_at_checkpoint_when_finishing_translation_then_translation_status_is_updated_and_no_new_vector_is_generated():
    position = (50.1, 54.9)
    robot_status = RobotStatus((45, 50), 90)
    robot_status.target_position = (50, 55)
    pathfinder = Pathfinder(ExecutionLogger())
    pathfinder.robot_status = robot_status
    servo_wheels_manager = ServoWheelsManager(None, None, ExecutionLogger())

    path_status, new_vector = servo_wheels_manager.finish_translation_and_get_new_path_status_and_vector(position,
                                                                                                         pathfinder)

    assert servo_wheels_manager.translation_status == TranslationStatus.MOVING
    assert new_vector is None
    assert path_status == PathStatus.CHECKPOINT_REACHED


def test_given_start_heading_correction_for_rotation_then_rotation_status_is_updated_and_command_is_sent_to_wheels():
    heading = 75
    robot_status = RobotStatus((50, 50), 90)
    robot_status.target_heading = 79
    servo_wheels_manager = ServoWheelsManager(None, None, ExecutionLogger())
    wheels_controller = SimulatedWheelsController()

    servo_wheels_manager.rotating_start_heading_correction(heading, robot_status, wheels_controller)

    assert servo_wheels_manager.rotation_status == RotationStatus.CORRECTING_HEADING
    assert int(wheels_controller.last_degrees_of_rotation_given) == 4


def test_given_finishing_rotation_movement_then_rotation_status_is_reinitialized_and_new_robot_position_is_assigned():
    position = (48, 37)
    robot_status = RobotStatus((50, 50), 90)
    servo_wheels_manager = ServoWheelsManager(None, None, ExecutionLogger())

    servo_wheels_manager.finish_rotation_and_set_new_robot_position(position, robot_status)

    assert servo_wheels_manager.rotation_status == RotationStatus.ROTATING
    assert robot_status.get_position() == position
