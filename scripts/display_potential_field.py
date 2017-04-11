import cv2
import numpy as np
import math
from design.pathfinding.graph import Graph
from design.pathfinding.constants import MAXIMUM_GRID_NODE_HEIGHT

if __name__ == "__main__":
    graph = Graph()
    obstacle_list = [[(80, 115), "N"], [(20, 115), "S"]]
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
    resized = cv2.resize(img, None, fx=5, fy=5, interpolation=cv2.INTER_LINEAR)
    cv2.imshow("Potential field", resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
