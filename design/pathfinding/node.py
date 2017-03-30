# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 22:41:48 2017

@author: IMEN
"""
import math


class Node(object):
    def __init__(self, x_position, y_position, distance, distance_estimate):
        """ Initialize new node """
        self.x_position = x_position
        self.y_position = y_position
        self.distance = distance
        self.distance_estimate = distance_estimate
        self.connected_nodes_list = []

    def add_node_in_connected_nodes_list(self, node):
        """ Add node in the list of connected nodes """
        self.connected_nodes_list.append(node)

    def update_distance(self, position):
        """ Update the distance """
        self.distance_estimate = self.distance + self.estimate(position)

    def estimate(self, position):
        """ Calculate distance estimate """
        return math.sqrt(
            (position.x - self.x_position) * (position.x - self.x_position) + (position.y - self.y_position) * (
                position.y - self.y_position))
