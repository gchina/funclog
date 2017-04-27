"""
This module provides a decorator that can be added to any function to provide
debug output that shows the values of the arguments passed in as well as the
return value.  If a Logger object is passed in to the decorator, all debug
output will go to that Logger object.  Otherwise, the output will go to the
default Logger object.

Tip: If using the default Logger object, don't forget to set the logging level
     to DEBUG if you want to see output on stdout.

"""
import sys
import os
import functools
from logging import Logger, getLogger
import inspect


def funclog(logger):
    """A decorator function that provides debug input/output logging."""

    # If a Logger object is passed in, use that.  Otherwise, get the default
    # Logger.
    real_logger = logger if isinstance(logger, Logger) else getLogger()

    # __qualname__ is prettier but it didn't get added until 3.5
    name_attr = '__name__' if sys.version_info < (3, 5) else '__qualname__'

    def get_arg_string(args, kwargs):
        """Convert args and kwargs to a pretty string."""
        return ', '.join(["'{}'".format(a) if type(a) == str else
                          '{}'.format(a) for a in args] +
                         ["{}='{}'".format(a, v) if type(v) == str else
                          '{}={}'.format(a, v) for a, v in kwargs.items()])

    def real_decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            frame_info = inspect.getframeinfo(inspect.stack()[1][0])
            filename = os.path.basename(frame_info.filename)
            lineno = frame_info.lineno
            func_name = getattr(fn, name_attr)
            arg_string = get_arg_string(args, kwargs)
            source_info = '{}:{}:{}({})'.format(filename, lineno, func_name,
                                                arg_string)
            real_logger.debug(u'calling %s', source_info)
            try:
                res = fn(*args, **kwargs)
            except Exception as e:
                real_logger.exception(u'%s threw exception:\n%s',
                                      source_info, e)
                raise
            real_logger.debug(u'%s returned: %s', source_info, res)
            return res
        return wrapper

    if type(logger) == type(real_decorator):
        return real_decorator(logger)

    return real_decorator
