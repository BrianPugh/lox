lox: Concurrency Made Easy
==========================

Many programs are `embaressingly parallel <https://en.wikipedia.org/wiki/Embarrassingly_parallel>`_ and can gain large performance boost by simply parallelizing portions of the code. However, multithreading a program is still typically seen as a difficult task and placed at the bottom of the TODO list. **lox** aims to make it as simple and intuitive as possible to parallelize functions and methods in python. This includes both invoking functions, as well as providing easy-to-use guards for
shared resources.

**lox** provides a simple, shallow learning-curve toolset to implement multithreading or multiprocessing that will work in most projects. **lox** is not meant to be the bleeding edge of performance; for absolute maximum performance, you code will have to be more fine tuned and may benefit from python3's builtin **asyncio**, **greenlet**, or other async libraries. **lox**'s primary goal is to provide that maximum concurrency performance in the least amount of time and the
smallest refactor.

A very simple example is as follows.

.. doctest::

    >>> import lox
    >>>
    >>> @lox.thread(4)  # Will operate with a maximum of 4 threads
    ... def foo(x, y):
    ...     return x * y
    ...
    >>> foo(3, 4)
    12
    >>> for i in range(5):
    ...     foo.scatter(i, i + 1)
    ...
    -ignore-
    >>> # foo is currently being executed in 4 threads
    >>> results = foo.gather()  # block until results are ready
    >>> print(results)  # Results are in the same order as scatter() calls
    [0, 2, 6, 12, 20]

Features
========

* **Multithreading**: Powerful, intuitive multithreading in just 2 additional lines of code.

* **Multiprocessing**: Truly parallel function execution with the same interface as **multithreading**.

* **Synchronization**: Advanced thread synchronization, communication, and resource management tools.


Contents
========

.. toctree::
   :maxdepth: 2

   installation
   modules
   examples

.. toctree::
   :maxdepth: 1

   FAQ
   contributing
   authors
   history


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
