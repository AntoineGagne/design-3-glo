"""Contain the exceptions related to numeric vision's errors."""


class VerticesNotFound(Exception):
    """Exception triggered when a figure's vertices could not be found."""
    pass


class PaintingFrameNotFound(Exception):
    """Exception triggered when a painting's frame could not be found."""
    pass


class GameMapNotFound(Exception):
    """Exception triggered when the game map could not be found"""
    print("One or many game map items could not be found")
    pass


class RobotNotFound(Exception):
    """Exception triggered when the game map could not be found"""
    pass
