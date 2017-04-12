""" This module includes a graph represented by an adjacency matrix. Used for the robot's pathfinding. """
import math
from design.pathfinding.constants import GRAPH_GRID_WIDTH, OBSTACLE_RADIUS, ROBOT_SAFETY_MARGIN, \
    MAXIMUM_GRID_NODE_HEIGHT, ROBOT_HALF_WIDTH


class Graph():

    def __init__(self):
        self.matrix = None
        self.matrix_width = 0
        self.matrix_height = 0
        self.obstacle_safe_radius = (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN) // GRAPH_GRID_WIDTH

    def initialize_graph_matrix(self, southeastern_corner, northwestern_corner, obstacle_list):

        table_width = northwestern_corner[0] - southeastern_corner[0]
        table_height = northwestern_corner[1] - southeastern_corner[1]

        self.convert_obstacle_position_to_index(obstacle_list)

        self.matrix_width = table_width // GRAPH_GRID_WIDTH
        self.matrix_height = table_height // GRAPH_GRID_WIDTH

        self.matrix = [[0 for y in range(self.matrix_height)] for x in range(self.matrix_width)]
        self.generate_potential_field_in_graph_matrix(obstacle_list)

    def convert_obstacle_position_to_index(self, obstacle_list):
        for obstacle in obstacle_list:
            obstacle[0] = self.get_grid_element_index_from_position(obstacle[0])

    def generate_potential_field_in_graph_matrix(self, obstacle_list):
        self.generate_impassable_zones_in_graph_matrix(obstacle_list)
        self.add_weight_in_graph_matrix()

    def generate_impassable_zones_in_graph_matrix(self, obstacle_list):
        self.add_walls_safety_margin()
        self.place_obstacles_in_matrix(obstacle_list)
        self.connect_obstacles_and_walls(obstacle_list)

    def add_walls_safety_margin(self):
        num_square = ROBOT_HALF_WIDTH // GRAPH_GRID_WIDTH + 1
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
                self.connect_obstacle_to_closest_impassable_zone(obstacle)

    def connect_obstacle_to_closest_impassable_zone(self, obstacle):
        i = self.determine_starting_row(obstacle)
        no_infinite_weight_in_row = True
        while no_infinite_weight_in_row:
            for j in range(obstacle[0][1] - self.obstacle_safe_radius, obstacle[0][1] + self.obstacle_safe_radius):
                if self.matrix[i][j] == math.inf:
                    no_infinite_weight_in_row = False
                else:
                    self.matrix[i][j] = math.inf
            i = self.move_to_next_row(i, obstacle[1])

    def determine_starting_row(self, obstacle):
        if obstacle[1] == "N":
            return max(obstacle[0][0] - self.obstacle_safe_radius - 1, 1)
        else:
            return min(obstacle[0][0] + self.obstacle_safe_radius, self.matrix_width-1)

    def move_to_next_row(self, current_row_index, obstacle_orientation):
        if obstacle_orientation == "N":
            return current_row_index - 1
        else:
            return current_row_index + 1

    def add_weight_in_graph_matrix(self):
        weight = math.inf
        while weight > GRAPH_GRID_WIDTH:
            self.propagate(weight)
            weight = self.decrement_weight(weight)

    def propagate(self, weight):
        next_weight = self.decrement_weight(weight)
        for i in range(self.matrix_width):
            for j in range(self.matrix_height):
                if self.matrix[i][j] == weight:
                    for neighbour_index in self.get_four_neighbours_indexes_from_element_index((i, j)):
                        if self.matrix[neighbour_index[0]][neighbour_index[1]] < next_weight:
                            self.matrix[neighbour_index[0]][neighbour_index[1]] = next_weight

    def decrement_weight(self, weight):
        assert(weight > 0)
        if weight == math.inf:
            return MAXIMUM_GRID_NODE_HEIGHT
        else:
            return weight - GRAPH_GRID_WIDTH

    def get_grid_element_index_from_position(self, position):

        i = position[0] // GRAPH_GRID_WIDTH
        j = position[1] // GRAPH_GRID_WIDTH

        return i, j

    def get_position_from_grid_element_index(self, i, j):
        return i * GRAPH_GRID_WIDTH,  j * GRAPH_GRID_WIDTH

    def get_edge_distance(self, source_index, destination_index):

        source_i, source_j = source_index
        destination_i, destination_j = destination_index

        distance = self.get_euclidian_distance(source_index, destination_index)

        weight_difference = self.matrix[destination_i][destination_j] - self.matrix[source_i][source_j]
        return self.matrix[destination_i][destination_j] + weight_difference + distance

    def get_eight_neighbours_indexes_from_element_index(self, element_index):
        # FIXME: this is a bad name because there can be less than 8 neighbours returned, but it shows which neighbours are considered
        element_i, element_j = element_index
        neighbours = []

        for i in range(element_i - 1, element_i + 2):
            for j in range(element_j - 1, element_j + 2):
                if i != element_i and j != element_j and self.is_index_inside_matrix((i, j)):
                    neighbours.append((i, j))

        return neighbours

    def get_four_neighbours_indexes_from_element_index(self, element_index):
        # FIXME: this is a bad name because there can be less than 4 neighbours returned, but it shows which neighbours are considered
        i, j = element_index
        neighbours = [(i, j-1), (i, j+1), (i-1, j), (i+1, j)]

        for neighbour in neighbours:
            if not self.is_index_inside_matrix(neighbour):
                neighbours.remove(neighbour)

        return neighbours

    def is_index_inside_matrix(self, index):
        return 0 <= index[0] < self.matrix_width and 0 <= index[1] < self.matrix_height

    def get_weight_of_element(self, element_index):
        return self.matrix[element_index[0]][element_index[1]]
