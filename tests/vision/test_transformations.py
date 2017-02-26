import numpy as np
import pytest

import design.vision.transformations as transformations


ANGLE_IN_DEGREE = 45
ANGLE_IN_RADIANS = np.pi / 4


@pytest.fixture
def square():
    return np.array([[[0, 0]],
                     [[5, 0]],
                     [[5, 5]],
                     [[0, 5]]])


def test_that_given_cartesian_coordinates_when_convert_to_homogeneous_coordinates_then_it_is_converted(square):
    homogeneous_square = transformations.convert_to_homogeneous_coordinates(square)
    assert np.array_equal(homogeneous_square, np.array([[[0, 0, 1]],
                                                        [[5, 0, 1]],
                                                        [[5, 5, 1]],
                                                        [[0, 5, 1]]]))


def test_that_given_homogeneous_coordinates_when_convert_to_cartesian_coordinates_then_it_is_converted(square):
    homogeneous_square = np.array([[[0, 0, 1]],
                                   [[5, 0, 1]],
                                   [[5, 5, 1]],
                                   [[0, 5, 1]]])
    assert np.array_equal(transformations.convert_to_cartesian_coordinates(homogeneous_square), square)


def test_that_given_coordinates_when_rotate_then_it_is_rotated(square):
    square_figure = transformations.Figure(square)
    rotate_transformation = transformations.RotateTransformation(ANGLE_IN_DEGREE)

    assert np.array_equal(square_figure.apply_transformations(rotate_transformation).coordinates,
                          np.array([[[2, -1]],
                                    [[6, 2]],
                                    [[2, 6]],
                                    [[-1, 2]]]))


def test_that_given_coordinates_and_angle_in_radian_when_rotate_then_it_is_rotated(square):
    square_figure = transformations.Figure(square)
    rotate_transformation = transformations.RotateTransformation(ANGLE_IN_RADIANS, True)

    assert np.array_equal(square_figure.apply_transformations(rotate_transformation).coordinates,
                          np.array([[[2, -1]],
                                    [[6, 2]],
                                    [[2, 6]],
                                    [[-1, 2]]]))


def test_that_given_coordinates_when_translate_then_it_is_translated(square):
    square_figure = transformations.Figure(square)
    translation_transformation = transformations.TranslateTransformation(5, 5)

    assert np.array_equal(square_figure.apply_transformations(translation_transformation).coordinates,
                          np.array([[[5, 5]],
                                    [[10, 5]],
                                    [[10, 10]],
                                    [[5, 10]]]))


def test_that_given_coordinates_when_scale_then_it_is_scaled(square):
    square_figure = transformations.Figure(square)
    scale_transformation = transformations.ScaleTransformation(2)

    assert np.array_equal(square_figure.apply_transformations(scale_transformation).coordinates,
                          np.array([[[-2, -2]],
                                    [[7, -2]],
                                    [[7, 7]],
                                    [[-2, 7]]]))
