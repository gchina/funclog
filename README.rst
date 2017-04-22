A Python function logger
========================
funclog is a Python decorator to log debug information for all accesses to a
function or class method.

=====

Usage

-----

The most basic usage of the funclog decorator is simply to add it in front of
whatever function or class method that is to be logged::

    @funclog
    def my_func(msg):
        print(msg)


