"""test structlog compatibility."""
from __future__ import absolute_import, print_function

import inspect

import structlog
from funclog import funclog


logger = structlog.getLogger()


@funclog(logger)
def foo(a, b, c=None):
    """A simple function with args and kwargs."""
    return (a + c) / b if c else a / b


def test_simple_functions_with_args_and_kwargs(caplog):
    """test."""
    linenum, _ = inspect.currentframe().f_lineno, foo(12, 3, c=6)
    exp_output = (
        'calling test_structlog.py:{}:foo(12, 3, c=6)'.format(linenum),
        'test_structlog.py:{}:foo(12, 3, c=6) returned: 6.0'.format(linenum),
    )
    for idx, log in enumerate(caplog.records):
        assert log.message == exp_output[idx]


@funclog
def bar(a=None, b=None):
    """A simple function with only kwargs."""
    return a == b


def test_simple_functions_with_kwargs(caplog):
    """test."""
    linenum, _ = inspect.currentframe().f_lineno, bar(a='a', b=1)
    assert caplog.records[0].message in (
        "calling test_structlog.py:{}:bar(a='a', b=1)".format(linenum),
        "calling test_structlog.py:{}:bar(b=1, a='a')".format(linenum),
    )
    assert caplog.records[1].message in (
        "test_structlog.py:{}:bar(a='a', b=1) returned: False".format(linenum),
        "test_structlog.py:{}:bar(b=1, a='a') returned: False".format(linenum),
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
    linenum, _ = inspect.currentframe().f_lineno, cls.instance_method(1, 2)
    assert caplog.records[0].message.startswith(
        "calling test_structlog.py:{}:Foo.instance_method(<test_structlog.Foo object at 0x".format(linenum))
    assert caplog.records[1].message.startswith(
        "test_structlog.py:{}:Foo.instance_method(<test_structlog.Foo object at 0x".format(linenum))
