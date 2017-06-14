A Python function logger
========================
funclog is a Python decorator to log debug information for all accesses to a
function or class method.

------------
Installation
------------

Install via pip::

    pip install funclog

-----
Usage
-----

The most basic usage of the funclog decorator is simply to add it in front of
whatever function or class method that is to be logged.  This example file:

.. code:: python

    import logging
    from funclog import funclog

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s %(name)s %(levelname)s %(message)s')

    @funclog
    def foo(a):
        return a * 2

    foo(3)

will produce the following output using the root logger:

.. code::

    2017-04-26 20:01:43,384 root DEBUG calling example.py:11:foo(3)
    2017-04-26 20:01:43,384 root DEBUG example.py:11:foo(3) returned: 6


Other logger objects can be passed in as well as an argument to funclog():

.. code:: python

    import logging
    from funclog import funclog

    logger = logging.getLogger('test')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)-15s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    @funclog(logger)
    def foo(a):
        return a * 2

    foo(3)

will produce the following output using the logger named 'test':

.. code::

    2017-04-27 18:08:40,616 test DEBUG calling example.py:16:foo(3)
    2017-04-27 18:08:40,616 test DEBUG example.py:16:foo(3) returned: 6

The funclog() decorator will also work on class methods:

.. code:: python

    class Foo(object):
        @funclog(logger)
        def do_stuff(self, a):
            return a + 2

    foo = Foo()
    foo.do_stuff(3)

produces:

.. code::

    2017-04-27 18:23:02,748 test DEBUG calling example.py:24:Foo.do_stuff(<__main__.Foo object at 0x10560e240>, 3)
    2017-04-27 18:23:02,748 test DEBUG example.py:24:Foo.do_stuff(<__main__.Foo object at 0x10560e240>, 3) returned: 5

-------
License
-------
This project is licensed under the MIT License - see the LICENSE.txt file for details

