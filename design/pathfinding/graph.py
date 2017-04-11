""" This module includes a graph represented by an adjacency matrix. Used for the robot's pathfinding. """
import math
from design.pathfinding.constants import GRAPH_GRID_WIDTH, OBSTACLE_RADIUS, ROBOT_SAFETY_MARGIN, \
    MAXIMUM_GRID_NODE_HEIGHT


class Graph():

    def __init__(self):
        self.matrix = None
        self.matrix_width = 0
        self.matrix_height = 0
        self.obstacle_safe_radius = (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN) // GRAPH_GRID_WIDTH

    def initialize_graph_matrix(self, southeastern_corner, northwestern_corner):

        table_width = northwestern_corner[0] - southeastern_corner[0]
        table_height = northwestern_corner[1] - southeastern_corner[1]

        self.matrix_width = table_width // GRAPH_GRID_WIDTH
        self.matrix_height = table_height // GRAPH_GRID_WIDTH

        self.matrix = [[0 for y in range(self.matrix_height)] for x in range(self.matrix_width)]

    def generate_impassable_zones_in_matrix(self, obstacle_list):
        self.add_walls_safety_margin()
        self.place_obstacles_in_matrix(obstacle_list)
        self.connect_obstacles_and_walls(obstacle_list)

    def add_walls_safety_margin(self):
        num_square = ROBOT_SAFETY_MARGIN // GRAPH_GRID_WIDTH + 1
        for i in range(self.matrix_width):
            for j in range(self.matrix_height):
                if i <= num_square or i > self.matrix_width - num_square:
                    self.matrix[i][j] = math.inf
                elif j <= num_square or j > self.matrix_height - num_square:
                    self.matrix[i][j] = math.inf

    def place_obstacles_in_matrix(self, obstacle_list):
        for obstacle in obstacle_list:
            self.place_obstacle_in_matrix(obstacle)

    def place_obstacle_in_matrix(self, obstacle):
        for i in range(*self.get_index_range(obstacle[0][0], self.matrix_width - 1)):
            for j in range(*self.get_index_range(obstacle[0][1], self.matrix_height - 1)):
                if self.get_euclidian_distance((i, j), obstacle[0]) <= self.obstacle_safe_radius:
                    self.matrix[i][j] = math.inf

    def get_index_range(self, coordinate, maximum_value):
        min_index = max(0, coordinate - self.obstacle_safe_radius)
        max_index = min(coordinate + self.obstacle_safe_radius, maximum_value)
        return min_index, max_index

    def get_euclidian_distance(self, point1, point2):
        return math.hypot(point2[0] - point1[0], point2[1] - point1[1])

    def connect_obstacles_and_walls(self, obstacle_list):
        for obstacle in obstacle_list:
            if obstacle[1] != "O":
                sign = self.determine_sign()
                i = obstacle[0][0] + sign * self.obstacle_safe_radius
                no_infinite_weight = True
                while no_infinite_weight:
                    for j in range(obstacle[0][1] - self.obstacle_safe_radius, obstacle[0][1] + self.obstacle_safe_radius):
                        if self.matrix[i][j] == math.inf:
                            no_infinite_weight = False
                        else:
                            self.matrix[i][j] = math.inf
                    i = i + sign

    def get_grid_element_index_from_position(self, position):

        i = position[0] // GRAPH_GRID_WIDTH
        j = position[1] // GRAPH_GRID_WIDTH

        return i, j

    def get_middle_position_from_grid_element_index(self, i, j):
        return (i * GRAPH_GRID_WIDTH) + (0.5 * GRAPH_GRID_WIDTH),  (j * GRAPH_GRID_WIDTH) + (0.5 * GRAPH_GRID_WIDTH)

    def get_edge_distance(self, source_index, destination_index):

        source_i, source_j = source_index
        destination_i, destination_j = destination_index

        return MAXIMUM_GRID_NODE_HEIGHT + (self.matrix[destination_i][destination_j] - self.matrix[source_i][source_j])

    def get_neighbours_indexes_from_element_index(self, index):

        i, j = index
        neighbours = []

        neighbours.append((i + 1, j))
        neighbours.append((i - 1, j))
        neighbours.append((i + 1, j + 1))
        neighbours.append((i - 1, j - 1))
        neighbours.append((i + 1, j - 1))
        neighbours.append((i - 1, j + 1))
        neighbours.append((i, j - 1))
        neighbours.append((i, j + 1))

        for neighbour_index in neighbours:
            neighbour_i, neighbour_j = neighbour_index
            if neighbour_i < 0 or neighbour_j < 0 or neighbour_i >= self.matrix_width \
                    or neighbour_j >= self.matrix_height:
                neighbours.remove((neighbour_i, neighbour_j))

        return neighbours
