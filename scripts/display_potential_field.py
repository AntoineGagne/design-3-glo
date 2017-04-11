import cv2
import numpy as np
import math
from design.pathfinding.graph import Graph
from design.pathfinding.pathfinder import Pathfinder, RobotStatus
from design.pathfinding.constants import MAXIMUM_GRID_NODE_HEIGHT

if __name__ == "__main__":
    graph = Graph()
    obstacle_list = [[(14, 125), "N"], [(76, 125), "O"]]
    graph.initialize_graph_matrix((0, 0), (111, 230), obstacle_list)
    pathfinder = Pathfinder(None)
    robotStatus = RobotStatus((90, 20), 90)
    pathfinder.graph = graph
    pathfinder.robot_status = robotStatus
    pathfinder.nodes_queue_to_checkpoint.clear()
    pathfinder.generate_path_to_checkpoint((90, 200))

    hsv_img = np.zeros((graph.matrix_width, graph.matrix_height, 3), np.uint8)
    hsv_img[:, :] = (255, 255, 255)

    for i in range(graph.matrix_width):
        for j in range(graph.matrix_height):
            if graph.matrix[i][j] == math.inf:
                hsv_img[i, j] = (0, 0, 0)
            else:
                hsv_img[i, j] = (120 - (120 / MAXIMUM_GRID_NODE_HEIGHT) * graph.matrix[i][j], 255, 255)

    img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
    for i in range(len(pathfinder.nodes_queue_to_checkpoint)-1):
        cv2.circle(img, pathfinder.nodes_queue_to_checkpoint[i], 1, (114, 37, 116), -1)
        cv2.line(img, pathfinder.nodes_queue_to_checkpoint[i], pathfinder.nodes_queue_to_checkpoint[i+1], (114, 37, 116), 1)
    cv2.circle(img, pathfinder.nodes_queue_to_checkpoint[-1], 1, (114, 37, 116), -1)
    resized = cv2.resize(img, None, fx=5, fy=5, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("Potential field", resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
