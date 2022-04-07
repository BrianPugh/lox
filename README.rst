.. image:: assets/lox_200w.png


.. image:: https://img.shields.io/pypi/v/lox.svg
        :target: https://pypi.python.org/pypi/lox

.. image:: https://circleci.com/gh/BrianPugh/lox.svg?style=svg
        :target: https://circleci.com/gh/BrianPugh/lox

.. image:: https://readthedocs.org/projects/lox/badge/?version=latest
        :target: https://lox.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


Threading and multiprocessing made easy.


* Free software: Apache-2.0 license
* Documentation: https://lox.readthedocs.io.
* Python >=3.6


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

Or, for example, if you aren't allowed to directly decorate the function you
would like multithreaded/multiprocessed, you can just directly invoke the
decorator:

.. code-block:: pycon

    >>> # Lets say we don't have direct access to this function
    ... def foo(x, y):
    ...     return x * y
    ...
    >>>
    >>> def my_func():
    ...     foo_threaded = lox.thread(foo)
    ...     for i in range(5):
    ...         foo_threaded.scatter(i, i + 1)
    ...     results = foo_threaded.gather()
    ...     # foo is currently being executed in default 50 thread executor pool
    ...     return results
    ...


This also makes it easier to dynamically control the number of
thread/processes in the executor pool. The syntax is a little weird, but
this is just explicitly invoking a decorator that has optional arguments:

.. code-block:: pycon

    >>> # Set the number of executer threads to 10
    >>> foo_threaded = lox.thread(10)(foo)


Easy Multiprocessing
^^^^^^^^^^^^^^^^^^^^

.. code-block:: pycon

    >>> import lox
    >>>
    >>> @lox.process(4)  # Will operate with a pool of 4 processes
    ... def foo(x, y):
    ...     return x * y
    ...
    >>> foo(3, 4)  # normal function calls still work
    12
    >>> for i in range(5):
    ...     foo.scatter(i, i + 1)
    ...
    -ignore-
    >>> # foo is currently being executed in 4 processes
    >>> results = foo.gather()  # block until results are ready
    >>> print(results)  # Results are in the same order as scatter() calls
    [0, 2, 6, 12, 20]


Progress Bar Support (tqdm)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: pycon

    >>> import lox
    >>> from random import random
    >>> from time import sleep
    >>>
    >>> @lox.thread(2)
    ... def foo(multiplier):
    ...     sleep(multiplier * random())
    ...
    >>> for i in range(10):
    >>> foo.scatter(i)
    >>> results = foo.gather(tqdm=True)
    90%|████████████████████████████████▌        | 9/10 [00:03<00:00,  1.32it/s]
    100%|███████████████████████████████████████| 10/10 [00:06<00:00,  1.46s/it]
