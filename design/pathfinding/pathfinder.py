""" This module allows mocking of pathfinder object """

from collections import deque
from enum import Enum
from design.pathfinding.game_map import GameMap
from design.pathfinding.figures_information import FiguresInformation
from design.pathfinding.robot_status import RobotStatus
from design.pathfinding.graph import Graph
from design.pathfinding.priority_queue import PriorityQueue
from design.pathfinding.exceptions import CheckpointNotAccessibleError


class PathStatus(Enum):
    """ Enum of pathfinding status """
    MOVING_TOWARDS_TARGET = 0
    INTERMEDIATE_NODE_REACHED = 1
    CHECKPOINT_REACHED = 2


class Pathfinder():
    """Mocks pathfinder object"""

    def __init__(self, logger):
        """ TEST CASE """

        self.logger = logger

        self.game_map = GameMap()
        self.figures = FiguresInformation()
        self.robot_status = None
        self.graph = None

        self.nodes_queue_to_checkpoint = deque()  # in cm

    def set_game_map(self, game_map_data):
        """ Sets game map elements like corners, objectives and
        obstacles """

        robot_information = game_map_data.get("robot")
        if robot_information:
            self.logger.log("Pathfinder - Assigning start position = {0} and orientation = {1}".format(
                robot_information[0], robot_information[1]))
            self.robot_status = RobotStatus(robot_information[0], robot_information[1])
        else:
            self.robot_status = RobotStatus((20, 20), 90)

        obstacles = game_map_data.get("obstacles")
        if obstacles:
            self.logger.log("Pathfinder - Assigning obstacles: {0}".format(obstacles))
            self.graph = Graph(obstacles)
        else:
            self.graph = Graph([])

        self.graph.generate_nodes_of_graph()
        self.graph.generate_graph()

        # table_corners_positions = None
        table_corners_positions = game_map_data.get("table_corners")
        if table_corners_positions:
            self.logger.log("Pathfinding - Assigning table corner positions: {0}".format(table_corners_positions))
            self.figures.compute_positions(table_corners_positions[0], table_corners_positions[1],
                                           table_corners_positions[2], table_corners_positions[3])
        else:
            self.figures.compute_positions((0, 0), (0, 231), (112, 231), (112, 0))

        # drawing_zone_corners = None
        drawing_zone_corners = game_map_data.get("drawing_zone")
        if drawing_zone_corners:
            self.logger.log("Pathfinding - Assigning drawing zone corners: {0}".format(drawing_zone_corners))
            self.game_map.set_drawing_zone_borders(game_map_data.get("drawing_zone"))
            self.game_map.set_antenna_search_points(table_corners_positions[3])
        else:
            self.game_map.set_drawing_zone_borders(((26, 27), (26, 87), (86, 87), (86, 27)))
            self.game_map.set_antenna_search_points((112, 0))

    def get_vector_to_next_node(self, current_robot_position=None):
        """ If close enough to next node (within THRESHOLD), switch to new one """

        if current_robot_position:
            self.robot_status.set_position(current_robot_position)

        if self.robot_status.position_has_reached_target_position_within_threshold():
            if self.nodes_queue_to_checkpoint:
                new_vector = self.robot_status.generate_new_translation_vector_towards_new_target(
                    self.nodes_queue_to_checkpoint.popleft())
                return (PathStatus.INTERMEDIATE_NODE_REACHED, new_vector)
            else:
                self.robot_status.generate_new_translation_vector_towards_new_target(
                    self.robot_status.get_position())
                return (PathStatus.CHECKPOINT_REACHED, None)
        else:
            return (PathStatus.MOVING_TOWARDS_TARGET, None)

    def get_point_of_interest(self, point_of_interest):
        """ Returns any data about the specified point of interest within
        the game map """
        return self.game_map.get_point_of_interest(point_of_interest)

    def get_current_path(self):
        """ Takes the current path contained in nodes queue to checkpoint, copies it and adds
        origin of movement and current target. Returns a new queue. """
        path = deque()
        for node in self.nodes_queue_to_checkpoint:
            path.append(node)

        path.appendleft(self.robot_status.target_position)
        path.appendleft(self.robot_status.get_position())

        return path

    def generate_path_to_checkpoint_a_to_b(self, checkpoint_position):
        """ Generates shortest path to checkpoint and updates the node queue
        accordingly.
        :raise: CheckpointNotAccessibleException if the checkpoint_position is not accessible"""
        if checkpoint_position in self.graph.list_of_inaccessible_nodes:
            raise CheckpointNotAccessibleError("Le point d'arrivé est non accessible par le robot")

        print("Generate path to checkpoint a to b - checkpoint pos = {0}".format(checkpoint_position))

        self.nodes_queue_to_checkpoint.clear()
        self.nodes_queue_to_checkpoint.append(checkpoint_position)

        self.robot_status.generate_new_translation_vector_towards_new_target(
            self.nodes_queue_to_checkpoint.popleft())

    def generate_path_to_checkpoint(self, checkpoint_position):
        """ Generates shortest path to checkpoint and updates the node queue
        accordingly.
        :raise: CheckpointNotAccessibleException if the checkpoint_position is not accessible"""

        print("Generating path with A star. Checkpoint position = {0}".format(checkpoint_position))

        if checkpoint_position in self.graph.list_of_inaccessible_nodes:
            raise CheckpointNotAccessibleError("Le point d'arrivé est non accessible par le robot")
        else:
            self.nodes_queue_to_checkpoint.clear()
            start_node = self.robot_status.get_position()
            print("Generating path with A star. start position = {0}".format(start_node))
            self.graph.add_start_end_node(start_node, checkpoint_position)
            priority_queue = PriorityQueue()
            priority_queue.put(start_node, 0)
            came_from = {}
            cost_so_far = {}
            came_from[start_node] = None
            cost_so_far[start_node] = 0

            while not priority_queue.empty():
                current = priority_queue.get()
                if current == checkpoint_position:
                    break
                if (self.graph.get_position_minimum_of_graph() > checkpoint_position[1]) and (self.graph.get_position_minimum_of_graph() > current[1]):
                    came_from[checkpoint_position] = current
                    break
                for next_node in self.graph.graph_dict[current]:
                    new_cost = cost_so_far[current] + self.graph.estimate_distance(current, next_node)
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + self.graph.estimate_distance(next_node, checkpoint_position)
                        priority_queue.put(next_node, priority)
                        came_from[next_node] = current

            self.graph.graph_dict[self.graph.graph_dict.get(start_node)[0]].remove(start_node)
            self.graph.graph_dict[self.graph.graph_dict.get(checkpoint_position)[0]].remove(checkpoint_position)
            del self.graph.graph_dict[start_node]
            del self.graph.graph_dict[checkpoint_position]

            current = checkpoint_position
            while current != start_node:
                self.nodes_queue_to_checkpoint.append(current)
                current = came_from.get(current)

            self.nodes_queue_to_checkpoint.reverse()

            self.robot_status.generate_new_translation_vector_towards_new_target(
                self.nodes_queue_to_checkpoint.popleft())
