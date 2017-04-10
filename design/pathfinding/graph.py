""" Generate the graph """

from design.pathfinding.constants import ROBOT_SAFETY_MARGIN
from design.pathfinding.constants import OBSTACLE_RADIUS
from design.pathfinding.constants import TABLE_X
from design.pathfinding.constants import TABLE_Y
import operator
import math


class Graph:
    def __init__(self, obstacles_list):
        """Initialize new graph """
        self.obstacles_list = obstacles_list
        self.graph_dict = {}
        self.list_of_inaccessible_nodes = []

    def generate_graph(self):
        """ Generate all connections between the nodes"""

        if ((len(self.obstacles_list) == 2) and (len(self.graph_dict) >= 4)) or (len(self.obstacles_list) > 2):
            node_dict_sorted = sorted(self.graph_dict)
            node_dict_sorted = sorted(node_dict_sorted, key=operator.itemgetter(1))
            i = 0
            while i <= (len(node_dict_sorted) - 4):
                node1 = node_dict_sorted[i]
                i += 1
                node2 = node_dict_sorted[i]
                i += 1
                node3 = node_dict_sorted[i]
                i += 1
                node4 = node_dict_sorted[i]
                i += 1
                if (node1[1] < node2[1]) and (node3[1] == node4[1]):
                    self.add_edge_of_graph(node2, node3)
                    self.add_edge_of_graph(node2, node4)
                if (node1[1] != node2[1]) and (node1[1] != node3[1]):
                    if (node2[1] <= node3[1]) and (node1[0] == node2[0]):
                        self.add_edge_of_graph(node2, node3)
                    else:
                        self.delete_edge_of_graph(node2, node4)
                        self.add_edge_of_graph(node3, node4)
                if (node1[1] == node2[1]) and (node3[1] == node4[1]) and (i <= (len(node_dict_sorted) - 2)):
                    x = node1[0]
                    i -= 2
                    node1 = node_dict_sorted[i]
                    i += 1
                    node2 = node_dict_sorted[i]
                    i += 1
                    node3 = node_dict_sorted[i]
                    i += 1
                    node4 = node_dict_sorted[i]
                    i += 1
                    if node3[1] != node4[1]:
                        self.add_edge_of_graph(node1, node3)
                        self.add_edge_of_graph(node2, node3)
                    if (node3[1] == node4[1]) and (node1[0] == x):
                        self.add_edge_of_graph(node1, node3)
                        self.add_edge_of_graph(node2, node3)
                        self.add_edge_of_graph(node1, node4)
                        self.add_edge_of_graph(node2, node4)
                i -= 2

    def generate_nodes_of_graph(self):
        """ Generating the list of nodes of the graph"""
        if len(self.obstacles_list) == 1:
            self.generate_nodes_of_graph_with_closed_obstacle(self.obstacles_list[0])
        if len(self.obstacles_list) == 2:
            self.generate_nodes_of_graph_with_two_obstacle(self.obstacles_list[0], self.obstacles_list[1])
        if len(self.obstacles_list) == 3:
            if (abs(self.obstacles_list[0][0][1] - self.obstacles_list[1][0][1]) > 46) and \
                    (abs(self.obstacles_list[1][0][1] - self.obstacles_list[2][0][1]) > 46) \
                    and (abs(self.obstacles_list[0][0][1] - self.obstacles_list[2][0][1]) > 46):
                self.generate_nodes_of_graph_with_closed_obstacle(self.obstacles_list[0])
                self.generate_nodes_of_graph_with_closed_obstacle(self.obstacles_list[1])
                self.generate_nodes_of_graph_with_closed_obstacle(self.obstacles_list[2])
            else:
                self.generate_nodes_of_graph_with_obstacle(self.obstacles_list[0])
                self.generate_nodes_of_graph_with_obstacle(self.obstacles_list[1])
                self.generate_nodes_of_graph_with_obstacle(self.obstacles_list[2])
        if len(self.obstacles_list) > 3:
            for obstacle in self.obstacles_list:
                self.generate_nodes_of_graph_with_obstacle(obstacle)

    def generate_nodes_of_graph_with_two_obstacle(self, first_obstacle, second_obstacle):
        """ Generating the list of nodes of the graph associated with two obstacle"""
        if abs(first_obstacle[0][1] - second_obstacle[0][1]) > 46:
            self.generate_nodes_of_graph_with_closed_obstacle(first_obstacle)
            self.generate_nodes_of_graph_with_closed_obstacle(second_obstacle)
        else:
            if first_obstacle[1] == "N" and second_obstacle[1] == "N":
                if (second_obstacle[0][0] - first_obstacle[0][0]) > 32:
                    self.generate_nodes_of_graph_with_closed_obstacle(first_obstacle)
                elif (second_obstacle[0][0] - first_obstacle[0][0]) < (-32):
                    self.generate_nodes_of_graph_with_closed_obstacle(second_obstacle)
                else:
                    if second_obstacle[0][0] > first_obstacle[0][0]:
                        self.generate_nodes_of_graph_with_closed_obstacle(second_obstacle)
                    if second_obstacle[0][0] <= first_obstacle[0][0]:
                        self.generate_nodes_of_graph_with_closed_obstacle(first_obstacle)

            elif first_obstacle[1] == "S" and second_obstacle[1] == "S":
                if (second_obstacle[0][0] - first_obstacle[0][0]) > 32:
                    self.generate_nodes_of_graph_with_closed_obstacle(second_obstacle)
                elif (second_obstacle[0][0] - first_obstacle[0][0]) < (-32):
                    self.generate_nodes_of_graph_with_closed_obstacle(first_obstacle)
                else:
                    if second_obstacle[0][0] > first_obstacle[0][0]:
                        self.generate_nodes_of_graph_with_closed_obstacle(first_obstacle)
                    if second_obstacle[0][0] <= first_obstacle[0][0]:
                        self.generate_nodes_of_graph_with_closed_obstacle(second_obstacle)
            elif (first_obstacle[1] == "N" and second_obstacle[1] == "S") or (
                    first_obstacle[1] == "S" and second_obstacle[1] == "N"):
                if (first_obstacle[1] == "S") and (first_obstacle[0][0] <= first_obstacle[0][0]):
                    if first_obstacle[0][0] > 32:
                        self.generate_nodes_of_graph_with_closed_obstacle(first_obstacle)
                    else:
                        self.generate_nodes_of_graph_with_closed_obstacle(second_obstacle)
            elif (first_obstacle[1] == "O") and (second_obstacle[1] == "O"):
                if ((second_obstacle[0][0] - first_obstacle[0][0]) > 32) and (first_obstacle[0][0] > 32):
                    self.generate_nodes_of_graph_with_obstacle(first_obstacle)
                elif ((first_obstacle[0][0] - second_obstacle[0][0]) > 32) and (second_obstacle[0][0] > 32):
                    self.generate_nodes_of_graph_with_obstacle(second_obstacle)
                else:
                    self.generate_nodes_of_graph_with_obstacle(second_obstacle)
            else:
                self.generate_nodes_of_graph_with_obstacle(first_obstacle)
                self.generate_nodes_of_graph_with_obstacle(second_obstacle)

    def generate_nodes_of_graph_with_obstacle(self, obstacle):
        """ Generating the list of nodes of the graph associated with the obstacle"""
        if obstacle[1] == "O":
            node1 = ((obstacle[0][0] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] - OBSTACLE_RADIUS))
            node2 = ((obstacle[0][0] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] + OBSTACLE_RADIUS))
            node3 = ((obstacle[0][0] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] - OBSTACLE_RADIUS))
            node4 = ((obstacle[0][0] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] + OBSTACLE_RADIUS))
            self.add_node_in_graph_dict(node1)
            self.add_node_in_graph_dict(node2)
            self.add_node_in_graph_dict(node3)
            self.add_node_in_graph_dict(node4)
            self.add_edge_of_graph(node1, node2)
            self.add_edge_of_graph(node3, node4)
        if obstacle[1] == "N":
            node1 = ((obstacle[0][0] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] - OBSTACLE_RADIUS))
            node2 = ((obstacle[0][0] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] + OBSTACLE_RADIUS))
            self.add_node_in_graph_dict(node1)
            self.add_node_in_graph_dict(node2)
            self.add_edge_of_graph(node1, node2)
        if obstacle[1] == "S":
            node1 = ((obstacle[0][0] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] - OBSTACLE_RADIUS))
            node2 = ((obstacle[0][0] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] + OBSTACLE_RADIUS))
            self.add_node_in_graph_dict(node1)
            self.add_node_in_graph_dict(node2)
            self.add_edge_of_graph(node1, node2)

    def generate_nodes_of_graph_with_closed_obstacle(self, obstacle):
        """ Generating the list of nodes of the graph associated with the obstacle"""
        if obstacle[1] == "O":
            node1 = ((obstacle[0][0] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN)))
            node2 = ((obstacle[0][0] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN)))
            node3 = ((obstacle[0][0] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN)))
            node4 = ((obstacle[0][0] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN)))
            self.add_node_in_graph_dict(node1)
            self.add_node_in_graph_dict(node2)
            self.add_node_in_graph_dict(node3)
            self.add_node_in_graph_dict(node4)
            self.add_edge_of_graph(node1, node2)
            self.add_edge_of_graph(node3, node4)
        if obstacle[1] == "N":
            node1 = ((obstacle[0][0] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN)))
            node2 = ((obstacle[0][0] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN)))
            self.add_node_in_graph_dict(node1)
            self.add_node_in_graph_dict(node2)
            self.add_edge_of_graph(node1, node2)
        if obstacle[1] == "S":
            node1 = ((obstacle[0][0] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN)))
            node2 = ((obstacle[0][0] - (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN + 2)), (obstacle[0][1] + (OBSTACLE_RADIUS + ROBOT_SAFETY_MARGIN)))
            self.add_node_in_graph_dict(node1)
            self.add_node_in_graph_dict(node2)
            self.add_edge_of_graph(node1, node2)

    def add_node_in_graph_dict(self, node):
        """ Add node in the dict nodes of graph """
        self.graph_dict[node] = []

    def add_edge_of_graph(self, node1, node2):
        """ connect two nodes """
        for node in self.graph_dict.keys():
            if node == node1:
                self.graph_dict[node1].append(node2)
            if node == node2:
                self.graph_dict[node2].append(node1)

    def delete_edge_of_graph(self, node1, node2):
        """ remove connection for two nodes """
        if node2 in self.graph_dict[node1]:
            self.graph_dict[node1].remove(node2)
        if node1 in self.graph_dict[node2]:
            self.graph_dict[node2].remove(node1)

    def add_start_end_node(self, start_node, checkpoint_node):
        self.add_node_in_graph_dict(start_node)
        self.add_node_in_graph_dict(checkpoint_node)
        self.add_edge_of_graph(start_node, self.search_nearest_node(start_node))
        self.add_edge_of_graph(checkpoint_node, self.search_nearest_node(checkpoint_node))

    def search_nearest_node(self, node):
        """" search """
        distance_min = 280
        nearest_node = (0, 0)
        for node_of_graph in self.graph_dict.keys():
            if (self.estimate_distance(node, node_of_graph) < distance_min) and (node_of_graph != node):
                nearest_node = node_of_graph
                distance_min = self.estimate_distance(node, node_of_graph)
        return nearest_node

    def estimate_distance(self, current_position, next_position):
        """ Calculate distance estimate """
        return math.sqrt(
            ((next_position[0] - current_position[0]) ** 2) + ((next_position[1] - current_position[1]) ** 2))

    def get_position_minimum_of_graph(self):
        """ """
        min = 230
        for node in self.graph_dict.keys():
            if node[1] < min:
                min = node[1]
        return min

    def set_zone_of_obstacles(self):
        """ Draw the area not accessible for all obstacles """
        for node in self.obstacles_list:
            self.draw_zone_obstacle(node)

    def draw_zone_obstacle(self, obstacle):
        """ Draw obstacle zone """
        total = ROBOT_SAFETY_MARGIN + OBSTACLE_RADIUS
        if obstacle[1] == "O":
            for x in range(obstacle[0][0] - total, obstacle[0][0] + total + 1):
                for y in range(obstacle[0][1] - total, obstacle[0][1] + total + 1):
                    self.list_of_inaccessible_nodes.append((x, y))
        if obstacle[1] == "S":
            for x in range(obstacle[0][0] - total, TABLE_X):
                for y in range(obstacle[0][1] - total, obstacle[0][1] + total + 1):
                    self.list_of_inaccessible_nodes.append((x, y))
        if obstacle[1] == "N":
            for x in range(0, obstacle[0][0] + total + 1):
                for y in range(obstacle[0][1] - total, obstacle[0][1] + total + 1):
                    self.list_of_inaccessible_nodes.append((x, y))

    def draw_wall(self):
        """ Draw the safety zone for the walls"""
        for x in range(TABLE_X):
            for y in range(TABLE_Y):
                if (x <= ROBOT_SAFETY_MARGIN) or (
                    x >= (TABLE_X - ROBOT_SAFETY_MARGIN)) or (
                        y <= ROBOT_SAFETY_MARGIN) or (y >= (TABLE_Y - ROBOT_SAFETY_MARGIN)):
                    self.list_of_inaccessible_nodes.append((x, y))
