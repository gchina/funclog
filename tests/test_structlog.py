"""test structlog compatibility."""
from __future__ import absolute_import, print_function
import pytest

import structlog
from funclog import funclog


logger = structlog.getLogger()


@funclog(logger)
def foo(a, b, c=None):
    """A simple function with args and kwargs."""
    return (a + c) / b if c else a / b


def test_simple_functions_with_args_and_kwargs(caplog):
    """test."""
    foo(12, 3, c=6)
    exp_output = (
        'calling test_structlog.py:20:foo(12, 3, c=6)',
        'test_structlog.py:20:foo(12, 3, c=6) returned: 6.0'
    )
    for idx, log in enumerate(caplog.records):
        assert log.message == exp_output[idx]


@funclog
def bar(a=None, b=None):
    """A simple function with only kwargs."""
    return a == b


def test_simple_functions_with_kwargs(caplog):
    """test."""
    bar(a='a', b=1)
    assert caplog.records[0].message in (
        "calling test_structlog.py:37:bar(a='a', b=1)",
        "calling test_structlog.py:37:bar(b=1, a='a')",
    )
    assert caplog.records[1].message in (
        "test_structlog.py:37:bar(a='a', b=1) returned: False",
        "test_structlog.py:37:bar(b=1, a='a') returned: False",
    )


class Foo(object):
    """Test class with instance, static and class methods."""

    @funclog(logger)
    def instance_method(self, a, b):
        """Test instance method."""
        return a + b

    @staticmethod
    @funclog(logger)
    def static_method(a, b):
        """Test static method."""
        return a - b

    @classmethod
    @funclog(logger)
    def class_method(cls, a, b):
        """Test class method."""
        return a * b


def test_instance_method(caplog):
    """test."""
    cls = Foo()
    cls.instance_method(1, 2)
    assert caplog.records[0].message.startswith(
        "calling test_structlog.py:72:Foo.instance_method(<test_structlog.Foo object at 0x")
    assert caplog.records[1].message.startswith(
        "test_structlog.py:72:Foo.instance_method(<test_structlog.Foo object at 0x")
