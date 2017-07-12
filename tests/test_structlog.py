"""test structlog compatibility."""
from __future__ import absolute_import, print_function

import sys
import inspect

import structlog
from funclog import funclog


logger = structlog.PrintLogger(sys.stderr)


@funclog(logger)
def foo(a, b, c=None):
    """A simple function with args and kwargs."""
    return (a + c) / b if c else a / b


def test_simple_function_with_args_and_kwargs(caplog):
    """test."""
    linenum, _ = inspect.currentframe().f_lineno, foo(12, 3, c=6)
    exp_output = (
        'calling test_structlog.py:{}:foo(12, 3, c=6)'.format(linenum),
        'test_structlog.py:{}:foo(12, 3, c=6) returned: 6'.format(linenum),
    )
    for idx, exp in enumerate(exp_output):
        assert caplog.records[idx].name == 'root'
        assert caplog.records[idx].levelname == 'DEBUG'
        assert caplog.records[idx].message.startswith(exp)


@funclog
def bar(a=None, b=None):
    """A simple function with only kwargs."""
    return a == b


def test_simple_function_with_kwargs(caplog):
    """test."""
    linenum, _ = inspect.currentframe().f_lineno, bar(a='a', b=1)
    exp_output = (
        "calling test_structlog.py:{}:bar(a='a', b=1)".format(linenum),
        "test_structlog.py:{}:bar(a='a', b=1) returned: False".format(linenum),
    )
    for idx, exp in enumerate(exp_output):
        assert caplog.records[idx].name == 'root'
        assert caplog.records[idx].levelname == 'DEBUG'
        assert caplog.records[idx].message == exp


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
    if sys.version_info < (3, 5):
        signature = 'instance_method'
    else:
        signature = 'Foo.instance_method'
    exp_output = (
        'calling test_structlog.py:{}:{}(<test_structlog.Foo object at 0x'.format(linenum, signature),
        'test_structlog.py:{}:{}(<test_structlog.Foo object at 0x'.format(linenum, signature),
    )
    for idx, exp in enumerate(exp_output):
        assert caplog.records[idx].name == 'root'
        assert caplog.records[idx].levelname == 'DEBUG'
        assert caplog.records[idx].message.startswith(exp)
