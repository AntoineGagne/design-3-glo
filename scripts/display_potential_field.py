import cv2
import numpy as np
import math
from design.pathfinding.graph import Graph
from design.pathfinding.pathfinder import Pathfinder, RobotStatus
from design.pathfinding.constants import MAXIMUM_GRID_NODE_HEIGHT
from design.pathfinding.exceptions import CheckpointNotAccessibleError

if __name__ == "__main__":
    starting_point = (40, 25)
    destination = (23, 207)
    graph = Graph()
    obstacle_list = [[(40, 70), "N"], [(90, 120), "S"], [(30, 180), "N"]]
    print("Initializing potential field")
    graph.initialize_graph_matrix((0, 0), (111, 230), obstacle_list)

    hsv_img = np.zeros((graph.matrix_width, graph.matrix_height, 3), np.uint8)
    hsv_img[:, :] = (255, 255, 255)

    for i in range(graph.matrix_width):
        for j in range(graph.matrix_height):
            if graph.matrix[i][j] == math.inf:
                hsv_img[i, j] = (0, 0, 0)
            else:
                hsv_img[i, j] = (120 - (120 / MAXIMUM_GRID_NODE_HEIGHT) * graph.matrix[i][j], 255, 255)

    img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)

    pathfinder = Pathfinder(None)
    robotStatus = RobotStatus(starting_point, 90)
    pathfinder.graph = graph
    pathfinder.robot_status = robotStatus
    print("Calculating path")
    try:
        pathfinder.generate_path_to_checkpoint(destination)
        pathfinder.filtered_nodes_queue_to_checkpoint.appendleft(starting_point)
        pathfinder.filtered_nodes_queue_to_checkpoint.append(destination)

        for i in range(len(pathfinder.nodes_queue_to_checkpoint)):
            x, y = pathfinder.graph.get_grid_element_index_from_position(pathfinder.nodes_queue_to_checkpoint[i])
            cv2.rectangle(img, (y, x), (y + 1, x + 1), (255, 255, 255), 1)
            if i < len(pathfinder.nodes_queue_to_checkpoint) - 1:
                x2, y2 = pathfinder.graph.get_grid_element_index_from_position(
                    pathfinder.nodes_queue_to_checkpoint[i + 1])
                cv2.line(img, (y, x), (y2, x2), (255, 255, 255), 1)

        for i in range(len(pathfinder.filtered_nodes_queue_to_checkpoint)):
            x, y = pathfinder.graph.get_grid_element_index_from_position(pathfinder.filtered_nodes_queue_to_checkpoint[i])
            cv2.rectangle(img, (y, x), (y + 1, x + 1), (114, 37, 116), 1)
            if i < len(pathfinder.filtered_nodes_queue_to_checkpoint) - 1:
                x2, y2 = pathfinder.graph.get_grid_element_index_from_position(
                    pathfinder.filtered_nodes_queue_to_checkpoint[i + 1])
                cv2.line(img, (y, x), (y2, x2), (114, 37, 116), 1)
    except CheckpointNotAccessibleError:
        print("Checkpoint is not accessible!")

    resized = cv2.resize(img, None, fx=7, fy=7, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("Potential field", resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
