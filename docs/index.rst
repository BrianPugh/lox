lox: threading made easy
========================

Many programs are `embaressingly parallel <https://en.wikipedia.org/wiki/Embarrassingly_parallel>`_ and can gain large performance boost by simply parallelizing portions of the code. However, multithreading a program is still typically seen as a difficult task and placed at the bottom of the TODO list. **lox** aims to make it as simple and intuitive as possible to parallelize functions in python. This includes both invoking functions, as well as providing easy-to-use guards for
shared resources.

A very simple example is as follows.

::

    >>> import lox
    >>> @lox.pool(4) # Will operate with a maximum of 4 threads
    >>> def foo(x,y):
    >>>     print("Foo: %d * %d" % (x,y))
    >>>     return x*y
    >>> 
    >>> foo(1)
    Foo: 3 * 4
    12
    >>> for i in range(5):
    >>>     foo.scatter(i, i+1)
    >>> 
    Foo: 0 * 1
    Foo: 1 * 2
    Foo: 2 * 3
    Foo: 3 * 4
    Foo: 4 * 5
    >>> results = foo.gather()
    >>> print(results)
    [0, 2, 6, 12, 20]


Features
========

* **Multithreading**: Powerful, intuitive multithreading in just 2 additional lines of code.

* **Synchronization**: Advanced thread synchronization, communication, and resource management tools.

Contents
========

.. toctree::
   :maxdepth: 2

   readme
   installation
   usage
   modules
   contributing
   authors
   history


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
