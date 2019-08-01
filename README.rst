.. image:: assets/lox_200w.png


.. image:: https://img.shields.io/pypi/v/lox.svg
        :target: https://pypi.python.org/pypi/lox

.. image:: https://circleci.com/gh/BrianPugh/lox.svg?style=svg
        :target: https://circleci.com/gh/BrianPugh/lox

.. image:: https://readthedocs.org/projects/lox/badge/?version=latest
        :target: https://lox.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/BrianPugh/lox/shield.svg
        :target: https://pyup.io/repos/github/BrianPugh/lox/
        :alt: Updates


Threading and multiprocessing made easy.


* Free software: MIT license
* Documentation: https://lox.readthedocs.io.


**Lox** provides decorators and synchronization primitives to quickly add 
concurrency to your projects.

Installation
------------

    pip3 install --user lox

Features
--------

* **Multithreading**: Powerful, intuitive multithreading in just 2 additional lines of code.

* **Multiprocessing**: Truly parallel function execution with the same interface as **multithreading**.

* **Synchronization**: Advanced thread synchronization, communication, and resource management tools.

Todos
-----

* All objects except ``lox.process`` are for threads. These will eventually be multiprocess friendly.

* Chaining of scatter calls to multiple worker pools

Usage
-----

Easy Multithreading
^^^^^^^^^^^^^^^^^^^

    >>> import lox
    >>>
    >>> @lox.thread(4) # Will operate with a maximum of 4 threads
    ... def foo(x,y):
    ...     return x*y
    >>> foo(3,4) # normal function calls still work
    12
    >>> for i in range(5):
    ...     foo.scatter(i, i+1)
    -ignore-
    >>> # foo is currently being executed in 4 threads
    >>> results = foo.gather() # block until results are ready
    >>> print(results) # Results are in the same order as scatter() calls
    [0, 2, 6, 12, 20]

Easy Multiprocessing
^^^^^^^^^^^^^^^^^^^^

    >>> import lox
    >>>
    >>> @lox.process(4) # Will operate with a pool of 4 processes
    ... def foo(x,y):
    ...     return x*y
    >>> foo(3,4) # normal function calls still work
    12
    >>> for i in range(5):
    ...     foo.scatter(i, i+1)
    -ignore-
    >>> # foo is currently being executed in 4 processes
    >>> results = foo.gather() # block until results are ready
    >>> print(results) # Results are in the same order as scatter() calls
    [0, 2, 6, 12, 20]

