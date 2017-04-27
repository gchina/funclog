"""
Unit tests for funclog decorator.

Currently the method tests expected output is formatted for Python >=3.5.

TODO: Right now the expected line numbers are hard-coded, which is just stupid.

"""
from __future__ import absolute_import, print_function
import pytest
import logging
import sys
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
    expected_buf = [
        u'root DEBUG calling test_funclog.py:75:bar()',
        u'root DEBUG test_funclog.py:75:bar() returned: True'
    ]
    bar()
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf
    assert len(log_buffer.getvalue()) == 0

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    expected_buf = [
        u'test DEBUG calling test_funclog.py:88:foo(12, 3, c=6)',
        u'test DEBUG test_funclog.py:88:foo(12, 3, c=6) returned: 6'
    ]
    foo(12, 3, c=6)
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert temp_buf[0] == expected_buf[0]
    assert temp_buf[1].startswith(expected_buf[1])

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    expected_buf = [
        u"test DEBUG calling test_funclog.py:103:foo(12, 3, c='hello')",
        u"test ERROR test_funclog.py:103:foo(12, 3, c='hello') threw exception:",
        u"unsupported operand type(s) for +: 'int' and 'str'"
    ]
    with pytest.raises(TypeError):
        foo(12, 3, c='hello')
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf[:3]
    temp_buf = log_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf[:3]

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    expected_buf = [
        u"root DEBUG calling test_funclog.py:117:bar('a', 1)",
        u"root DEBUG test_funclog.py:117:bar('a', 1) returned: False"
    ]
    bar('a', 1)
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf
    assert len(log_buffer.getvalue()) == 0

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    expected_buf = [
        u"test DEBUG calling test_funclog.py:132:foo('a', 3)",
        u"test ERROR test_funclog.py:132:foo('a', 3) threw exception:",
        u"unsupported operand type(s) for /: 'str' and 'int'"
    ]
    with pytest.raises(TypeError):
        foo('a', 3)
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
    expected_buf = [
        u"root DEBUG calling test_funclog.py:148:bar(a='a', b=1)",
        u"root DEBUG test_funclog.py:148:bar(a='a', b=1) returned: False",
    ]
    bar(a='a', b=1)
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf
    assert len(log_buffer.getvalue()) == 0

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    expected_buf = [
        u"root DEBUG calling test_funclog.py:161:bar(a='a', b=<function foo at ",
        u"root DEBUG test_funclog.py:161:bar(a='a', b=<function foo at "
    ]
    bar(a='a', b=foo)
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert temp_buf[0].startswith(expected_buf[0])
    assert temp_buf[1].startswith(expected_buf[1])
    assert len(log_buffer.getvalue()) == 0

    root_buffer.truncate(0)
    root_buffer.seek(0)
    log_buffer.truncate(0)
    log_buffer.seek(0)
    expected_buf = [
        u"test DEBUG calling test_funclog.py:177:foo(4, 2)",
        u"test DEBUG test_funclog.py:177:foo(4, 2) returned: 2",
        u"root DEBUG calling test_funclog.py:177:bar(a='a', b=2",
        u"root DEBUG test_funclog.py:177:bar(a='a', b=2) returned: False",
    ]
    bar(a='a', b=foo(4, 2))
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf[0] == temp_buf[0]
    assert temp_buf[1].startswith(expected_buf[1])
    assert temp_buf[2].startswith(expected_buf[2])
#    assert expected_buf[3] == temp_buf[3]


def test_simple_methods():
    root_buffer.truncate(0)
    root_buffer.seek(0)
    if sys.version_info < (3, 5):
        expected_buf = [
            "test DEBUG calling test_funclog.py:198:instance_method(<test_funclog.Foo object at",
            "test DEBUG test_funclog.py:198:instance_method(<test_funclog.Foo object at"
        ]
    else:
        expected_buf = [
            "test DEBUG calling test_funclog.py:198:Foo.instance_method(<test_funclog.Foo object at",
            "test DEBUG test_funclog.py:198:Foo.instance_method(<test_funclog.Foo object at"
        ]
    Foo().instance_method(1, 2)
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert temp_buf[0].startswith(expected_buf[0])
    assert temp_buf[1].startswith(expected_buf[1])

    root_buffer.truncate(0)
    root_buffer.seek(0)
    if sys.version_info < (3, 5):
        expected_buf = [
            u"test DEBUG calling test_funclog.py:215:static_method(12, 3)",
            u"test DEBUG test_funclog.py:215:static_method(12, 3) returned: 9"
        ]
    else:
        expected_buf = [
            u"test DEBUG calling test_funclog.py:215:Foo.static_method(12, 3)",
            u"test DEBUG test_funclog.py:215:Foo.static_method(12, 3) returned: 9"
        ]
    Foo.static_method(12, 3)
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf

    root_buffer.truncate(0)
    root_buffer.seek(0)
    if sys.version_info < (3, 5):
        expected_buf = [
            u"test DEBUG calling test_funclog.py:231:class_method(<class 'test_funclog.Foo'>, 5, 6)",
            u"test DEBUG test_funclog.py:231:class_method(<class 'test_funclog.Foo'>, 5, 6) returned: 30",
        ]
    else:
        expected_buf = [
            u"test DEBUG calling test_funclog.py:231:Foo.class_method(<class 'test_funclog.Foo'>, 5, 6)",
            u"test DEBUG test_funclog.py:231:Foo.class_method(<class 'test_funclog.Foo'>, 5, 6) returned: 30",
        ]
    Foo.class_method(5, 6)
    temp_buf = root_buffer.getvalue().strip().split('\n')
    assert expected_buf == temp_buf
