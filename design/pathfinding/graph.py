""" This module includes a graph represented by an adjacency matrix. Used for the robot's pathfinding. """
from design.pathfinding.constants import GRAPH_GRID_WIDTH


class Graph():

    def __init__(self):
        self.matrix = None

    def initialize_graph_matrix(self, southeastern_corner, northwestern_corner):

        table_width = northwestern_corner[0] - southeastern_corner[0]
        table_height = northwestern_corner[1] - southeastern_corner[1]

        self.matrix = [[0 for x in range(table_width // GRAPH_GRID_WIDTH)] for y in range(table_height // GRAPH_GRID_WIDTH)]

    def get_grid_element_index_from_position(self, position):

        i = position[0] // GRAPH_GRID_WIDTH
        j = position[1] // GRAPH_GRID_WIDTH

        return i, j

    def get_middle_position_from_grid_element_index(self, i, j):
        return (i * GRAPH_GRID_WIDTH) + (0.5 * GRAPH_GRID_WIDTH),  (j * GRAPH_GRID_WIDTH) + (0.5 * GRAPH_GRID_WIDTH)

    def get_edge_distance(self, source_index, destination_index):

        source_i, source_j = source_index
        destination_i, destination_j = destination_index

        return self.matrix[destination_i][destination_j] - self.matrix[source_i][source_j]

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
            if neighbour_i < 0 or neighbour_j < 0:
                neighbours.remove((neighbour_i, neighbour_j))

        return neighbours
