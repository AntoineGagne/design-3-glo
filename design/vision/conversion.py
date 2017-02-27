import numpy as np


def get_world_coordinates(camera_matrix, height, u, v):
    """
    :param camera_matrix: complete 3x4 camera matrix (extrinsic and intrinsic parameters combined)
    :param height: the object's height from which we want to find its coordinates
    :type height: int
    :param u: first coordinate of image object
    :type u: list
    :param v: second coordinate of image object
    :type v: list
    :return: tridimensionnal coordinates of the object
    :type: list
    """
    A1, A2 = ([] for l in range(2))
    A3 = [0, 0, 1, -height]
    for i in range(0, 4):
        A1.append(camera_matrix.item((0, i)) - u * camera_matrix.item((2, i)))
        A2.append(camera_matrix.item((1, i)) - v * camera_matrix.item((2, i)))
    n1 = np.array(A1[:3])
    n2 = np.array(A2[:3])
    n3 = np.array(A3[:3])
    P = (-A1[3] * (n2.dot(n3)) - -A2[3] * n3.dot(n1) - A3[3] * n1.dot(n2)) / n1.T * (n2.dot(n3))
    return P.tolist()
