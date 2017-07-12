"""Unit tests for funclog decorator."""
from __future__ import absolute_import, print_function
import sys
import logging
import inspect
import collections

import pytest
from funclog import funclog


logfmt = '%(name)s %(levelname)s %(message)s'
logging.basicConfig(format=logfmt, level=logging.DEBUG)
logger = logging.getLogger('abc')

Expected = collections.namedtuple('Expected', 'name level message')


@funclog(logger)
def foo(a, b, c=None):
    """A simple function with args and kwargs."""
    return (a + c) / b if c else a / b


@funclog
def bar(a=None, b=None):
    """A simple function with only kwargs."""
    return a == b


class Foo(object):
    """Test class with instance, static and class methods."""
    @funclog(logger)
    def instance_method(self, a, b):
        """Test instance method."""
        return a + b

    @staticmethod
    @funclog
    def static_method(a, b):
        """Test static method."""
        return a - b

    @classmethod
    @funclog(logger)
    def class_method(cls, a, b):
        """Test class method."""
        return a * b


def test_simple_function_with_no_args(caplog):
    linenum, _ = inspect.currentframe().f_lineno, bar()
    expected = (
        Expected(name='root',
                 level='DEBUG',
                 message='calling test_funclog.py:{}:bar()'.format(linenum)),
        Expected(name='root',
                 level='DEBUG',
                 message='test_funclog.py:{}:bar() returned: True'.format(linenum)),
    )
    for idx, exp in enumerate(expected):
        assert caplog.records[idx].name == exp.name
        assert caplog.records[idx].levelname == exp.level
        assert caplog.records[idx].message == exp.message


def test_simple_function_with_args_and_kwargs(caplog):
    linenum, _ = inspect.currentframe().f_lineno, foo(12, 3, c=6)
    expected = (
        Expected(name='abc',
                 level='DEBUG',
                 message='calling test_funclog.py:{}:foo(12, 3, c=6)'.format(linenum)),
        Expected(name='abc',
                 level='DEBUG',
                 message='test_funclog.py:{}:foo(12, 3, c=6) returned: 6'.format(linenum)),
    )
    for idx, exp in enumerate(expected):
        assert caplog.records[idx].name == exp.name
        assert caplog.records[idx].levelname == exp.level
        assert caplog.records[idx].message.startswith(exp.message)


def test_simple_function_with_typeerror(caplog):
    with pytest.raises(TypeError):
        linenum = inspect.currentframe().f_lineno + 1
        foo(12, 3, c='hello')
    expected = (
        Expected(name='abc',
                 level='DEBUG',
                 message="calling test_funclog.py:{}:foo(12, 3, c='hello')".format(linenum)),
        Expected(name='abc',
                 level='ERROR',
                 message="""test_funclog.py:{}:foo(12, 3, c='hello') threw exception:\nunsupported operand type(s) for +: 'int' and 'str'""".format(linenum)),
    )
    for idx, exp in enumerate(expected):
        assert caplog.records[idx].name == exp.name
        assert caplog.records[idx].levelname == exp.level
        assert caplog.records[idx].message == exp.message


def test_simple_function_with_other_args(caplog):
    linenum, _ = inspect.currentframe().f_lineno, bar('a', 1)
    expected = (
        Expected(name='root',
                 level='DEBUG',
                 message="calling test_funclog.py:{}:bar('a', 1)".format(linenum)),
        Expected(name='root',
                 level='DEBUG',
                 message="test_funclog.py:{}:bar('a', 1) returned: False".format(linenum)),
    )
    for idx, exp in enumerate(expected):
        assert caplog.records[idx].name == exp.name
        assert caplog.records[idx].levelname == exp.level
        assert caplog.records[idx].message == exp.message


def test_simple_function_with_another_typeerror(caplog):
    with pytest.raises(TypeError):
        linenum = inspect.currentframe().f_lineno + 1
        foo('a', 3)
    expected = (
        Expected(name='abc',
                 level='DEBUG',
                 message="calling test_funclog.py:{}:foo('a', 3)".format(linenum)),
        Expected(name='abc',
                 level='ERROR',
                 message="test_funclog.py:{}:foo('a', 3) threw exception:\nunsupported operand type(s) for /: 'str' and 'int'".format(linenum)),
    )
    for idx, exp in enumerate(expected):
        assert caplog.records[idx].name == exp.name
        assert caplog.records[idx].levelname == exp.level
        assert caplog.records[idx].message == exp.message


def test_simple_function_with_kwargs(caplog):
    linenum, _ = inspect.currentframe().f_lineno, bar(a='a', b=1)
    expected = (
        Expected(name='root',
                 level='DEBUG',
                 message="calling test_funclog.py:{}:bar(a='a', b=1)".format(linenum)),
        Expected(name='root',
                 level='DEBUG',
                 message="test_funclog.py:{}:bar(a='a', b=1) returned: False".format(linenum)),
    )
    for idx, exp in enumerate(expected):
        assert caplog.records[idx].name == exp.name
        assert caplog.records[idx].levelname == exp.level
        assert caplog.records[idx].message == exp.message


def test_simple_function_with_funcwargs(caplog):
    linenum, _ = inspect.currentframe().f_lineno, bar(a='a', b=foo)
    expected = (
        Expected(name='root',
                 level='DEBUG',
                 message="calling test_funclog.py:{}:bar(a='a', b=<function foo at 0x".format(linenum)),
        Expected(name='root',
                 level='DEBUG',
                 message="test_funclog.py:{}:bar(a='a', b=<function foo at 0x".format(linenum)),
    )
    for idx, exp in enumerate(expected):
        assert caplog.records[idx].name == exp.name
        assert caplog.records[idx].levelname == exp.level
        assert caplog.records[idx].message.startswith(exp.message)


def test_nested_functions(caplog):
    linenum, _ = inspect.currentframe().f_lineno, bar(a='a', b=int(foo(4, 2)))
    expected = (
        Expected(name='abc',
                 level='DEBUG',
                 message="calling test_funclog.py:{}:foo(4, 2)".format(linenum)),
        Expected(name='abc',
                 level='DEBUG',
                 message="test_funclog.py:{}:foo(4, 2) returned: 2".format(linenum)),
        Expected(name='root',
                 level='DEBUG',
                 message="calling test_funclog.py:{}:bar(a='a', b=2)".format(linenum)),
        Expected(name='root',
                 level='DEBUG',
                 message="test_funclog.py:{}:bar(a='a', b=2) returned: False".format(linenum)),
    )
    for idx, exp in enumerate(expected):
        assert caplog.records[idx].name == exp.name
        assert caplog.records[idx].levelname == exp.level
        assert caplog.records[idx].message.startswith(exp.message)


def test_instance_method(caplog):
    linenum, _ = inspect.currentframe().f_lineno, Foo().instance_method(1, 2)
    if sys.version_info < (3, 5):
        signature = 'instance_method'
    else:
        signature = 'Foo.instance_method'
    expected = (
        Expected(name='abc',
                 level='DEBUG',
                 message='calling test_funclog.py:{}:{}(<test_funclog.Foo object at 0x'.format(linenum, signature)),
        Expected(name='abc',
                 level='DEBUG',
                 message='test_funclog.py:{}:{}(<test_funclog.Foo object at 0x'.format(linenum, signature)),
    )
    for idx, exp in enumerate(expected):
        assert caplog.records[idx].name == exp.name
        assert caplog.records[idx].levelname == exp.level
        assert caplog.records[idx].message.startswith(exp.message)


def test_static_method(caplog):
    linenum, _ = inspect.currentframe().f_lineno, Foo.static_method(12, 3)
    if sys.version_info < (3, 5):
        signature = 'static_method'
    else:
        signature = 'Foo.static_method'
    expected = (
        Expected(name='root',
                 level='DEBUG',
                 message="calling test_funclog.py:{}:{}(12, 3)".format(linenum, signature)),
        Expected(name='root',
                 level='DEBUG',
                 message="test_funclog.py:{}:{}(12, 3) returned: 9".format(linenum, signature)),
    )
    for idx, exp in enumerate(expected):
        assert caplog.records[idx].name == exp.name
        assert caplog.records[idx].levelname == exp.level
        assert caplog.records[idx].message == exp.message


def test_class_method(caplog):
    linenum, _ = inspect.currentframe().f_lineno, Foo.class_method(5, 6)
    if sys.version_info < (3, 5):
        signature = 'class_method'
    else:
        signature = 'Foo.class_method'
    expected = (
        Expected(name='abc',
                 level='DEBUG',
                 message="calling test_funclog.py:{}:{}(<class 'test_funclog.Foo'>, 5, 6)".format(linenum, signature)),
        Expected(name='abc',
                 level='DEBUG',
                 message="test_funclog.py:{}:{}(<class 'test_funclog.Foo'>, 5, 6) returned: 30".format(linenum, signature)),
    )
    for idx, exp in enumerate(expected):
        assert caplog.records[idx].name == exp.name
        assert caplog.records[idx].levelname == exp.level
        assert caplog.records[idx].message.startswith(exp.message)
