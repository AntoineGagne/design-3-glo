"""Useful functions for image processing."""

from itertools import chain
from operator import itemgetter


def order_points(points):
    """Order the points so that they are in this order:
       Top-left, top-right, bottom-right, bottom-left

       :param points: The points to order
       :return: The points in the previously specified order
    """
    points = chain.from_iterable(points)
    points = sorted(points, key=itemgetter(1))
    top_points = sorted(points[:2], key=itemgetter(0))
    bottom_points = sorted(points[2:], key=itemgetter(0), reverse=True)
    return list(chain(top_points, bottom_points))
