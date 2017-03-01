import math
import os
import sys


def compare_objects(object_1, object_2):
    """Compare two object for equality.

    :param object_1: The first object
    :param object_2: The second object
    :raises AssertionError: If the two object are not equal or not of the same
                            types
    """
    assert (isinstance(object_1, object_2.__class__) and
            object_1.__dict__ == object_2.__dict__)


def list_files(folder, predicate=lambda _: True):
    """List all the files recursively within a given folder.

    :param folder: The folder to list
    :type folder: str
    :param predicate: A predicate to filter files
    :type predicate: function
    :returns: A generator of the listed files
    .. Taken from:
       http://stackoverflow.com/questions/12420779/simplest-way-to-get-the-equivalent-of-find-in-python
    """
    for root, folders, files in os.walk(folder):
        for filename in files:
            if predicate(filename):
                yield os.path.join(root, filename)


class ImageAssertionHelper:
    """Custom assert helper for images' tests."""

    def __init__(self, maximum_error_percentage: float=0.05):
        """Initialize the assert helper.

        :param maximum_error_percentage: The maximum percentage of errors that
                                         can be reached (default: 0.95)
        :type maximum_error_percentage: float
        """
        assert 0 < maximum_error_percentage < 1
        self._maximum_error_percentage = maximum_error_percentage
        self._failures = []
        self._assertion_number = 0

    def assert_equal(self, assertion_value, **kwargs):
        """Assert that the two values are equals. Otherwise, put them in the
           list of failures.

        :param assertion_value: The assertion value
        :type assertion_value: bool
        :param kwargs: The parameters to log in the console
        """
        self._assertion_number += 1
        try:
            assert assertion_value
        except AssertionError:
            self._failures.append(dict(kwargs))

    def assert_close(self, actual, expected, **kwargs):
        """Assert that the two values are close. Otherwise, put them in the
           list of failures.

        :param actual: The actual value
        :param expected: The expected value
        :param kwargs: The parameters to log in the console
        """
        self._assertion_number += 1
        try:
            assert calculate_norm(actual, expected) < 25
        except AssertionError:
            self._failures.append(dict(kwargs))

    def assert_all_close(self, actual, expected, **kwargs):
        """Assert that all the corresponding coordinates are close. Otherwise,
           put them in the list of failures.

        :param actual: The actual coordinates list
        :param expected: The expected coordinates list
        :param kwargs: The parameters to log in the console
        """
        self._assertion_number += 1
        corresponding_points = match_coordinates(actual, expected)

        try:
            for actual_coordinate, expected_coordinate in corresponding_points.items():
                norm = calculate_norm(actual_coordinate, expected_coordinate)
                assert norm <= 25
        except AssertionError:
            self._failures.append(dict(kwargs))

    def assert_below_threshold(self):
        """Assert that the percentage of failed images is below the expected
           value.

        :raises AssertionError: If the percentage of failed images is greater
                                than the expected value
        """
        percentage_failed = len(self._failures) / self._assertion_number
        print(self._pretty_print_failures(), file=sys.stderr)
        print(self._pretty_print_test_information(), file=sys.stderr)
        assert percentage_failed <= self._maximum_error_percentage

    def _pretty_print_failures(self):
        """Return a pretty printed version of the failures.

        :returns: Pretty printed version of the failures
        :rtype: str
        """
        failure_strings = [_pad_with_delimiter('Failed Pictures')]
        for failure in self._failures:
            for key, value in failure.items():
                failure_strings.append('{0} = {1}'.format(key, value))
            failure_strings.append('-' * 80)

        return '\n'.join(failure_strings)

    def _pretty_print_test_information(self):
        """Return a pretty printed version of the test's information.

        :returns: Pretty printed version of the test's information
        :rtype: str
        """
        percentage_failed = len(self._failures) / self._assertion_number
        information_strings = (
            _pad_with_delimiter('Percentage Failed'),
            'Total: {0}'.format(self._assertion_number),
            'Failed: {0}'.format(len(self._failures)),
            'Percentage failed: {0:.2%}'.format(percentage_failed)
        )
        return '\n'.join(information_strings)


def _pad_with_delimiter(title, maximum_length=80, delimiter='='):
    """Pad the given title with the specified delimiter for a maximum of the
       specified line length.

    :param title: The title to enclose with delimiters
    :param maximum_length: The maximum length of the string
    :param delimiter: The delimiter to use to enclose the title
    :returns: The enclosed title
    :rtype: str
    """
    delimiter_length = math.floor((maximum_length - (len(title) + 2)) / 2)
    half_delimiter_block = delimiter * delimiter_length
    return ''.join(('\n\n',
                    half_delimiter_block,
                    ' {0} '.format(title.title()),
                    half_delimiter_block))


def calculate_norm(point1, point2):
    """Calculate the distance between two points

    :param point1: first point
    :param point2: second point
    :type point1: tuple or list
    :type point2: tuple or list
    :returns: norm between the two points
    :rtype: float
    """
    norm = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
    return norm


def match_coordinates(coordinates1, coordinates2):
    """Match coordinates of two lists with equivalent number of coordinates.

    :param coordinates1: coordinates from first container
    :param coordinates2: coordinates from second container
    :type coordinates1: list or tuple
    :type coordinates2: list or tuple
    :returns:

    .. note:: If there's more or less coordinates in one of the lists, only the
              closest coordinates will be returned with minimal number of
              coordinates.
    """
    corresponding_points = {}
    already_matched_points = []
    for i in range(len(coordinates1)):
        minimal_norm = sys.maxsize
        for j in range(len(coordinates2)):
            if coordinates2[j] not in already_matched_points:
                norm = calculate_norm(coordinates1[i], coordinates2[j])
                if norm < minimal_norm:
                    minimal_norm = norm
                    corresponding_points[tuple(coordinates1[i])] = tuple(coordinates2[j])
        already_matched_points.append(tuple(corresponding_points[tuple(coordinates1[i])]))
    return corresponding_points
