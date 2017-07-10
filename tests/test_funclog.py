"""
Unit tests for funclog decorator.

Currently the method tests expected output is formatted for Python >=3.5.
"""
from __future__ import absolute_import, print_function
import pytest
import logging
import sys
import inspect
from io import StringIO
from funclog import funclog


logfmt = '%(name)s %(levelname)s %(message)s'
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_formatter = logging.Formatter(logfmt)
root_buffer = StringIO()
root_handler = logging.StreamHandler(root_buffer)
root_handler.setFormatter(root_formatter)
root_logger.addHandler(root_handler)

log_buffer = StringIO()
logger = logging.getLogger('test')
logger.setLevel(logging.DEBUG)
fh = logging.StreamHandler(log_buffer)
fh.setFormatter(logging.Formatter(logfmt))
logger.addHandler(fh)


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
    @funclog(logger)
    def static_method(a, b):
        """Test static method."""
        return a - b

    @classmethod
    @funclog(logger)
    def class_method(cls, a, b):
        """Test class method."""
        return a * b


def test_simple_functions():
    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    linenum, _ = inspect.currentframe().f_lineno, bar()
    expected_buf = [
        u'root DEBUG calling test_funclog.py:{}:bar()'.format(linenum),
        u'root DEBUG test_funclog.py:{}:bar() returned: True'.format(linenum),
    ]
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf
    assert len(log_buffer.getvalue()) == 0

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    linenum, _ = inspect.currentframe().f_lineno, foo(12, 3, c=6)
    expected_buf = [
        u'test DEBUG calling test_funclog.py:{}:foo(12, 3, c=6)'.format(linenum),
        u'test DEBUG test_funclog.py:{}:foo(12, 3, c=6) returned: 6'.format(linenum),
    ]
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert temp_buf[0] == expected_buf[0]
    assert temp_buf[1].startswith(expected_buf[1])

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    with pytest.raises(TypeError):
        linenum = inspect.currentframe().f_lineno + 1
        foo(12, 3, c='hello')
    expected_buf = [
        u"test DEBUG calling test_funclog.py:{}:foo(12, 3, c='hello')".format(linenum),
        u"test ERROR test_funclog.py:{}:foo(12, 3, c='hello') threw exception:".format(linenum),
        u"unsupported operand type(s) for +: 'int' and 'str'"
    ]
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf[:3]
    temp_buf = log_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf[:3]

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    linenum, _ = inspect.currentframe().f_lineno, bar('a', 1)
    expected_buf = [
        u"root DEBUG calling test_funclog.py:{}:bar('a', 1)".format(linenum),
        u"root DEBUG test_funclog.py:{}:bar('a', 1) returned: False".format(linenum),
    ]
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf
    assert len(log_buffer.getvalue()) == 0

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    with pytest.raises(TypeError):
        linenum = inspect.currentframe().f_lineno + 1
        foo('a', 3)
    expected_buf = [
        u"test DEBUG calling test_funclog.py:{}:foo('a', 3)".format(linenum),
        u"test ERROR test_funclog.py:{}:foo('a', 3) threw exception:".format(linenum),
        u"unsupported operand type(s) for /: 'str' and 'int'"
    ]
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf[:3]
    temp_buf = log_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf[:3]

    # Testing kwargs-only arguments.  This is tricky because the kwargs
    # dictionary could be randomly re-ordered.
    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    linenum, _ = inspect.currentframe().f_lineno, bar(a='a', b=1)
    expected_buf = [
        u"root DEBUG calling test_funclog.py:{}:bar(a='a', b=1)".format(linenum),
        u"root DEBUG test_funclog.py:{}:bar(a='a', b=1) returned: False".format(linenum),
    ]
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf
    assert len(log_buffer.getvalue()) == 0

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    linenum, _ = inspect.currentframe().f_lineno, bar(a='a', b=foo)
    expected_buf = [
        u"root DEBUG calling test_funclog.py:{}:bar(a='a', b=<function foo at ".format(linenum),
        u"root DEBUG test_funclog.py:{}:bar(a='a', b=<function foo at ".format(linenum),
    ]
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert temp_buf[0].startswith(expected_buf[0])
    assert temp_buf[1].startswith(expected_buf[1])
    assert len(log_buffer.getvalue()) == 0

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    linenum, _ = inspect.currentframe().f_lineno, bar(a='a', b=foo(4, 2))
    expected_buf = [
        u"test DEBUG calling test_funclog.py:{}:foo(4, 2)".format(linenum),
        u"test DEBUG test_funclog.py:{}:foo(4, 2) returned: 2".format(linenum),
        u"root DEBUG calling test_funclog.py:{}:bar(a='a', b=2".format(linenum),
        u"root DEBUG test_funclog.py:{}:bar(a='a', b=2) returned: False".format(linenum),
    ]
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf[0] == temp_buf[0]
    assert temp_buf[1].startswith(expected_buf[1])
    assert temp_buf[2].startswith(expected_buf[2])
#    assert expected_buf[3] == temp_buf[3]


def test_simple_methods():
    root_buffer.truncate(0)
    root_buffer.seek(0)
    linenum, _ = inspect.currentframe().f_lineno, Foo().instance_method(1, 2)
    if sys.version_info < (3, 5):
        expected_buf = [
            "test DEBUG calling test_funclog.py:{}:instance_method(<test_funclog.Foo object at".format(linenum),
            "test DEBUG test_funclog.py:{}:instance_method(<test_funclog.Foo object at".format(linenum),
        ]
    else:
        expected_buf = [
            "test DEBUG calling test_funclog.py:{}:Foo.instance_method(<test_funclog.Foo object at".format(linenum),
            "test DEBUG test_funclog.py:{}:Foo.instance_method(<test_funclog.Foo object at".format(linenum),
        ]
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert temp_buf[0].startswith(expected_buf[0])
    assert temp_buf[1].startswith(expected_buf[1])

    root_buffer.truncate(0)
    root_buffer.seek(0)
    linenum, _ = inspect.currentframe().f_lineno, Foo.static_method(12, 3)
    if sys.version_info < (3, 5):
        expected_buf = [
            u"test DEBUG calling test_funclog.py:{}:static_method(12, 3)".format(linenum),
            u"test DEBUG test_funclog.py:{}:static_method(12, 3) returned: 9".format(linenum),
        ]
    else:
        expected_buf = [
            u"test DEBUG calling test_funclog.py:{}:Foo.static_method(12, 3)".format(linenum),
            u"test DEBUG test_funclog.py:{}:Foo.static_method(12, 3) returned: 9".format(linenum),
        ]
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf

    root_buffer.truncate(0)
    root_buffer.seek(0)
    linenum, _ = inspect.currentframe().f_lineno, Foo.class_method(5, 6)
    if sys.version_info < (3, 5):
        expected_buf = [
            u"test DEBUG calling test_funclog.py:{}:class_method(<class 'test_funclog.Foo'>, 5, 6)".format(linenum),
            u"test DEBUG test_funclog.py:{}:class_method(<class 'test_funclog.Foo'>, 5, 6) returned: 30".format(linenum),
        ]
    else:
        expected_buf = [
            u"test DEBUG calling test_funclog.py:{}:Foo.class_method(<class 'test_funclog.Foo'>, 5, 6)".format(linenum),
            u"test DEBUG test_funclog.py:{}:Foo.class_method(<class 'test_funclog.Foo'>, 5, 6) returned: 30".format(linenum),
        ]
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf
