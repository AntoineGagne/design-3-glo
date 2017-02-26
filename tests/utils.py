import os
import math


def compare_objects(object_1, object_2):
    """Compare two object for equality.

    :param object_1: The first object
    :param object_2: The second object
    :raises AssertionError: If the two object are not equal or not of the same
                            types
    """
    assert (isinstance(object_1, object_2.__class__) and
            object_1.__dict__ == object_2.__dict__)


def list_files(folder):
    """List all the files recursively within a given folder.

    :param folder: The folder to list
    :type folder: str
    :returns: A generator of the listed files
    .. Taken from:
       http://stackoverflow.com/questions/12420779/simplest-way-to-get-the-equivalent-of-find-in-python
    """
    for root, folders, files in os.walk(folder):
        for filename in files:
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

    def assert_equal(self, actual, expected, **kwargs):
        """Assert that the two values are equals. Otherwise, put them in the
           list of failures.

        :param actual: The actual value
        :param expected: The expected value
        :param kwargs: The parameters to log in the console
        """
        self._assertion_number += 1
        try:
            assert actual == expected
        except AssertionError:
            self._failures.append(dict(kwargs))

    def assert_below_threshold(self):
        """Assert that the percentage of failed images is below the expected
           value.

        :raises AssertionError: If the percentage of failed images is greater
                                than the expected value
        """
        percentage_failed = len(self._failures) / self._assertion_number
        print(self._pretty_print_failures())
        print(self._pretty_print_test_information())
        assert percentage_failed <= self._maximum_error_percentage

    def _pretty_print_failures(self):
        """Return a pretty printed version of the failures.

        :return: Pretty printed version of the failures
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

        :return: Pretty printed version of the test's information
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
    :return: The enclosed title
    :rtype: str
    """
    delimiter_length = math.floor((maximum_length - (len(title) + 2)) / 2)
    half_delimiter_block = delimiter * delimiter_length
    return ''.join(('\n\n',
                    half_delimiter_block,
                    ' {0} '.format(title.title()),
                    half_delimiter_block))
