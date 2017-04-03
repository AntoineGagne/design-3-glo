from itertools import chain
from operator import itemgetter

import os


def order_points(points):
    points = chain.from_iterable(points)
    points = sorted(points, key=itemgetter(1))
    top_points = sorted(points[:2], key=itemgetter(0))
    bottom_points = sorted(points[2:], key=itemgetter(0), reverse=True)
    return list(chain(top_points, bottom_points))


class StdErrOutputDisplayManager:
    def __init__(self):
        self.null_file_descriptor = os.open(os.devnull, os.O_RDWR)
        self.saved_file_descriptor = os.dup(2)

    def __enter__(self):
        os.dup2(self.null_file_descriptor, 2)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        os.dup2(self.saved_file_descriptor, 2)
