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

    def get_edge_delta_weight(self, source_position, destination_position):

        source_i, source_j = self.get_grid_element_index_from_position(source_position)
        destination_i, destination_j = self.get_grid_element_index_from_position(destination_position)

        return self.matrix[destination_i][destination_j] - self.matrix[source_i][source_j]

    def get_vertex_weight(self, position):

        i, j = self.get_grid_element_index_from_position(position)
        return self.matrix[i][j]