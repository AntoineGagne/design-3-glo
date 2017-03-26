"""Useful functions for image processing."""

from itertools import chain
from operator import itemgetter

import os


def order_points(points):
    """Order the points so that they are in this order:
       Top-left, top-right, bottom-right, bottom-left

    :param points: The points to order
    :returns: The points in the previously specified order

    .. doctest::
        >>> points = [[[5, 5]], [[0, 5]], [[5, 0]], [[0, 0]]]
        >>> order_points(points)
        [[0, 0], [5, 0], [5, 5], [0, 5]]
    """
    points = chain.from_iterable(points)
    points = sorted(points, key=itemgetter(1))
    top_points = sorted(points[:2], key=itemgetter(0))
    bottom_points = sorted(points[2:], key=itemgetter(0), reverse=True)
    return list(chain(top_points, bottom_points))


class StdErrOutputDisplayManager:
    """Hide OpenCV's stderr output."""

    def __init__(self):
        """Initialize the manager."""
        self.null_file_descriptor = os.open(os.devnull, os.O_RDWR)
        self.saved_file_descriptor = os.dup(2)

    def __enter__(self):
        """Enter the context manager."""
        os.dup2(self.null_file_descriptor, 2)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """Exit the context manager.

        :param exception_type: The exception's type
        :param exception_value: The exception's value
        :param exception_traceback: The exception's traceback

        .. note:: Those exception parameters are all *None* if no exceptions
                  were raised. Also, since the exceptions are not handled, they
                  will propagate to the outer scope.
        """
        os.dup2(self.saved_file_descriptor, 2)
