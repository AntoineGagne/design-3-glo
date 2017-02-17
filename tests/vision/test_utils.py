import design.vision.utils as utils


def test_that_given_unordered_points_when_order_points_then_points_are_ordered():
    some_points = [[[5, 5]], [[0, 5]], [[5, 0]], [[0, 0]]]
    ordered_points = utils.order_points(some_points)
    assert [[0, 0], [5, 0], [5, 5], [0, 5]] == ordered_points
