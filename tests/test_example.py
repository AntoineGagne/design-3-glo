import pytest


def foo(x):
    if x != 3:
        raise Exception('U don goofed m8')
    return x


def test_that_given_a_valid_x_when_fooing_then_it_returns_a_x():
    assert foo(3) == 3


def test_that_given_an_invalid_x_when_fooing_then_it_returns_an_exception():
    with pytest.raises(Exception):
        foo(2)
