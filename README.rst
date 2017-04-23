A Python function logger
========================
funclog is a Python decorator to log debug information for all accesses to a
function or class method.

=====

Usage

-----

The most basic usage of the funclog decorator is simply to add it in front of
whatever function or class method that is to be logged::

    >>> import logging
    >>> from funclog.funclog import funclog
    >>> logging.basicConfig(level=logging.DEBUG)
    >>> @funclog
    ... def foo(a):
    ...     return a * 2
    ...
    >>> foo(3)
    DEBUG:root:calling <stdin>:1:foo(3)
    DEBUG:root:<stdin>:1:foo(3) returned: 6
    6


