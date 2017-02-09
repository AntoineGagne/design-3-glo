def compare_objects(object_1, object_2):
    """Compare two object for equality.

    :param object_1: The first object
    :param object_2: The second object
    :raises AssertionError: If the two object are not equal or not of the same
                            types
    """
    assert isinstance(object_1, object_2.__class__)

    for attribute in object_1.__dict__.keys():
        assert object_1.__dict__.get(attribute) == object_2.__dict__.get(attribute)
